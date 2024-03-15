import asyncio
import aiohttp
import random
from bs4 import BeautifulSoup
import pandas as pd

import logging

douban_df = pd.read_csv('douban.csv')


async def fetch(session, num):  # function to fetch the page content
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
    logging.basicConfig(filename='txt/error.log', level=logging.ERROR)  # set logging configuration
    headers = {'User-Agent': random.choice(user_agents)}
    url = f'https://www.douban.com/doulist/111454660/?start={num}&sort=seq&playable=0&sub_type='  # construct the URL
    async with session.get(url, headers=headers, allow_redirects=False, ssl=False) as response:
        if response.status == 200:
            print(num, 'IN')
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')
            links = {link.get('href') for link in soup.find_all('a', href=True) if
                     link.get('href').startswith('https://movie.douban.com/subject/')}
            existing_urls_txt = set()
            existing_urls_csv = set()
            douban_df = pd.read_csv("douban.csv")
            existing_urls_csv.update(douban_df['URL'])

            existing_urls_failed = set()
            with open("txt/failed_at_2.txt", "r") as file_failed:
                for line_failed in file_failed:
                    existing_urls_failed.add(line_failed.strip())
            with open("txt/failed_at_1.txt", "r") as file_failed:
                for line_failed in file_failed:
                    existing_urls_failed.add(line_failed.strip())
            with open("txt/links.txt", "r") as file_failed:
                for line_failed in file_failed:
                    existing_urls_failed.add(line_failed.strip())

            new_urls_count = 0
            with open("txt/links.txt", "a") as file:
                for link in links:
                    if link not in existing_urls_txt and link not in existing_urls_failed and link not in existing_urls_csv:
                        new_urls_count += 1
                        file.write(f"{link}\n")
            return new_urls_count
        else:
            print(response.status)
            logging.error(f"Failed to fetch the webpage. Status code: {response.status}")
            return 0


async def create_tasks(session, num_list):
    tasks = []  # List to store tasks
    for n in num_list:
        tasks.append(fetch(session, n))  # Create task for each value in num
    return await asyncio.gather(*tasks)  # Execute tasks concurrently


async def main():
    async with aiohttp.ClientSession() as outer_session:
        num = [i for i in range(0, 3000, 25)]  # Generate num values from 0 to 75 with step 25
        new_urls_counts = await create_tasks(outer_session, num)
        total_new_urls = sum(new_urls_counts)
        print(f"Total new URLs appended: {total_new_urls}")


if __name__ == '__main__':
    asyncio.run(main())
