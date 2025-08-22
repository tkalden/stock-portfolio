"""
AI Sentiment Analyzer Service

This module provides sentiment analysis capabilities for the AI investment system.
It analyzes text from various sources (Reddit, Twitter, News) to determine sentiment scores.
"""

import logging
import re
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass

# For future ML implementation
# from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
# import torch

logger = logging.getLogger(__name__)

@dataclass
class SentimentResult:
    """Result of sentiment analysis"""
    text: str
    sentiment_score: float  # -1.0 to 1.0 (negative to positive)
    confidence: float  # 0.0 to 1.0
    source: str
    timestamp: datetime
    keywords: List[str]
    volume: int = 1

class SentimentAnalyzer:
    """Basic sentiment analyzer using rule-based approach (placeholder for ML)"""
    
    def __init__(self):
        self.positive_words = {
            'bull', 'bullish', 'moon', 'rocket', 'pump', 'buy', 'long', 'profit',
            'gain', 'rise', 'up', 'strong', 'good', 'great', 'excellent', 'amazing',
            'outperform', 'beat', 'surge', 'rally', 'breakout', 'breakthrough'
        }
        
        self.negative_words = {
            'bear', 'bearish', 'dump', 'sell', 'short', 'loss', 'drop', 'down',
            'weak', 'bad', 'terrible', 'awful', 'underperform', 'miss', 'crash',
            'plunge', 'decline', 'breakdown', 'failure', 'bankruptcy'
        }
        
        self.intensifiers = {
            'very': 1.5, 'extremely': 2.0, 'super': 1.8, 'mega': 2.0,
            'ultra': 1.8, 'insane': 2.0, 'crazy': 1.5, 'wild': 1.3
        }
        
        self.negators = {
            'not', 'no', 'never', 'none', 'nobody', 'nothing', 'neither',
            'nowhere', 'hardly', 'barely', 'scarcely', 'doesnt', 'isnt', 'arent'
        }
    
    def analyze_text(self, text: str, source: str = "unknown") -> SentimentResult:
        """Analyze sentiment of a single text"""
        try:
            # Clean text
            cleaned_text = self._clean_text(text)
            
            # Calculate sentiment score
            sentiment_score = self._calculate_sentiment(cleaned_text)
            
            # Extract keywords
            keywords = self._extract_keywords(cleaned_text)
            
            # Calculate confidence (simplified)
            confidence = self._calculate_confidence(cleaned_text, sentiment_score)
            
            return SentimentResult(
                text=text,
                sentiment_score=sentiment_score,
                confidence=confidence,
                source=source,
                timestamp=datetime.now(),
                keywords=keywords
            )
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return SentimentResult(
                text=text,
                sentiment_score=0.0,
                confidence=0.0,
                source=source,
                timestamp=datetime.now(),
                keywords=[]
            )
    
    def analyze_batch(self, texts: List[str], source: str = "unknown") -> List[SentimentResult]:
        """Analyze sentiment of multiple texts"""
        results = []
        for text in texts:
            result = self.analyze_text(text, source)
            results.append(result)
        return results
    
    def aggregate_sentiment(self, results: List[SentimentResult]) -> Dict:
        """Aggregate sentiment results into summary statistics"""
        if not results:
            return {
                'overall_sentiment': 0.0,
                'confidence': 0.0,
                'volume': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'top_keywords': [],
                'sources': {}
            }
        
        # Calculate weighted average sentiment
        total_weight = sum(r.confidence for r in results)
        if total_weight > 0:
            overall_sentiment = sum(r.sentiment_score * r.confidence for r in results) / total_weight
        else:
            overall_sentiment = 0.0
        
        # Count sentiment categories
        positive_count = sum(1 for r in results if r.sentiment_score > 0.1)
        negative_count = sum(1 for r in results if r.sentiment_score < -0.1)
        neutral_count = len(results) - positive_count - negative_count
        
        # Aggregate keywords
        all_keywords = []
        for result in results:
            all_keywords.extend(result.keywords)
        
        keyword_counts = pd.Series(all_keywords).value_counts()
        top_keywords = keyword_counts.head(10).index.tolist()
        
        # Aggregate by source
        sources = {}
        for result in results:
            if result.source not in sources:
                sources[result.source] = {
                    'sentiment': 0.0,
                    'volume': 0,
                    'confidence': 0.0
                }
            sources[result.source]['sentiment'] += result.sentiment_score
            sources[result.source]['volume'] += result.volume
            sources[result.source]['confidence'] += result.confidence
        
        # Normalize source aggregations
        for source in sources:
            if sources[source]['volume'] > 0:
                sources[source]['sentiment'] /= sources[source]['volume']
                sources[source]['confidence'] /= sources[source]['volume']
        
        return {
            'overall_sentiment': overall_sentiment,
            'confidence': np.mean([r.confidence for r in results]),
            'volume': len(results),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'top_keywords': top_keywords,
            'sources': sources
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s!?.,#$%&*()]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score using rule-based approach"""
        words = text.split()
        score = 0.0
        negation_count = 0
        
        for i, word in enumerate(words):
            word_score = 0.0
            
            # Check for positive words
            if word in self.positive_words:
                word_score = 1.0
            elif word in self.negative_words:
                word_score = -1.0
            
            # Apply intensifiers
            if i > 0 and words[i-1] in self.intensifiers:
                word_score *= self.intensifiers[words[i-1]]
            
            # Check for negators
            if i > 0 and words[i-1] in self.negators:
                word_score *= -1
                negation_count += 1
            
            score += word_score
        
        # Normalize score
        if len(words) > 0:
            score = score / len(words)
        
        # Clamp to [-1, 1]
        score = max(-1.0, min(1.0, score))
        
        return score
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        words = text.split()
        keywords = []
        
        # Extract words that might be stock tickers (all caps, 1-5 letters)
        for word in words:
            if re.match(r'^[A-Z]{1,5}$', word):
                keywords.append(word)
        
        # Extract words from sentiment dictionaries
        for word in words:
            if word in self.positive_words or word in self.negative_words:
                keywords.append(word)
        
        return list(set(keywords))
    
    def _calculate_confidence(self, text: str, sentiment_score: float) -> float:
        """Calculate confidence in sentiment analysis"""
        words = text.split()
        if len(words) == 0:
            return 0.0
        
        # Base confidence on text length and sentiment strength
        length_factor = min(1.0, len(words) / 50.0)  # More words = higher confidence
        strength_factor = abs(sentiment_score)  # Stronger sentiment = higher confidence
        
        # Check for sentiment words
        sentiment_words = sum(1 for word in words if word in self.positive_words or word in self.negative_words)
        sentiment_factor = min(1.0, sentiment_words / len(words))
        
        confidence = (length_factor + strength_factor + sentiment_factor) / 3.0
        return min(1.0, confidence)

class RedditSentimentCollector:
    """Collect sentiment data from Reddit"""
    
    def __init__(self):
        self.subreddits = ['wallstreetbets', 'investing', 'stocks', 'StockMarket']
        self.sentiment_analyzer = SentimentAnalyzer()
    
    async def collect_sentiment(self, ticker: str, hours: int = 24) -> List[SentimentResult]:
        """Collect sentiment data for a specific ticker"""
        # Placeholder for Reddit API integration
        # In production, this would use PRAW or Reddit API
        logger.info(f"Collecting Reddit sentiment for {ticker}")
        
        # Mock data for demonstration
        mock_posts = [
            f"{ticker} to the moon! 🚀🚀🚀",
            f"I'm bullish on {ticker}, strong fundamentals",
            f"{ticker} is going to crash, terrible earnings",
            f"Not sure about {ticker}, mixed signals",
            f"{ticker} is undervalued, great buying opportunity"
        ]
        
        results = []
        for post in mock_posts:
            result = self.sentiment_analyzer.analyze_text(post, "reddit")
            results.append(result)
        
        return results

class TwitterSentimentCollector:
    """Collect sentiment data from Twitter/X"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
    
    async def collect_sentiment(self, ticker: str, hours: int = 24) -> List[SentimentResult]:
        """Collect sentiment data for a specific ticker"""
        # Placeholder for Twitter API integration
        logger.info(f"Collecting Twitter sentiment for {ticker}")
        
        # Mock data for demonstration
        mock_tweets = [
            f"$AAPL looking strong today! #stocks",
            f"Not feeling good about {ticker} earnings",
            f"{ticker} is a solid long-term play",
            f"Short {ticker} - technical breakdown",
            f"Bullish on {ticker} fundamentals"
        ]
        
        results = []
        for tweet in mock_tweets:
            result = self.sentiment_analyzer.analyze_text(tweet, "twitter")
            results.append(result)
        
        return results

class NewsSentimentCollector:
    """Collect sentiment data from news sources"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
    
    async def collect_sentiment(self, ticker: str, hours: int = 24) -> List[SentimentResult]:
        """Collect sentiment data for a specific ticker"""
        # Placeholder for news API integration
        logger.info(f"Collecting news sentiment for {ticker}")
        
        # Mock data for demonstration
        mock_news = [
            f"{ticker} reports strong quarterly earnings",
            f"Analyst downgrades {ticker} stock rating",
            f"{ticker} announces new product launch",
            f"Market volatility affects {ticker} performance",
            f"{ticker} expands into new markets"
        ]
        
        results = []
        for news in mock_news:
            result = self.sentiment_analyzer.analyze_text(news, "news")
            results.append(result)
        
        return results

class AISentimentService:
    """Main service for AI sentiment analysis"""
    
    def __init__(self):
        self.reddit_collector = RedditSentimentCollector()
        self.twitter_collector = TwitterSentimentCollector()
        self.news_collector = NewsSentimentCollector()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    async def get_comprehensive_sentiment(self, ticker: str) -> Dict:
        """Get comprehensive sentiment analysis for a ticker"""
        try:
            # Collect sentiment from all sources
            reddit_results = await self.reddit_collector.collect_sentiment(ticker)
            twitter_results = await self.twitter_collector.collect_sentiment(ticker)
            news_results = await self.news_collector.collect_sentiment(ticker)
            
            # Combine all results
            all_results = reddit_results + twitter_results + news_results
            
            # Aggregate sentiment
            aggregated = self.sentiment_analyzer.aggregate_sentiment(all_results)
            
            # Add metadata
            aggregated['ticker'] = ticker
            aggregated['timestamp'] = datetime.now().isoformat()
            aggregated['data_sources'] = ['reddit', 'twitter', 'news']
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Error getting comprehensive sentiment for {ticker}: {e}")
            return {
                'ticker': ticker,
                'overall_sentiment': 0.0,
                'confidence': 0.0,
                'volume': 0,
                'error': str(e)
            }
    
    async def get_sentiment_trend(self, ticker: str, days: int = 7) -> Dict:
        """Get sentiment trend over time"""
        # Placeholder for historical sentiment analysis
        logger.info(f"Getting sentiment trend for {ticker} over {days} days")
        
        # Mock trend data
        trend_data = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            sentiment = 0.1 + (i * 0.05)  # Mock trend
            trend_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'sentiment': sentiment,
                'volume': 100 + (i * 10)
            })
        
        return {
            'ticker': ticker,
            'trend': trend_data,
            'trend_direction': 'increasing' if days > 3 else 'stable'
        }

# Global instance
ai_sentiment_service = AISentimentService()
