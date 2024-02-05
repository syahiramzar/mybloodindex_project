import pandas as pd
import requests
import telegram.ext
from datetime import datetime

# key values are located in the /home/key_values.csv file, created by ETL script and will be refreshed at 10:00 AM everyday:
# last_date - iloc[0,0]
# last_value - iloc[0,1]
# pctdiff_yesterday - iloc[0,2]
# pctdiff_lastyear - iloc[0,3]

# with formatting:
# last_date = str(pd.read_csv("/home/ubuntu/key_values.csv").iloc[0, 0])
# last_value = str(pd.read_csv("/home/ubuntu/key_values.csv").iloc[0, 1])
# pctdiff_yesterday = f'{pd.read_csv("/home/ubuntu/key_values.csv").iloc[0, 2]:.2f}'
# pctdiff_lastyear = f'{pd.read_csv("/home/ubuntu/key_values.csv").iloc[0, 3]:.2f}'


def relative(input):
    if input > 0:
        return "higher"
    if input < 0:
        return "lower"

tg_token = '<<bot_token_id>>'

updater = telegram.ext.Updater(tg_token, use_context=True)
dispatch = updater.dispatcher

def start(update, context):
    update.message.reply_text(
        f"""
Hi, this bot presents daily Malaysian Blood Donation report.

Use these commands to get information on the following cases:

/new - New recorded blood donations nationwide in 2024.
/trend - Blood donations trend in Malaysia from 2006 - current.
/state - Breakdown of total donations by state from 2006 - current.
/returndonor - Percentage of returning donors by state from 2006 - current.
/agegroup - Heatmaps of returning donor by age groups from 2013 - current.
/about - About this project.

Data source: MoH Malaysia. Data updated as of {str(pd.read_csv("/home/ubuntu/key_values.csv").iloc[0, 0])}.
        """)

def home(update, context):
    update.message.reply_text(
        """
Follow these commands to get updates on the following cases:

/new - New recorded blood donations nationwide in 2024.
/trend - Blood donations trend in Malaysia from 2006 - current.
/state - Breakdown of total donations by state from 2006 - current.
/returndonor - Percentage of returning donors by state from 2006 - current.
/agegroup - Heatmaps of returning donor by age groups from 2013 - current.
/about - About this project.
        """)

def new(update, context):
    update.message.reply_text('Hold on, fetching data...')
    update.message.bot.send_photo(update.message.chat.id, open('/home/ubuntu/plots/chart1.png', 'rb'))
    update.message.bot.send_photo(update.message.chat.id, open('/home/ubuntu/plots/chart2.png', 'rb'))
    update.message.reply_text(
        f'For <b>{str(pd.read_csv("/home/ubuntu/key_values.csv").iloc[0, 0])}</b>, there are <b>{str(pd.read_csv("/home/ubuntu/key_values.csv").iloc[0, 1])}</b> new recorded donations nationwide, that is <b>{pd.read_csv("/home/ubuntu/key_values.csv").iloc[0, 2]:.2f}%</b> {relative(pd.read_csv("/home/ubuntu/key_values.csv").iloc[0, 2])} than the previous day.'
        f'\nCurrent cumulative total in 2024 is <b>{pd.read_csv("/home/ubuntu/key_values.csv").iloc[0, 3]:.2f}%</b> {relative(pd.read_csv("/home/ubuntu/key_values.csv").iloc[0, 3])} than last year (same date).'
        f'\n\n(C1) The weekly trend is rather consistent every week. Highest total number of daily donations are being recorded on weekends. While the two lowest being at Monday and Friday.'
        f'\n(C2) 2024 cumulative by states with W.P. KL being the highest contributor. In every states, 75-80% of the blood donations are from returning donors, which is a good sign.'
        f'\n\nType <b>/home</b> to get other information.',
    parse_mode=telegram.ParseMode.HTML)

def trend(update, context):
    update.message.reply_text('Hold on, fetching data...')
    update.message.bot.send_photo(update.message.chat.id, open('/home/ubuntu/plots/chart3.png', 'rb'))
    update.message.reply_text(
        f'C3 presents the trend of blood donation in Malaysia from 2006-01-01 to {str(pd.read_csv("/home/ubuntu/key_values.csv").iloc[0, 0])}.'
        f'\n\nC3 (top) depicts the monthly trend, with red dots indicating the months featuring the lowest total blood donations in their respective years. Primarily, these months align with the occurrences of '
        f'cultural/major events like Fasting Month, Eid Celebration, C19-MCO, etc.'
        f'\n\nIn C3 (bottom), the overall trend of blood donations in Malaysia is consistently on the rise year by year. Recorded decreases in 2020 and 2021 are likely attributed to the impact of the Covid-19 pandemic, '
        f'with a noticeable upward trend resuming from 2022 onwards.'
        f'\n\nType <b>/home</b> to get other information.',
    parse_mode=telegram.ParseMode.HTML)

