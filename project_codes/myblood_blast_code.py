import requests
from datetime import datetime

def myblood_blast():
    #notify users new report is ready
    tg_token = '<your_tg_bot_token>'

    text = (f'Hi, the daily blood donation reports in Malaysia for {datetime.now().strftime("%Y-%m-%d")} is ready.'
            f'\n\nType /start to view.'
            f'\n\nPrepared by @syahiramzar')
    blast = requests.post(f'https://api.telegram.org/bot{tg_token}/sendMessage?chat_id=<chatid>text={text}')