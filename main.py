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
    return render_template('home.html', title= "Welcome StockNity Members!")

@app.route('/stock', methods=['POST','GET'])
def index():
    return render_template('stockSelector.html', ticker_sector_lists=helper.index_select_attributes(), title= "Select Your Investment Strategy")

@app.route('/portfolio', methods=['POST','GET'])
def stock():
    if request.form["btn"]=="Search":
        if request.method== 'POST':
            session["sector"] = request.form.get('sector')
            session["index"] = request.form.get('index')
            session["stock_type"] = request.form.get('stock_type')
            ticker_lists = stockValueExtractor.update_strength_data(sector=session["sector"], index =session["index"],stock_type = session["stock_type"]
            ,fileName=helper.get_pickle_file()["stock"])
            session["ticker_lists"] = sorted(ticker_lists)  
            return render_template('stocks.html',stocks=helper.get_stock_dict(session["ticker_lists"], len(set(session["ticker_lists"]))),parameters=helper.get_optimization_parameters(),title= "Build Portfolio")
    elif request.form["btn"]=="Optimize":
        if request.method== 'POST':
            app.logger.info("Extracting form data")
            threshold = request.form["threshold"]
            investing_amount = request.form["investing_amount"]
            expected_return_value = request.form["expected_return_value"]
            selected_ticker_lists = (list(set(request.form.getlist("stock[]"))))
            session["selected_ticker_lists"] = selected_ticker_lists
            stockValueExtractor.cache_portfolio(expected_return_value, threshold, investing_amount,selected_ticker_lists)
            return redirect(url_for('portfolio'))

@app.route('/portfolio/data')
def stock_data():
    return {'data': pd.read_pickle(helper.get_pickle_file()["stock"]).to_dict('records')}

@app.route('/my-portfolio', methods=["GET","POST"])
def portfolio():
     return render_template('portfolio.html',title= "My Portfolio")

@app.route('/my-portfolio/data')
def portfolio_data():
    return {'data': pd.read_pickle(helper.get_pickle_file()["portfolio"]).to_dict('records')}

@app.route('/value-chart')
def valueChart():
    stockValueExtractor = stockValueExtract.stock()
    charts = stockValueExtractor.get_chart_data(helper.get_pickle_file()["value"],helper.StockType.VALUE.value,helper.Metric.STRENGTH.value)
    return render_template('chart.html',charts = charts,title= "Top Value Stocks" )

@app.route('/growth-chart')
def growthChart():
    stockValueExtractor = stockValueExtract.stock()
    charts = stockValueExtractor.get_chart_data(helper.get_pickle_file()["growth"], helper.StockType.GROWTH.value, helper.Metric.STRENGTH.value)
    return render_template('chart.html',charts = charts, title= "Top Growth Stocks")

@app.route('/dividend-chart')
def dividendChart():
    stockValueExtractor = stockValueExtract.stock()
    charts = stockValueExtractor.get_chart_data(helper.get_pickle_file()["dividend"], helper.StockType.NONE.value, helper.Metric.DIVIDEND.value)
    return render_template('chart.html',charts = charts, title= "Top Dividend Stocks" )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
