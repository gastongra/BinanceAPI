import PySimpleGUI as sg
import ccxt
import requests
import json
from configparser import ConfigParser
import logging

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
logging.info('Reading config file ...')
cfg = ConfigParser()
cfg.read('config.ini')
apiKey = cfg.get('binance','apiKey')
apiSecret = cfg.get('binance','apiSecret')
logging.info('Initiating ...')

#Setting theme for pysimplegui:
sg.theme('LightGray1')
sg.SetOptions(element_padding=(0, 0), background_color='white')


#Getting BSWAP APYs from public endpoint not in the docs:
#https://www.binance.com/gateway-api/v1/public/swap-api/pool/pairList?type=STAKE
resp = requests.get('https://www.binance.com/gateway-api/v1/public/swap-api/pool/pairList?type=STAKE', verify=False, timeout=(5,40) )
if resp.status_code != 200:
    logging.info('Get response not 200 OK')
jsonResponse = resp.json()
poolsList = jsonResponse['data'] #poolsList is a list of dictionaries
for pool in poolsList:
    coinPair = pool.get('coinPair')
    apyOneWeek = float(pool.get('apyOneWeek'))*100
    logging.info("Pool: {:10} APY: {:6.2f}".format(coinPair, apyOneWeek))

#Setting window layout:
frame_layout = [
    [sg.Text('', size=(40, 1),pad=(41,0), font=("Helvetica", 12),background_color='#33FFFF')],
    [sg.Text('Binance Liquidity Pools', key='HEADER',justification='center', background_color='#33FFFF', size=(30, 1), font=("Helvetica", 16))],
    [sg.Text('', background_color='#33FFFF', font=("Helvetica", 7))]
]
layout = [
    [sg.Frame('', frame_layout,  background_color='#33FFFF',border_width=0)],
    [sg.Text('', font=("Helvetica", 7),background_color='white')]
]
layout += [
    [sg.Text(poolsList[i].get('coinPair'), size=(14, 1),pad=(40,1), font=("Helvetica", 12),background_color='white'),
    sg.Text("{:8.4f} %".format(float(poolsList[i].get('apyOneWeek'))*100 ), size=(14, 1), font=("Helvetica", 12),background_color='white')
    ] for i in range(len(poolsList))
]
layout += [[sg.Text('', font=("Helvetica", 7),background_color='white')]]

#Getting my BSWAP shares from binance API:
ccxtversion = 'CCXT version:' + ccxt.__version__
logging.info(ccxtversion) # requires CCXT version > 1.20.31
binance = ccxt.binance({
    'apiKey': apiKey,
    'secret': apiSecret,
    'enableRateLimit': True,
})
liq = binance.sapi_get_bswap_liquidity()
logging.info('My shares:')
logging.info(liq)
[logging.info('%s: %s', share.get('poolName'), share.get('share').get('asset')) for share in liq]

shares_layout = [
    [sg.Text('', background_color='#33FFFF')],
    [sg.Text('My Shares:', size=(14, 2),pad=(40,2), font=("Helvetica", 12),background_color='#33FFFF')]
]
for share in liq:
    if share.get('share').get('shareAmount') != '0':
        poolName = share.get('poolName')
        poolAsset1 = list(share.get('share').get('asset').items())[0]
        poolAsset2 = list(share.get('share').get('asset').items())[1]
        displayAsset = "{:4.2f} {} + {:4.2f} {}".format(float(poolAsset1[1]), poolAsset1[0], float(poolAsset2[1]), poolAsset2[0] )
        shares_layout += [
        [sg.Text(poolName, size=(10, 2),pad=(40,0), font=("Helvetica", 12),background_color='#33FFFF'),
        #sg.Text(displayAsset, size=(30, 2), font=("Helvetica", 12),background_color='#33FFFF')]
        sg.Text(displayAsset, size=(30,2), font=("Helvetica", 12),background_color='#33FFFF')]
        ]

#shares_layout += [[sg.Text(share.get('poolName'), size=(14, 2),pad=(80,2), font=("Helvetica", 12),background_color='white'), sg.Text(share.get('share').get('asset'), size=(40, 2), font=("Helvetica", 12),background_color='white')] for share in liq]

layout += [
[sg.Frame('', shares_layout, background_color='#33FFFF',border_width=0)]
]
bottom_layout = [
    [sg.Text('', size=(40, 2),pad=(41,0), font=("Helvetica", 12),background_color='#33FFFF')],
    [sg.Exit(font=('Helvetica',16), size=(8, 2),pad=(150,0))],
    [sg.Text('',background_color='#33FFFF')]
]
layout += [
[sg.Frame('', bottom_layout, background_color='#33FFFF',border_width=0)]
]
#window = sg.Window('Binance Liquidity Pools', default_element_size=(40, 1), no_titlebar=True, grab_anywhere=True, alpha_channel=.8, margins=(0, 0), border_depth=0).Layout(layout)
window = sg.Window('Binance Liquidity Pools', no_titlebar=True, grab_anywhere=True, alpha_channel=.8, margins=(0, 0), border_depth=0).Layout(layout)
while True:  # Event Loop
    event, values = window.read()
    #print('Event: {}'.format(event))
    logging.info('Event Receved: %s - Values: %s', event, str(values))
    if event is None or event == 'Exit' or event == 'Cancel':                # always check for closed window
        break
window.close()
