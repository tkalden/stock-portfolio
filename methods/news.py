from finvizfinance.news import News
import requests
from bs4 import BeautifulSoup

def get_news():
    news = News()
    news = news.get_news()['news']
    return news



            
