from googlesearch import search
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urlparse

import sys
import pandas as pd
import time
import traceback
import re

class WebScraper:
    AUTHOR_MAX_WORDS = 3
    SLEEP_INTERVAL = 2

    p_elementList= []

    def __call__(self, queryString, num_results, tbs='qdr:y'):
        urls = self.getgoogleUrls(queryString, num_results, tbs)

        context = {
            'url': [], 'title': [],
            'description': [], 'maintext': [], 'date_publish': []}
        context['url'] = urls

        dataSet = []
        driver = webdriver.Firefox()
        for url in urls:
            print(f'Scraping from => {url}')
            try:
                data = self.getContent(driver,url)
                print(data)
                if (data['title'] !='' or data['content'] != ''):
                    content = data['content']
                    # adding your owner key word here to filter content
                    if ((content.strip().startswith('Log In')) or \
                        (content.lower() in 'live sex')
                    ):
                        print("content Excluded!!")
                    else:
                        dataSet.append(data)
            except Exception as e:
                print(f"An unexpected error occurred with URL => {url}: {e}")

        driver.close() 
        df = pd.DataFrame(dataSet)     
        return df

    def getgoogleUrls(self, queryString, num_results, tbs):
        urls = []
        try:        
            for url in search(queryString, stop=num_results, tbs=tbs):
                urls.append(url)
        except Exception as e:
            print(f'You have already meet Google Search quota limit. Please try again after 2 hours. Thank!, {e}')
            sys.exit(0)
        
        return urls


    # Cuntion for Getting Date from Content
    def extractDate(self, string):
        try:
        # Define a regular expression for the date format DD/MM/YYYY and optional time
            date_time_pattern = re.compile(
                r"^\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b"  # Matches dates like DD/MM/YYYY at the start of the string
                r"|^\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b"  # Matches dates like December 20, 2023
                r"|^\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\d{4}\b"  # Matches dates like December 20, 2023
                r"|^\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}\b"  # Matches dates like Dec 20, 2023
                r"|^\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\d{4}\b"  # Matches dates like Dec 20, 2023
                r"(?:\s+\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?\s*(?:ET|WT)?\b)?$",  # Optionally matches times with optional AM/PM and time zone
                re.IGNORECASE  # Make the pattern case-insensitive
            )
            # Check if the entire string matches the pattern
            match = date_time_pattern.match(string)
            return bool(match)
        except Exception as e:
            print("Error accessing a text:", e)
        return False
    
    # Function to simluate with human behavior
    def humanAction(self, driver):
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 1000);")
        # Wait for another moment to simulate reading time or viewing content
        time.sleep(1)
        # Scroll back up to the top of the page
        driver.execute_script("window.scrollTo(0, -1000);")


    # Function for Getting Content from url
    def getContent(self,driver,url):
        try:
            parsed_url = urlparse(url)

            authors = '' 
            source_domain = parsed_url.netloc
            copyright = ''
            paragraph = ''
            title = ''
            date = ''
            driver.get(url)

            self.humanAction(driver)

            H1_elements = driver.find_elements(By.TAG_NAME, "h1")
            p_elements = driver.find_elements(By.TAG_NAME, "p")
                
            # Getting Title
            for h1 in H1_elements:
                try:
                    title = h1.text
                    break  # Assuming you only need the first h1's text
                except Exception as e:
                    print("Error accessing h1 text:", e)
                    continue

            # Getting Content
            for p in p_elements:
                try:
                    value = p.text
                    # Filter out authors
                    # adding your owner key word here to filter out the authors
                    if ((value.lower().strip().startswith('written by:')) or\
                        (value.lower().strip().startswith('article by:'))
                        ):
                        value.replace('Article by:', '')
                        authors = value.replace('Written by:', '') 
                        #authors = value.lower().replace('by ', '') 
                        #words = authors.split()
                        #if len(words) <= AUTHOR_MAX_WORDS and not authors:
                        #    authors = value
                        #else:
                        #    authors = ''
                        continue
                    # Filter out Copyright
                    if '©' in value or 'All Rights Reserved' in value:
                        copyright = value
                        continue

                    # call date function to extract the date
                    # adding your owner key word here to filter out the published date
                    if ((value.lower().strip().startswith('updated on')) or \
                        (value.lower().strip().startswith('published on')) or \
                        (value.lower().strip().startswith('published online')) 
                        ):
                        value = value.replace('Updated on', '').replace(':', '') 
                        value = value.replace('Published on', '').replace(':', '') 
                        value = value.replace('Published Online', '').replace(':', '') 
                        if (self.extractDate(value.strip())):
                            date = value
                            continue

                    paragraph += value + ' '
                except Exception as e:
                    print(f"Error accessing paragraph text from {url}:\n", e)
                    continue
        except TimeoutException:
            authors = ''
            print(f"Timeout waiting for elements on the page: {url}")
        except NoSuchElementException:
            authors = ''
            print(f"An element was not found on the page: {url}")
        except Exception as e:
            authors = ''
            print(f"An unexpected error occurred with URL => {url}: {e}")

        return {'authors': authors, 'date' : date, 'title' : title, 'content': paragraph, 'source_domain': source_domain, 'url' : url, 'copyright': copyright } 


    def save_to_csv_with_pandas(self, recordSet, filename):
        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(recordSet)
        # Save the DataFrame to a CSV file
        df.to_csv(filename, index=False, encoding='utf-8')
