# CanTekWebScraping

## Mandatory library

pip install selenium pandas google

## Setup search results

Modify main.py valiable NO_OF_SEARCH to adjust the Total No. of result.

## Running Program
Complie and run with main.py

## Using on WebScraper
**The Following must using selenium with FireFox web driver.
Be sure that Firefox has been installed on the local machine. 
The Script may only running on LOCAL MACHINE ONLY** 

### Import library
from WebScraper import WebScraper

### Initizate 
webScraping = WebScraper()

### Usage
webScraping([query string where user input], [Total No. of result])

It will return a dataframe for further usage

