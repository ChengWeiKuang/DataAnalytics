# Web Scraper - eCommerce Site
***

### Introduction  
This project is just a simple attempt to create a **web scraper** that can **extract key information from an eCommerce website**, where there is no way to download the data directly, and there is no publicly available API for it.  

Here, a [**test site**](https://webscraper.io/test-sites/e-commerce/ajax) is used to simulate an actual use case. This website comes with many useful information, such as the list of products available for sale, product models, prices and reviews. Although these information is publicly available on the website, there is no direct way to download all these information, and it is also not easily obtainable through other sources. In real-world case, getting these information will be very helpful for a company to make decisions on their business direction.  

Here is a quick summary of how the scraper extract the information from the website:  
- As the products are separated into multiple product categories and pages, the scraper first **goes into one of the categories**, and **extract the URL of every single products** under that category.
- Then, the scraper **opens all the product URLs**, one-by-one, and then **extracts all the key information** available in that product page.
- The process is then **repeated for all other product categories**.
- The collected data is then **saved into a CSV file** to be used by others. 


### Files 
For more details on how the whole process is performed, feel free to refer to the files in this folder for reference: 
1. ecommerce_scraper.py - The Python file used to scrape the test website. 
2. scraped_raw.csv - The data scraped from the website. 