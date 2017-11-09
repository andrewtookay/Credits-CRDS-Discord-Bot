import discord
import requests
import asyncio
import json

with open('botParams.json') as json_input_file:
    json_bot_input = json.load(json_input_file)

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as:')
    print('Name: ', client.user.name)
    print('ID: ', client.user.id)
    print('-----------------------')

@client.event
async def on_message(message):
    sign = message.content[0]
    final_message = ''

    if message.content.startswith('?help'):
        final_message = 'These are the available commands:\n$<currency ticker>\n?help'
    
    elif message.content.startswith(json_bot_input['exitPassword']):
        await client.logout()

    elif sign == '$':
        coin_ticker = message.content[1:7]
        coin_ticker = coin_ticker.upper()

        goCMC = 0
        goCoinsM = 0

        cmc_api = 'https://api.coinmarketcap.com/v1/ticker/'
        json_cmc = requests.get(cmc_api).json()
        for ticker in json_cmc:
            if ticker['symbol'] == coin_ticker:
                goCMC = 1
                coinCMC = ticker

        if goCMC == 0:
            coinsm_api = 'https://coinsmarkets.com/apicoin.php'
            trade_ticker = 'BTC_' + coin_ticker
            json_coinsm = requests.get(coinsm_api).json()
            for ticker in json_coinsm:
                if ticker == trade_ticker:
                    goCoinsM = 1

        if goCMC == 0 and goCoinsM == 0:    
            final_message = 'Invalid ticker.'

        elif goCMC == 1:
            json_coin_name = coinCMC['name']
            json_price_btc = coinCMC['price_btc']
            json_price_usd = coinCMC['price_usd']
            json_24h_volume = coinCMC['24h_volume_usd']
            json_percent_change = coinCMC['percent_change_24h']

            final_message = 'Coin Name: ' + str(json_coin_name) + '\nTicker: ' + coin_ticker + '\n' + 'Price (BTC): ' + str(json_price_btc)  + '\n' + 'Price (USD): ' + str(json_price_usd)  + '\n' + 'Volume(24h): ' + str(json_24h_volume) + ' USD\n' + 'Change (24h): ' + str(json_percent_change) + '%'

        elif goCoinsM == 1:
            json_last_price = json_coinsm[trade_ticker]['last']
            json_24h_volume = json_coinsm[trade_ticker]['24htrade']

            final_message = 'Ticker: ' + coin_ticker + '\n' + 'Last price: ' + str(json_last_price)  + ' BTC\n' + 'Volume(24h): ' + str(json_24h_volume) + ' BTC'

        else:
            final_message = 'Something went wrong. Contact the team.'

    elif message.content[1] != ' ' and ((sign == '?' and message.content[1] != '?') or (sign == '$' and message.content[1] != '$')):
        final_message = 'Invalid command. Use ?help to see the available commands.'

    if final_message != '':
        await client.send_message(message.channel, '```' + final_message + '```')

client.run(json_bot_input['token'])
