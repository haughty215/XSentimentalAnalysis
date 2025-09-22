# XSentimentalAnalysis

This tool retrieves tweets using the **Twitter (X) API**, performs **sentiment analysis** using **TextBlob**, saves results into a **CSV file**, and optionally uploads them to **AWS S3** for storage.  

---

## Features
- Fetch recent tweets based on a keyword  
- Perform sentiment analysis (positive, negative, neutral)  
- Save results to a CSV file  
- Upload results to AWS S3 for persistence  
- Generate a summary with sentiment distribution  

---

## Requirements

- Python 3.8+  
- Twitter (X) Developer account with **Bearer Token**  
- AWS Account with S3 Bucket  

---

## Getting Your Twitter (X) Developer Bearer Token  

1. Go to the [Twitter/X Developer Portal](https://developer.x.com/en/portal/dashboard)  
2. Log in with your Twitter/X account  
3. Create a new **Project & App** (or use an existing one)  
4. Navigate to **Keys and Tokens → Authentication Tokens**  
5. Copy your **Bearer Token**  
6. Paste it into the script:  

   ```python
   BEARER_TOKEN = "YOUR_BEARER_TOKEN_HERE"
