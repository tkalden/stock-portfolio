from flask import Blueprint
import stockValueExtract
import helper
from flask import render_template, request,flash
import pandas as pd
from __init__ import create_app
from flask_login import current_user,login_required
import logging

main = Blueprint('main', __name__)


stockValueExtractor = stockValueExtract.stock()

@main.route('/', methods=['POST','GET'])
def home():
   stockValueExtractor.cache_stock_data()
   return render_template('home.html')

@main.route('/profile', methods=['POST','GET'])
@login_required
def profile():
   stockValueExtractor.cache_stock_data()
   return render_template('profile.html',name = current_user.name)

@main.route('/screener', methods=["GET","POST"])
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

@main.route('/portfolio', methods=["GET","POST"])
@login_required
def build():
    portfolio = pd.DataFrame()
    stock_data = pd.read_pickle(helper.get_pickle_file()["stock"])
    ticker_list = sorted(list(set(stock_data["Ticker"])))
    total_portfolio_return = 0
    total_portfolio_risk = 0
    if request.method == 'POST':
        if request.form["btn"]=="Build":
            strength_df = stockValueExtractor.update_strength_data(sector=request.form.get('sector'), index = request.form.get('index'),stock_type = request.form.get('stock_type'))
            portfolio = stockValueExtractor.build_portfolio_with_top_stocks(strength_df,request.form.get('investing_amount'),request.form.get('max_stock_price'),request.form.get('risk_tolerance'))
        elif request.form["btn"]=="Optimize":
            logging.info("Extracting form data")
            strength_df = stockValueExtractor.update_strength_data(sector = 'Any', index = 'S&P 500',stock_type = request.form["stock_type"])       
            portfolio = stockValueExtractor.build_portfolio_from_user_input_tickers(strength_df,(list(set(request.form.getlist("stock[]")))),request.form["expected_return_value"], request.form["investing_amount"],request.form.get('risk_tolerance'))
        elif request.form["btn"]=="Save Portfolio":
             # for some reason the portfolio varible goes to empty dataframe when the save is clicked.Following
            # is the work around
             portfolio = pd.read_pickle(helper.get_pickle_file()["portfolio"])
             if not portfolio.empty:
                app.logger.info(f'Saving portfolio Data %',portfolio)
                stockValueExtractor.save_portfolio_data(portfolio,current_user.id)
                flash('Successfully Saved Porfolio')
        total_portfolio_return = round(stockValueExtractor.calculate_portfolio_return(portfolio),2)
        total_portfolio_risk = round(stockValueExtractor.calculate_portfolio_risk(portfolio),2)
    stockValueExtractor.pickle_file(portfolio,'portfolio')  
    title = "Portfolio Return: {portfolio_return} % | Portfolio Risk: {risk} %".format(portfolio_return = total_portfolio_return, risk = total_portfolio_risk)
    return render_template('buildPortfolio.html',stock_types = helper.get_stock_type(),ticker_list = ticker_list,parameters=helper.get_optimization_parameters(),ticker_sector_lists=helper.index_select_attributes(),title= title,columns = helper.build_porfolio_column(),risks = helper.risk())

@main.route('/screener/data')
def stock_data():  
    #by default if there is no screener data at all then populate with defualt stock data
    if not stockValueExtractor.checkFile('screener'):
        data = pd.read_pickle(helper.get_pickle_file()["stock"]).to_dict('records')
    else:
        data = pd.read_pickle(helper.get_pickle_file()["screener"]).to_dict('records')
    return {'data': data}

@main.route('/my-portfolio', methods=["GET","POST"])
@login_required
def portfolio():
    porfolio = stockValueExtractor.get_portfolios_by_user_id(current_user.id)
    return render_template('portfolio.html', columns = helper.build_porfolio_column(), total_porfolios = len(porfolio) - 1)

@main.route('/my-portfolio/data')
def portfolio_data():
    return {'data': stockValueExtractor.get_porfolio()}

@main.route('/portfolio/data')
def build_portfolio_data():
    return {'data': pd.read_pickle(helper.get_pickle_file()["portfolio"]).to_dict('records')}

@main.route('/value-chart')
def valueChart():
    stockValueExtractor = stockValueExtract.stock()
    charts = stockValueExtractor.get_chart_data("value",helper.StockType.VALUE.value,helper.Metric.STRENGTH.value,overwrite=False)
    return render_template('chart.html',charts = charts,title= "Top Value Stocks" )

@main.route('/growth-chart')
def growthChart():
    stockValueExtractor = stockValueExtract.stock()
    charts = stockValueExtractor.get_chart_data("growth", helper.StockType.GROWTH.value, helper.Metric.STRENGTH.value,overwrite=False)
    return render_template('chart.html',charts = charts, title= "Top Growth Stocks")

@main.route('/dividend-chart')
def dividendChart():
    stockValueExtractor = stockValueExtract.stock()
    charts = stockValueExtractor.get_chart_data("dividend", helper.StockType.NONE.value, helper.Metric.DIVIDEND.value,overwrite=False)
    return render_template('chart.html',charts = charts, title= "Top Dividend Stocks" )

app = create_app() # we initialize our flask app using the __init__.py function
if __name__ == '__main__':
    app.run(debug=True) # run the flask app on debug mode
