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

            data.append({'date': date, 'value': value})

    # Write data to CSV file
    with open('boe_rates.csv', 'w') as f:
        f.write('date,value\n')
        for row in data:
            f.write(f'{row['date']},{row['value']}\n')
        f.close()

    return data

if __name__ == "__main__":
    print('----- Collecting Data -----', end='\r')
    data = download_boe_historical_data()
    print('----- Collecting Data: Done -----')

    print('----- Data into Database -----', end='\r')
    country_id = get_country_id('UK')
    metric_id = get_metric_id('policy interest rate')
    insert_data(country_id=country_id, metric_id=metric_id, data=data)
    print('----- Data into Database: Done -----')

