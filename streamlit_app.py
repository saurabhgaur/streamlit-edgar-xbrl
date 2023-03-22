import os
import streamlit as st
import pandas as pd
from sec_edgar_downloader import Downloader
from xbrl import XBRLParser


def download_financial_statements_xbrl(ticker, start_year, end_year, report_type):
    dl = Downloader()
    for year in range(start_year, end_year + 1):
        for quarter in range(1, 5):
            dl.get(report_type, ticker, amount=1,
                   after_date=f'{year}-{quarter * 3 - 2}-01')
            filename = f"{ticker}_{report_type}_{year}_Q{quarter}"
            os.makedirs(filename, exist_ok=True)
            os.rename('sec_edgar_filings', os.path.join(
                filename, 'sec_edgar_filings'))


def parse_financial_statements_xbrl(ticker, start_year, end_year, report_type):
    parser = XBRLParser()

    for year in range(start_year, end_year + 1):
        for quarter in range(1, 5):
            dir_name = f"{ticker}_{report_type}_{year}_Q{quarter}"
            xbrl_files = [os.path.join(root, name)
                          for root, dirs, files in os.walk(dir_name)
                          for name in files
                          if name.endswith((".xml", ".xsd"))]

            for xbrl_file in xbrl_files:
                try:
                    xbrl_obj = parser.parse(
                        open(xbrl_file, "r", encoding="utf-8"))

                    balance_sheet = parser.balance_sheet_to_dict(xbrl_obj)
                    income_statement = parser.income_statement_to_dict(
                        xbrl_obj)

                    if balance_sheet and income_statement:
                        st.write(
                            f"{report_type} for {ticker} - {year} Q{quarter}")
                        st.write("Balance Sheet")
                        st.write(pd.DataFrame.from_dict(
                            balance_sheet, orient='index'))
                        st.write("Income Statement")
                        st.write(pd.DataFrame.from_dict(
                            income_statement, orient='index'))

                except Exception as e:
                    print(f"Error parsing {xbrl_file}: {e}")


# Streamlit interface
st.title("EDGAR Financial Statements Downloader")
ticker = st.text_input("Enter the stock ticker of the company (e.g. AAPL)")
start_year = st.number_input(
    "Enter the start year (e.g. 2020)", min_value=1900, max_value=2100, step=1)
end_year = st.number_input(
    "Enter the end year (e.g. 2021)", min_value=1900, max_value=2100, step=1)
report_type = st.selectbox(
    "Select the financial statement to download", ["10-Q", "10-K"])

if st.button("Download and Parse"):
    if not ticker or start_year > end_year:
        st.warning("Please enter a valid stock ticker and year range.")
    else:
        download_financial_statements_xbrl(
            ticker, start_year, end_year, report_type)
        parse_financial_statements_xbrl(
            ticker, start_year, end_year, report_type)
