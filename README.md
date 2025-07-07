# Stock-market-analysis-using-ai
Here are the commands in order to make the code work (download these libraries in command promt or if using vscode in vscode terminal)
1.yfinance (Yahoo Finance API wrapper)
pip install yfinance
2.pandas (Data manipulation and analysis)
pip install pandas
(Often comes pre-installed with Anaconda or similar distributions, but good to run if you get errors.)
3.requests (For making HTTP requests to APIs like Finnhub)
pip install requests
(Also often pre-installed, but essential.)
4.plotly (For interactive charts)
pip install plotly
5.reportlab (For PDF generation)
pip install reportlab
6.openpyxl (Engine for reading/writing .xlsx Excel files with pandas)
pip install openpyxl
This is necessary for the download_sales_data_to_excel function, as pandas uses it in the background.
7.kaleido (Optional, for exporting Plotly charts as static images)
If you ever decide to export your interactive Plotly charts as static image files (like PNG, JPEG, SVG, PDF), you'll need kaleido. This isn't strictly required for the current interactive chart display but is very useful.
pip install kaleido
