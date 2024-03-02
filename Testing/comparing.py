import logging
import os
import asyncio
import aiohttp
import random

import certifi
from bs4 import BeautifulSoup
import pandas as pd
from googletrans import Translator
import time
import ssl


async def fetch(session, movie_id):
    url = f'https://movie.douban.com/subject/{movie_id}/'
    async with session.get(url) as response:
        return await response.text()


async def get_movie_info(movie_id, session):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/96.0.1054.62",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
    ]  # user agents

    logging.basicConfig(filename='../txt/error.log', level=logging.ERROR)

    url = f'https://movie.douban.com/subject/{movie_id}/'
    headers = {'User-Agent': random.choice(user_agents)}
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")
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
            logging.error(f"{movie_id}. Status code: {response.status}")
            return None


async def main():
    start_time = time.time()
    movie_data = []
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        tasks = [get_movie_info(movie_id, session) for movie_id in range(1, 10)]
        movie_data = await asyncio.gather(*tasks)
        try:
            df = pd.DataFrame(movie_data)
            # Write to CSV file
            with open('../douban.csv', 'a', newline='', encoding='utf-8') as f:
                df.to_csv(f, index=False, header=f.tell()==0)
            # Write to Excel file
            file_exists = os.path.exists('douban.xlsx')
            with pd.ExcelWriter('douban.xlsx', mode='a', engine='openpyxl') as writer:
                if not file_exists:
                    df.to_excel(writer, index=False)
                else:
                    df.to_excel(writer, index=False, header=False)
            end_time = time.time()
            print(f"Scraping completed in {end_time - start_time} seconds.")
        except Exception as e:
            print("Error writing to files:", e)


if __name__ == "__main__":
    asyncio.run(main())
