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


@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html', ticker_sector_lists=helper.index_select_attributes(), title= "Select Your Investment Strategy")

@app.route('/stock', methods=['POST', 'GET'])
def stock():
    if request.method == "POST":
        session["sector"] = request.form.get('sector')
        session["index"] = request.form.get('index')
        session["stock_type"] = request.form.get('stock_type')
        stockValueExtractor = stockValueExtract.stock(
            session["sector"], session["stock_type"], session["index"])
        combined_data = stockValueExtractor.get_stock_data_by_sector_and_index()
        combined_data = np.round(combined_data, decimals=2)
        strength_calculated_df = stockValueExtractor.calculate_strength_value(
            combined_data)
        strength_calculated_df.reset_index(drop=True, inplace=True)
        strength_calculated_df  = strength_calculated_df.fillna(0)
        #need to think about how to cache this in the production
        strength_calculated_df.to_pickle("./stock.pkl")
        ticker_lists = strength_calculated_df["Ticker"].to_list()
        session["ticker_lists"] = ticker_lists
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
        if len(selected_ticker_lists) == 0:
            flash('The stock list should not be null')
        elif len(selected_ticker_lists) != len(set(selected_ticker_lists)):
            flash('The stocks must be unique')
        elif threshold == '':
            flash('Threshold should not be blank')
        elif len(set(selected_ticker_lists)) < int(float(threshold)):
            flash('The stock list must be greater than threshold')
        elif investing_amount == '':
            flash('Investment Amount must not be blank')
        elif expected_return_value == '':
            flash('Expected Return Value must not be blank')
        else:
            print("HERE")
            app.logger.info("Optimizing the stock data")
            portfolio = stockValueExtract.stock(session["sector"], session["stock_type"], session["index"]).build_portfolio(df=pd.read_pickle("./stock.pkl"), selected_ticker_list=session["selected_ticker_lists"], desired_return=np.divide(int(
                expected_return_value), 100), threshold=int(threshold), investing_amount=int(investing_amount))
            portfolio = np.round(portfolio, decimals=2)
            portfolio.to_pickle("./portfolio.pkl")
            return redirect(url_for('portfolio'))

    return render_template('create.html', ticker_lists=session["ticker_lists"], stocks=helper.get_stock_dict(session["ticker_lists"], len(set(session["ticker_lists"]))), parameters=helper.get_optimization_parameters())



@app.route('/portfolio', methods=["GET","POST"])
def portfolio():
     return render_template('portfolio.html')

@app.route('/portfolio/data')
def portfolio_data():
    return {'data': pd.read_pickle("./portfolio.pkl").to_dict('records')}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
