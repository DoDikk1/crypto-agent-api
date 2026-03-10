from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
import os  # <--- ЭТО ДОБАВИТЬ

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "Crypto Agent API is running",
        "endpoints": ["/portfolio/<user_id>"]
    })

@app.route('/portfolio/<int:user_id>', methods=['GET'])
def get_portfolio(user_id):
    try:
        # ПРАВИЛЬНЫЙ ПУТЬ ДЛЯ RENDER
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'portfolio.json')
        
        print(f"Читаем файл: {file_path}")  # для отладки
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        user_coins = data.get(str(user_id), [])
        result = []
        total_usd = 0
        
        for coin in user_coins:
            symbol = coin['symbol']
            amount = coin['amount']
            avg_price = coin.get('avg_price', 0)
            current_price = coin.get('current_price', 0)
            
            # Получаем свежую цену с Binance
            try:
                url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
                current_price = float(requests.get(url).json()['price'])
            except:
                pass
            
            total_value = current_price * amount
            total_usd += total_value
            
            # Получаем изменение за 24ч
            try:
                change_url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
                change_data = requests.get(change_url).json()
                change = float(change_data['priceChangePercent'])
            except:
                change = 0
            
            result.append({
                'symbol': symbol,
                'price': current_price,
                'amount': amount,
                'total_value': total_value,
                'change': change
            })
        
        return jsonify({
            'success': True,
            'coins': result,
            'total_usd': total_usd
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'file_path': file_path if 'file_path' in locals() else 'unknown'
        }), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)