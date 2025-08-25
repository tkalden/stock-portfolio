import logging
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Conditional imports for optional optimization packages
try:
    from scipy.optimize import minimize
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("scipy not available - advanced optimization features disabled")

try:
    import cvxpy as cp
    CVXPY_AVAILABLE = True
except ImportError:
    CVXPY_AVAILABLE = False
    logging.warning("cvxpy not available - convex optimization features disabled")

try:
    from sklearn.covariance import LedoitWolf
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available - machine learning features disabled")

class AdvancedPortfolioOptimizer:
    """
    Advanced Portfolio Optimization using multiple state-of-the-art algorithms
    """
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% risk-free rate
        self.logger = logging.getLogger(__name__)
    
    def calculate_returns_and_covariance(self, df):
        """
        Calculate historical returns and covariance matrix with robust estimation
        """
        try:
            # Extract price data and calculate returns
            price_cols = ['price'] if 'price' in df.columns else ['Price']
            if price_cols[0] not in df.columns:
                raise ValueError("Price column not found in data")
            
            # For now, we'll use the expected returns from the data
            # In a real implementation, you'd calculate historical returns
            returns = df[['Ticker', 'expected_annual_return', 'expected_annual_risk']].copy()
            returns = returns.set_index('Ticker')
            
            # Create a covariance matrix based on risk and correlation assumptions
            n_assets = len(returns)
            correlation_matrix = self._estimate_correlation_matrix(returns)
            
            # Create covariance matrix: Cov = Corr * std_i * std_j
            std_devs = returns['expected_annual_risk'].values
            covariance_matrix = np.outer(std_devs, std_devs) * correlation_matrix
            
            return returns['expected_annual_return'].values, covariance_matrix, returns.index.tolist()
            
        except Exception as e:
            self.logger.error(f"Error calculating returns and covariance: {e}")
            raise
    
    def _estimate_correlation_matrix(self, returns_df):
        """
        Estimate correlation matrix using sector-based correlations
        """
        n_assets = len(returns_df)
        
        # Base correlation matrix (assuming some sector-based correlation)
        # In practice, you'd use historical correlation data
        base_corr = 0.3  # Base correlation between stocks
        correlation_matrix = np.full((n_assets, n_assets), base_corr)
        np.fill_diagonal(correlation_matrix, 1.0)
        
        # Add some random variation to make it more realistic
        np.random.seed(42)  # For reproducibility
        noise = np.random.normal(0, 0.1, (n_assets, n_assets))
        noise = (noise + noise.T) / 2  # Make symmetric
        np.fill_diagonal(noise, 0)
        
        correlation_matrix += noise
        correlation_matrix = np.clip(correlation_matrix, -0.9, 0.9)
        
        return correlation_matrix
    
    def markowitz_optimization(self, returns, covariance, target_return=None, risk_aversion=1.0):
        """
        Modern Portfolio Theory (Markowitz) optimization
        """
        if not CVXPY_AVAILABLE:
            raise ImportError("cvxpy is required for Markowitz optimization. Install with: pip install cvxpy")
            
        n_assets = len(returns)
        
        # Define the optimization problem
        weights = cp.Variable(n_assets)
        
        # Expected portfolio return
        portfolio_return = cp.sum(cp.multiply(weights, returns))
        
        # Portfolio variance
        portfolio_variance = cp.quad_form(weights, covariance)
        
        # Objective function: maximize Sharpe ratio (return - risk_aversion * variance)
        objective = portfolio_return - risk_aversion * portfolio_variance
        
        # Constraints
        constraints = [
            cp.sum(weights) == 1,  # Weights sum to 1
            weights >= 0,  # No short selling
        ]
        
        if target_return is not None:
            constraints.append(portfolio_return >= target_return)
        
        # Solve the optimization problem
        problem = cp.Problem(cp.Maximize(objective), constraints)
        problem.solve()
        
        if problem.status == 'optimal':
            optimal_weights = weights.value
            portfolio_ret = portfolio_return.value
            portfolio_vol = np.sqrt(portfolio_variance.value)
            sharpe_ratio = (portfolio_ret - self.risk_free_rate) / portfolio_vol
            
            return {
                'weights': optimal_weights,
                'expected_return': portfolio_ret,
                'volatility': portfolio_vol,
                'sharpe_ratio': sharpe_ratio,
                'method': 'Markowitz'
            }
        else:
            raise ValueError("Markowitz optimization failed to converge")
    
    def risk_parity_optimization(self, returns, covariance):
        """
        Risk Parity optimization - equal risk contribution from each asset
        """
        if not SCIPY_AVAILABLE:
            raise ImportError("scipy is required for risk parity optimization. Install with: pip install scipy")
            
        n_assets = len(returns)
        
        def risk_contribution(weights):
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(covariance, weights)))
            marginal_risk = np.dot(covariance, weights) / portfolio_vol
            risk_contrib = weights * marginal_risk
            return risk_contrib
        
        def objective(weights):
            risk_contrib = risk_contribution(weights)
            # Minimize the variance of risk contributions
            return np.var(risk_contrib)
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Weights sum to 1
        ]
        
        # Bounds: no short selling
        bounds = [(0, 1) for _ in range(n_assets)]
        
        # Initial guess: equal weights
        initial_weights = np.ones(n_assets) / n_assets
        
        # Optimize
        result = minimize(objective, initial_weights, method='SLSQP', 
                         bounds=bounds, constraints=constraints)
        
        if result.success:
            optimal_weights = result.x
            portfolio_ret = np.dot(optimal_weights, returns)
            portfolio_vol = np.sqrt(np.dot(optimal_weights.T, np.dot(covariance, optimal_weights)))
            sharpe_ratio = (portfolio_ret - self.risk_free_rate) / portfolio_vol
            
            return {
                'weights': optimal_weights,
                'expected_return': portfolio_ret,
                'volatility': portfolio_vol,
                'sharpe_ratio': sharpe_ratio,
                'method': 'Risk Parity'
            }
        else:
            raise ValueError("Risk Parity optimization failed to converge")
    
    def maximum_sharpe_optimization(self, returns, covariance):
        """
        Maximum Sharpe Ratio optimization
        """
        n_assets = len(returns)
        
        def negative_sharpe(weights):
            portfolio_ret = np.dot(weights, returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(covariance, weights)))
            return -(portfolio_ret - self.risk_free_rate) / portfolio_vol
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Weights sum to 1
        ]
        
        # Bounds: no short selling
        bounds = [(0, 1) for _ in range(n_assets)]
        
        # Initial guess: equal weights
        initial_weights = np.ones(n_assets) / n_assets
        
        # Optimize
        result = minimize(negative_sharpe, initial_weights, method='SLSQP', 
                         bounds=bounds, constraints=constraints)
        
        if result.success:
            optimal_weights = result.x
            portfolio_ret = np.dot(optimal_weights, returns)
            portfolio_vol = np.sqrt(np.dot(optimal_weights.T, np.dot(covariance, optimal_weights)))
            sharpe_ratio = (portfolio_ret - self.risk_free_rate) / portfolio_vol
            
            return {
                'weights': optimal_weights,
                'expected_return': portfolio_ret,
                'volatility': portfolio_vol,
                'sharpe_ratio': sharpe_ratio,
                'method': 'Maximum Sharpe'
            }
        else:
            raise ValueError("Maximum Sharpe optimization failed to converge")
    
    def hierarchical_risk_parity(self, returns, covariance, linkage_method='single'):
        """
        Hierarchical Risk Parity (HRP) - clustering-based portfolio optimization
        """
        from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
        from scipy.spatial.distance import squareform
        
        n_assets = len(returns)
        
        # Convert correlation matrix to distance matrix
        correlation_matrix = self._covariance_to_correlation(covariance)
        
        # Ensure correlation matrix is valid
        correlation_matrix = np.clip(correlation_matrix, -0.999, 0.999)
        
        # Calculate distance matrix
        distance_matrix = np.sqrt(0.5 * (1 - correlation_matrix))
        
        # Ensure distance matrix is symmetric
        distance_matrix = (distance_matrix + distance_matrix.T) / 2
        np.fill_diagonal(distance_matrix, 0)
        
        # Convert to condensed distance matrix
        condensed_distances = squareform(distance_matrix)
        
        # Perform hierarchical clustering
        linkage_matrix = linkage(condensed_distances, method=linkage_method)
        
        # Get cluster assignments
        clusters = fcluster(linkage_matrix, n_assets, criterion='maxclust')
        
        # Calculate weights using HRP algorithm
        weights = self._hrp_weights(correlation_matrix, clusters)
        
        # Calculate portfolio metrics
        portfolio_ret = np.dot(weights, returns)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(covariance, weights)))
        sharpe_ratio = (portfolio_ret - self.risk_free_rate) / portfolio_vol
        
        return {
            'weights': weights,
            'expected_return': portfolio_ret,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe_ratio,
            'method': 'Hierarchical Risk Parity'
        }
    
    def _covariance_to_correlation(self, covariance):
        """Convert covariance matrix to correlation matrix"""
        std_devs = np.sqrt(np.diag(covariance))
        correlation = covariance / np.outer(std_devs, std_devs)
        return correlation
    
    def _hrp_weights(self, correlation_matrix, clusters):
        """Calculate HRP weights based on clustering"""
        n_assets = len(correlation_matrix)
        weights = np.zeros(n_assets)
        
        # Group assets by cluster
        unique_clusters = np.unique(clusters)
        
        for cluster in unique_clusters:
            cluster_indices = np.where(clusters == cluster)[0]
            cluster_size = len(cluster_indices)
            
            if cluster_size == 1:
                # Single asset cluster
                weights[cluster_indices[0]] = 1.0 / len(unique_clusters)
            else:
                # Multiple asset cluster - use inverse variance weighting
                cluster_corr = correlation_matrix[np.ix_(cluster_indices, cluster_indices)]
                cluster_weights = np.ones(cluster_size) / cluster_size
                
                # Distribute cluster weight among assets
                cluster_weight = 1.0 / len(unique_clusters)
                for i, idx in enumerate(cluster_indices):
                    weights[idx] = cluster_weight * cluster_weights[i]
        
        return weights
    
    def black_litterman_optimization(self, returns, covariance, market_caps=None, views=None):
        """
        Black-Litterman model for incorporating views into portfolio optimization
        """
        n_assets = len(returns)
        
        # If no market caps provided, assume equal market cap
        if market_caps is None:
            market_caps = np.ones(n_assets)
        
        # Calculate market equilibrium returns (reverse optimization)
        market_weights = market_caps / np.sum(market_caps)
        delta = 2.5  # Risk aversion parameter
        pi = delta * np.dot(covariance, market_weights)
        
        # If no views provided, use market equilibrium
        if views is None:
            return self.markowitz_optimization(pi, covariance)
        
        # Incorporate views using Black-Litterman formula
        # This is a simplified version - in practice you'd need more sophisticated view modeling
        tau = 0.05  # Scaling factor for views
        
        # For simplicity, assume views are on individual assets
        view_matrix = np.eye(n_assets)
        view_returns = returns  # Use current expected returns as views
        
        # Black-Litterman posterior
        omega = tau * np.dot(np.dot(view_matrix, covariance), view_matrix.T)
        bl_returns = np.linalg.inv(np.linalg.inv(tau * covariance) + 
                                  np.dot(np.dot(view_matrix.T, np.linalg.inv(omega)), view_matrix))
        bl_returns = np.dot(bl_returns, 
                           np.dot(np.linalg.inv(tau * covariance), pi) + 
                           np.dot(np.dot(view_matrix.T, np.linalg.inv(omega)), view_returns))
        
        bl_covariance = covariance + np.linalg.inv(np.linalg.inv(tau * covariance) + 
                                                  np.dot(np.dot(view_matrix.T, np.linalg.inv(omega)), view_matrix))
        
        return self.markowitz_optimization(bl_returns, bl_covariance)
    
    def optimize_portfolio(self, df, method='markowitz', **kwargs):
        """
        Main optimization method that selects and runs the appropriate algorithm
        """
        try:
            # Calculate returns and covariance
            returns, covariance, tickers = self.calculate_returns_and_covariance(df)
            
            self.logger.info(f"Optimizing portfolio with {len(returns)} assets using {method} method")
            
            # Select optimization method
            if method.lower() == 'markowitz':
                result = self.markowitz_optimization(returns, covariance, **kwargs)
            elif method.lower() == 'risk_parity':
                result = self.risk_parity_optimization(returns, covariance)
            elif method.lower() == 'max_sharpe':
                result = self.maximum_sharpe_optimization(returns, covariance)
            elif method.lower() == 'hrp':
                result = self.hierarchical_risk_parity(returns, covariance)
            elif method.lower() == 'black_litterman':
                result = self.black_litterman_optimization(returns, covariance, **kwargs)
            else:
                raise ValueError(f"Unknown optimization method: {method}")
            
            # Add ticker information to result
            result['tickers'] = tickers
            
            self.logger.info(f"Optimization completed. Expected return: {result['expected_return']:.4f}, "
                           f"Volatility: {result['volatility']:.4f}, Sharpe: {result['sharpe_ratio']:.4f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Portfolio optimization failed: {e}")
            raise
    
    def compare_methods(self, df):
        """
        Compare all optimization methods and return results
        """
        methods = ['markowitz', 'risk_parity', 'max_sharpe', 'hrp']
        results = {}
        
        for method in methods:
            try:
                results[method] = self.optimize_portfolio(df, method=method)
            except Exception as e:
                self.logger.warning(f"Method {method} failed: {e}")
                results[method] = None
        
        return results
    
    def calculate_portfolio_metrics(self, weights, returns, covariance):
        """
        Calculate comprehensive portfolio metrics
        """
        portfolio_return = np.dot(weights, returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(covariance, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
        
        # Calculate diversification ratio
        weighted_vol = np.sum(weights * np.sqrt(np.diag(covariance)))
        diversification_ratio = weighted_vol / portfolio_volatility
        
        # Calculate maximum drawdown (simplified)
        # In practice, you'd use historical data for this
        max_drawdown = portfolio_volatility * 2.5  # Rough estimate
        
        return {
            'expected_return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': sharpe_ratio,
            'diversification_ratio': diversification_ratio,
            'max_drawdown_estimate': max_drawdown,
            'risk_free_rate': self.risk_free_rate
        } 