import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import os

class QuotexScraper:
    def __init__(self, url):
        self.url = url
        self.candles = []
        self.load_candles()
        
    def load_candles(self):
        """আগের ডাটা লোড করো"""
        try:
            with open('data/candles.json', 'r') as f:
                self.candles = json.load(f)
        except:
            self.candles = []
    
    def save_candles(self):
        """ডাটা সেভ করো"""
        os.makedirs('data', exist_ok=True)
        with open('data/candles.json', 'w') as f:
            json.dump(self.candles, f, indent=2)
    
    def scrape_candle(self):
        """ক্যান্ডেল ডাটা স্ক্র্যাপ করো"""
        try:
            # সাইট থেকে ডাটা নাও
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/137.0.0.0'
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # ডাটা এক্সট্র্যাক্ট করো (সাইটের HTML স্ট্রাকচার অনুযায়ী)
            # নিচের সিলেক্টরগুলো সাইটের রিয়েল ক্লাস অনুযায়ী আপডেট করতে হবে
            price_element = soup.find('div', {'class': 'price'})
            if price_element:
                price = float(price_element.text.replace('$', '').replace(',', ''))
            else:
                return None
            
            # ভলিউম (যদি পাওয়া যায়)
            volume_element = soup.find('span', {'class': 'volume'})
            volume = float(volume_element.text) if volume_element else 0
            
            # টাইমস্ট্যাম্প
            timestamp = time.time()
            
            # ক্যান্ডেল ডাটা তৈরি
            candle = {
                'timestamp': timestamp,
                'datetime': datetime.now().isoformat(),
                'price': price,
                'volume': volume,
                'open': price,      # সিম্পল ভার্সন
                'high': price,
                'low': price,
                'close': price
            }
            
            self.candles.append(candle)
            self.save_candles()
            
            return candle
            
        except Exception as e:
            print(f"❌ স্ক্র্যাপিং এরর: {e}")
            return None
    
    def get_latest_candles(self, count=50):
        """শেষ N টা ক্যান্ডেল"""
        return self.candles[-count:] if self.candles else []
    
    def get_candle_data(self):
        """সব ক্যান্ডেল ডাটা"""
        return self.candles