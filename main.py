import logging
import threading
from threading import Thread

import pandas as pd
from flask import Blueprint, request, redirect, url_for, jsonify, current_app
from flask_login import current_user, login_required

import enums.enum as enum
import services.news as news
import utilities.helper as helper
from services.chart import chart
from services.portfolio import portfolio as buildPortfolio
from services.screener import Screener
from services.strengthCalculator import StrengthCalculator
import numpy as np

main = Blueprint('main', __name__)

screenerService = Screener()
buildPortfolio = buildPortfolio()
strengthCalculator = StrengthCalculator()
chart = chart()

@main.route('/api/home', methods=['GET'])
def api_home():
   """API endpoint for home page data"""
   try:
       news_df = news.get_news()
       if not news_df.empty:
           return jsonify({'data': news_df.to_dict('records')})
       else:
           return jsonify({'data': []})
   except Exception as e:
       current_app.logger.error(f"Error fetching news: {e}")
       return jsonify({'data': [], 'error': str(e)})

@main.route('/api/profile', methods=['GET'])
@login_required
def api_profile():
   """API endpoint for user profile data"""
   return jsonify({
       'user': {
           'id': current_user.id,
           'name': current_user.name,
           'email': current_user.email
       }
   })

@main.route('/api/screener', methods=["GET","POST"])
def api_screener():
    """API endpoint for stock screener"""
    if request.method == 'POST':
        sector = request.form.get('sector')
        index = request.form.get('index')
        screenerService.update_key_sector_and_index(sector=sector, index=index)
    
    # Return screener data
    stock_data = screenerService.get_sp500_data()
    return jsonify({'data': stock_data.to_dict('records')})

@main.route('/api/portfolio', methods=["GET","POST"])
@login_required
def api_portfolio():
    """API endpoint for portfolio management"""
    if request.method == 'POST':
        try:
            current_app.logger.info(f"Portfolio POST request. Form data: {dict(request.form)}")
            btn_value = request.form.get("btn", "")
            current_app.logger.info(f"Button value: {btn_value}")
            
            if btn_value == "Build":
                current_app.logger.info("Building top stock portfolio")
                strength_df = strengthCalculator.calculate_strength_value(
                    sector=request.form.get('sector'), 
                    index=request.form.get('index'),
                    stock_type=request.form.get('stock_type')
                )
                portfolio = buildPortfolio.build_portfolio_with_top_stocks(
                    strength_df,
                    request.form.get('investing_amount'),
                    request.form.get('max_stock_price'),
                    request.form.get('risk_tolerance')
                )
                current_app.logger.info(f"Built portfolio with {len(portfolio)} stocks")
                
            elif btn_value == "Optimize":
                current_app.logger.info("Optimizing custom portfolio")
                strength_df = strengthCalculator.calculate_strength_value(
                    sector='Any', 
                    index='S&P 500',
                    stock_type=request.form["stock_type"]
                )
                selected_stocks = list(set(request.form.getlist("stock[]")))
                current_app.logger.info(f"Selected stocks: {selected_stocks}")
                portfolio = buildPortfolio.build_portfolio_from_user_input_tickers(
                    strength_df,
                    selected_stocks,
                    request.form["expected_return_value"], 
                    request.form["investing_amount"],
                    request.form.get('risk_tolerance')
                )
                current_app.logger.info(f"Optimized portfolio with {len(portfolio)} stocks")
                
            elif btn_value == "Save Portfolio":
                current_app.logger.info("Saving portfolio")
                portfolio = buildPortfolio.get_build_porfolio()
                current_app.logger.info(f'Save Portfolio button clicked. Portfolio empty: {portfolio.empty}')
                if not portfolio.empty:
                    current_app.logger.info(f'Saving portfolio Data: {len(portfolio)} stocks')
                    current_app.logger.info(f'Current user ID: {current_user.id}')
                    success = buildPortfolio.save_portfolio_data(portfolio, current_user.id)
                    current_app.logger.info(f'Portfolio save result: {success}')
                    return jsonify({'success': success})
                else:
                    current_app.logger.warning('Attempted to save empty portfolio')
                    return jsonify({'success': False, 'error': 'No portfolio to save'})
            
            # Return JSON response for portfolio operations
            if not portfolio.empty:
                return jsonify({
                    'success': True,
                    'data': portfolio.to_dict('records'),
                    'message': 'Portfolio built successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to build portfolio'
                })
            
        except Exception as e:
            current_app.logger.error(f"Error in portfolio build: {e}")
            return jsonify({'success': False, 'error': str(e)})
    
    # GET request - return current portfolio data
    return jsonify({'message': 'Portfolio API endpoint'})

