import logging
import random

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    else:
        logger.error("Failed to fetch the webpage. Status code: %d", response.status_code)
except requests.exceptions.HTTPError as e:
    logger.error("HTTP error occurred: %s", e)
except requests.exceptions.ConnectionError as e:
    logger.error("Connection error occurred: %s", e)
except requests.exceptions.Timeout as e:
    logger.error("Timeout error occurred: %s", e)
except requests.exceptions.RequestException as e:
    logger.error("An error occurred: %s", e)
except Exception as e:
    logger.error("An error occurred: %s", e)

if content:
    print(content)
else:
    logger.warning("No content fetched.")
