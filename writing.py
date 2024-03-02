import asyncio
import random
import logging
import os
import ssl
import sys
import time

import certifi
import pandas as pd
import aiohttp
from bs4 import BeautifulSoup
from googletrans import Translator
import logging

logging.basicConfig(filename='error.log', level=logging.ERROR)  # Set logging configuration
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # Set the desired logging level
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger('').addHandler(console_handler)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def load_existing_data(csv_file):
    if os.path.exists(csv_file):
        existing_data = pd.read_csv(csv_file)
        return existing_data.drop_duplicates(subset=['URL'])  # Filter out duplicate entries based on URL
    else:
        return pd.DataFrame(columns=['Title', 'English Title', 'Year', 'Country', 'Rating', 'Number of Raters', 'URL'])

async def get_movie_info(url, session):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/96.0.1054.62",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    ]  # user agents
    await asyncio.sleep(random.uniform(30, 50))  # sleep for a random time
    logging.basicConfig(filename='error.log', level=logging.ERROR)  # set logging configuration
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        headers = {'User-Agent': random.choice(user_agents)}
        async with session.get(url, headers=headers, allow_redirects=False) as response:
            logging.info(f"Requesting URL: {url}, Status Code: {response.status}")
            if response.status == 200:
                content = await response.text()  # extract the content
                soup = BeautifulSoup(content, "html.parser")  # parse the content
                language_span = soup.find('span', class_='pl', string='制片国家/地区:')  # find the language span
                episode_span = soup.find('span', class_='pl', string='集数:')  # find the episode span
                votes_span = soup.find('span', property='v:votes')  # find the votes span
                if votes_span is None or language_span is None or episode_span is None:
                    print("failed at 1")
                    with open("failed_at_1.txt", "a") as file:
                        file.write(f"{url}\n")
                    return None
                year_span = soup.find('span', class_='year')  # find the year span
                if year_span is None:
                    return None
                votes = int(votes_span.text.strip())
                year = int(year_span.text.strip().strip('()'))
                rating_tag = soup.find('strong', class_='ll rating_num', property='v:average')
                language = language_span.find_next_sibling(string=True).strip()
                if language == '美国 / 英国' or int(
                        votes) < 20000 or year < 2000 or rating_tag is None or language == '美国' or language == '英国':
                    print("failed at 2")
                    with open("failed_at_2.txt", "a") as file:
                        file.write(f"{url}\n")
                    return None
                title_span = soup.find('span', {'property': 'v:itemreviewed'})  # find the title span
                title = title_span.text.strip()
                rating = float(rating_tag.text.strip())  # extract the rating
                translator = Translator()  # create a translator object
                translated_language = translator.translate(language_span.find_next_sibling(string=True).strip(),
                                                           src='zh-cn', dest='en').text
                translated_title = translator.translate(title, src='zh-cn', dest='en').text
                pl_element = soup.find('span', class_='pl', string='又名:')
                movie_id = url.split('/')[-2]
                if pl_element is not None:
                    next_sibling = pl_element.find_next_sibling(string=True)
                    if next_sibling is not None:
                        translated_title = next_sibling.strip().split('/')[-1].strip()
                print('success: ', translated_title)
                return {
                    'Title': title,
                    'English Title': translated_title,
                    'Year': year,
                    'Country': translated_language,
                    'Rating': rating,
                    'Number of Raters': votes_span.text.strip(),
                    'URL': url,
                    'ID': movie_id
                }
            elif response.status == 404:
                with open("404.txt", "a") as file:
                    file.write(f"{url}\n")
                return None
            elif response.status == 301:
                new_url = response.headers['Location']
                logging.info(f"Redirecting to: {new_url}")
                url = new_url
                retry_count += 1
                continue
            elif response.status == 302:
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(5)
                    continue
                else:
                    print("failed at 3")
                    with open("302.txt", "a") as file:
                        file.write(f"{url}\n")
                    return None
            else:
                logging.error(f"{url}.Status code: {response.status}")
                return None


def read_urls_from_file(file_path):
    urls = []
    with open(file_path, 'r') as file:
        for line in file:
            urls.append(line.strip())
    return urls


def load_existing_data(csv_file):
    if not os.path.exists(csv_file):
        return pd.DataFrame(
            columns=['Title', 'English Title', 'Year', 'Country', 'Rating', 'Number of Raters', 'URL', 'ID'])
    return pd.read_csv(csv_file)


def check_urls_against_csv(urls, csv_data):
    new_urls = []
    existing_urls = set(csv_data['URL'])
    for url in urls:
        if url not in existing_urls:
            new_urls.append(url)
    return new_urls


async def scrape_unique_urls(text_file, csv_file):
    unique_urls = set()

    # Read unique URLs from CSV file
    existing_urls = set()
    if csv_file:
        existing_data = pd.read_csv(csv_file)
        existing_urls.update(existing_data['URL'])

    # Read unique URLs from text file and add to the set if not in CSV
    with open(text_file, 'r') as file:
        for line in file:
            url = line.strip()
            if url not in existing_urls:
                unique_urls.add(url)

    ssl_context = ssl.create_default_context(cafile=certifi.where())
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        tasks = [get_movie_info(url, session) for url in unique_urls]
        movie_data = await asyncio.gather(*tasks)
        return [data for data in movie_data if data is not None]



async def main():
    start_time = time.time()
    text_file = 'combined.txt'
    csv_file = 'douban.csv'
    async with aiohttp.ClientSession() as session:
        movie_data = await scrape_unique_urls(text_file, csv_file)
        try:
            if os.path.exists(csv_file):
                existing_data = load_existing_data(csv_file)
            else:
                existing_data = pd.DataFrame(
                    columns=['Title', 'English Title', 'Year', 'Country', 'Rating', 'Number of Raters', 'URL', 'ID'])

            new_movie_data = [data for data in movie_data if
                              data is not None and data['URL'] not in existing_data['URL'].values]
            if new_movie_data:
                num_new_urls = len(new_movie_data)
                print(f"Number of new URLs added: {num_new_urls}")

                new_movie_df = pd.DataFrame(new_movie_data)

                # Filter out existing URLs from new data
                existing_urls = set(existing_data['URL'])
                new_movie_df = new_movie_df[~new_movie_df['URL'].isin(existing_urls)]

                df = pd.concat([existing_data, new_movie_df], ignore_index=True)

                if not os.path.exists(csv_file):
                    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                        df.to_csv(f, index=False)
                else:
                    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                        df.to_csv(f, index=False)

                end_time = time.time()
                print(f"Scraping completed in {end_time - start_time} seconds.")
            else:
                print("No new URLs to append.")
        except Exception as e:
            print("Error writing to files:", e)

if __name__ == '__main__':
    asyncio.run(main())
