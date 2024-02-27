import logging
import os
import time

import requests
import random
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from googletrans import Translator


def load_existing_data(csv_file, excel_file):  # function for loading existing df
    if os.path.exists(csv_file):
        return pd.read_csv(csv_file)
    elif os.path.exists(excel_file):
        return pd.read_excel(excel_file)
    else:  # if df doesn't exist
        return pd.DataFrame(columns=['Title', 'English Title', 'Year', 'Country', 'Rating', 'Number of Raters', 'URL'])


def get_movie_info(movie_id):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/96.0.1054.62",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
    ]  # user agents
    logging.basicConfig(filename='error.log', level=logging.ERROR)
    url = f'https://movie.douban.com/subject/{movie_id}/'  # construct the URL
    headers = {'User-Agent': random.choice(user_agents)}  # random user agent
    response = requests.get(url, headers=headers)  # get request

    if response.status_code == 200:  # if the request is successful
        content = response.text  # extract the content
        soup = BeautifulSoup(content, "html.parser")  # parse the content
        language_span = soup.find('span', class_='pl', string='制片国家/地区:')
        episode_span = soup.find('span', class_='pl', string='集数:')
        votes_span = soup.find('span', property='v:votes')
        votes = int(votes_span.text.strip())
        language = language_span.find_next_sibling(string=True).strip()
        if language == '美国 / 英国' or episode_span is None or int(votes) < 10000:
            pass
        title_span = soup.find('span', {'property': 'v:itemreviewed'})
        title = title_span.text.strip()
        year_span = soup.find('span', class_='year')
        year = int(year_span.text.strip().strip('()'))
        rating_tag = soup.find('strong', class_='ll rating_num', property='v:average')
        rating = float(rating_tag.text.strip())
        translator = Translator()
        translated_title = translator.translate(title, src='zh-cn', dest='en').text
        translated_language = translator.translate(language_span.find_next_sibling(string=True).strip(),
                                                   src='zh-cn', dest='en').text
        return {
            'Title': title,
            'English Title': translated_title,
            'Year': year,
            'Country': translated_language,
            'Rating': rating,
            'Number of Raters': votes_span.text.strip(),
            'URL': url
        }
    else:
        logging.error(f"{movie_id}. Status code: {response.status_code}")
        return None


if __name__ == "__main__":
    start_time = time.time()
    movie_data = []
    with ThreadPoolExecutor() as executor:
        for data in executor.map(get_movie_info, range(35041292, 35041292+1)):
            if data:
                movie_data.append(data)
    try:
        df = pd.DataFrame(movie_data)
        df.to_csv('douban.csv', index=False)
        df.to_excel('douban.xlsx', index=False)
        end_time = time.time()
        print(f"Scraping completed in {end_time - start_time} seconds.")

    except Exception as e:
        print("Error writing to files:", e)
