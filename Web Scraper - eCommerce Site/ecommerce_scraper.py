# Import libraries
import pandas as pd
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By  # To locate elements by XPATH or other criteria 
from time import sleep
from random import random  # Just to randomize manual sleep interval
from selenium.webdriver.support.wait import WebDriverWait  # Explicit wait
from selenium.webdriver.support import expected_conditions as EC  # For explicit wait
from selenium.common.exceptions import NoSuchElementException  # Handling for some products that doesn't have certain elements


# Driver setup scripts referenced from selenium-stealth API docs: https://pypi.org/project/selenium-stealth/
# Set a few options for the Chrome driver. 
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument("--incognito")
# options.add_argument("--headless")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Initiate the driver. 
driver = webdriver.Chrome(options=options)

# Added to reduce chance of getting detected, just in case, 
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

# Set implicit wait for the driver (short one will do, because it will wait for the full length in the product pages. )
driver.implicitly_wait(2)

# Initialize an empty Data Frame to store all product data, will write into it with loop. 
df_master = pd.DataFrame()
rownum = 0  # Just for writing into the df. 

# List of main pages that we want to scrape. 
dict_url = {"Laptop": "https://webscraper.io/test-sites/e-commerce/ajax/computers/laptops", 
            "Tablet": "https://webscraper.io/test-sites/e-commerce/ajax/computers/tablets", 
            "Phone": "https://webscraper.io/test-sites/e-commerce/ajax/phones/touch"}

# Loop through all the main pages 
for temp_cat, temp_url in dict_url.items():
    # Open the main page
    driver.get(temp_url)
    
    # Initialize a few loop variables first
    bool_next_enabled = True # Whether the Next button is enabled
    list_prod_url = [] # To store all product URLs

    # Loop through all pages for that category, and get all product URLs
    while bool_next_enabled:
        sleep(random()*3 + 1)  # Wait for extra 1-4 (random) seconds just in case
        
        # Get all the URLs from each items in the page. 
        list_elements = driver.find_elements(by = By.XPATH, value = "//a[@class='title']")
        for temp_element in list_elements:
            list_prod_url.append(temp_element.get_attribute("href"))
    
        # Check if the "Next" button is enabled, and click on it if yes. 
        button_next = driver.find_element(by = By.XPATH, value = "//button[@class = 'btn btn-default next']")
        bool_next_enabled = button_next.is_enabled()
        if bool_next_enabled:
            button_next.click()
            # Explicit wait for the next page to be loaded. Check based on the last element in the previous page. 
            element = WebDriverWait(driver, 10).until(EC.staleness_of(list_elements[-1]))

    # Loop through each product URLs
    for temp_prod_url in list_prod_url:
        # Open the product URL page
        driver.get(temp_prod_url)
        sleep(random()*3 + 1)  # Wait for extra 1-4 (random) seconds just in case

        # Category (from dict in the outer loop)
        str_category = temp_cat
        # Product Name
        str_prod_name = driver.find_element(by = By.XPATH, value = "//h4[@class = 'title card-title']").text
        # Product Description
        str_prod_desc = driver.find_element(by = By.XPATH, value = "//p[@class = 'description card-text']").text
        # Number of review
        str_num_review = driver.find_element(by = By.XPATH, value = "//p[@class = 'review-count']").text
        # Number of star
        int_num_star = len(driver.find_elements(by = By.XPATH, value = "//p[@class = 'review-count']/span[@class = 'ws-icon ws-icon-star']"))
        
        # Color 
        try: 
            dropdown_items = driver.find_elements(by = By.XPATH, value = "//div[@class = 'dropdown']/select/option[@class = 'dropdown-item']")
            list_color = []
            for temp_item in dropdown_items:
                temp_color = temp_item.get_attribute("value")
                if temp_color != "":  # Filter out "Select color" which has no value
                    list_color.append(temp_color)
            str_color = ", ".join(list_color)
            if len(list_color) == 0:  # Some products (especially laptops) may have no color choices
                str_color = "None"
        except NoSuchElementException as e:  # In fact find_elements won't throw exceptions, but just in case. 
            str_color = "None"
        
        # Product model & price (different for every model)
        try: 
            swatches_buttons = driver.find_elements(by = By.XPATH, value = "//div[@class = 'swatches']/button") 
            if len(swatches_buttons) == 0:  # Some products (especially phones) may have no model choices
                raise NoSuchElementException(msg = "Model selection not available for this product. ")
            # For each model, click the button and then get the price, then write into the df. 
            for temp_button in swatches_buttons:
                temp_button.click()
                sleep(random() + 1)  # For some reason explicit wait doesn't work here, so I manually wait for extra 1-2 (random) seconds
                price_label = driver.find_element(by = By.XPATH, value = "//h4[@class = 'price float-end pull-right']")
                str_model = temp_button.get_attribute("value")
                str_price = price_label.text
        
                # Write into df. 
                df_master.at[rownum, "prod_name"] = str_prod_name
                df_master.at[rownum, "category"] = str_category
                df_master.at[rownum, "prod_desc"] = str_prod_desc
                df_master.at[rownum, "num_review"] = str_num_review
                df_master.at[rownum, "num_star"] = int_num_star
                df_master.at[rownum, "color"] = str_color
                df_master.at[rownum, "model"] = str_model
                df_master.at[rownum, "price"] = str_price
                rownum += 1
        except NoSuchElementException as e:  # Some products (especially phones) may have no model choices
            str_model = "None"
            str_price = driver.find_element(by = By.XPATH, value = "//h4[@class = 'price float-end pull-right']").text
            # Only one row, so directly write into df
            df_master.at[rownum, "prod_name"] = str_prod_name
            df_master.at[rownum, "category"] = str_category
            df_master.at[rownum, "prod_desc"] = str_prod_desc
            df_master.at[rownum, "num_review"] = str_num_review
            df_master.at[rownum, "num_star"] = int_num_star
            df_master.at[rownum, "color"] = str_color
            df_master.at[rownum, "model"] = str_model
            df_master.at[rownum, "price"] = str_price
            rownum += 1

# Save the final data to a CSV file. 
df_master.to_csv("scraped_raw.csv", index = False)

# Close the driver 
driver.quit()
