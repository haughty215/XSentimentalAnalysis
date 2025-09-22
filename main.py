"""
Twitter Sentiment Analysis Tool
This script retrieves tweets using Twitter API, performs sentiment analysis,
saves results to CSV, and uploads to AWS S3.
"""

import tweepy
from textblob import TextBlob
import boto3
import csv
import pandas as pd
from datetime import datetime

# Configuration
BEARER_TOKEN = "YOUR_BEARER_TOKEN"  # Replace with your Twitter Bearer Token
AWS_BUCKET_NAME = "YOUR_BUCKET_NAME"  # Replace with your S3 bucket name
SEARCH_KEYWORD = "AWS"  # Change this to any topic you want to analyze
TWEET_COUNT = 10  # Number of tweets to fetch (max 100 for recent search)

def authenticate_twitter():
    """Authenticate with Twitter API using Bearer Token"""
    try:
        client = tweepy.Client(bearer_token=BEARER_TOKEN)
        print("✓ Successfully connected to Twitter API")
        return client
    except Exception as e:
        print(f"✗ Error connecting to Twitter API: {e}")
        return None

def fetch_tweets(client, keyword, count=10):
    """Fetch recent tweets based on keyword"""
    try:
        # Build query (English tweets only, no retweets)
        query = f"{keyword} lang:en -is:retweet"
        
        # Get tweets with additional fields
        tweets = client.search_recent_tweets(
            query=query, 
            max_results=count,
            tweet_fields=["created_at", "author_id", "lang", "public_metrics"]
        )
        
        if tweets.data:
            print(f"✓ Successfully fetched {len(tweets.data)} tweets")
            return tweets.data
        else:
            print("✗ No tweets found for the given query")
            return []
            
    except Exception as e:
        print(f"✗ Error fetching tweets: {e}")
        return []

def analyze_sentiment(tweet_text):
    """Analyze sentiment of a single tweet using TextBlob"""
    blob = TextBlob(tweet_text)
    polarity = blob.sentiment.polarity
    
    # Classify sentiment based on polarity
    if polarity > 0:
        sentiment = 'positive'
    elif polarity < 0:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    return sentiment, polarity

def process_tweets(tweets):
    """Process all tweets and perform sentiment analysis"""
    results = []
    
    for i, tweet in enumerate(tweets, 1):
        # Clean tweet text (remove newlines for CSV)
        clean_text = tweet.text.replace('\n', ' ').replace('\r', ' ')
        
        # Analyze sentiment
        sentiment, polarity = analyze_sentiment(clean_text)
        
        # Collect all data
        tweet_data = {
            'tweet_id': tweet.id,
            'text': clean_text,
            'created_at': tweet.created_at,
            'sentiment': sentiment,
            'polarity_score': round(polarity, 3),
            'retweet_count': tweet.public_metrics['retweet_count'] if tweet.public_metrics else 0,
            'like_count': tweet.public_metrics['like_count'] if tweet.public_metrics else 0
        }
        
        results.append(tweet_data)
        print(f"  Tweet {i}: {sentiment} (polarity: {polarity:.3f})")
    
    return results

def save_to_csv(results, filename='tweet_sentiments.csv'):
    """Save sentiment analysis results to CSV file"""
    try:
        # Define CSV headers
        headers = ['tweet_id', 'text', 'created_at', 'sentiment', 
                  'polarity_score', 'retweet_count', 'like_count']
        
        # Write to CSV
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"✓ Results saved to {filename}")
        return True
        
    except Exception as e:
        print(f"✗ Error saving to CSV: {e}")
        return False

def upload_to_s3(filename, bucket_name):
    """Upload CSV file to AWS S3"""
    try:
        s3 = boto3.client('s3')
        
        # Generate S3 key with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        s3_key = f"sentiment_analysis/{timestamp}_{filename}"
        
        # Upload file
        s3.upload_file(filename, bucket_name, s3_key)
        print(f"✓ File uploaded to S3: s3://{bucket_name}/{s3_key}")
        return True
        
    except Exception as e:
        print(f"✗ Error uploading to S3: {e}")
        print("  Make sure your AWS credentials are configured correctly")
        return False

def generate_summary(results):
    """Generate a summary of sentiment analysis results"""
    if not results:
        print("No results to summarize")
        return
    
    # Count sentiments
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    total_polarity = 0
    
    for result in results:
        sentiment_counts[result['sentiment']] += 1
        total_polarity += result['polarity_score']
    
    # Calculate percentages
    total_tweets = len(results)
    
    print("\n" + "="*50)
    print("SENTIMENT ANALYSIS SUMMARY")
    print("="*50)
    print(f"Total tweets analyzed: {total_tweets}")
    print(f"Search keyword: {SEARCH_KEYWORD}")
    print("\nSentiment Distribution:")
    
    for sentiment, count in sentiment_counts.items():
        percentage = (count / total_tweets) * 100
        bar = '█' * int(percentage / 5)  # Create visual bar
        print(f"  {sentiment.capitalize():8} : {count:2} tweets ({percentage:5.1f}%) {bar}")
    
    avg_polarity = total_polarity / total_tweets
    print(f"\nAverage Polarity Score: {avg_polarity:.3f}")
    
    if avg_polarity > 0.1:
        overall = "POSITIVE"
    elif avg_polarity < -0.1:
        overall = "NEGATIVE"
    else:
        overall = "NEUTRAL"
    
    print(f"Overall Sentiment: {overall}")
    print("="*50)

def main():
    """Main function to run the sentiment analysis pipeline"""
    print("\n🐦 TWITTER SENTIMENT ANALYSIS TOOL")
    print("="*50)
    
    # Step 1: Authenticate with Twitter
    print("\n1. Connecting to Twitter API...")
    client = authenticate_twitter()
    if not client:
        return
    
    # Step 2: Fetch tweets
    print(f"\n2. Fetching {TWEET_COUNT} tweets about '{SEARCH_KEYWORD}'...")
    tweets = fetch_tweets(client, SEARCH_KEYWORD, TWEET_COUNT)
    if not tweets:
        return
    
    # Step 3: Perform sentiment analysis
    print("\n3. Performing sentiment analysis...")
    results = process_tweets(tweets)
    
    # Step 4: Save to CSV
    print("\n4. Saving results to CSV...")
    csv_filename = 'tweet_sentiments.csv'
    if not save_to_csv(results, csv_filename):
        return
    
    # Step 5: Generate summary
    generate_summary(results)
    
    # Step 6: Upload to S3 (optional)
    print("\n5. Uploading to AWS S3...")
    if AWS_BUCKET_NAME != "YOUR_BUCKET_NAME":
        upload_to_s3(csv_filename, AWS_BUCKET_NAME)
    else:
        print("  ⚠ Skipped: Please configure your S3 bucket name")
    
    print("\n✅ Sentiment analysis complete!")
    print(f"   Results saved in: {csv_filename}")
    print("   You can now open this file in Excel to create Pivot Tables and charts")

if __name__ == "__main__":
    main()
