# Overview


- ## Purpose
  DB is China biggest movie website, with millions of reviews about different movies and show. BD holds valuable insights and trends in movie ratings, user reviews, and demographic information by scraping DB and comparing it with MDL, the world's most popular foreign drama website. By systematically comparing DB and MDL data, a comprehensive and global perspective on audience preferences, cultural influences, and viewing habits can be derived. This comparative analysis enriches our understanding of the entertainment landscape and sheds light on the cross-cultural dynamics shaping the reception of movies and shows.

  ## Method 1
-  The first method of scraping the website will be writing a number from 1 - 37 millions and plugging the number into the domain 'movie.douban.com/subject/{int}/' For each number the website will throw a 404, 302, or 200 response.
    * 404 means that the website doesn't exist.
    * 302 indicates that the website also doesn't exist and is trying to redirect the user to the homepage.
    * 200 means the website exists, and the user can scrape the information.
* The problem with this method is that DB is not a well-built website, which means that the backend / underlying proxy is unstable. I have ran multiple test where despite processing the same webpage the reponses are different.
* Method one could work however, it has a lot of potential of skipping over valid URLs and sending responses as 302 when it should be a 200 and there's no natural way of knowing because there are over 37 millions URLS to test.


  ## Method 2
- Method two involve picking a random drama/movie title and going through list made by other users based on the drama.
  - First, pick a drama; after picking the drama, there will be a list of other  dramas based on the current drama.
  - Parse all the href into a txt file.
  - From that txt file, go through the list, get the URLS of the dramas in the list, and check if the URLs already exist in the CSV file.
  - If the URLS doesn't exist in the csv file, parse it into a new txt file.
  - From that txt file, run the URLs through the scraper and fetch all the information.
  - If the information doesn't fit the requirement, such as more than 20k raters or newer than 2000, then send the URLs to another txt file called 'failed_at_2'
  - This will help differentiate URLs failing because of timeout errors vs URLs that have already been checked. 
