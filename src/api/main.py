import json
import logging
import threading
from threading import Thread
from datetime import datetime


import pandas as pd
from flask import Blueprint, request, redirect, url_for, jsonify, current_app
from flask_login import current_user, login_required

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import enums.enum as enum
import services.news as news
import utilities.helper as helper
from services.chart import chart
from services.portfolio import portfolio as buildPortfolio
from services.screener import Screener
from services.strengthCalculator import StrengthCalculator
from services.async_scheduler import (
    start_scheduler, 
    stop_scheduler, 
    get_scheduler_status,
    manual_refresh_data,
    force_refresh_all
)
from services.annualReturn import AnnualReturn
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
    # Get sector and index from query parameters
    sector = request.args.get('sector', 'Any')
    index = request.args.get('index', 'S&P 500')
    
    # Update screener parameters
    screenerService.update_key_sector_and_index(sector=sector, index=index)
    
    stock_data = screenerService.get_screener_data()
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
                current_app.logger.info('Returning latest saved portfolio')
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
            logging.info('Getting value chart data')
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
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear all cached data"""
    try:
        from utilities.redis_data import redis_manager
        
        # Clear all stock data keys
        keys = redis_manager.r.keys("stock_data:*")
        if keys:
            redis_manager.r.delete(*keys)
            current_app.logger.info(f"Cleared {len(keys)} cached stock data keys")
        
        # Clear annual returns cache
        annual_keys = redis_manager.r.keys("annual_returns:*")
        if annual_keys:
            redis_manager.r.delete(*annual_keys)
            current_app.logger.info(f"Cleared {len(annual_keys)} cached annual returns keys")
        
        # Clear chart data cache
        chart_keys = redis_manager.r.keys("chart_data:*")
        if chart_keys:
            redis_manager.r.delete(*chart_keys)
            current_app.logger.info(f"Cleared {len(chart_keys)} cached chart data keys")
        
        return jsonify({
            'success': True,
            'message': f'Cleared {len(keys) + len(annual_keys) + len(chart_keys)} cached items',
            'cleared_stock_keys': len(keys),
            'cleared_annual_keys': len(annual_keys),
            'cleared_chart_keys': len(chart_keys)
        })
    except Exception as e:
        current_app.logger.error(f"Error clearing cache: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@main.route('/api/ai/sentiment/<ticker>', methods=['GET'])
def get_ai_sentiment(ticker):
    """Get AI-powered sentiment analysis for a stock"""
    try:
        # Validate ticker
        if not ticker or ticker.strip() == '':
            return jsonify({
                'error': 'Ticker symbol is required',
                'ticker': ticker
            }), 400
        
        import asyncio
        from services.ai_sentiment_analyzer import ai_sentiment_service
        
        # Run async sentiment analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        sentiment_data = loop.run_until_complete(
            ai_sentiment_service.get_comprehensive_sentiment(ticker.upper().strip())
        )
        loop.close()
        
        return jsonify(sentiment_data)
    except Exception as e:
        current_app.logger.error(f"Error getting AI sentiment for {ticker}: {e}")
        return jsonify({
            'error': str(e),
            'ticker': ticker
        }), 500

@main.route('/api/ai/sentiment/<ticker>/trend', methods=['GET'])
def get_sentiment_trend(ticker):
    """Get sentiment trend over time"""
    try:
        import asyncio
        from services.ai_sentiment_analyzer import ai_sentiment_service
        
        days = request.args.get('days', 7, type=int)
        
        # Run async sentiment trend analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        trend_data = loop.run_until_complete(
            ai_sentiment_service.get_sentiment_trend(ticker.upper(), days)
        )
        loop.close()
        
        return jsonify(trend_data)
    except Exception as e:
        current_app.logger.error(f"Error getting sentiment trend for {ticker}: {e}")
        return jsonify({
            'error': str(e),
            'ticker': ticker
        }), 500

@main.route('/api/ai/recommendations', methods=['GET'])
def get_ai_recommendations():
    """Get AI-powered stock recommendations"""
    try:
        time_horizon = request.args.get('time_horizon', 'medium')
        risk_tolerance = request.args.get('risk_tolerance', 'medium')
        sector = request.args.get('sector', None)
        limit = request.args.get('limit', 10, type=int)
        
        # Mock AI recommendations for now
        # In production, this would use trained ML models
        mock_recommendations = [
            {
                "ticker": "AAPL",
                "score": 0.85,
                "confidence": 0.78,
                "risk_score": 0.25,
                "predicted_return": 0.12,
                "time_horizon": time_horizon,
                "reasoning": "Strong fundamentals, positive sentiment, technical breakout",
                "data_sources": ["technical", "sentiment", "fundamental"]
            },
            {
                "ticker": "MSFT",
                "score": 0.82,
                "confidence": 0.75,
                "risk_score": 0.30,
                "predicted_return": 0.10,
                "time_horizon": time_horizon,
                "reasoning": "Cloud growth, solid earnings, institutional buying",
                "data_sources": ["fundamental", "technical", "sentiment"]
            },
            {
                "ticker": "NVDA",
                "score": 0.88,
                "confidence": 0.82,
                "risk_score": 0.45,
                "predicted_return": 0.18,
                "time_horizon": time_horizon,
                "reasoning": "AI leadership, strong momentum, positive sentiment",
                "data_sources": ["sentiment", "technical", "fundamental"]
            }
        ]
        
        # Filter by sector if specified
        if sector:
            # In production, this would filter based on actual sector data
            mock_recommendations = mock_recommendations[:2]  # Mock filtering
        
        # Limit results
        mock_recommendations = mock_recommendations[:limit]
        
        return jsonify({
            'recommendations': mock_recommendations,
            'time_horizon': time_horizon,
            'risk_tolerance': risk_tolerance,
            'total_count': len(mock_recommendations),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Error getting AI recommendations: {e}")
        return jsonify({
            'error': str(e)
        }), 500

@main.route('/api/ai/performance', methods=['GET'])
def get_ai_performance():
    """Get AI model performance metrics"""
    try:
        # Mock performance metrics
        # In production, this would come from actual model monitoring
        performance_data = {
            "models": {
                "sentiment": {
                    "accuracy": 0.82,
                    "precision": 0.79,
                    "recall": 0.85,
                    "f1_score": 0.82,
                    "last_updated": datetime.now().isoformat()
                },
                "price_prediction": {
                    "mae": 0.045,
                    "rmse": 0.067,
                    "r2_score": 0.73,
                    "last_updated": datetime.now().isoformat()
                },
                "recommendation": {
                    "win_rate": 0.68,
                    "avg_return": 0.12,
                    "sharpe_ratio": 1.2,
                    "max_drawdown": 0.08,
                    "last_updated": datetime.now().isoformat()
                }
            },
            "overall_performance": {
                "total_recommendations": 1250,
                "profitable_recommendations": 850,
                "avg_holding_period": "45 days",
                "last_updated": datetime.now().isoformat()
            }
        }
        
        return jsonify(performance_data)
    except Exception as e:
        current_app.logger.error(f"Error getting AI performance: {e}")
        return jsonify({
            'error': str(e)
        }), 500

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

@main.route('/api/cache/info', methods=['GET'])
def api_cache_info():
    """Get basic cache information (public)"""
    try:
        from utilities.redis_data import redis_manager
        from utilities.constant import SECTORS, INDEX
        
        if not redis_manager.available:
            return jsonify({
                'success': False,
                'error': 'Redis not available'
            }), 503
        
        # Count cached combinations
        cached_count = 0
        total_combinations = 0
        
        for index in INDEX:
            for sector in SECTORS + ['Any']:
                total_combinations += 1
                key = f"stock_data:{index}:{sector}"
                if redis_manager.r.exists(key):
                    cached_count += 1
        
        # Get memory usage
        try:
            info = redis_manager.r.info('memory')
            memory_usage = info.get('used_memory_human', 'Unknown')
        except:
            memory_usage = 'Unknown'
        
        cache_info = {
            'redis_available': redis_manager.available,
            'cached_combinations': cached_count,
            'total_combinations': total_combinations,
            'cache_percentage': round((cached_count / total_combinations) * 100, 1) if total_combinations > 0 else 0,
            'memory_usage': memory_usage,
            'message': f'Cache is working. {cached_count}/{total_combinations} combinations cached.',
            'note': 'Check logs for detailed cache usage information'
        }
        
        return jsonify({
            'success': True,
            'cache_info': cache_info
        })
    except Exception as e:
        logging.error(f"Error getting cache info: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get cache info'
        }), 500

@main.route('/api/cache/tracking', methods=['GET'])
def api_cache_tracking():
    """Get detailed cache tracking information (public)"""
    try:
        from utilities.redis_tracker import redis_tracker
        
        summary = redis_tracker.get_tracking_summary()
        cache_status = redis_tracker.get_cache_status()
        api_history = redis_tracker.get_api_call_history(limit=20)
        
        tracking_info = {
            'summary': summary,
            'cache_status': cache_status,
            'recent_api_calls': api_history,
            'pending_requests': len(redis_tracker.pending_requests)
        }
        
        return jsonify({
            'success': True,
            'tracking_info': tracking_info
        })
    except Exception as e:
        logging.error(f"Error getting cache tracking: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get cache tracking'
        }), 500

@main.route('/api/cache/tracking/clear', methods=['POST'])
def api_clear_tracking():
    """Clear tracking data (admin only)"""
    try:
        from utilities.redis_tracker import redis_tracker
        
        success = redis_tracker.clear_tracking_data()
        
        return jsonify({
            'success': success,
            'message': 'Tracking data cleared' if success else 'Failed to clear tracking data'
        })
    except Exception as e:
        logging.error(f"Error clearing tracking data: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to clear tracking data'
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

# Health check endpoint
@main.route('/api/health', methods=['GET'])
def api_health():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Stocknity API Server is running',
        'version': '1.0.0',
        'timestamp': pd.Timestamp.now().isoformat()
    })

# Scheduler management endpoints
@main.route('/api/scheduler/start', methods=['POST'])
def api_scheduler_start():
    """Start the async scheduler"""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_scheduler())
        return jsonify({
            'success': True,
            'message': 'Scheduler started successfully'
        })
    except Exception as e:
        current_app.logger.error(f"Error starting scheduler: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/scheduler/stop', methods=['POST'])
def api_scheduler_stop():
    """Stop the async scheduler"""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(stop_scheduler())
        return jsonify({
            'success': True,
            'message': 'Scheduler stopped successfully'
        })
    except Exception as e:
        current_app.logger.error(f"Error stopping scheduler: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/scheduler/status', methods=['GET'])
def api_scheduler_status():
    """Get scheduler status"""
    try:
        status = get_scheduler_status()
        return jsonify(status)
    except Exception as e:
        current_app.logger.error(f"Error getting scheduler status: {e}")
        return jsonify({
            'error': str(e)
        }), 500

@main.route('/api/scheduler/refresh', methods=['POST'])
def api_scheduler_refresh():
    """Manually refresh data"""
    try:
        import asyncio
        data = request.get_json() or {}
        index = data.get('index')
        sector = data.get('sector')
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(manual_refresh_data(index, sector))
        
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error refreshing data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/scheduler/force-refresh', methods=['POST'])
def api_scheduler_force_refresh():
    """Force refresh all data"""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(force_refresh_all())
        
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error force refreshing data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
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