@main.route('/api/screener/data')
def api_stock_data():  
    """API endpoint for stock data"""
    stock_data = screenerService.get_sp500_data()
    return jsonify({'data': stock_data.to_dict('records')})

@main.route('/api/delete-portfolio/<portfolio_id>', methods=['POST'])
@login_required
def api_delete_portfolio(portfolio_id):
    """API endpoint for deleting portfolios"""
    current_app.logger.info(f'Delete portfolio endpoint called. Portfolio ID: {portfolio_id}, User: {current_user.id}')
    success = buildPortfolio.delete_portfolio(portfolio_id, current_user.id)
    current_app.logger.info(f'Delete portfolio result: {success}')
    return jsonify({'success': success})

@main.route('/api/my-portfolio/data')
@login_required
def api_portfolio_data():
    """API endpoint for user portfolio data"""
    current_app.logger.info(f'Portfolio data endpoint called. User authenticated: {current_user.is_authenticated}')
    current_app.logger.info(f'Current user ID: {current_user.id if current_user.is_authenticated else "Not authenticated"}')
    
    if not current_user.is_authenticated:
        current_app.logger.warning('User not authenticated for portfolio data request')
        return jsonify({'data': []})
    
    portfolios = buildPortfolio.get_portfolios_by_user_id(current_user.id)
    current_app.logger.info(f'Portfolio data endpoint called. User: {current_user.id}, Portfolios: {len(portfolios)}')
    
    if portfolios:
        current_app.logger.info(f'First portfolio structure: {type(portfolios[0])}')
        if hasattr(portfolios[0], 'keys'):
            current_app.logger.info(f'First portfolio keys: {list(portfolios[0].keys())}')
        current_app.logger.info(f'First portfolio data length: {len(portfolios[0]) if hasattr(portfolios[0], "__len__") else "N/A"}')
        
        # Log portfolio IDs for debugging
        portfolio_ids = []
        for portfolio in portfolios:
            if hasattr(portfolio, 'keys') and 'portfolio_id' in portfolio:
                portfolio_ids.append(portfolio['portfolio_id'])
            elif len(portfolio) > 0 and 'portfolio_id' in portfolio[0]:
                portfolio_ids.append(portfolio[0]['portfolio_id'])
        current_app.logger.info(f'Portfolio IDs: {portfolio_ids}')
    else:
        current_app.logger.warning('No portfolios found for user')
    
    return jsonify({'data': portfolios})

@main.route('/api/portfolio/data')
def api_build_portfolio_data():
    """API endpoint for current portfolio data"""
    built_portfolio = buildPortfolio.get_build_porfolio()
    current_app.logger.info(f'Build portfolio data endpoint called. Built portfolio empty: {built_portfolio.empty}')
    
    if not built_portfolio.empty:
        current_app.logger.info(f'Returning built portfolio with {len(built_portfolio)} stocks')
        return jsonify({'data': built_portfolio.to_dict('records')})
    else:
        if current_user.is_authenticated:
            portfolios = buildPortfolio.get_portfolios_by_user_id(current_user.id)
            current_app.logger.info(f'User has {len(portfolios)} saved portfolios')
            if portfolios and len(portfolios) > 0:
                latest_portfolio = portfolios[-1]
                current_app.logger.info(f'Returning latest saved portfolio')
                return jsonify({'data': latest_portfolio})
        
        current_app.logger.info('No portfolios found, returning S&P 500 data')
        stock_data = screenerService.get_sp500_data()
        if not stock_data.empty:
            stock_data['expected_annual_return'] = 0
            stock_data['expected_annual_risk'] = 0
            stock_data['return_risk_ratio'] = 0
            stock_data['weight'] = 0
            stock_data['weighted_expected_return'] = 0
            stock_data['total_shares'] = 0
            stock_data['invested_amount'] = 0
            return jsonify({'data': stock_data.to_dict('records')})
        else:
            return jsonify({'data': []})

