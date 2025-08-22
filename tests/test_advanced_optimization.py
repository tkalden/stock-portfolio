#!/usr/bin/env python3
"""
Test script for advanced portfolio optimization algorithms
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
import pandas as pd
import numpy as np
from services.advanced_optimization import AdvancedPortfolioOptimizer
from services.backtesting import PortfolioBacktester
from services.portfolio import portfolio
from services.strengthCalculator import StrengthCalculator
from utilities.redis_data import redis_manager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_advanced_optimization():
    """Test the advanced optimization algorithms"""
    
    print("=" * 60)
    print("ADVANCED PORTFOLIO OPTIMIZATION TEST")
    print("=" * 60)
    
    # Initialize services
    optimizer = AdvancedPortfolioOptimizer()
    backtester = PortfolioBacktester()
    strength_calc = StrengthCalculator()
    
    try:
        # Get sample data from Redis
        print("\n1. Loading sample data from Redis...")
        stock_data = redis_manager.get_stock_data('S&P 500', 'Any')
        
        if stock_data.empty:
            print("No data found in Redis. Please run the scheduler first.")
            return
        
        print(f"Loaded {len(stock_data)} stocks")
        
        # Calculate strength data
        print("\n2. Calculating strength data...")
        strength_df = strength_calc.calculate_strength_value('Value', 'Any', 'S&P 500')
        
        if strength_df.empty:
            print("No strength data available.")
            return
        
        print(f"Calculated strength for {len(strength_df)} stocks")
        
        # Filter data for optimization
        print("\n3. Filtering data for optimization...")
        df_filtered = strength_df[
            (strength_df['strength'] > 0) & 
            (strength_df['expected_annual_return'].astype(float) > 0) &
            (strength_df['price'].astype(float) < 100)  # Max price $100
        ].head(10)  # Top 10 stocks
        
        print(f"Selected {len(df_filtered)} stocks for optimization")
        
        if df_filtered.empty:
            print("No stocks passed the filters.")
            return
        
        # Test different optimization methods
        print("\n4. Testing optimization methods...")
        methods = ['markowitz', 'risk_parity', 'max_sharpe', 'hrp']
        
        results = {}
        for method in methods:
            try:
                print(f"\n   Testing {method.upper()} method...")
                result = optimizer.optimize_portfolio(df_filtered, method=method)
                results[method] = result
                
                print(f"   Expected Return: {result['expected_return']:.4f} ({result['expected_return']*100:.2f}%)")
                print(f"   Volatility: {result['volatility']:.4f} ({result['volatility']*100:.2f}%)")
                print(f"   Sharpe Ratio: {result['sharpe_ratio']:.4f}")
                
            except Exception as e:
                print(f"   Error with {method}: {e}")
                results[method] = None
        
        # Compare methods
        print("\n5. Method Comparison Summary:")
        print("-" * 80)
        print(f"{'Method':<15} {'Return':<12} {'Volatility':<12} {'Sharpe':<10} {'Top Holdings'}")
        print("-" * 80)
        
        for method, result in results.items():
            if result is not None:
                # Get top 3 holdings by weight
                weights = result['weights']
                tickers = result['tickers']
                top_holdings = [tickers[i] for i in np.argsort(weights)[-3:][::-1]]
                top_weights = [weights[i] for i in np.argsort(weights)[-3:][::-1]]
                
                holdings_str = ", ".join([f"{t}({w:.1%})" for t, w in zip(top_holdings, top_weights)])
                
                print(f"{method.upper():<15} "
                      f"{result['expected_return']*100:>8.2f}% "
                      f"{result['volatility']*100:>10.2f}% "
                      f"{result['sharpe_ratio']:>8.2f} "
                      f"{holdings_str}")
        
        # Backtesting
        print("\n6. Running backtesting...")
        if any(results.values()):
            # Use the best performing method for backtesting
            best_method = max(results.keys(), 
                            key=lambda x: results[x]['sharpe_ratio'] if results[x] else -999)
            best_result = results[best_method]
            
            print(f"Using {best_method.upper()} method for backtesting...")
            
            # Generate historical data
            tickers = best_result['tickers']
            weights = best_result['weights']
            historical_prices = backtester.generate_historical_data(tickers)
            
            # Define strategies
            strategies = {
                'Equal Weight': np.ones(len(tickers)) / len(tickers),
                f'{best_method.upper()}': weights,
            }
            
            # Run backtesting
            backtest_results = backtester.compare_strategies(historical_prices, strategies)
            
            # Print backtesting report
            report = backtester.generate_report(backtest_results)
            print("\n" + report)
        
        print("\n7. Advanced Optimization Test Completed Successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

def test_portfolio_integration():
    """Test the integration with the existing portfolio service"""
    
    print("\n" + "=" * 60)
    print("PORTFOLIO SERVICE INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Initialize portfolio service
        portfolio_service = portfolio()
        
        # Get sample data
        strength_calc = StrengthCalculator()
        strength_df = strength_calc.calculate_strength_value('Value', 'Any', 'S&P 500')
        
        if strength_df.empty:
            print("No strength data available for integration test.")
            return
        
        # Test advanced optimization
        print("\nTesting advanced portfolio optimization...")
        result_df = portfolio_service.build_portfolio_with_advanced_optimization(
            strength_df, 
            investing_amount=10000, 
            maximum_stock_price=100, 
            risk_tolerance='Medium',
            method='markowitz'
        )
        
        if not result_df.empty:
            print(f"Successfully built portfolio with {len(result_df)} stocks")
            print("\nPortfolio Summary:")
            print(f"Total Investment: $10,000")
            print(f"Expected Return: {portfolio_service.get_optimization_metrics().get('expected_return', 0)*100:.2f}%")
            print(f"Expected Volatility: {portfolio_service.get_optimization_metrics().get('volatility', 0)*100:.2f}%")
            print(f"Sharpe Ratio: {portfolio_service.get_optimization_metrics().get('sharpe_ratio', 0):.3f}")
            
            print("\nTop Holdings:")
            for _, row in result_df.head(5).iterrows():
                print(f"  {row['Ticker']}: {row['weight']:.1%} (${row['invested_amount']:.0f})")
        
        # Test method comparison
        print("\nTesting method comparison...")
        comparison_results = portfolio_service.compare_optimization_methods(
            strength_df, 
            investing_amount=10000, 
            maximum_stock_price=100, 
            risk_tolerance='Medium'
        )
        
        print("\nMethod Comparison Results:")
        for method, result in comparison_results.items():
            if result:
                print(f"  {method.upper()}: Return={result['expected_return']*100:.2f}%, "
                      f"Vol={result['volatility']*100:.2f}%, Sharpe={result['sharpe_ratio']:.3f}")
        
        print("\nPortfolio Service Integration Test Completed Successfully!")
        
    except Exception as e:
        print(f"Error during integration test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting Advanced Portfolio Optimization Tests...")
    
    # Test 1: Advanced optimization algorithms
    test_advanced_optimization()
    
    # Test 2: Portfolio service integration
    test_portfolio_integration()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Install additional dependencies: pip install scipy cvxpy scikit-learn seaborn")
    print("2. Run the scheduler to populate Redis with data")
    print("3. Test the optimization in your web application")
    print("4. Review the documentation in docs/ADVANCED_OPTIMIZATION.md") 