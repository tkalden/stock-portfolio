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
    if request.method == 'POST':
        if request.form["btn"]=="Search":
            session["sector"] = request.form.get('sector')
            session["index"] = request.form.get('index')
            session["stock_type"] = request.form.get('stock_type')
            strength_df = stockValueExtractor.update_strength_data(sector=session["sector"], index =session["index"],stock_type = session["stock_type"])
            portfolio = stockValueExtractor.build_portfolio_with_top_stocks(strength_df,100000)
        elif request.form["btn"]=="Optimize":
            app.logger.info("Extracting form data")
            threshold = request.form["threshold"]
            stock_type = request.form["stock_type"]
            investing_amount = request.form["investing_amount"]
            expected_return_value = request.form["expected_return_value"]
            selected_ticker_list = (list(set(request.form.getlist("stock[]"))))
            strength_df = stockValueExtractor.update_strength_data(sector = 'Any', index = 'S&P 500',stock_type = stock_type)
            portfolio = stockValueExtractor.build_portfolio_from_user_input_tickers(strength_df,selected_ticker_list, threshold,expected_return_value, investing_amount)
        elif request.form["btn"]=="Save Portfolio":
             # for some reason the portfolio varible goes to empty dataframe when the save is clicked.Following
            # is the work around
             portfolio = pd.read_pickle(helper.get_pickle_file()["portfolio"])
             if not portfolio.empty:
                app.logger.info(f'Saving portfolio Data %',portfolio)
                stockValueExtractor.save_portfolio_data(portfolio,session['user_id'])
                stockValueExtractor.save_user_data(session['user_id'])
    stockValueExtractor.pickle_file(portfolio,'portfolio')  
    return render_template('buildPortfolio.html',stock_types = helper.get_stock_type(),ticker_list = ticker_list,parameters=helper.get_optimization_parameters(),ticker_sector_lists=helper.index_select_attributes(),title= "Build Portfolio")

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
     # render the data from database
     return render_template('portfolio.html',title= "Logged in as {user_id}".format(user_id = session["user_id"]))

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
