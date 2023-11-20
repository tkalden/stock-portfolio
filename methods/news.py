from finvizfinance.news import News
import logging


def get_news():
    logging.info("Getting news");
    news = News()
    news = news.get_news()['news']
    logging.info("News %s",news.head(5))
    return news

            
