import requests
import json
from datetime import datetime

class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
    
    def send_message(self, text, parse_mode='HTML'):
        """মেসেজ পাঠাও"""
        url = f"{self.base_url}/sendMessage"
        data = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        try:
            response = requests.post(url, data=data)
            return response.json()
        except Exception as e:
            print(f"❌ টেলিগ্রাম এরর: {e}")
            return None
    
    def send_candle(self, candle):
        """ক্যান্ডেল ডাটা পাঠাও"""
        message = f"""
📊 <b>নতুন ক্যান্ডেল ডাটা</b>
⏰ {datetime.fromtimestamp(candle['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
💰 প্রাইস: ${candle['price']:.2f}
📊 ভলিউম: {candle['volume']:.2f}
📈 ওপেন: ${candle['open']:.2f}
📉 ক্লোজ: ${candle['close']:.2f}
        """
        self.send_message(message)
    
    def send_signal(self, signal):
        """সিগন্যাল পাঠাও"""
        emoji = "🟢" if signal['action'] == 'BUY' else "🔴"
        message = f"""
{emoji} <b>{signal['action']} সিগন্যাল!</b>

💰 প্রাইস: ${signal['price']:.2f}
📊 RSI: {signal['rsi']:.2f}
📈 SMA20: {signal['sma20']:.2f}
📉 SMA50: {signal['sma50']:.2f}
📝 কারণ: {signal['reason']}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        self.send_message(message)