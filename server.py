import stockValueExtract
import helper
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_toastr import Toastr
import pandas as pd
import numpy as np
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
# For data manipulation


from finvizfinance.screener.financial import Financial
from finvizfinance.screener.ticker import Ticker
from finvizfinance.screener.technical import Technical
from finvizfinance.screener.ownership import Ownership
from finvizfinance.screener.valuation import Valuation
from finvizfinance.screener.performance import Performance
from finvizfinance.screener.overview import Overview
from finvizfinance.screener.technical import Technical

foverview = Overview()
fvaluation = Valuation()
fownership = Ownership()
ftechnical = Technical()
fperformance = Performance()
financial = Financial()
ticker = Ticker()


toastr = Toastr()

app = Flask(__name__)
app.secret_key = "e0af172472bfdc4bc8292763f86e3abe0e2eb9a8cf68d12f"
toastr.init_app(app)

#optimized_result = {"Stock": ['', ''], "Optimized Expected Return": [
   # '', ''], "Optimized Weight": ['', ''], 'Total Cost': ['', ''], 'Number of Shares': ['', '']}
optimized_net_result = {}
ticker_lists = []
selected_ticker_lists = []
metric_dic = {}
df_dict = {}
selectedList = []



@app.route('/', methods=['POST', 'GET'])
def index():
    if (request.method == "POST"):
        selectedList.append([request.form.get('sector'), request.form.get(
            'index'), request.form.get('stock type')])
    return render_template('index.html', selectedList=selectedList, ticker_sector_lists=helper.index_select_attributes(),tables=[pd.DataFrame(df_dict).to_html(classes='data', header="true")])


@app.route('/stock', methods=['POST', 'GET'])
def stock():
    if request.method == "POST":
        sector = request.form.get('sector')
        index = request.form.get('index')
        stock_type = request.form.get('stock type')
        metric_dic.update({"sector":sector,"index":index,"stock_type": stock_type})
        print([sector, index, stock_type])
        stockValueExtractor = stockValueExtract.stock(
            sector, stock_type, index)
        valuation = stockValueExtractor.get_metric_data(
            fvaluation, 1)[helper.get_valuation_metric()]
        financial_df = stockValueExtractor.get_metric_data(
            financial, 1)[helper.get_financial_metric()]
        technical = stockValueExtractor.get_metric_data(
            ftechnical, 1)[helper.get_techical_metric()]
        ownership = stockValueExtractor.get_metric_data(
            fownership, 1)[helper.get_ownership_metric()]
        combined_data = pd.concat(
            [valuation, financial_df, technical, ownership], join='inner', axis=1)
        combined_data.to_pickle("./stock.pkl")
        stockValueExtractor.update_metric_df(combined_data)
        print("Combined Data", combined_data)
        df_dict.update(combined_data.to_dict())
        ticker_lists.clear()
        ticker_lists.extend(stockValueExtractor.get_ticker_list())
        return redirect(url_for('index'))


@app.route('/create/', methods=["POST", "GET"])
def create():
    if request.method == 'POST':
        app.logger.info("Extracting form data")
        threshold = request.form["threshold"]
        investing_amount = request.form["investing_amount"]
        expected_return_value = request.form["expected_return_value"]
        selected_ticker_lists = request.form.getlist("stock[]")
        print("list", selected_ticker_lists)
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
            print("DF DIC", df_dict)
            print("STOCK TYPE",metric_dic["stock_type"])
            portfolio = stockValueExtract.stock(metric_dic["sector"], metric_dic["stock_type"], metric_dic["index"]).build_portfolio(df=pd.read_pickle("./stock.pkl"), selected_ticker_list=selected_ticker_lists, desired_return= np.divide(int(
                expected_return_value),100), threshold=int(threshold), investing_amount=int(investing_amount))
            print("PORT", portfolio)
            optimized_net_result.update(portfolio.to_dict())
            #optimized_net_result.append(
               # {"title": "Total Invested Amount", "content": investing_amount})
            #optimized_net_result.append({"title": "Total Expected Return", "content": sum(portfolio['Expected Return'].replace(np.nan, 0).to_numpy())})
            #optimized_result.update(
               # stockValueExtract.get_optimized_result(portfolio))
            return redirect(url_for('portfolio'))

    return render_template('create.html', ticker_lists=ticker_lists, stocks=helper.get_stock_dict(ticker_lists, len(set(ticker_lists))), parameters=helper.get_optimization_parameters())


@app.route('/portfolio', methods=["GET"])
def portfolio():
    df = pd.DataFrame(optimized_net_result)
    return df.to_html(header="true", table_id="table")


if __name__ == "__main__":
    app.run(host='0.0.0.0')

