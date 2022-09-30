import stockValueExtract
import helper
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_toastr import Toastr
import pandas as pd

toastr = Toastr()

app = Flask(__name__)
app.secret_key = "e0af172472bfdc4bc8292763f86e3abe0e2eb9a8cf68d12f"
toastr.init_app(app)

meta_dictionary = stockValueExtract.get_gs_meta()
colours = ['Red', 'Blue', 'Black', 'Orange']
optimized_result = {"Stock": ['', ''], "Optimized Expected Return": [
    '', ''], "Optimized Weight": ['', ''], 'Total Cost': ['', ''], 'Number of Shares': ['', '']}
optimized_net_result = []
ticker_lists = []
selected_ticker_lists = []
metric_dic = []
stock_type = ''
sector_index = []
index_lists = []
sector_lists = []
stock_data = []

@app.route('/',methods=["POST", "GET"])
def index():
    index_lists = helper.get_index()
    sector_lists = helper.get_sector()
    return render_template('index.html', index_lists = index_lists, sector_lists = sector_lists, messages=optimized_net_result, tables=[pd.DataFrame(stock_data).to_html(classes='data', header="true")])

@app.route('/stock',methods=["POST", "GET"])
def stock():
    sector = request.form.get('sector')
    index = request.form.get('index')
    df = stockValueExtract.get_stocks_by_sector_and_index(sector,index)
    ticker_lists.extend(df['Ticker'].values.tolist())
    return redirect(url_for('create'))

@app.route('/create/', methods=["POST", "GET"])
def create():
    if request.method == 'POST':
        app.logger.info("Extracting form data")
        stock_type = request.form["stock_type"] 
        threshold = request.form["threshold"]
        investing_amount = request.form["investing_amount"]
        expected_return_value = request.form["expected_return_value"]
        selected_ticker_lists = request.form.getlist("stock[]")
        stockValueExtract.remove_empty_element(selected_ticker_lists)
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
            portfolio = stockValueExtract.build_portfolio(stock_list=selected_ticker_lists, metric_dic=metric_dic, stock_type=stock_type, desired_expected_return=int(
                expected_return_value), threshold=int(threshold), investing_amount=int(investing_amount), optimal_number_of_stocks=int(threshold))
            optimized_net_result.append(
                {"title": "Total Invested Amount", "content": investing_amount})
            optimized_net_result.append({"title": "Total Expected Return", "content": sum(
                stockValueExtract.get_array('Expected Return', portfolio))})
            optimized_result.update(
                stockValueExtract.get_optimized_result(portfolio))
            return redirect(url_for('index'))

    return render_template('create.html', ticker_lists = ticker_lists, stocks=helper.get_stock_dict(), parameters=helper.get_optimization_parameters())


@app.route('/portfolio', methods=["GET"])
def portfolio():
    df = stockValueExtract.get_data_from_sheet(service_file_path=meta_dictionary.get(
        'auth_json_path'), spreadsheet_id=meta_dictionary.get('spreadsheet_key'), sheet_name=meta_dictionary.get('wks_name'))
    return df.to_html(header="true", table_id="table")


if __name__ == "__main__":
    app.run()
