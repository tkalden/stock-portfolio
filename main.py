from math import comb
import stockValueExtract
import helper
from flask import Flask, render_template, request, session,redirect,url_for
from flask_toastr import Toastr
import pandas as pd
import numpy as np
import os

toastr = Toastr()

config = {
    "SECRET_KEY": "e0af172472bfdc4bc8292763f86e3abe0e2eb9a8cf68d12f"
}

app = Flask(__name__)
app.config.from_mapping(config)

toastr.init_app(app)

stockValueExtractor = stockValueExtract.stock()

@app.route('/', methods=['POST','GET'])
def home():
   stockValueExtractor.cache_stock_data()
   return render_template('home.html', title= "Welcome StockNity Members!")

@app.route('/login', methods=['POST','GET'])
def login():
   return 'LOGIN COMING SOON'

@app.route('/screener', methods=["GET","POST"])
def screener():
 index = 'S&P 500'
 sector = ''
 if request.method == 'POST': 
    if request.form["btn"]=="Search":
        sector = request.form.get('sector')
        index = request.form.get('index')
        data = stockValueExtractor.get_stock_data_by_sector_and_index(sector = sector, index=index)
        stockValueExtractor.pickle_file(data,'screener')      
 return render_template('screener.html', index_sector_lists = helper.index_sector(), title = "{index} {sector} Data".format(sector = sector, index =index)
 )

@app.route('/portfolio', methods=["GET","POST"])
def build():
    portfolio = pd.DataFrame()
    stock_data = pd.read_pickle(helper.get_pickle_file()["stock"])
    ticker_list = sorted(list(set(stock_data["Ticker"])))
    session['user_id'] = 'albertkalden@gmail.com'
    total_portfolio_return = 0
    total_portfolio_risk = 0
    if request.method == 'POST':
        if request.form["btn"]=="Build":
            sector = request.form.get('sector')
            index = request.form.get('index')
            stock_type = request.form.get('stock_type')
            investing_amount = request.form.get('investing_amount')
            maximum_stock_price = request.form.get('max_stock_price')
            strength_df = stockValueExtractor.update_strength_data(sector=sector, index = index,stock_type = stock_type)
            portfolio = stockValueExtractor.build_portfolio_with_top_stocks(strength_df,investing_amount,maximum_stock_price)
        elif request.form["btn"]=="Optimize":
            app.logger.info("Extracting form data")
            threshold = request.form["threshold"]
            stock_type = request.form["stock_type"]
            investing_amount = request.form["investing_amount"]
            maximum_stock_price = request.form.get('max_stock_price')
            expected_return_value = request.form["expected_return_value"]
            selected_ticker_list = (list(set(request.form.getlist("stock[]"))))
            strength_df = stockValueExtractor.update_strength_data(sector = 'Any', index = 'S&P 500',stock_type = stock_type)       
            portfolio = stockValueExtractor.build_portfolio_from_user_input_tickers(strength_df,selected_ticker_list, threshold,expected_return_value, investing_amount,maximum_stock_price)
        elif request.form["btn"]=="Save Portfolio":
             # for some reason the portfolio varible goes to empty dataframe when the save is clicked.Following
            # is the work around
             portfolio = pd.read_pickle(helper.get_pickle_file()["portfolio"])
             if not portfolio.empty:
                app.logger.info(f'Saving portfolio Data %',portfolio)
                stockValueExtractor.save_portfolio_data(portfolio,session['user_id'])
                stockValueExtractor.save_user_data(session['user_id'])
        total_portfolio_return = stockValueExtractor.calculate_portfolio_return(portfolio)
        total_portfolio_risk = stockValueExtractor.calculate_portfolio_risk(portfolio)
    stockValueExtractor.pickle_file(portfolio,'portfolio')  
    title = "Portfolio Return: {portfolio_return} % | Portfolio Risk: {risk} %".format(portfolio_return = total_portfolio_return, risk = total_portfolio_risk)
    return render_template('buildPortfolio.html',stock_types = helper.get_stock_type(),ticker_list = ticker_list,parameters=helper.get_optimization_parameters(),ticker_sector_lists=helper.index_select_attributes(),title= title,columns = helper.build_porfolio_column() )

@app.route('/screener/data')
def stock_data():  
    #by default if there is no screener data at all then populate with defualt stock data
    if not stockValueExtractor.checkFile('screener'):
        data = pd.read_pickle(helper.get_pickle_file()["stock"]).to_dict('records')
    else:
        data = pd.read_pickle(helper.get_pickle_file()["screener"]).to_dict('records')
    return {'data': data}

@app.route('/my-portfolio', methods=["GET","POST"])
def portfolio():
    user_id = ''
    if session.get('user_id') is not None:
         user_id = session['user_id']
    return render_template('portfolio.html',user_id = user_id, columns = helper.build_porfolio_column())

@app.route('/my-portfolio/data')
def portfolio_data():
    return {'data': stockValueExtractor.get_portfolios_by_user_id(session['user_id']).to_dict('records')}

@app.route('/portfolio/data')
def build_portfolio_data():
    return {'data': pd.read_pickle(helper.get_pickle_file()["portfolio"]).to_dict('records')}

@app.route('/value-chart')
def valueChart():
    stockValueExtractor = stockValueExtract.stock()
    charts = stockValueExtractor.get_chart_data("value",helper.StockType.VALUE.value,helper.Metric.STRENGTH.value,overwrite=False)
    return render_template('chart.html',charts = charts,title= "Top Value Stocks" )

@app.route('/growth-chart')
def growthChart():
    stockValueExtractor = stockValueExtract.stock()
    charts = stockValueExtractor.get_chart_data("growth", helper.StockType.GROWTH.value, helper.Metric.STRENGTH.value,overwrite=False)
    return render_template('chart.html',charts = charts, title= "Top Growth Stocks")

@app.route('/dividend-chart')
def dividendChart():
    stockValueExtractor = stockValueExtract.stock()
    charts = stockValueExtractor.get_chart_data("dividend", helper.StockType.NONE.value, helper.Metric.DIVIDEND.value,overwrite=False)
    return render_template('chart.html',charts = charts, title= "Top Dividend Stocks" )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
