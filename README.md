# Overview


- ### Purpose
  DB is China biggest movie website, with millions of reviews about different movies and show. BD holds valuable insights and trends in movie ratings, user reviews, and demographic information by scraping DB and comparing it with MDL, the world's most popular foreign drama website. By systematically comparing DB and MDL data, a comprehensive and global perspective on audience preferences, cultural influences, and viewing habits can be derived. This comparative analysis enriches our understanding of the entertainment landscape and sheds light on the cross-cultural dynamics shaping the reception of movies and shows.

- ### Method 1
  The first method of scraping the website will be writing a number from 1 - 37 millions and plugging the number into the domain 'movie.douban.com/subject/{int}/' For each number the website will throw a 404, 302, or 200 response.
  404 means that the website doesn't exist, and 302 indicates that the website also doesn't exist and is trying to redirect the user to the homepage. Finally, 200 means the website exists, and the user can scrape the information.
  The problem with this method is that DB is not a well-built website, which means that the backend proxy is unstable.
