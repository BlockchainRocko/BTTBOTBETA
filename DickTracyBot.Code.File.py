Python 3.11.3 (v3.11.3:f3909b8bc8, Apr  4 2023, 20:12:10) [Clang 13.0.0 (clang-1300.0.29.30)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
```
import requests
import json
import uniswap
import pancake_swap
import time
import re
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler


# Set up webhook for Telegram bot
def set_webhook():
    bot = telegram.Bot(token=6240559565:AAE6WzrKIHlZAHwVNoNy87Q6_s5fM1Im5Zk)
    bot.setWebhook(url=f"{https://api.telegram.org/bot<6240559565:AAE6WzrKIHlZAHwVNoNy87Q6_s5fM1Im5Zk>/}/{6240559565:AAE6WzrKIHlZAHwVNoNy87Q6_s5fM1Im5Zk}")
    

# Get latest pairs launched on Uniswap and PancakeSwap within the last hour
def get_latest_pairs():
    pairs = []
    url_uni = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'
    url_pancake = 'https://api.pancakeswap.com/api/v1/exchange_info'
    unix_time = int(time.time()) - 3600
    
    # Get data from Uniswap API
    query_uni = f"""{{
        pairs(first: 1000, orderBy: createdAtTimestamp, orderDirection: desc, where: {{ createdAtTimestamp_gt: {unix_time} }}) {{
            id
            token0 {{
                id
                symbol
                name
            }}
            token1 {{
                id
                symbol
                name
            }}
            createdAtTimestamp
            reserveUSD
            volumeUSD
        }}
    }}"""
    try:
        response_uni = requests.post(url_uni, json={'query': query_uni})
        for pair in response_uni.json()['data']['pairs']:
            pair_data = {}
            pair_data['id'] = pair['id']
            pair_data['exchange'] = 'Uniswap'
            pair_data['token0'] = pair['token0']['symbol']
            pair_data['token1'] = pair['token1']['symbol']
            pair_data['createdAtTimestamp'] = pair['createdAtTimestamp']
            pair_data['reserveUSD'] = float(pair['reserveUSD'])
            pair_data['volumeUSD'] = float(pair['volumeUSD'])
            pairs.append(pair_data)
    except:
        pass
    
    # Get data from PancakeSwap API
    try:
        response_pancake = requests.get(url_pancake)
        for pair in response_pancake.json()['data']:
            if pair['createdTime'] / 1000 > unix_time:
                pair_data = {}
                pair_data['id'] = pair['pair']
                pair_data['exchange'] = 'PancakeSwap'
                pair_data['token0'] = pair['baseAssetName']
                pair_data['token1'] = pair['quoteAssetName']
                pair_data['createdAtTimestamp'] = pair['createdTime'] / 1000
                pair_data['reserveUSD'] = float(pair['baseAssetVolume']) * float(pair['close'])
                pair_data['volumeUSD'] = float(pair['quoteAssetVolume'])
                pairs.append(pair_data)
    except:
        pass
    
    return pairs


# Analyze pairs and rate them in a list from 1 to 10 based on potential of being honeypots or rug pulls
def analyze_pairs(pairs):
    analyzed_pairs = []
    for pair in pairs:
        rating = 10  # default rating is 10
        if pair['exchange'] == 'PancakeSwap':
            rating -= 1  # PancakeSwap pairs are generally riskier than Uniswap pairs
        if pair['reserveUSD'] < 50000:
            rating -= 2  # pairs with low liquidity are riskier
        if pair['volumeUSD'] < 10000:
            rating -= 1  # pairs with low trading volume are riskier
        if re.search(r'\b(a+b+c+d+e+f+g+h+i+j+k+l+m+n+o+p+q+r+s+t+u+v+w+x+y+z)\1{2,}\b', pair['token0'] + pair['token1'], re.IGNORECASE):
            rating -= 2  # pairs with token names containing repeating letters are riskier
        if rating < 1:
            rating = 1  # rating must be between 1 and 10
        pair['rating'] = rating
        analyzed_pairs.append(pair)
    return sorted(analyzed_pairs, key=lambda x: x['rating'], reverse=True)


# Retrieve details and rating of a selected pair
def get_pair_details(pair_id):
    url_uni = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'
    url_pancake = 'https://api.pancakeswap.com/api/v1/ticker/24hr'

    if pair_id.startswith('0x'):
        # Get data from Uniswap API
        query_uni = f"""{{
            pair(id: "{pair_id}") {{
                id
                token0 {{
                    id
                    symbol
                }}
                token1 {{
                    id
                    symbol
                }}
                reserveUSD
                volumeUSD
                totalSupply
                createdAtTimestamp
            }}
        }}"""
        try:
            response_uni = requests.post(url_uni, json={'query': query_uni})
            pair_data = response_uni.json()['data']['pair']
            rating = analyze_pairs([pair_data])[0]['rating']
            return f"Pair ID: {pair_data['id']}\nToken 1: {pair_data['token0']['symbol']}\nToken 2: {pair_data['token1']['symbol']}\nReserve: ${round(pair_data['reserveUSD'])}\nVolume: ${round(pair_data['volumeUSD'])}\nTotal Supply: {round(float(pair_data['totalSupply']))}\nCreated At: {time.ctime(pair_data['createdAtTimestamp'])}\nHoneypot or Rug Pull Rating: {rating}/10"
        except:
            pass
    else:
        # Get data from PancakeSwap API
        try:
            response_pancake = requests.get(url_pancake)
            for pair in response_pancake.json()['data']:
                if pair['symbol'] == pair_id:
                    rating = analyze_pairs([pair])[0]['rating']
                    return f"Pair ID: {pair_id}\nReserve: ${round(float(pair['baseVolume']) * float(pair['closePrice']))}\nVolume: ${round(float(pair['quoteVolume']))}\nHoneypot or Rug Pull Rating: {rating}/10"
        except:
            pass
    return None


# Handle /honeypot command
... def honeypot(update, context):
...     pairs = get_latest_pairs()
...     analyzed_pairs = analyze_pairs(pairs)
...     message = ''
...     for pair in analyzed_pairs:
...         message += f"{pair['token0']}/{pair['token1']} ({pair['exchange']}) - {pair['rating']}/10\n"
...     message += '\nTo see details and individual rating for a pair, click on its name:'
...     keyboard = []
...     for pair in analyzed_pairs:
...         keyboard.append([InlineKeyboardButton(pair['token0'] + '/' + pair['token1'], callback_data=pair['id'])])
...     reply_markup = InlineKeyboardMarkup(keyboard)
...     update.message.reply_text(text=message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
... 
... 
... # Handle CallbackQuery
... def button(update, context):
...     query = update.callback_query
...     query.answer()
...     details = get_pair_details(query.data)
...     if details:
...         query.edit_message_text(text=details, parse_mode=ParseMode.HTML)
...     else:
...         query.edit_message_text(text='Failed to retrieve details')
... 
... 
... # Set up and run the bot
... if __name__ == '__main__':
...     # Set up Telegram bot
...     updater = Updater(token=6240559565:AAE6WzrKIHlZAHwVNoNy87Q6_s5fM1Im5Zk, use_context=True)
...     dispatcher = updater.dispatcher
... 
...     # Add command handlers
...     dispatcher.add_handler(CommandHandler('honeypot', honeypot))
...     dispatcher.add_handler(CallbackQueryHandler(button))
... 
    # Start webhook
    PORT = int(os.environ.get('PORT', 5000))
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=6240559565:AAE6WzrKIHlZAHwVNoNy87Q6_s5fM1Im5Zk)
    set_webhook()
    updater.idle()
