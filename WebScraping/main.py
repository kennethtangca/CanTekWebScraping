from WebScraper import WebScraper

import warnings

warnings.filterwarnings('ignore')

if __name__ == "__main__":
    webScraping = WebScraper()
    NO_OF_SEARCH = 5

    while True:
        queryString = input("Which query content do you want to search?(Quit to exit)")
        if queryString.lower() == ('quit'):
            break

        print('Start Scraping from the Google with FireFox...')
        dataframe = webScraping(queryString, NO_OF_SEARCH)
        print(dataframe)
        #webScraping.save_to_csv_with_pandas(dataframe, queryString.replace('?','')+ '.csv')