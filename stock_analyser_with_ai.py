import yfinance as yf
import pandas as pd
import datetime
import requests
import os
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# For PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

# --- Configuration ---
# IMPORTANT: Replace 'YOUR_FINNHUB_API_KEY_HERE' with your actual Finnhub API key.
FINNHUB_API_KEY = ''

# --- Data Fetching Functions ---

def get_current_price_realtime_api(ticker_symbol, api_key):
    """
    Fetches the real-time (or near real-time) price using Finnhub API.
    """
    if not api_key:
        return None

    url = f"https://finnhub.io/api/v1/quote?symbol={ticker_symbol}&token={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data and 'c' in data and data['c'] != 0:
            price = float(data['c'])
            return price
        elif 'error' in data:
            return None
        else:
            return None
    except requests.exceptions.HTTPError as e:
        # print(f"HTTP error fetching real-time price: {e}") # Suppress for cleaner output
        return None
    except requests.exceptions.ConnectionError as e:
        # print(f"Connection error fetching real-time price: {e}")
        return None
    except (ValueError, TypeError) as e:
        # print(f"Data parsing error fetching real-time price: {e}")
        return None
    except Exception as e:
        # print(f"An unexpected error occurred while fetching real-time price: {e}")
        return None

def get_company_profile_finnhub(ticker_symbol, api_key):
    """
    Fetches detailed company profile using Finnhub API.
    """
    if not api_key:
        return None

    url = f"https://finnhub.io/api/v1/stock/profile2?symbol={ticker_symbol}&token={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data and data != {}:
            return data
        elif 'error' in data:
            # print(f"Finnhub API error for company profile: {data.get('error')}")
            return None
        else:
            return None
    except requests.exceptions.HTTPError as e:
        # print(f"HTTP error fetching company profile: {e}")
        return None
    except requests.exceptions.ConnectionError as e:
        # print(f"Connection error fetching company profile: {e}")
        return None
    except (ValueError, TypeError) as e:
        # print(f"Data parsing error fetching company profile: {e}")
        return None
    except Exception as e:
        # print(f"An unexpected error occurred while fetching company profile: {e}")
        return None

def search_symbol_finnhub(query, api_key):
    """
    Searches for ticker symbols based on a query (company name or partial ticker).
    """
    if not api_key:
        print("Finnhub API key is not set. Cannot perform symbol search.")
        return []

    url = f"https://finnhub.io/api/v1/search?q={query}&token={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data and 'result' in data and data['result']:
            return data['result']
        else:
            # print(f"No results found for search query '{query}'.") # Suppress for cleaner output
            return []
    except requests.exceptions.HTTPError as e:
        # print(f"HTTP error during symbol search: {e}")
        return []
    except requests.exceptions.ConnectionError as e:
        # print(f"Connection error during symbol search: {e}")
        return []
    except (ValueError, TypeError) as e:
        # print(f"Data parsing error during symbol search: {e}")
        return []
    except Exception as e:
        # print(f"An unexpected error occurred during symbol search: {e}")
        return []

def get_current_price_yfinance(ticker_symbol):
    """
    Fetches the current market price using yfinance (near real-time).
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        price = info.get('currentPrice') or \
                info.get('regularMarketPrice') or \
                info.get('ask')

        if price:
            return price
        else:
            # print(f"No current price found in yfinance info for {ticker_symbol}.")
            return None
    except Exception as e:
        # print(f"Error fetching current price from yfinance for {ticker_symbol}: {e}")
        return None

def get_yfinance_info(ticker_symbol):
    """
    Fetches comprehensive stock information using yfinance's info attribute.
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        if not info:
            # print(f"No info found for {ticker_symbol} using yfinance.")
            return None
        return info
    except Exception as e:
        # print(f"Error fetching yfinance info for {ticker_symbol}: {e}")
        return None