@main.route('/api/chart/<chart_type>', methods=['GET'])
def api_chart(chart_type):
    """API endpoint for chart data"""
    try:
        if chart_type == 'value':
            logging.info(f'Getting value chart data')
            charts = chart.get_chart_data(enum.StockType.VALUE.value)
        elif chart_type == 'growth':
            charts = chart.get_chart_data(enum.StockType.GROWTH.value)
        elif chart_type == 'dividend':
            charts = chart.get_chart_data(enum.StockType.DIVIDEND.value)
        else:
            return jsonify({'error': 'Invalid chart type'}), 400
        
        return jsonify({'data': charts})
    except Exception as e:
        current_app.logger.error(f"Error fetching chart data: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/clear-built-portfolio', methods=['POST'])
@login_required
def api_clear_built_portfolio():
    """API endpoint to clear built portfolio"""
    buildPortfolio.clear_built_portfolio()
    return jsonify({'success': True, 'message': 'Built portfolio cleared successfully'})

@main.route('/api/portfolio/advanced', methods=['POST'])
@login_required
def api_advanced_portfolio():
    """API endpoint for advanced portfolio optimization"""
    try:
        current_app.logger.info("Advanced portfolio optimization request")
        
        # Get parameters from request
        data = request.get_json() if request.is_json else request.form
        method = data.get('method', 'markowitz')
        investing_amount = float(data.get('investing_amount', 10000))
        max_stock_price = float(data.get('max_stock_price', 100))
        risk_tolerance = data.get('risk_tolerance', 'Medium')
        sector = data.get('sector', 'Any')
        index = data.get('index', 'S&P 500')
        stock_type = data.get('stock_type', 'Value')
        
        current_app.logger.info(f"Advanced optimization parameters: method={method}, amount={investing_amount}, max_price={max_stock_price}")
        
        # Get strength data
        strength_df = strengthCalculator.calculate_strength_value(stock_type, sector, index)
        
        if strength_df.empty:
            return jsonify({'success': False, 'error': 'No strength data available'})
        
        # Build advanced portfolio
        portfolio_df = buildPortfolio.build_portfolio_with_advanced_optimization(
            strength_df, investing_amount, max_stock_price, risk_tolerance, method
        )
        
        if portfolio_df.empty:
            return jsonify({'success': False, 'error': 'Failed to build portfolio'})
        
        # Get optimization metrics
        metrics = buildPortfolio.get_optimization_metrics()
        
        return jsonify({
            'success': True,
            'data': portfolio_df.to_dict('records'),
            'metrics': metrics,
            'method': method,
            'message': f'Portfolio built successfully using {method.upper()} optimization'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in advanced portfolio optimization: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/portfolio/compare-methods', methods=['POST'])
@login_required
def api_compare_optimization_methods():
    """API endpoint for comparing different optimization methods"""
    try:
        current_app.logger.info("Portfolio method comparison request")
        
        # Get parameters from request
        data = request.get_json() if request.is_json else request.form
        investing_amount = float(data.get('investing_amount', 10000))
        max_stock_price = float(data.get('max_stock_price', 100))
        risk_tolerance = data.get('risk_tolerance', 'Medium')
        sector = data.get('sector', 'Any')
        index = data.get('index', 'S&P 500')
        stock_type = data.get('stock_type', 'Value')
        
        # Get strength data
        strength_df = strengthCalculator.calculate_strength_value(stock_type, sector, index)
        
        if strength_df.empty:
            return jsonify({'success': False, 'error': 'No strength data available'})
        
        # Compare methods
        comparison_results = buildPortfolio.compare_optimization_methods(
            strength_df, investing_amount, max_stock_price, risk_tolerance
        )
        
        # Format results for frontend
        formatted_results = {}
        for method, result in comparison_results.items():
            if result:
                formatted_results[method] = {
                    'expected_return': result['expected_return'],
                    'volatility': result['volatility'],
                    'sharpe_ratio': result['sharpe_ratio'],
                    'method': result['method'],
                    'top_holdings': []
                }
                
                # Get top 3 holdings
                weights = result['weights']
                tickers = result['tickers']
                top_indices = np.argsort(weights)[-3:][::-1]
                
                for idx in top_indices:
                    formatted_results[method]['top_holdings'].append({
                        'ticker': tickers[idx],
                        'weight': float(weights[idx])
                    })
        
        return jsonify({
            'success': True,
            'results': formatted_results,
            'message': 'Method comparison completed successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in method comparison: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/portfolio/backtest', methods=['POST'])
@login_required
def api_portfolio_backtest():
    """API endpoint for portfolio backtesting"""
    try:
        current_app.logger.info("Portfolio backtesting request")
        
        # Get parameters from request
        data = request.get_json() if request.is_json else request.form
        investing_amount = float(data.get('investing_amount', 10000))
        max_stock_price = float(data.get('max_stock_price', 100))
        risk_tolerance = data.get('risk_tolerance', 'Medium')
        sector = data.get('sector', 'Any')
        index = data.get('index', 'S&P 500')
        stock_type = data.get('stock_type', 'Value')
        
        # Get strength data
        strength_df = strengthCalculator.calculate_strength_value(stock_type, sector, index)
        
        if strength_df.empty:
            return jsonify({'success': False, 'error': 'No strength data available'})
        
        # Run backtesting
        backtest_results = buildPortfolio.backtest_portfolio(
            strength_df, investing_amount, max_stock_price, risk_tolerance
        )
        
        if not backtest_results:
            return jsonify({'success': False, 'error': 'Backtesting failed'})
        
        # Format results for frontend
        formatted_results = {}
        for strategy_name, result in backtest_results['results'].items():
            if result:
                metrics = result['metrics']
                formatted_results[strategy_name] = {
                    'total_return': metrics['total_return'],
                    'annualized_return': metrics['annualized_return'],
                    'volatility': metrics['volatility'],
                    'sharpe_ratio': metrics['sharpe_ratio'],
                    'max_drawdown': metrics['max_drawdown'],
                    'var_95': metrics['var_95'],
                    'cvar_95': metrics['cvar_95'],
                    'calmar_ratio': metrics['calmar_ratio'],
                    'information_ratio': metrics['information_ratio']
                }
        
        return jsonify({
            'success': True,
            'backtest_results': formatted_results,
            'report': backtest_results['report'],
            'portfolio_data': backtest_results['portfolio_data'].to_dict('records'),
            'message': 'Backtesting completed successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in portfolio backtesting: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/portfolio/optimization-methods', methods=['GET'])
def api_get_optimization_methods():
    """API endpoint to get available optimization methods"""
    methods = [
        {
            'id': 'markowitz',
            'name': 'Modern Portfolio Theory (Markowitz)',
            'description': 'Maximizes expected return for a given level of risk by considering correlations between assets.',
            'advantages': ['Scientifically proven', 'Considers correlations', 'Optimizes risk-return tradeoff'],
            'disadvantages': ['Sensitive to input estimates', 'Assumes normal returns']
        },
        {
            'id': 'risk_parity',
            'name': 'Risk Parity',
            'description': 'Allocates capital so that each asset contributes equally to portfolio risk.',
            'advantages': ['Better risk diversification', 'Less sensitive to return estimates', 'Performs well in different markets'],
            'disadvantages': ['May overweight low-risk assets', 'Doesn\'t consider expected returns']
        },
        {
            'id': 'max_sharpe',
            'name': 'Maximum Sharpe Ratio',
            'description': 'Maximizes the risk-adjusted return (Sharpe ratio) of the portfolio.',
            'advantages': ['Optimizes risk-adjusted returns', 'Widely accepted measure', 'Considers both return and risk'],
            'disadvantages': ['Sensitive to return estimates', 'May be concentrated in high-return assets']
        },
        {
            'id': 'hrp',
            'name': 'Hierarchical Risk Parity (HRP)',
            'description': 'Uses clustering algorithms to group similar assets and allocate weights based on hierarchical relationships.',
            'advantages': ['Robust to estimation errors', 'No optimization required', 'Handles large portfolios efficiently'],
            'disadvantages': ['Doesn\'t consider expected returns', 'Clustering results can vary']
        }
    ]
    
    return jsonify({
        'success': True,
        'methods': methods
    })

@main.route('/api/cache/status', methods=['GET'])
@login_required
def api_cache_status():
    """Get cache status for monitoring (admin only)"""
    try:
        # Check if user is admin
        if not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Admin access required'
            }), 403
        
        from services.annualReturn import AnnualReturn
        annual_return = AnnualReturn()
        status = annual_return.get_cache_status()
        return jsonify({
            'success': True,
            'cache_status': status
        })
    except Exception as e:
        logging.error(f"Error getting cache status: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get cache status'
        }), 500

@main.route('/api/cache/refresh', methods=['POST'])
@login_required
def api_cache_refresh():
    """Force refresh of Yahoo Finance cache (admin only)"""
    try:
        # Check if user is admin
        if not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Admin access required'
            }), 403
        
        from services.annualReturn import AnnualReturn
        annual_return = AnnualReturn()
        df = annual_return.force_refresh_annual_returns()
        
        if not df.empty:
            return jsonify({
                'success': True,
                'message': f'Successfully refreshed cache with {len(df)} stocks',
                'count': len(df)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to refresh cache'
            }), 500
    except Exception as e:
        logging.error(f"Error refreshing cache: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to refresh cache'
        }), 500

# Root endpoint for API health check
@main.route('/', methods=['GET'])
def api_root():
    """API root endpoint"""
    return jsonify({
        'message': 'Stocknity API Server',
        'status': 'running',
        'version': '1.0.0'
    })
