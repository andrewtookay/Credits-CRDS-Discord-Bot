import discord
import requests
import asyncio
import json
import re

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
    final_message = ''
    link = ''

    if message.content.startswith('!help'):
        final_message = 'These are the available commands:\n$<currency ticker>\n!website\n!explorer\n!mnroi <no. of MN>\n!help'
    
    elif message.content.startswith(json_bot_input['exitPassword']):
        await client.logout()

    elif message.content.startswith('$'):
        coin_ticker = message.content[1:7]
        coin_ticker = coin_ticker.upper()

        goCMC = 0

        cmc_api = 'https://api.coinmarketcap.com/v1/ticker/'
        json_cmc = requests.get(cmc_api).json()
        for coin in json_cmc:
            if ticker['symbol'] == coin_ticker:
                goCMC = 1
                coinCMC = coin
                
        if coin_ticker.upper() == 'CRDS':
            try:
                crds_usd = requests.get('https://crds.co/calc/crds_usd.txt')
                crds_usd = float(crds_usd.text)

                crds_btc = requests.get('https://crds.co/calc/crds_btc.txt')
                crds_btc = float(crds_btc.text)

                supply = requests.get('https://crds.co/calc/crds_supply.txt')
                supply = supply.text

                volume = requests.get('https://crds.co/calc/crds_vol.txt')
                volume = float(volume.text)

                supply = re.sub(',', '', supply)
                supply = float(supply)
                
                marketcap = round(crds_usd * supply, 2)

                final_message = 'Coin Name: Credits' + '\nTicker: ' + coin_ticker + '\n' + 'Last price: ' + str('{0:.8f}'.format(round(crds_btc, 8)))  + ' BTC\n' + 'Volume(24h): ' + str(volume) + ' BTC\n' + 'Marketcap: ' + str(marketcap) + ' USD'

            except:
                final_message = 'Invalid command due to factors outside our control.'

        elif goCMC == 1:
            json_coin_name = coinCMC['name']
            json_price_btc = coinCMC['price_btc']
            json_price_usd = coinCMC['price_usd']
            json_24h_volume = coinCMC['24h_volume_usd']
            json_percent_change = coinCMC['percent_change_24h']

            final_message = 'Coin Name: ' + str(json_coin_name) + '\nTicker: ' + coin_ticker + '\n' + 'Price (BTC): ' + str(json_price_btc)  + '\n' + 'Price (USD): ' + str(json_price_usd)  + '\n' + 'Volume(24h): ' + str(json_24h_volume) + ' USD\n' + 'Change (24h): ' + str(json_percent_change) + '%'
            
        else:
            final_message = 'Something went wrong. Contact the team.'

    elif message.content.startswith('!mnroi'):
        no_mn = message.content[6:]

        try:
            no_mn = int(no_mn.strip())
            final_message = getMnRoi(no_mn)
            
        except ValueError:
            final_message = 'Invalid number of Masternodes.'

    elif message.content.startswith('!website') or message.content.startswith('!site'):
        final_message = 'Credits Website: '
        link = 'https://crds.co/'

    elif message.content.startswith('!explorer'):
        final_message = 'Credits Explorer: '
        link = 'https://explorer.crds.co/'

    elif len(message.content) > 1 and message.content[1] != ' ' and ((message.content[0] == '!' and message.content[1] != '!' and message.content[1] != '?') or (message.content[0] == '$' and message.content[1] != '$')):
        final_message = 'Invalid command. Use !help to see the available commands.'

    if final_message != '':
        await client.send_message(message.channel, '`' + final_message + '`' + link)

def getMnRoi(no_mn):
    final_message = ''

    try:
        json_cmc = requests.get('https://api.coinmarketcap.com/v1/ticker/').json()
        btc_usd = float(json_cmc[0]['price_usd'])

        crds_btc = requests.get('https://crds.co/calc/crds_btc.txt')
        crds_btc = float(crds_btc.text)

        mncount = requests.get('https://crds.co/calc/crds_mncount.txt')
        mncount = float(mncount.text)

        blockcount = requests.get('https://crds.co/calc/crds_blockcount.txt')
        blockcount = int(blockcount.text)

    except:
        return 'Command unavailable due to downtime of explorer or APIs.'

    crds_usd = crds_btc * btc_usd

    if blockcount <= 375000:
        reward = 1
    elif blockcount <= 500000: 
        reward = 2
    elif blockcount <= 625000:
        reward = 3
    elif blockcount <= 750000:
        reward = 4
    elif blockcount <= 875000:
        reward = 5
    elif blockcount <= 1000000:
        reward = 6
    elif blockcount <= 1125000:
        reward = 7
    elif blockcount <= 1375000:
        reward = 8
    elif blockcount <= 1500000:
        reward = 7
    elif blockcount <= 1625000:
        reward = 6
    elif blockcount <= 1750000:
        reward = 5
    elif blockcount <= 1875000:
        reward = 4
    elif blockcount <= 2000000:
        reward = 3
    else:
        reward = 2

    reward = float(reward)

    final_message = 'No. of Masternodes: ' + str(no_mn)
    final_message += '\nCollateral (CRDS): ' + str(5000 * no_mn)
    final_message += '\nCRDS Value (BTC): ' + str('{0:.8f}'.format(round(crds_btc, 8))) + ' BTC / ' + str(round(crds_usd, 4)) + ' USD'
    final_message += '\n'

    total_crds_col = float(no_mn * 5000)
    total_btc_col = round(total_crds_col * crds_btc, 8)
    total_usd_col = round(total_crds_col * crds_usd, 2)

    final_message += '\nTotal collateral cost for ' + str(no_mn) + ' MN: ' + str(total_btc_col) + ' BTC / ' + str(total_usd_col) + ' USD'
    final_message += '\n'

    mncount = float(mncount)
    crds_per_day_per_mn = reward * 675 / mncount
        
    final_message += '\nMasternode Block Reward: ' + str(int(reward)) + ' CRDS'
    final_message += '\nCRDS per day for ' + str(int(no_mn)) + ' MN: ' + str(round(no_mn * crds_per_day_per_mn, 4))
    final_message += '\nBTC per day for ' + str(int(no_mn)) + ' MN: ' + str('{0:.8f}'.format(round(no_mn * crds_per_day_per_mn * crds_btc, 8)))
    final_message += '\n'

    usd_per_day_per_mn = crds_per_day_per_mn * crds_usd

    final_message += '\nUSD per day for ' + str(int(no_mn)) + ' MN: ' + str(round(no_mn * usd_per_day_per_mn, 4))
    final_message += '\nUSD per month for ' + str(int(no_mn)) + ' MN: ' + str(round(no_mn * usd_per_day_per_mn * 30, 4))
    final_message += '\nUSD per annum for ' + str(int(no_mn)) + ' MN: ' + str(round(no_mn * usd_per_day_per_mn * 365, 4))
    final_message += '\n'

    roi = (usd_per_day_per_mn * 365) / (5000 * crds_usd) * 100

    final_message += '\nROI: ' + str(round(roi, 2)) + '%'

    return final_message

client.run(json_bot_input['token'])