def state(update, context):
    update.message.reply_text('Hold on, fetching data...')
    update.message.bot.send_photo(update.message.chat.id, open('/home/ubuntu/plots/chart4.png', 'rb'))
    update.message.reply_text(
        f'C4 present the breakdown of total donations by state from 2006-01-01 to {str(pd.read_csv("/home/ubuntu/key_values.csv").iloc[0, 0])}.'
        f'\n\nGenerally, most states maintain a consistent percentage proportion each year, with W.P KL being the largest contributor. '
        f'Pahang and Johor have shown an increase in donations since 2020, while states like Kedah have experienced declines in donations since the same year.'
        f'\n\nAn interactive version of C4 can be opened using the link: https://rb.gy/37wfn0 (best viewed using web desktop browser)'
        f'\n\nType <b>/home</b> to get other information.',
    parse_mode=telegram.ParseMode.HTML)

def returndonor(update, context):
    update.message.reply_text('Hold on, fetching data...')
    update.message.bot.send_photo(update.message.chat.id, open('/home/ubuntu/plots/chart5.png', 'rb'))
    update.message.reply_text(
        f'C5 presents a butterfly chart on cumulative breakdown of total donations by state from 2006-01-01 to {str(pd.read_csv("/home/ubuntu/key_values.csv").iloc[0, 0])}, with the right side showing the percentage of returning donor from each state.'
        f'\n\nWhile W.P KL being the biggest contributor, the percentage of returning donor is not the highest. States like Sarawak and Pulau Pinang recorded better results in retaining blood donors.'
        f'\n\nType <b>/home</b> to get other information.',
    parse_mode=telegram.ParseMode.HTML)

def agegroup(update, context):
    update.message.reply_text('Hold on, fetching data...')
    update.message.bot.send_photo(update.message.chat.id, open('/home/ubuntu/plots/chart6.png', 'rb'))
    update.message.bot.send_photo(update.message.chat.id, open('/home/ubuntu/plots/chart7.png', 'rb'))
    update.message.reply_text(
        f'C6 and C7 depict heatmaps of returning donors from 2013 to the present, categorized by age group (both current and at first visit) and their visiting frequency. Key insights derived from these charts include:'
        f'\n\n1. From C6, a notable percentage of donors initiate their contributions at a young age (17-20 years old), reflecting a positive trend that young individuals are actively engaged in blood donation awareness.'
        f'\n2. However, it is observed that a significant proportion of returning donors tends to discontinue after their second visit. This is evidenced by the concentrated movement of the darker region towards the right side as donors age, as depicted in the transition from C6 to C7.'
        f'\n3. In C7, the higher percentage of total visits (6 times and above) for age groups above 30 suggests that donors are inclined to return more frequently once they establish a regular pattern of donation.'
        f'\n\nThese insights contribute to a nuanced understanding of donor behavior, emphasizing the importance of targeted strategies to encourage sustained engagement, especially after the initial donations.'
        f'\n\nType <b>/home</b> to get other information.',
    parse_mode=telegram.ParseMode.HTML)

def about(update, context):
    update.message.reply_text(
        f'A personal project made by @syahiramzar - GitHub repo: https://github.com/syahiramzar/mybloodindex_project'
        f'\n\nData updated everyday, at 10:00AM (MYT).'
        f'\n\nData source: MoH Malaysia - https://github.com/MoH-Malaysia/data-darah-public'
        f'\n\nLast data updated as of {str(pd.read_csv("/home/ubuntu/key_values.csv").iloc[0, 0])}. Released on {datetime.now().strftime("%Y-%m-%d")}'
        f'\n\nType <b>/home</b> to get other information.',
    parse_mode=telegram.ParseMode.HTML)

dispatch.add_handler(telegram.ext.CommandHandler('start', start))
dispatch.add_handler(telegram.ext.CommandHandler('home', start))
dispatch.add_handler(telegram.ext.CommandHandler('new', new))
dispatch.add_handler(telegram.ext.CommandHandler('trend', trend))
dispatch.add_handler(telegram.ext.CommandHandler('state', state))
dispatch.add_handler(telegram.ext.CommandHandler('returndonor', returndonor))
dispatch.add_handler(telegram.ext.CommandHandler('agegroup', agegroup))
dispatch.add_handler(telegram.ext.CommandHandler('about', about))

updater.start_polling()

updater.idle()
