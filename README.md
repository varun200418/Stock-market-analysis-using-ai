# Stock-market-analysis-using-ai
This project is a Python-based interactive stock analysis tool designed to help users gather information, visualize data, and get basic "AI-like" conceptual insights into individual stocks and compare multiple stocks.

Here's a breakdown of what it does:

**Core Functionality:**

**Stock Symbol Resolution:**

It can take a company name (e.g., "Apple") or a ticker symbol (e.g., "AAPL") as input.

It uses the Finnhub API to search for and validate the correct ticker symbol, providing a list of possible matches if the input isn't a direct ticker.

**Company Details Display:**

Fetches and presents essential company information using the Finnhub API, such as:

Company Name

Exchange

Industry & Sector

Country

IPO Date

Market Capitalization

Shares Outstanding

Website and Contact Information

**Stock Analysis with Interactive Charting:**

Retrieves current (real-time or near real-time) stock prices using either Finnhub (preferred, if API key is set) or yfinance as a fallback.

Fetches historical price data (specifically, the 'Close' price for the last year) using yfinance.

Calculates common Simple Moving Averages (SMAs): the 20-day SMA and 50-day SMA.

**Generates an interactive Plotly chart that displays:**

The historical closing price of the stock.

The 20-day Simple Moving Average (SMA).

The 50-day Simple Moving Average (SMA).

This chart allows users to zoom, pan, and hover for detailed price information.

Provides a conceptual "AI Assistant's Market Signal Interpretation": This part analyzes the relationship between the current price and the moving averages (e.g., "Golden Cross," "Death Cross," price above/below SMAs) to give a basic bullish, bearish, or neutral outlook. It comes with a strong disclaimer emphasizing its simplified nature.

**Specific Buy/Sell Recommendation:**

Offers a more direct "BUY," "SELL," or "HOLD/NEUTRAL" recommendation based on the current price and the 20-day and 50-day SMAs, along with clear reasoning.

Crucially, this feature also includes a very prominent disclaimer to remind users that this is a simplified model and not financial advice.

**Annual Sales Data Download:**

Allows the user to specify a number of past years.

Fetches the annual revenue (sales) from the company's financial statements using yfinance.

Exports this data into an Excel file (.xlsx), making it easy for the user to review.

**Multiple Stock Comparison (Key Feature):**

Enables users to input multiple ticker symbols for comparison.

Generates a summary table showing key metrics for each selected stock side-by-side (Current Price, Market Cap, Industry, P/E Ratio, Dividend Yield).

Crucially, it generates an interactive Plotly chart that displays the normalized performance of all selected stocks over a chosen period (default: 1 year). This normalization means all stocks start at the same base (e.g., 1.0), allowing for direct comparison of their percentage gains or losses relative to each other, regardless of their initial price.

**Comprehensive Stock Report Generation:**

Consolidates various pieces of analysis (company details, current price, SMAs, AI recommendation summary, and a brief financial summary of sales data) into two formats:

A plain text file (.txt)

A formatted PDF document (.pdf) for easy sharing and readability.

Purpose of the Project:
