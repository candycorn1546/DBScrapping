import logging
import random

import requests

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/96.0.1054.62",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
]  # user agents

url = 'https://movie.douban.com/subject/35041292/'  # construct the URL
headers = {'User-Agent': random.choice(user_agents)}  # random user agent

content = None  # Initialize content outside the try block

try:
    response = requests.get(url, headers=headers, allow_redirects=False)  # get request
    response.raise_for_status()  # raise an exception for 4XX and 5XX status codes
    if response.status_code == 200:  # if the request is successful
        content = response.text  # extract the content
except requests.exceptions.HTTPError as e:
    print(f"HTTP error occurred: {e}")
except requests.exceptions.ConnectionError as e:
    print(f"Connection error occurred: {e}")
except requests.exceptions.Timeout as e:
    print(f"Timeout error occurred: {e}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

print(content)
