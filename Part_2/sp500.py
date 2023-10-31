import bs4 as bs
import requests


def get_sp500_tickers(amount: int):
    """Gets specified amount of sp500 stocks by scraping Wikipedia table"""
    # Request the table of S&P500 companies from Wikipedia and "scrape" it of the page
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})

    # Create empty list of tickers
    tickers = list()

    # Find a ticker in each row and put it in the tickers list
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)

    # Remove all the newlines from the list
    tickers = [s.replace('\n', '') for s in tickers]

    # Return the specified amount of tickers in a list
    return tickers[:amount]

