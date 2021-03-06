from bs4 import BeautifulSoup
import requests

FINVIZ_URL = "https://www.finviz.com/quote.ashx?t="

def download_ticker(tickr = "AMZN"):
    to_download_url = FINVIZ_URL + tickr
    req = requests.get(to_download_url, headers = {'user-agent': 'chrome'})
    response = req.text

    html = BeautifulSoup(response, 'html')
    news_table = html.find(id='news-table
    


download_ticker()