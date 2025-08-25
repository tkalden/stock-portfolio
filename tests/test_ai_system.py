#!/usr/bin/env python3
"""
Test script for AI Investment System

This script demonstrates the AI-powered sentiment analysis and recommendation capabilities.
"""

import asyncio
import requests
import json
from datetime import datetime

def test_ai_sentiment():
    """Test AI sentiment analysis"""
    print("🤖 Testing AI Sentiment Analysis")
    print("=" * 50)
    
    # Test sentiment for different stocks
    test_tickers = ['AAPL', 'TSLA', 'NVDA', 'MSFT']
    
    for ticker in test_tickers:
        print(f"\n📊 Analyzing sentiment for {ticker}...")
        try:
            response = requests.get(f"http://localhost:5001/api/ai/sentiment/{ticker}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Overall Sentiment: {data['overall_sentiment']:.3f}")
                print(f"   Confidence: {data['confidence']:.3f}")
                print(f"   Volume: {data['volume']} mentions")
                print(f"   Positive: {data['positive_count']}, Negative: {data['negative_count']}, Neutral: {data['neutral_count']}")
                
                # Show top keywords
                if data['top_keywords']:
                    print(f"   Top Keywords: {', '.join(data['top_keywords'][:5])}")
            else:
                print(f"   ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_ai_recommendations():
    """Test AI recommendations"""
    print("\n🎯 Testing AI Stock Recommendations")
    print("=" * 50)
    
    # Test different time horizons
    time_horizons = ['short', 'medium', 'long']
    
    for horizon in time_horizons:
        print(f"\n📈 {horizon.title()}-term recommendations:")
        try:
            response = requests.get(
                f"http://localhost:5001/api/ai/recommendations",
                params={'time_horizon': horizon, 'limit': 3}
            )
            if response.status_code == 200:
                data = response.json()
                for i, rec in enumerate(data['recommendations'], 1):
                    print(f"   {i}. {rec['ticker']} (Score: {rec['score']:.2f}, Confidence: {rec['confidence']:.2f})")
                    print(f"      Risk: {rec['risk_score']:.2f}, Predicted Return: {rec['predicted_return']:.1%}")
                    print(f"      Reasoning: {rec['reasoning']}")
            else:
                print(f"   ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_ai_performance():
    """Test AI model performance metrics"""
    print("\n📊 Testing AI Model Performance")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:5001/api/ai/performance")
        if response.status_code == 200:
            data = response.json()
            
            print("\n🤖 Model Performance Metrics:")
            for model_name, metrics in data['models'].items():
                print(f"\n   {model_name.upper()} Model:")
                for metric, value in metrics.items():
                    if metric != 'last_updated':
                        if isinstance(value, float):
                            print(f"     {metric}: {value:.3f}")
                        else:
                            print(f"     {metric}: {value}")
            
            print(f"\n📈 Overall Performance:")
            overall = data['overall_performance']
            for metric, value in overall.items():
                if metric != 'last_updated':
                    print(f"   {metric}: {value}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_sentiment_trend():
    """Test sentiment trend analysis"""
    print("\n📈 Testing Sentiment Trend Analysis")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:5001/api/ai/sentiment/AAPL/trend?days=7")
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Sentiment trend for {data['ticker']}:")
            print(f"   Trend Direction: {data['trend_direction']}")
            print(f"   Recent sentiment data:")
            
            for i, day_data in enumerate(data['trend'][:3], 1):
                print(f"   {i}. {day_data['date']}: Sentiment {day_data['sentiment']:.3f}, Volume {day_data['volume']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all AI system tests"""
    print("🚀 AI Investment System Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test all components
    test_ai_sentiment()
    test_ai_recommendations()
    test_ai_performance()
    test_sentiment_trend()
    
    print("\n✅ AI System Test Complete!")
    print("=" * 60)
    print("\n📚 Next Steps:")
    print("   1. Review the AI Investment System documentation")
    print("   2. Implement real data sources (Reddit, Twitter, News APIs)")
    print("   3. Train and deploy ML models for sentiment and prediction")
    print("   4. Add real-time data collection and processing")
    print("   5. Implement advanced ML algorithms (LSTM, BERT, etc.)")

if __name__ == "__main__":
    main()
