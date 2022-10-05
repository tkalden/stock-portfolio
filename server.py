import stockValueExtract
import helper
from flask import Flask, render_template, request, flash, session,redirect,url_for
from flask_toastr import Toastr
import pandas as pd
import numpy as np
import asyncio
from array import array

toastr = Toastr()

config = {
    "SECRET_KEY": "e0af172472bfdc4bc8292763f86e3abe0e2eb9a8cf68d12f"
}

app = Flask(__name__)
app.config.from_mapping(config)

toastr.init_app(app)


@app.route('/', methods=['POST','GET'])
def index():
    if request.method == "POST":
        session["sector"] = request.form.get('sector')
        session["index"] = request.form.get('index')
        session["stock_type"] = request.form.get('stock_type')
        return redirect(url_for('stock'))
    return render_template('index.html', ticker_sector_lists=helper.index_select_attributes())


@app.route('/stock', methods=['POST', 'GET'])
def stock():
    stockValueExtractor = stockValueExtract.stock(
        session["sector"], session["stock_type"], session["index"])
    combined_data = asyncio.run(stockValueExtractor.get_stock_data_for_pages(4))
    strength_calculated_df = stockValueExtractor.calculate_strength_value(
        combined_data)
    strength_calculated_df.reset_index(drop=True, inplace=True)
    strength_calculated_df.to_pickle("./stock.pkl")
    ticker_lists = strength_calculated_df["Ticker"].to_list()
    session["ticker_lists"] = ticker_lists
    return render_template('stocks.html', tables=[strength_calculated_df.to_html(classes='data', header="true")])


@app.route('/create/', methods=["POST", "GET"])
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
            app.logger.info("Optimizing the stock data")
            portfolio = stockValueExtract.stock(session["sector"], session["stock_type"], session["index"]).build_portfolio(df=pd.read_pickle("./stock.pkl"), selected_ticker_list=session["selected_ticker_lists"], desired_return=np.divide(int(
                expected_return_value), 100), threshold=int(threshold), investing_amount=int(investing_amount))
            session["optimized_net_result"] = portfolio.to_dict()
            return redirect(url_for('portfolio'))

    return render_template('create.html', ticker_lists=session["ticker_lists"], stocks=helper.get_stock_dict(session["ticker_lists"], len(set(session["ticker_lists"]))), parameters=helper.get_optimization_parameters())


@app.route('/portfolio', methods=["GET","POST"])
def portfolio():
     df = pd.DataFrame(session["optimized_net_result"])[helper.portfolio_attributes()]
     df.reset_index(drop=True,inplace=True)
     session["portfolio"] = df.to_dict()
     return render_template('portfolio.html', tables=[pd.DataFrame(session["portfolio"]).to_html(classes='data', header="true")])

if __name__ == "__main__":
    app.run(host='0.0.0.0')
