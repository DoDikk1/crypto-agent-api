from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

@app.route('/portfolio/<int:user_id>', methods=['GET'])
def get_portfolio(user_id):
    try:
        with open(r'C:\Users\User1\OneDrive\Desktop\mcrypto_info_bot\portfolio.json', 'r') as f:
            data = json.load(f)
            print("Содержимое файла:", data)
        
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
                pass  # оставляем старую, если не получилось
            
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
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)