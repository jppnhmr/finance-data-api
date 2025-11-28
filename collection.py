import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime

from database import get_country_id, get_metric_id, insert_data

def download_boe_historical_data():

    url = 'https://www.bankofengland.co.uk/boeapps/database/fromshowcolumns.asp?Travel=NIxAZxSUx&FromSeries=1&ToSeries=50&DAT=RNG&FNY=N&CSVF=TT&html.x=66&html.y=26&SeriesCodes=IUDBEDR&UsingCodes=Y&Filter=N&title=IUDBEDR&VPD=Y#'
    today = datetime.now()
    params = {
        'FD': '1',
        'FM': 'Jan',
        'FY': '2000',
        # get most up to date data
        'TD': today.strftime('%d'),
        'TM': today.strftime('%b'),
        'TY': today.strftime('%Y')
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    html = response.text
    soup = bs(html, 'html.parser')
    rows = soup.find('tbody').find_all('tr')

    data = []
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 2:
            date_str = cells[0].text.strip() # 20 Jan 25
            value_str = cells[1].text.strip()

            date = datetime.strptime(date_str, '%d %b %y').strftime('%Y-%m-%d')
            value = float(value_str)

            data.append({'date': date, 'value': value,})

    return data

def download_fred_historical_data():
    today = datetime.now().strftime('%Y-%m-%d')
    csv_download_url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23ebf3fb&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1320&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=DFF&scale=left&cosd=2000-01-01&coed={today}&line_color=%230073e6&link_values=false&line_style=solid&mark_type=none&mw=3&lw=3&ost=-99999&oet=99999&mma=0&fml=a&fq=Daily%2C%207-Day&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date={today}&revision_date={today}&nd=1954-07-01'

    response = requests.get(csv_download_url)
    data = []
    for line in response.text.splitlines():
        items = line.strip().split(',')
        data.append({'date': items[0], 'value': items[1],})
    
    return data

if __name__ == "__main__":
    print('----- Collecting Data -----', end='\r')
    
    print('----- Collecting Data: Done -----')

    print('----- Data into Database -----', end='\r')
    # UK - Policy Interest Rates
    data = download_boe_historical_data()
    country_id = get_country_id('UK')
    metric_id = get_metric_id('policy interest rate')
    insert_data(country_id=country_id, metric_id=metric_id, data=data)
    # US - Policy Interest Rates
    data = download_fred_historical_data()
    country_id = get_country_id('US')
    metric_id = get_metric_id('policy interest rate')
    insert_data(country_id=country_id, metric_id=metric_id, data=data)    
    
    print('----- Data into Database: Done -----')