def get_historical_data_yfinance(ticker_symbol, period="1y"):
    """
    Fetches historical stock data for a given ticker symbol using yfinance.
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        hist_data = stock.history(period=period)
        if hist_data.empty:
            # print(f"No historical data found for {ticker_symbol} for period {period}.")
            return None
        return hist_data
    except Exception as e:
        # print(f"Error fetching historical data for {ticker_symbol} with yfinance: {e}")
        return None

def get_annual_financials_yfinance(ticker_symbol):
    """
    Fetches annual financial statements (Income Statement) using yfinance.
    """
    try:
        stock = yf.Ticker(ticker_symbol)
        financials = stock.financials # This typically fetches annual data
        if financials.empty:
            print(f"No annual financial data found for {ticker_symbol}.")
            return None
        return financials
    except Exception as e:
        print(f"Error fetching annual financial data for {ticker_symbol} with yfinance: {e}")
        print("This might occur if the ticker is invalid or data is not available.")
        return None

# --- AI Assistant / Analysis Logic ---

def resolve_ticker_symbol(user_input_query): # Renamed parameter for clarity
    """
    Attempts to resolve a user's input (which might be a name or a ticker)
    into a valid ticker symbol using Finnhub search.
    """
    resolved_ticker = user_input_query.upper().strip()

    # Check if the directly entered ticker works (using Finnhub for real-time check)
    print(f"Attempting to validate '{resolved_ticker}' as a direct ticker...")
    test_price = get_current_price_realtime_api(resolved_ticker, FINNHUB_API_KEY)
    if test_price is not None:
        print(f"'{resolved_ticker}' recognized as a valid ticker with real-time data.")
        return resolved_ticker
    else:
        print(f"'{resolved_ticker}' does not appear to be a direct valid ticker symbol or no real-time data found for it. Attempting search...")


    confirm_search = input(f"Would you like me to search for a ticker symbol for '{user_input_query}'? (yes/no): ").lower().strip()
    if confirm_search != 'yes':
        print("Symbol search skipped. Please try again with a valid ticker if needed.")
        return None

    print(f"Searching for '{user_input_query}'...")
    search_results = search_symbol_finnhub(user_input_query, FINNHUB_API_KEY)

    if search_results:
        print("\n--- Possible Ticker Symbols Found ---")
        relevant_results = [
            r for r in search_results
            if r.get('type') in ['Common Stock', 'ADRC', 'ETP', 'Equity'] and r.get('symbol') # Filter for common stock types and ensure symbol exists
        ]

        if not relevant_results:
            print(f"No relevant stock ticker symbols found for '{user_input_query}'. Please try a different query or check the spelling.")
            return None

        for i, result in enumerate(relevant_results):
            print(f"{i+1}. Ticker: {result.get('symbol')}, Name: {result.get('description')}")

        while True:
            try:
                choice = input("Enter the number of the correct ticker, or '0' to try a different search/exit: ").strip()
                if choice == '0':
                    return None

                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(relevant_results):
                    return relevant_results[choice_idx]['symbol']
                else:
                    print("Invalid number. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    else:
        print(f"No ticker symbols found for '{user_input_query}'. Please try a different query or check the spelling.")
        return None


def display_company_details(ticker_symbol):
    """
    Fetches and displays detailed company information using Finnhub.
    """
    print(f"\n--- Company Details for: {ticker_symbol} ---")

    company_profile = get_company_profile_finnhub(ticker_symbol, FINNHUB_API_KEY)

    if company_profile:
        print(f"Company Name: {company_profile.get('name', 'N/A')}")
        print(f"Exchange: {company_profile.get('exchange', 'N/A')}")
        print(f"Industry: {company_profile.get('finnhubIndustry', 'N/A')}")
        print(f"Sector: {company_profile.get('gsector', 'N/A')}")
        print(f"Country: {company_profile.get('country', 'N/A')}")
        print(f"IPO Date: {company_profile.get('ipo', 'N/A')}")

        market_cap = company_profile.get('marketCapitalization')
        if isinstance(market_cap, (int, float)):
            print(f"Market Capitalization: ${market_cap:,.2f} M")
        else:
            print(f"Market Capitalization: {market_cap or 'N/A'}")

        shares_outstanding = company_profile.get('shareOutstanding')
        if isinstance(shares_outstanding, (int, float)):
            print(f"Shares Outstanding: {shares_outstanding:,.2f} M")
        else:
            print(f"Shares Outstanding: {shares_outstanding or 'N/A'}")

        print(f"Website: {company_profile.get('weburl', 'N/A')}")
        print(f"Phone: {company_profile.get('phone', 'N/A')}")
        print(f"Currency: {company_profile.get('currency', 'N/A')}")
        print(f"Employee Total: {company_profile.get('employeeTotal', 'N/A')}")
    else:
        print(f"Could not retrieve full company details for {ticker_symbol}.")
        print("This might be due to an invalid ticker, missing API key, or data not available for this ticker.")


def analyze_stock_and_advise(ticker_symbol):
    """
    Performs stock analysis: fetches current price (with API fallback),
    calculates SMAs, plots data using Plotly, and provides conceptual AI-like interpretation.
    """
    print(f"\n--- AI Stock Analysis for: {ticker_symbol} ---")

    current_price = None
    print("Attempting to fetch real-time price...")
    if FINNHUB_API_KEY:
        current_price = get_current_price_realtime_api(ticker_symbol, FINNHUB_API_KEY)

    if current_price is None:
        print("Finnhub real-time price not available or failed. Falling back to yfinance (may be slightly delayed)...")
        current_price = get_current_price_yfinance(ticker_symbol)

    if current_price:
        print(f"** Current Price: ${current_price:.2f} **")
    else:
        print("Could not retrieve current price for analysis. Proceeding with historical data if available.")

    df = get_historical_data_yfinance(ticker_symbol, period="1y")

    if df is not None and not df.empty:
        print("\nLast 5 days of historical data:")
        print(df.tail())

        if len(df) >= 50:
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()

            print("\nLatest Moving Averages (last 5 days):")
            print(df[['Close', 'SMA_20', 'SMA_50']].tail())

            # --- Plotting with Plotly ---
            print(f"\nGenerating interactive chart for {ticker_symbol}...")
            fig = go.Figure()

            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price',
                                     line=dict(color='blue', width=2)))
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], mode='lines', name='20-Day SMA',
                                     line=dict(color='orange', width=1, dash='dot')))
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], mode='lines', name='50-Day SMA',
                                     line=dict(color='red', width=1, dash='dash')))

            fig.update_layout(
                title=f'{ticker_symbol} Close Price with Moving Averages (1 Year)',
                xaxis_title='Date',
                yaxis_title='Price (USD)',
                hovermode="x unified", # Shows all traces at a single x-coordinate on hover
                xaxis_rangeslider_visible=True, # Adds a range slider at the bottom
                template="plotly_white" # A clean template
            )
            fig.show()
            # --- End Plotly Plotting ---


            print("\n--- AI Assistant's Market Signal Interpretation (Conceptual) ---")
            # The logic for AI signal interpretation remains the same.
            # (Keeping it concise for this example to avoid huge code block repetition)
            if len(df) > 50 and not pd.isna(df['SMA_20'].iloc[-1]) and not pd.isna(df['SMA_50'].iloc[-1]):
                last_sma_20 = df['SMA_20'].iloc[-1]
                last_sma_50 = df['SMA_50'].iloc[-1]
                prev_sma_20 = df['SMA_20'].iloc[-2] if len(df) > 51 else None
                prev_sma_50 = df['SMA_50'].iloc[-2] if len(df) > 51 else None

                signal = "Neutral"
                reason = []

                if prev_sma_20 is not None and prev_sma_50 is not None and \
                   not pd.isna(prev_sma_20) and not pd.isna(prev_sma_50):
                    if last_sma_20 > last_sma_50 and prev_sma_20 <= prev_sma_50:
                        signal = "Potential Buy"
                        reason.append("The 20-Day Simple Moving Average (SMA) has recently crossed above the 50-Day SMA (a 'Golden Cross'). This is often considered a bullish signal, indicating potential upward momentum.")
                    elif last_sma_20 < last_sma_50 and prev_sma_20 >= prev_sma_50:
                        signal = "Potential Sell"
                        reason.append("The 20-Day Simple Moving Average (SMA) has recently crossed below the 50-Day SMA (a 'Death Cross'). This is often considered a bearish signal, indicating potential downward momentum.")
                    else:
                        if last_sma_20 > last_sma_50:
                            reason.append("The 20-Day SMA is currently above the 50-Day SMA, suggesting a positive short-term trend relative to the medium-term.")
                        elif last_sma_20 < last_sma_50:
                            reason.append("The 20-Day SMA is currently below the 50-Day SMA, suggesting a negative short-term trend relative to the medium-term.")
                        else:
                            reason.append("The 20-Day and 50-Day SMAs are very close, indicating a period of consolidation or indecision.")
                else:
                    reason.append("Not enough previous SMA data to check for recent crossovers. Relying on current SMA positions.")
                    if last_sma_20 > last_sma_50:
                        reason.append("The 20-Day SMA is currently above the 50-Day SMA, suggesting a positive short-term trend relative to the medium-term.")
                    elif last_sma_20 < last_sma_50:
                        reason.append("The 20-Day SMA is currently below the 50-Day SMA, suggesting a negative short-term trend relative to the medium-term.")
                    else:
                        reason.append("The 20-Day and 50-Day SMAs are very close, indicating a period of consolidation or indecision.")


                if current_price:
                    if current_price > last_sma_20 and current_price > last_sma_50:
                        if "Buy" in signal:
                             reason.append(f"Additionally, the current price (${current_price:.2f}) is trading above both SMAs, reinforcing a bullish outlook.")
                        elif "Sell" not in signal:
                            signal = "Potential Buy" if signal == "Neutral" else signal
                            reason.append(f"The current price (${current_price:.2f}) is trading above both the 20-Day and 50-Day SMAs, which *conceptually* supports an upward trend.")
                    elif current_price < last_sma_20 and current_price < last_sma_50:
                        if "Sell" in signal:
                            reason.append(f"Additionally, the current price (${current_price:.2f}) is trading below both SMAs, reinforcing a bearish outlook.")
                        elif "Buy" not in signal:
                            signal = "Potential Sell" if signal == "Neutral" else signal
                            reason.append(f"The current price (${current_price:.2f}) is trading below both the 20-Day and 50-Day SMAs, which *conceptually* supports a downward trend.")
                    else:
                        reason.append(f"The current price (${current_price:.2f}) is hovering between the SMAs, suggesting a potentially mixed or indecisive short-term market.")
                else:
                    reason.append("Current real-time price could not be obtained, so analysis is based purely on historical moving averages.")

                print(f"\nBased on Moving Average analysis, the AI Assistant's conceptual signal is: **{signal}**")
                print("Reasoning:")
                for r in reason:
                    print(f"- {r}")

            else:
                print("Not enough complete historical data or valid SMA values to provide a detailed AI Assistant interpretation based on Moving Averages.")

            print("\nIMPORTANT DISCLAIMER:")
            print("--------------------")
            print("This 'AI Assistant' is a simplified demonstration based purely on basic technical indicators (Moving Averages).")
            print("It does NOT incorporate fundamental analysis, market news, volume, volatility, or advanced predictive models.")
            print("Stock market investments carry inherent risks, and past performance is not indicative of future results.")
            print("This interpretation is FOR EDUCATIONAL PURPOSES ONLY and should NOT be considered financial advice.")
            print("Always conduct your own thorough research and consult with a qualified financial advisor before making any investment decisions.")

        else:
            print("Not enough historical data (less than 50 days) to calculate 20-Day and 50-Day SMAs for detailed analysis.")
    else:
        print("Could not retrieve historical data for analysis. Cannot perform in-depth analysis.")
    return df, current_price # Return df and current_price for report generation


def provide_buy_sell_recommendation(ticker_symbol):
    """
    Provides a direct buy/sell/hold recommendation based on current price and SMAs.
    """
    print(f"\n--- AI Assistant's Buy/Sell Recommendation for: {ticker_symbol} ---")

    current_price = None
    if FINNHUB_API_KEY:
        current_price = get_current_price_realtime_api(ticker_symbol, FINNHUB_API_KEY)
    if current_price is None:
        current_price = get_current_price_yfinance(ticker_symbol)

    if current_price is None:
        print("Could not retrieve current price for a direct recommendation.")
        print("Please ensure the ticker symbol is correct and the market is open.")
        print("Cannot provide a direct buy/sell recommendation at this time.")
        return None, None # Return None for recommendation and reason

    df = get_historical_data_yfinance(ticker_symbol, period="1y")

    if df is None or df.empty or len(df) < 50:
        print("Not enough historical data to calculate reliable Moving Averages (at least 50 days needed).")
        print("Cannot provide a direct buy/sell recommendation at this time.")
        return None, None # Return None for recommendation and reason

    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()

    last_sma_20 = df['SMA_20'].iloc[-1]
    last_sma_50 = df['SMA_50'].iloc[-1]

    if pd.isna(last_sma_20) or pd.isna(last_sma_50):
        print("Moving Averages could not be calculated for the most recent period.")
        print("This might be due to insufficient recent historical data.")
        print("Cannot provide a direct buy/sell recommendation.")
        return None, None # Return None for recommendation and reason

    print(f"Current Price: ${current_price:.2f}")
    print(f"20-Day SMA: ${last_sma_20:.2f}")
    print(f"50-Day SMA: ${last_sma_50:.2f}")

    recommendation = "HOLD / NEUTRAL"
    reason = []

    if len(df) >= 51:
        prev_sma_20 = df['SMA_20'].iloc[-2]
        prev_sma_50 = df['SMA_50'].iloc[-2]

        if not pd.isna(prev_sma_20) and not pd.isna(prev_sma_50):
            if last_sma_20 > last_sma_50 and prev_sma_20 <= prev_sma_50:
                recommendation = "BUY (Strong Signal)"
                reason.append("The 20-Day SMA has recently crossed ABOVE the 50-Day SMA (a 'Golden Cross'), indicating strong bullish momentum.")
            elif last_sma_20 < last_sma_50 and prev_sma_20 >= prev_sma_50:
                recommendation = "SELL (Strong Signal)"
                reason.append("The 20-Day SMA has recently crossed BELOW the 50-Day SMA (a 'Death Cross'), indicating strong bearish momentum.")

    if current_price > last_sma_20 and current_price > last_sma_50:
        if "BUY" in recommendation:
            reason.append(f"Current price (${current_price:.2f}) is significantly above both SMAs, reinforcing bullish sentiment.")
        elif recommendation == "HOLD / NEUTRAL":
            recommendation = "BUY"
            reason.append(f"Current price (${current_price:.2f}) is above both the 20-Day and 50-Day SMAs, suggesting an upward trend.")
    elif current_price < last_sma_20 and current_price < last_sma_50:
        if "SELL" in recommendation:
            reason.append(f"Current price (${current_price:.2f}) is significantly below both SMAs, reinforcing bearish sentiment.")
        elif recommendation == "HOLD / NEUTRAL":
            recommendation = "SELL"
            reason.append(f"The current price (${current_price:.2f}) is below both the 20-Day and 50-Day SMAs, which *conceptually* supports a downward trend.")
    else:
        if recommendation == "HOLD / NEUTRAL":
            reason.append(f"Current price (${current_price:.2f}) is oscillating between the 20-Day and 50-Day SMAs, indicating a lack of clear direction or consolidation.")
        else:
            reason.append(f"Note: Current price (${current_price:.2f}) is currently between the 20-Day and 50-Day SMAs, indicating some short-term indecision despite longer-term SMA signals.")

    if not reason:
        reason.append("Based on the provided data, the stock's movement relative to its simple moving averages is currently unclear, leading to a neutral outlook.")

    print(f"\nAI Assistant's Recommendation: **{recommendation}**")
    print("Reasoning:")
    for r in reason:
        print(f"- {r}")

    print("\n\n--- EXTREMELY IMPORTANT DISCLAIMER ---")
    print("------------------------------------")
    print("This 'AI Assistant' provides a HIGHLY SIMPLIFIED recommendation based SOLELY on two common Moving Averages and current price.")
    print("This is NOT financial advice. It does NOT consider:")
    print("  - Company fundamentals (earnings, debt, management)")
    print("  - Broader market conditions (economy, sector trends)")
    print("  - Trading volume, volatility, or other technical indicators (RSI, MACD, Bollinger Bands, etc.)")
    print("  - News events or market sentiment")
    print("  - Your individual financial situation, risk tolerance, or investment goals.")
    print("\nStock markets are complex and inherently risky. Prices can move against predictions.")
    print("ALWAYS conduct thorough research and consult with a certified financial advisor before making any investment decisions.")
    print("You are solely responsible for your investment choices.")
    return recommendation, reason # Return for report generation


def download_sales_data_to_excel(ticker_symbol):
    """
    Fetches annual sales (revenue) data for a given ticker and exports it to an Excel file,
    allowing the user to specify the number of past years.
    """
    print(f"\n--- Downloading Annual Sales Data for: {ticker_symbol} ---")

    num_years_str = input("How many past years of annual sales data do you need? (e.g., 5 for the last 5 years): ").strip()
    try:
        num_years = int(num_years_str)
        if num_years <= 0:
            print("Please enter a positive number of years.")
            return
    except ValueError:
        print("Invalid input. Please enter a whole number for the number of years.")
        return

    print(f"Attempting to fetch annual financial statements (Income Statement) for the last {num_years} years...")

    financials_df = get_annual_financials_yfinance(ticker_symbol)

    if financials_df is not None and not financials_df.empty:
        # Transpose to have years as columns and metrics as rows
        financials_df_T = financials_df.T

        sales_data = pd.DataFrame()
        # Check for common sales/revenue keys
        if 'Total Revenue' in financials_df_T.columns:
            sales_data['Sales'] = financials_df_T['Total Revenue']
        elif 'Revenue' in financials_df_T.columns:
            sales_data['Sales'] = financials_df_T['Revenue']
        elif 'Sales' in financials_df_T.columns: # Less common, but good to have
            sales_data['Sales'] = financials_df_T['Sales']
        else:
            print(f"Could not find 'Total Revenue', 'Revenue', or 'Sales' in the financial statements for {ticker_symbol}.")
            print("Available financial metrics are:")
            print(financials_df_T.columns.tolist())
            return

        if not sales_data.empty:
            # yfinance's financials index is typically a DatetimeIndex
            # Filter the data for the last 'num_years'
            if len(sales_data) > num_years:
                sales_data = sales_data.tail(num_years)
            elif len(sales_data) < num_years:
                print(f"Warning: Only {len(sales_data)} years of sales data are available, less than the requested {num_years} years.")

            # Ensure index is sorted for display and export
            sales_data = sales_data.sort_index(ascending=True)

            # Define filename
            filename = f"{ticker_symbol}_Annual_Sales_Data_Last_{num_years}_Years.xlsx"

            try:
                sales_data.to_excel(filename, index=True) # index=True to keep the year/date
                print(f"Successfully downloaded annual sales data to '{filename}'")
                print(f"You can open this Excel file to view the company's sales value for the past {len(sales_data)} years.")
                print("\nSales data exported (last few rows shown):")
                print(sales_data.tail(max(5, len(sales_data)))) # Show up to 5 rows, or all if less than 5
            except Exception as e:
                print(f"Error saving sales data to Excel: {e}")
                print("Please ensure you have the 'openpyxl' engine installed: pip install openpyxl")
        else:
            print("No sales data could be extracted from the financial statements after filtering.")
    else:
        print(f"Could not retrieve annual financial data for {ticker_symbol}.")
        print("Please check the ticker symbol and your internet connection. Data might not be available for this company.")


def compare_stocks():
    """
    Allows users to compare multiple stocks side-by-side in a table and a normalized chart.
    """
    print("\n--- Compare Multiple Stocks ---")
    tickers_input = input("Enter ticker symbols separated by commas (e.g., AAPL,MSFT,GOOG): ").strip()
    ticker_symbols = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]

    if not ticker_symbols:
        print("No ticker symbols entered. Returning to main menu.")
        return

    if len(ticker_symbols) < 2:
        print("Please enter at least two ticker symbols for comparison.")
        return

    comparison_data = []
    historical_dfs = {}
    valid_tickers_for_chart = [] # To keep track of tickers with valid historical data for the chart

    print(f"Gathering data for: {', '.join(ticker_symbols)}")

    for ticker in ticker_symbols:
        data = {'Ticker': ticker}
        current_price = get_current_price_realtime_api(ticker, FINNHUB_API_KEY)
        if current_price is None:
            current_price = get_current_price_yfinance(ticker)
        data['Current Price'] = f"${current_price:,.2f}" if current_price else "N/A"

        profile = get_company_profile_finnhub(ticker, FINNHUB_API_KEY)
        if profile:
            market_cap = profile.get('marketCapitalization')
            if isinstance(market_cap, (int, float)):
                data['Market Cap (M)'] = f"${market_cap:,.2f}"
            else:
                data['Market Cap (M)'] = "N/A"
            data['Industry'] = profile.get('finnhubIndustry', 'N/A')
        else:
            data['Market Cap (M)'] = "N/A"
            data['Industry'] = "N/A"

        yf_info = get_yfinance_info(ticker)
        if yf_info:
            data['P/E Ratio'] = f"{yf_info.get('trailingPE', 'N/A'):.2f}" if yf_info.get('trailingPE') else "N/A"
            data['Dividend Yield'] = f"{yf_info.get('dividendYield', 0) * 100:.2f}%" if yf_info.get('dividendYield') else "N/A"
        else:
            data['P/E Ratio'] = "N/A"
            data['Dividend Yield'] = "N/A"

        comparison_data.append(data)

        # Get historical data for chart
        hist_df = get_historical_data_yfinance(ticker, period="1y")
        if hist_df is not None and not hist_df.empty and not hist_df['Close'].iloc[0] == 0:
            # Normalize price to 1 at the start of the period for comparison
            initial_close = hist_df['Close'].iloc[0]
            historical_dfs[ticker] = hist_df['Close'] / initial_close
            valid_tickers_for_chart.append(ticker) # Add to list if valid for chart
        else:
            print(f"Warning: No valid historical data for chart comparison for {ticker}.")

    comparison_df = pd.DataFrame(comparison_data)
    comparison_df = comparison_df.set_index('Ticker') # Set Ticker as index for better table display
    print("\n--- Stock Comparison Summary ---")
    print(comparison_df.to_string())

    # --- Interactive Chart for Normalized Performance ---
    if valid_tickers_for_chart:
        print("\nGenerating interactive performance comparison chart...")
        
        # Create a single DataFrame suitable for plotly.express.line
        # Melt the historical_dfs dictionary into a long format DataFrame
        # First, ensure all Series share a common index or merge them carefully
        
        # Find the common date range among all valid historical data
        common_dates = None
        for ticker in valid_tickers_for_chart:
            if common_dates is None:
                common_dates = historical_dfs[ticker].index
            else:
                common_dates = common_dates.intersection(historical_dfs[ticker].index)
        
        if common_dates.empty:
            print("No common historical date range found for chart comparison. Skipping chart.")
            return

        chart_df_list = []
        for ticker in valid_tickers_for_chart:
            # Re-normalize over the common_dates to ensure all start at 1.0 on the first common date
            temp_series = historical_dfs[ticker].loc[common_dates].sort_index()
            if not temp_series.empty and temp_series.iloc[0] != 0:
                normalized_series = temp_series / temp_series.iloc[0]
                chart_df_list.append(pd.DataFrame({
                    'Date': normalized_series.index,
                    'Normalized Price': normalized_series.values,
                    'Ticker': ticker
                }))

        if chart_df_list:
            final_chart_df = pd.concat(chart_df_list).reset_index(drop=True)
            
            fig = px.line(final_chart_df, x='Date', y='Normalized Price', color='Ticker',
                          title='Normalized Stock Performance (Last 1 Year)',
                          labels={'Normalized Price': 'Normalized Price (Starting at 1.0)', 'Date': 'Date'},
                          hover_name="Ticker", # Show ticker name on hover
                          template="plotly_white")
            
            fig.update_layout(hovermode="x unified") # Shows all traces at a single x-coordinate on hover
            fig.update_xaxes(rangeslider_visible=True) # Adds a range slider at the bottom
            fig.show()
        else:
            print("\nCould not prepare data for performance comparison chart.")
    else:
        print("\nCould not generate performance comparison chart due to lack of valid historical data for chosen tickers.")


def generate_stock_report(ticker_symbol):
    """
    Generates a comprehensive report for a given stock, saving it as a text file and PDF.
    """
    print(f"\n--- Generating Report for: {ticker_symbol} ---")

    report_content = []
    styles = getSampleStyleSheet()
    h1 = styles['h1']
    h2 = styles['h2']
    h3 = styles['h3']
    normal = styles['Normal']
    # Custom style for disclaimers
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=normal,
        fontSize=8,
        textColor=colors.red,
        leading=10,
        spaceBefore=6
    )


    report_content.append(Paragraph(f"Stock Analysis Report: {ticker_symbol}", h1))
    report_content.append(Paragraph(f"Date Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal))
    report_content.append(Spacer(1, 0.2 * inch))

    # --- Company Details ---
    report_content.append(Paragraph("1. Company Details", h2))
    company_profile = get_company_profile_finnhub(ticker_symbol, FINNHUB_API_KEY)
    if company_profile:
        details = [
            ["Company Name:", company_profile.get('name', 'N/A')],
            ["Exchange:", company_profile.get('exchange', 'N/A')],
            ["Industry:", company_profile.get('finnhubIndustry', 'N/A')],
            ["Country:", company_profile.get('country', 'N/A')],
            ["IPO Date:", company_profile.get('ipo', 'N/A')],
            ["Market Cap:", f"${company_profile.get('marketCapitalization', 'N/A'):,.2f} M" if isinstance(company_profile.get('marketCapitalization'), (int, float)) else "N/A"],
            ["Shares Outstanding:", f"{company_profile.get('shareOutstanding', 'N/A'):,.2f} M" if isinstance(company_profile.get('shareOutstanding'), (int, float)) else "N/A"],
            ["Website:", company_profile.get('weburl', 'N/A')]
        ]
        table_data = []
        for key, value in details:
            table_data.append([Paragraph(key, normal), Paragraph(str(value), normal)])

        report_content.append(Table(table_data, colWidths=[2*inch, 4*inch]))
    else:
        report_content.append(Paragraph(f"Could not retrieve full company details for {ticker_symbol}.", normal))
    report_content.append(Spacer(1, 0.2 * inch))

    # --- Price and Moving Averages ---
    report_content.append(Paragraph("2. Price and Technical Analysis", h2))
    df, current_price_for_report = analyze_stock_and_advise(ticker_symbol) # Call existing analysis logic
    report_content.append(Spacer(1, 0.1 * inch))

    if current_price_for_report:
        report_content.append(Paragraph(f"Current Price: ${current_price_for_report:.2f}", normal))
    else:
        report_content.append(Paragraph("Current price could not be retrieved.", normal))

    if df is not None and not df.empty and len(df) >= 50:
        last_sma_20 = df['SMA_20'].iloc[-1]
        last_sma_50 = df['SMA_50'].iloc[-1]
        report_content.append(Paragraph(f"20-Day SMA: ${last_sma_20:.2f}", normal))
        report_content.append(Paragraph(f"50-Day SMA: ${last_sma_50:.2f}", normal))
        report_content.append(Spacer(1, 0.1 * inch))

        # Re-run recommendation logic to get recommendation string and reasons
        recommendation, reasons = provide_buy_sell_recommendation(ticker_symbol)
        if recommendation and reasons:
            report_content.append(Paragraph(f"AI Assistant's Recommendation: <b>{recommendation}</b>", normal))
            report_content.append(Paragraph("Reasoning:", normal))
            for r in reasons:
                report_content.append(Paragraph(f"- {r}", normal))
        else:
            report_content.append(Paragraph("Could not provide a direct buy/sell recommendation due to insufficient data or errors.", normal))

    else:
        report_content.append(Paragraph("Not enough historical data to perform full technical analysis or generate SMAs.", normal))
    report_content.append(Spacer(1, 0.2 * inch))

    # --- Financials Summary (Example: Last 3 Years Sales) ---
    report_content.append(Paragraph("3. Financials Summary (Last 3 Years Sales)", h2))
    financials_df = get_annual_financials_yfinance(ticker_symbol)
    if financials_df is not None and not financials_df.empty:
        financials_df_T = financials_df.T
        sales_data = pd.DataFrame()
        if 'Total Revenue' in financials_df_T.columns:
            sales_data['Sales'] = financials_df_T['Total Revenue']
        elif 'Revenue' in financials_df_T.columns:
            sales_data['Sales'] = financials_df_T['Revenue']
        elif 'Sales' in financials_df_T.columns:
            sales_data['Sales'] = financials_df_T['Sales']

        if not sales_data.empty:
            sales_data_filtered = sales_data.sort_index(ascending=True).tail(3)
            # Format sales data for table
            sales_table_data = [['Year', 'Sales']]
            for index, row in sales_data_filtered.iterrows():
                sales_table_data.append([str(index.year), f"${row['Sales']:,.0f}"]) # Format as currency, no decimals

            sales_table = Table(sales_table_data, colWidths=[1.5*inch, 2.5*inch])
            sales_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            report_content.append(sales_table)
        else:
            report_content.append(Paragraph("No sales data available for summary.", normal))
    else:
        report_content.append(Paragraph("Could not retrieve annual financial data for summary.", normal))
    report_content.append(Spacer(1, 0.2 * inch))

    # --- Disclaimer ---
    report_content.append(Paragraph("IMPORTANT DISCLAIMER:", styles['h3']))
    disclaimer_text = """
    This report is generated by an AI assistant for informational and educational purposes only.
    It relies on publicly available data and simplified technical indicators (Moving Averages).
    It does NOT constitute financial advice. Investing in the stock market involves significant risks,
    and past performance is not indicative of future results. Before making any investment decisions,
    it is crucial to conduct your own thorough research, consider all relevant market factors,
    and consult with a qualified and licensed financial advisor. The AI assistant does not consider
    your individual financial situation, risk tolerance, or investment objectives.
    You are solely responsible for your investment choices.
    """
    report_content.append(Paragraph(disclaimer_text, disclaimer_style))


    # --- Save as Text File ---
    text_filename = f"{ticker_symbol}_Stock_Report.txt"
    try:
        with open(text_filename, 'w') as f:
            for item in report_content:
                if isinstance(item, Paragraph):
                    f.write(item.text + "\n\n")
                elif isinstance(item, Spacer):
                    f.write("\n")
                elif isinstance(item, Table):
                    # Simple representation for text file
                    # Extract header
                    header = [p.text for p in item.data[0]] if item.data else []
                    # Extract rows and convert Paragraphs to text
                    rows = []
                    for row_data in item.data[1:]:
                        rows.append([p.text if isinstance(p, Paragraph) else str(p) for p in row_data])
                    
                    if header and rows:
                        f.write("\n" + pd.DataFrame(rows, columns=header).to_string(index=False) + "\n\n")
                    elif rows: # If no header, just print rows
                        f.write("\n" + pd.DataFrame(rows).to_string(index=False, header=False) + "\n\n")

        print(f"Basic stock report saved as text file: '{text_filename}'")
    except Exception as e:
        print(f"Error saving text report: {e}")

    # --- Save as PDF ---
    pdf_filename = f"{ticker_symbol}_Stock_Report.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    try:
        doc.build(report_content)
        print(f"Detailed stock report saved as PDF: '{pdf_filename}'")
    except Exception as e:
        print(f"Error generating PDF report: {e}")
        print("Please ensure you have 'ReportLab' installed: pip install reportlab")


# Main execution block
if __name__ == "__main__":
    print("Welcome to the AI Stock Analyzer!")
    print("This tool provides conceptual market signals and company details.")
    print("Remember: This is for educational purposes only and not financial advice.")
    while True:
        choice = input("\nWhat would you like to do?\n1. Analyze a stock (price, charts, general signal)\n2. Get company details\n3. Get specific Buy/Sell recommendation\n4. Download Annual Sales Data to Excel\n5. Compare Multiple Stocks\n6. Generate a Basic Stock Report\n7. Exit\nEnter your choice (1, 2, 3, 4, 5, 6, or 7): ").strip()

        if choice in ['1', '2', '3', '4', '5', '6']:
            if choice == '5': # Compare Multiple Stocks does not need an initial single ticker
                compare_stocks()
                continue # Go back to main loop after comparison
            
            user_input_ticker = input("Enter stock ticker symbol (e.g., AAPL, RELIANCE.NS) or company name (e.g., Apple, Apollo): ").strip()
            if not user_input_ticker:
                print("Input cannot be empty. Please try again.")
                continue

            resolved_ticker = resolve_ticker_symbol(user_input_ticker)

            if resolved_ticker:
                if choice == '1':
                    analyze_stock_and_advise(resolved_ticker)
                elif choice == '2':
                    display_company_details(resolved_ticker)
                elif choice == '3':
                    provide_buy_sell_recommendation(resolved_ticker)
                elif choice == '4':
                    download_sales_data_to_excel(resolved_ticker)
                elif choice == '6':
                    generate_stock_report(resolved_ticker)
            else:
                print("Could not resolve a valid ticker symbol. Please try again with a more specific input.")

        elif choice == '7':
            print("Exiting AI Stock Analyzer. Happy investing (responsibly)!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, or 7.")