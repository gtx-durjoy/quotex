import asyncio
import schedule
import time
from datetime import datetime
from config import *
from scraper import QuotexScraper
from telegram_bot import TelegramBot

class TradingBot:
    def __init__(self):
        self.scraper = QuotexScraper(TARGET_URL)
        self.telegram = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        self.candle_history = []
        self.signal_count = 0
        self.last_signal = None
        
    def calculate_rsi(self, prices, period=14):
        """RSI ক্যালকুলেশন"""
        if len(prices) < period + 1:
            return None
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            diff = prices[i] - prices[i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))
        
        avg_gain = sum(gains[-period:]) / period if gains else 0
        avg_loss = sum(losses[-period:]) / period if losses else 0
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_sma(self, prices, period):
        """SMA ক্যালকুলেশন"""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period
    
    def generate_signal(self, candles):
        """সিগন্যাল জেনারেট করো"""
        if len(candles) < 20:
            return None
        
        closes = [c['close'] for c in candles]
        current_price = closes[-1]
        
        rsi = self.calculate_rsi(closes)
        sma20 = self.calculate_sma(closes, 20)
        sma50 = self.calculate_sma(closes, 50)
        
        signal = {
            'price': current_price,
            'rsi': rsi,
            'sma20': sma20,
            'sma50': sma50,
            'action': 'HOLD',
            'reason': 'না'
        }
        
        # সিগন্যাল লজিক
        if rsi and rsi < RSI_OVERSOLD:
            signal['action'] = 'BUY'
            signal['reason'] = f'RSI ওভারসল্ড ({rsi:.2f})'
        elif rsi and rsi > RSI_OVERBOUGHT:
            signal['action'] = 'SELL'
            signal['reason'] = f'RSI ওভারবট ({rsi:.2f})'
        elif sma20 and sma50 and sma20 > sma50:
            signal['action'] = 'BUY'
            signal['reason'] = 'গোল্ডেন ক্রস (SMA20 > SMA50)'
        elif sma20 and sma50 and sma20 < sma50:
            signal['action'] = 'SELL'
            signal['reason'] = 'ডেথ ক্রস (SMA20 < SMA50)'
        
        return signal
    
    def run_task(self):
        """প্রতি ইন্টারভালে যা হবে"""
        print(f"\n🔄 {datetime.now().strftime('%H:%M:%S')} - স্ক্র্যাপ করছি...")
        
        # ক্যান্ডেল স্ক্র্যাপ
        candle = self.scraper.scrape_candle()
        if candle:
            print(f"📊 নতুন ক্যান্ডেল: ${candle['price']:.2f}")
            self.telegram.send_candle(candle)
            
            # ৫ ক্যান্ডেল পর সিগন্যাল চেক
            if len(self.scraper.candles) % 5 == 0:
                signal = self.generate_signal(self.scraper.candles)
                if signal and signal['action'] != 'HOLD':
                    self.telegram.send_signal(signal)
                    self.signal_count += 1
                    self.last_signal = signal
                    print(f"🚨 সিগন্যাল: {signal['action']}")

    def run(self):
        """প্রোগ্রাম চালাও"""
        print("🚀 ট্রেডিং বট স্টার্ট করছি...")
        print(f"📡 টার্গেট: {TARGET_URL}")
        print(f"⏳ ইন্টারভাল: {SCRAPE_INTERVAL} সেকেন্ড")
        print("="*50)
        
        self.telegram.send_message("🚀 ট্রেডিং বট চালু হয়েছে!")
        
        # শিডিউল সেট করো
        schedule.every(SCRAPE_INTERVAL).seconds.do(self.run_task)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 বট বন্ধ করা হচ্ছে...")
            self.telegram.send_message("🔴 ট্রেডিং বট বন্ধ হয়েছে।")

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()