from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import yfinance as yf


class StockDataToolInput(BaseModel):
    """Input schema for StockDataTool."""
    ticker: str = Field(..., description="Stock ticker symbol, e.g. 'AAPL' or 'MSFT'.")

class StockDataTool(BaseTool):
    name: str = "Stock Data Lookup"
    description: str = (
        "Fetches live market data for a single stock ticker from Yahoo Finance: "
        "current price, market cap, P/E, dividend yield, 52-week range, and "
        "1-month / 1-year price change. Use it to verify numbers for any stock you mention."
    )
    args_schema: Type[BaseModel] = StockDataToolInput

    def _run(self, ticker: str) -> str:
        ticker = ticker.strip().upper()
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            history = stock.history(period="1y")["Close"].dropna()
        except Exception as e:
            return f"Could not fetch data for {ticker}: {e}"

        if history.empty:
            return f"No price data found for ticker '{ticker}'. Check the symbol."

        last = history.iloc[-1]
        month_ago = history.iloc[max(-22, -len(history))]
        year_ago = history.iloc[0]
        dividend_yield = info.get("dividendYield")

        return "\n".join([
            f"{info.get('longName', ticker)} ({ticker})",
            f"Sector: {info.get('sector', 'n/a')}",
            f"Price: {last:.2f} {info.get('currency', '')}",
            f"Market cap: {info.get('marketCap', 'n/a')}",
            f"Trailing P/E: {info.get('trailingPE', 'n/a')}",
            f"Forward P/E: {info.get('forwardPE', 'n/a')}",
            f"Dividend yield: {f'{dividend_yield}%' if dividend_yield is not None else 'n/a'}",
            f"52-week range: {info.get('fiftyTwoWeekLow', 'n/a')} - {info.get('fiftyTwoWeekHigh', 'n/a')}",
            f"1-month change: {(last / month_ago - 1) * 100:.1f}%",
            f"1-year change: {(last / year_ago - 1) * 100:.1f}%",
        ])
