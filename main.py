import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from angel_login import get_smartconnect
from option_utils import get_atm_strike_price, get_option_symbol
import requests
import io

# Setup Page
st.set_page_config(page_title="Options Breakout Hunter", layout="wide")
st.title("📈 Options Breakout Hunter Dashboard")

# Login to SmartAPI
with st.spinner("Logging into Angel One SmartAPI..."):
    sc, auth_token, feed_token = get_smartconnect()


# Load all F&O stocks from Angel One CSV
@st.cache_data(ttl=3600)
def load_fo_stocks():
    url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.csv"
    content = requests.get(url).content
    df = pd.read_csv(io.StringIO(content.decode("utf-8")))
    df = df[(df["exch_seg"] == "NFO") & (df["name"] == "OPTSTK")]
    return df.drop_duplicates(subset="symbol")[["symbol", "token"]]


fo_stocks = load_fo_stocks()
st.write(f"Scanning top {len(fo_stocks)} F&O stocks")

breakouts = []

# Scan Breakouts
with st.spinner("Scanning for breakouts (5-min candles)..."):
    for _, row in fo_stocks.head(30).iterrows():  # You can increase the limit
        stock = row["symbol"]
        token = str(row["token"])
        from_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d 09:15")
        to_date = datetime.now().strftime("%Y-%m-%d %H:%M")

        try:
            data = sc.getCandleData(
                {
                    "exchange": "NSE",
                    "symboltoken": token,
                    "interval": "FIVE_MINUTE",
                    "fromdate": from_date,
                    "todate": to_date,
                }
            )

            df = pd.DataFrame(
                data["data"],
                columns=["Datetime", "Open", "High", "Low", "Close", "Volume"],
            )
            df["Datetime"] = pd.to_datetime(df["Datetime"])
            df.set_index("Datetime", inplace=True)

            prev_high = df.iloc[:-1]["High"].max()
            latest = df.iloc[-1]

            if latest["Close"] > prev_high:
                ltp = latest["Close"]
                strike = get_atm_strike_price(ltp)
                expiry = datetime.now().strftime("%d%b").upper()  # e.g., 13MAY
                option_symbol = get_option_symbol(stock, expiry, strike, "CE")

                breakouts.append(
                    {
                        "Stock": stock,
                        "LTP": ltp,
                        "Breakout": True,
                        "Prev High": prev_high,
                        "ATM Strike": strike,
                        "Option Symbol": option_symbol,
                    }
                )

        except Exception as e:
            st.error(f"Error fetching data for {stock}: {e}")

# Display Results
if breakouts:
    df_result = pd.DataFrame(breakouts)
    st.success("Breakout opportunities found!")
    st.dataframe(df_result)
else:
    st.warning("No breakouts found at the moment.")
