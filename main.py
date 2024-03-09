import logging
import threading
from threading import Thread

import pandas as pd
from flask import Blueprint, flash, render_template, request
from flask_login import current_user, login_required

import enums.enum as enum
import methods.news as news
import utilities.helper as helper
from __init__ import create_app
from methods.chart import chart
from methods.portfolio import portfolio as buildPortfolio
from methods.sourceDataMapper import SourceDataMapperService
from methods.stock import stock

main = Blueprint('main', __name__)

stock = stock()
buildPortfolio = buildPortfolio()
chart = chart()

@main.route('/', methods=['POST','GET'])
def home():
   news_df = news.get_news();
   return render_template('home.html', news_df = news_df)

@main.route('/profile', methods=['POST','GET'])
@login_required
def profile():
   return render_template('profile.html',name = current_user.name)

@main.route('/screener', methods=["GET","POST"])
def screener():
 if request.method == 'POST': 
    if request.form["btn"]=="Search":
        sector = request.form.get('sector')
        index = request.form.get('index')
        stock.update_key_sector_and_index(sector = sector, index=index)
 return render_template('screener.html', index_sector_lists = helper.index_sector(), title = stock.get_title())

@main.route('/portfolio', methods=["GET","POST"])
@login_required
def build():
    stock_data = stock.get_sp500_data()
    ticker_list = sorted(list(set(stock_data["Ticker"])))
    total_portfolio_return = 0
    total_portfolio_risk = 0
    portfolio = pd.DataFrame()
    if request.method == 'POST':
        if request.form["btn"]=="Build":
            strength_df = stock.update_strength_data(sector=request.form.get('sector'), index = request.form.get('index'),stock_type = request.form.get('stock_type'))
            portfolio = buildPortfolio.build_portfolio_with_top_stocks(strength_df,request.form.get('investing_amount'),request.form.get('max_stock_price'),request.form.get('risk_tolerance'))
        elif request.form["btn"]=="Optimize":
            logging.info("Extracting form data")
            strength_df = stock.update_strength_data(sector = 'Any', index = 'S&P 500',stock_type = request.form["stock_type"])       
            portfolio = buildPortfolio.build_portfolio_from_user_input_tickers(strength_df,(list(set(request.form.getlist("stock[]")))),request.form["expected_return_value"], request.form["investing_amount"],request.form.get('risk_tolerance'))
        elif request.form["btn"]=="Save Portfolio":
             portfolio = buildPortfolio.get_build_porfolio()
             if not portfolio.empty:
                app.logger.info('Saving portfolio Data %',portfolio)
                buildPortfolio.save_portfolio_data(portfolio,current_user.id)
                flash('Successfully Saved Porfolio')
        total_portfolio_return = round(buildPortfolio.calculate_portfolio_return(portfolio),2)
        total_portfolio_risk = round(buildPortfolio.calculate_portfolio_risk(portfolio),2)
    title = "Portfolio Return: {portfolio_return} % | Portfolio Risk: {risk} %".format(portfolio_return = total_portfolio_return, risk = total_portfolio_risk)
    return render_template('buildPortfolio.html',stock_types = helper.get_stock_type(),ticker_list = ticker_list,parameters=helper.get_optimization_parameters(),ticker_sector_lists=helper.index_select_attributes(),title= title,columns = helper.build_porfolio_column(),risks = helper.risk())

@main.route('/screener/data')
def stock_data():  
    data = stock.get_screener_data().to_dict('records')
    return {'data': data}

@main.route('/my-portfolio', methods=["GET","POST"])
@login_required
def portfolio():
    porfolio = buildPortfolio.get_portfolios_by_user_id(current_user.id)
    return render_template('portfolio.html', columns = helper.build_porfolio_column(), total_porfolios = len(porfolio) - 1)

@main.route('/my-portfolio/data')
def portfolio_data():
    return {'data': buildPortfolio.get_porfolio()}

@main.route('/portfolio/data')
def build_portfolio_data():
    return {'data': buildPortfolio.get_build_porfolio().to_dict('records')}

@main.route('/value-chart')
def value_chart():
    charts = chart.get_chart_data(enum.StockType.VALUE.value)
    return render_template('chart.html',charts = charts,title= "Top Value Stocks" )

@main.route('/growth-chart')
def growth_chart():
    charts = chart.get_chart_data(enum.StockType.GROWTH.value)
    return render_template('chart.html',charts = charts, title= "Top Growth Stocks")

@main.route('/dividend-chart')
def dividend_chart():
    charts = chart.get_chart_data(enum.StockType.DIVIDEND.value)
    return render_template('chart.html',charts = charts, title= "Top Dividend Stocks" )

app = create_app() # we initialize our flask app using the __init__.py function
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False) # we run our app in debug mode
