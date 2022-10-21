from math import comb
import stockValueExtract
import helper
from flask import Flask, render_template, request, flash, session,redirect,url_for
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
def index():
    return render_template('index.html', ticker_sector_lists=helper.index_select_attributes(), title= "Select Your Investment Strategy")

@app.route('/stock', methods=['POST', 'GET'])
def stock():
    if request.method == "POST":
        session["sector"] = request.form.get('sector')
        session["index"] = request.form.get('index')
        session["stock_type"] = request.form.get('stock_type')
        ticker_lists = stockValueExtractor.update_strength_data(sector=session["sector"], index =session["index"],stock_type = session["stock_type"])
        session["ticker_lists"] = sorted(ticker_lists)
        return render_template('stocks.html')
    elif request.method == "GET":
        #if there is no data show empty data
        return render_template('stocks.html')

@app.route('/stock/data')
def stock_data():
    return {'data': pd.read_pickle("./stock.pkl").to_dict('records')}

@app.route('/create', methods=["POST", "GET"])
def create():
    if request.method == "POST":
        app.logger.info("Extracting form data")
        threshold = request.form["threshold"]
        investing_amount = request.form["investing_amount"]
        expected_return_value = request.form["expected_return_value"]
        selected_ticker_lists = request.form.getlist("stock[]")
        session["selected_ticker_lists"] = selected_ticker_lists
        validation = stockValueExtractor.validate_input(selected_ticker_lists, expected_return_value, threshold, investing_amount)
        if validation:
            flash(validation)
        else :
            stockValueExtractor.cache_portfolio(expected_return_value, threshold, investing_amount,selected_ticker_lists)
            return redirect(url_for('portfolio'))
    return render_template('create.html',ticker_lists=session["ticker_lists"], stocks=helper.get_stock_dict(session["ticker_lists"], len(set(session["ticker_lists"]))), parameters=helper.get_optimization_parameters())



@app.route('/portfolio', methods=["GET","POST"])
def portfolio():
     return render_template('portfolio.html')

@app.route('/portfolio/data')
def portfolio_data():
    return {'data': pd.read_pickle("./portfolio.pkl").to_dict('records')}

@app.route('/value-chart')
def valueChart():
    stockValueExtractor = stockValueExtract.stock()
    charts = stockValueExtractor.get_chart_data("./valuechart.pkl",helper.StockType.VALUE.value)
    return render_template('chart.html',charts = charts )

@app.route('/growth-chart')
def growthChart():
    stockValueExtractor = stockValueExtract.stock()
    charts = stockValueExtractor.get_chart_data("./growthchart.pkl", helper.StockType.GROWTH.value)
    return render_template('chart.html',charts = charts )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
