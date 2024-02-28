import logging
import math
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
import logging

proxies = "http://54.193.86.81:3128"
def clear_files(file_paths):
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
        open(file_path, "a").close()


file_paths = ["success.txt", "failed_at_2.txt", "302.txt"]


def load_existing_data(csv_file):
    if os.path.exists(csv_file):
        existing_data = pd.read_csv(csv_file)
        return existing_data.drop_duplicates(subset=['URL'])  # Filter out duplicate entries based on URL
    else:
        return pd.DataFrame(columns=['Title', 'English Title', 'Year', 'Country', 'Rating', 'Number of Raters', 'URL'])


async def fetch(session, movie_id):  # function to fetch the page content
    url = f'https://movie.douban.com/subject/{movie_id}/'  # construct the URL
    async with session.get(url) as response:  # get request
        return await response.text()  # return the content


async def get_movie_info(movie_id, session):  # function to get the movie info
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

    url = f'https://movie.douban.com/subject/{movie_id}/'  # construct the URL
    headers = {'User-Agent': random.choice(user_agents)}  # random user agent
    retry_count = 0
    max_retries = 3
    while retry_count < max_retries:
        async with session.get(url, headers=headers, timeout=100, allow_redirects=False,proxy=proxies) as response:
            if response.status == 200:  # if the request is successful
                content = await response.text()  # extract the content
                soup = BeautifulSoup(content, "html.parser")  # parse the content
                language_span = soup.find('span', class_='pl', string='制片国家/地区:')  # find the language span
                episode_span = soup.find('span', class_='pl', string='集数:')  # find the episode span
                votes_span = soup.find('span', property='v:votes')  # find the votes span
                if votes_span is None or language_span is None or episode_span is None:
                    return None
                votes = int(votes_span.text.strip())
                year_span = soup.find('span', class_='year')  # find the year span
                year = int(year_span.text.strip().strip('()'))
                rating_tag = soup.find('strong', class_='ll rating_num', property='v:average')
                language = language_span.find_next_sibling(string=True).strip()
                if language == '美国 / 英国' or int(votes) < 60000 or year < 2000 or rating_tag is None:
                    with open("failed_at_2.txt", "a") as file:
                        file.write(f"{movie_id}\n")
                    return None
                title_span = soup.find('span', {'property': 'v:itemreviewed'})  # find the title span
                title = title_span.text.strip()
                rating = float(rating_tag.text.strip())  # extract the rating
                translator = Translator()  # create a translator object
                translated_title = translator.translate(title, src='zh-cn', dest='en').text
                translated_language = translator.translate(language_span.find_next_sibling(string=True).strip(),
                                                           src='zh-cn', dest='en').text
                with open("success.txt", "a") as file:
                    file.write(f"{translated_title},{movie_id}\n")
                return {
                    'Title': title,
                    'English Title': translated_title,
                    'Year': year,
                    'Country': translated_language,
                    'Rating': rating,
                    'Number of Raters': votes_span.text.strip(),
                    'URL': url
                }
            elif response.status == 404:
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
                    with open("302.txt", "a") as file:
                        file.write(f"{movie_id}\n")
                    return None
            else:
                logging.error(f"{movie_id}.Status code: {response.status}")
                return None


async def main(i, j):
    start_time = time.time()

    csv_file = 'douban.csv'
    existing_data = load_existing_data(csv_file)

    if existing_data is not None:
        movie_data = []
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            tasks = [get_movie_info(movie_id, session) for movie_id in range(i, j)]
            movie_data = await asyncio.gather(*tasks)
            try:
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
    else:
        print("Error loading existing data: CSV file not found.")


if __name__ == "__main__":
    start_movie_id = random.randint(25000000, 35000000)  # start movie id
    end_movie_id = start_movie_id + 2000000  # end movie id
    print(f"start id: {start_movie_id}")
    batch_size = 5000  # batch size
    total_movies = end_movie_id - start_movie_id + 1  # total movies
    num_batches = math.ceil(total_movies / batch_size)  # number of batches
    for batch_number in range(num_batches):
        clear_files(file_paths)
        i = start_movie_id + batch_number * batch_size
        j = min(start_movie_id + (batch_number + 1) * batch_size, end_movie_id + 1)
        asyncio.run(main(i, j))
        print(f"Batch {batch_number + 1} completed.")
        time.sleep(10)
