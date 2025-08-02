import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class PortfolioBacktester:
    """
    Comprehensive backtesting framework for portfolio optimization strategies
    """
    
    def __init__(self, risk_free_rate=0.02):
        self.risk_free_rate = risk_free_rate
        self.logger = logging.getLogger(__name__)
        
    def generate_historical_data(self, tickers, start_date='2020-01-01', end_date='2024-01-01'):
        """
        Generate synthetic historical data for backtesting
        In production, you'd use real market data from yfinance or other sources
        """
        np.random.seed(42)  # For reproducibility
        
        # Generate dates
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        dates = dates[dates.weekday < 5]  # Only weekdays
        
        # Generate synthetic price data
        data = {}
        for ticker in tickers:
            # Generate random walk with drift
            initial_price = np.random.uniform(50, 200)
            daily_returns = np.random.normal(0.0005, 0.02, len(dates))  # 0.05% daily return, 2% daily vol
            
            # Add some autocorrelation and volatility clustering
            for i in range(1, len(daily_returns)):
                daily_returns[i] = 0.1 * daily_returns[i-1] + 0.9 * daily_returns[i]
            
            prices = [initial_price]
            for ret in daily_returns[1:]:
                prices.append(prices[-1] * (1 + ret))
            
            data[ticker] = prices
        
        # Create DataFrame
        df = pd.DataFrame(data, index=dates)
        return df
    
    def calculate_rolling_returns(self, prices, window=252):
        """
        Calculate rolling returns for backtesting
        """
        returns = prices.pct_change().dropna()
        rolling_returns = returns.rolling(window=window).mean() * 252  # Annualized
        rolling_vol = returns.rolling(window=window).std() * np.sqrt(252)  # Annualized
        
        return rolling_returns, rolling_vol
    
    def backtest_strategy(self, prices, weights, rebalance_freq='M'):
        """
        Backtest a portfolio strategy with given weights
        """
        # Calculate returns
        returns = prices.pct_change().dropna()
        
        # Rebalance dates
        if rebalance_freq == 'M':
            rebalance_dates = returns.index.to_period('M').unique()
        elif rebalance_freq == 'Q':
            rebalance_dates = returns.index.to_period('Q').unique()
        else:
            rebalance_dates = returns.index
        
        # Initialize portfolio
        portfolio_values = [1.0]  # Start with $1
        portfolio_returns = []
        current_weights = weights.copy()
        
        for i, date in enumerate(returns.index):
            if i == 0:
                continue
                
            # Calculate portfolio return for this period
            period_return = np.sum(current_weights * returns.iloc[i])
            portfolio_returns.append(period_return)
            
            # Update portfolio value
            new_value = portfolio_values[-1] * (1 + period_return)
            portfolio_values.append(new_value)
            
            # Rebalance if needed
            if date in rebalance_dates:
                # In practice, you'd recalculate weights here
                # For now, we'll keep the same weights
                pass
        
        return np.array(portfolio_values), np.array(portfolio_returns)
    
    def calculate_performance_metrics(self, portfolio_values, portfolio_returns):
        """
        Calculate comprehensive performance metrics
        """
        # Total return
        total_return = (portfolio_values[-1] / portfolio_values[0]) - 1
        
        # Annualized return
        years = len(portfolio_values) / 252
        annualized_return = (portfolio_values[-1] / portfolio_values[0]) ** (1/years) - 1
        
        # Volatility
        volatility = np.std(portfolio_returns) * np.sqrt(252)
        
        # Sharpe ratio
        excess_returns = np.array(portfolio_returns) - self.risk_free_rate/252
        sharpe_ratio = np.mean(excess_returns) / np.std(portfolio_returns) * np.sqrt(252)
        
        # Maximum drawdown
        peak = np.maximum.accumulate(portfolio_values)
        drawdown = (portfolio_values - peak) / peak
        max_drawdown = np.min(drawdown)
        
        # VaR (Value at Risk) - 95% confidence
        var_95 = np.percentile(portfolio_returns, 5)
        
        # CVaR (Conditional Value at Risk) - 95% confidence
        cvar_95 = np.mean(portfolio_returns[portfolio_returns <= var_95])
        
        # Calmar ratio (return / max drawdown)
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Information ratio (assuming benchmark return of 0.08)
        benchmark_return = 0.08
        excess_return = annualized_return - benchmark_return
        tracking_error = np.std(portfolio_returns) * np.sqrt(252)
        information_ratio = excess_return / tracking_error if tracking_error != 0 else 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'calmar_ratio': calmar_ratio,
            'information_ratio': information_ratio
        }
    
    def monte_carlo_simulation(self, returns, weights, n_simulations=10000, time_horizon=252):
        """
        Monte Carlo simulation for portfolio risk analysis
        """
        # Calculate portfolio parameters
        portfolio_return = np.sum(weights * returns.mean())
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov(), weights)))
        
        # Generate simulations
        simulations = np.random.normal(portfolio_return, portfolio_vol, (n_simulations, time_horizon))
        
        # Calculate cumulative returns
        cumulative_returns = np.cumprod(1 + simulations, axis=1)
        
        # Calculate VaR and CVaR
        final_values = cumulative_returns[:, -1]
        var_95 = np.percentile(final_values, 5)
        cvar_95 = np.mean(final_values[final_values <= var_95])
        
        return {
            'simulations': simulations,
            'cumulative_returns': cumulative_returns,
            'final_values': final_values,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'expected_value': np.mean(final_values),
            'volatility': np.std(final_values)
        }
    
    def stress_test(self, portfolio_values, portfolio_returns, scenarios):
        """
        Stress testing under different market scenarios
        """
        results = {}
        
        for scenario_name, scenario_params in scenarios.items():
            # Apply scenario adjustments
            adjusted_returns = portfolio_returns * scenario_params.get('return_multiplier', 1.0)
            adjusted_vol = np.std(adjusted_returns) * scenario_params.get('vol_multiplier', 1.0)
            
            # Recalculate portfolio values
            adjusted_values = [1.0]
            for ret in adjusted_returns:
                adjusted_values.append(adjusted_values[-1] * (1 + ret))
            
            # Calculate metrics
            metrics = self.calculate_performance_metrics(adjusted_values, adjusted_returns)
            results[scenario_name] = metrics
        
        return results
    
    def compare_strategies(self, prices, strategies):
        """
        Compare multiple portfolio strategies
        """
        results = {}
        
        for strategy_name, weights in strategies.items():
            try:
                # Backtest strategy
                portfolio_values, portfolio_returns = self.backtest_strategy(prices, weights)
                
                # Calculate metrics
                metrics = self.calculate_performance_metrics(portfolio_values, portfolio_returns)
                
                # Monte Carlo simulation
                returns = prices.pct_change().dropna()
                mc_results = self.monte_carlo_simulation(returns, weights)
                
                results[strategy_name] = {
                    'metrics': metrics,
                    'portfolio_values': portfolio_values,
                    'portfolio_returns': portfolio_returns,
                    'monte_carlo': mc_results
                }
                
            except Exception as e:
                self.logger.error(f"Error backtesting strategy {strategy_name}: {e}")
                results[strategy_name] = None
        
        return results
    
    def plot_results(self, results, save_path=None):
        """
        Create comprehensive visualization of backtesting results
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Plot 1: Portfolio Value Evolution
        ax1 = axes[0, 0]
        for strategy_name, result in results.items():
            if result is not None:
                ax1.plot(result['portfolio_values'], label=strategy_name)
        ax1.set_title('Portfolio Value Evolution')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Portfolio Value')
        ax1.legend()
        ax1.grid(True)
        
        # Plot 2: Risk-Return Scatter
        ax2 = axes[0, 1]
        for strategy_name, result in results.items():
            if result is not None:
                metrics = result['metrics']
                ax2.scatter(metrics['volatility'], metrics['annualized_return'], 
                           label=strategy_name, s=100)
        ax2.set_title('Risk-Return Profile')
        ax2.set_xlabel('Volatility')
        ax2.set_ylabel('Annualized Return')
        ax2.legend()
        ax2.grid(True)
        
        # Plot 3: Drawdown Analysis
        ax3 = axes[1, 0]
        for strategy_name, result in results.items():
            if result is not None:
                portfolio_values = result['portfolio_values']
                peak = np.maximum.accumulate(portfolio_values)
                drawdown = (portfolio_values - peak) / peak
                ax3.plot(drawdown, label=strategy_name)
        ax3.set_title('Drawdown Analysis')
        ax3.set_xlabel('Time')
        ax3.set_ylabel('Drawdown')
        ax3.legend()
        ax3.grid(True)
        
        # Plot 4: Monte Carlo Distribution
        ax4 = axes[1, 1]
        for strategy_name, result in results.items():
            if result is not None:
                final_values = result['monte_carlo']['final_values']
                ax4.hist(final_values, bins=50, alpha=0.7, label=strategy_name, density=True)
        ax4.set_title('Monte Carlo Distribution (Final Values)')
        ax4.set_xlabel('Portfolio Value')
        ax4.set_ylabel('Density')
        ax4.legend()
        ax4.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def generate_report(self, results):
        """
        Generate comprehensive backtesting report
        """
        report = []
        report.append("=" * 60)
        report.append("PORTFOLIO BACKTESTING REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary table
        report.append("PERFORMANCE SUMMARY")
        report.append("-" * 40)
        report.append(f"{'Strategy':<20} {'Return':<10} {'Vol':<10} {'Sharpe':<10} {'MaxDD':<10}")
        report.append("-" * 60)
        
        for strategy_name, result in results.items():
            if result is not None:
                metrics = result['metrics']
                report.append(f"{strategy_name:<20} "
                            f"{metrics['annualized_return']*100:>8.2f}% "
                            f"{metrics['volatility']*100:>8.2f}% "
                            f"{metrics['sharpe_ratio']:>8.2f} "
                            f"{metrics['max_drawdown']*100:>8.2f}%")
        
        report.append("")
        
        # Detailed metrics
        report.append("DETAILED METRICS")
        report.append("-" * 40)
        
        for strategy_name, result in results.items():
            if result is not None:
                metrics = result['metrics']
                mc = result['monte_carlo']
                
                report.append(f"\n{strategy_name.upper()}:")
                report.append(f"  Total Return: {metrics['total_return']*100:.2f}%")
                report.append(f"  Annualized Return: {metrics['annualized_return']*100:.2f}%")
                report.append(f"  Volatility: {metrics['volatility']*100:.2f}%")
                report.append(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
                report.append(f"  Maximum Drawdown: {metrics['max_drawdown']*100:.2f}%")
                report.append(f"  VaR (95%): {metrics['var_95']*100:.2f}%")
                report.append(f"  CVaR (95%): {metrics['cvar_95']*100:.2f}%")
                report.append(f"  Calmar Ratio: {metrics['calmar_ratio']:.3f}")
                report.append(f"  Information Ratio: {metrics['information_ratio']:.3f}")
                report.append(f"  Monte Carlo VaR (95%): {mc['var_95']:.3f}")
                report.append(f"  Monte Carlo Expected Value: {mc['expected_value']:.3f}")
        
        return "\n".join(report) 