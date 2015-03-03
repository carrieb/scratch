from selenium import webdriver
import os
import time
import sys
from string import Template

## TODO: Set up command line args
## Run all night - currently 21633 pages, not really more than like 20 pages added in a day

ARTOO_PATH = 'scripts/artoo.js'
EXTRACTION_SCRIPT_FILENAME = 'scripts/extract.js'
DEFAULT_LIMIT = 21650
DEFAULT_CHROMEDRIVER_PATH = "/Users/carolyn/projects/scratch/crawler/chromedriver"
DEFAULT_OUTPUT_DIR = "/Users/carolyn/projects/scratch/crawler/data"
PAGE_URL = "https://www.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10&p=%(page)d"
DEFAULT_OUTPUT_PATH = "fanfic_data_"

def main(argv):
    print argv
    start_time = time.time()
    driver = setup_chromedriver()

    limit = DEFAULT_LIMIT
    artoo_path = ARTOO_PATH
    extract_path = EXTRACTION_SCRIPT_FILENAME
    crawl(driver, PAGE_URL, DEFAULT_LIMIT, artoo_path, extract_path, DEFAULT_OUTPUT_PATH)

def crawl(driver, page_url, limit, artoo_path, extract_path, output_path):
    start_time = time.time()
    i = 4454
    while i < limit:
        page = page_url % {"page" : i}
        print "Fetching " + page
        
        d = driver.get(page)
        with open(artoo_path, 'r') as f:
            print "Executing artoo ..."
            driver.execute_script(f.read())
        
        print "Sleeping for 2 seconds..."
        time.sleep(2)
        
        with open(extract_path, 'r') as f:
            print "Executing our script ..."
            driver.execute_script(f.read() % {"counter" : i, "output_path" : output_path})
        
        print driver.page_source[:100] + " ... "
        print "Sleeping for 1 second..."
        time.sleep(1)

        i+=1
        print "Woke up!"
    
    elapsed_time = time.time() - start_time
    print "Total time taken:", elapsed_time
    driver.close()
    driver.quit()
    return

def setup_chromedriver(driver_fn=DEFAULT_CHROMEDRIVER_PATH, output_dir=DEFAULT_OUTPUT_DIR):
    chrome_options = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : output_dir}
    print chrome_options
    chrome_options.add_experimental_option("prefs", prefs)
    chromedriverpath = driver_fn
    os.environ["webdriver.chrome.driver"] = chromedriverpath
    driver = webdriver.Chrome(executable_path=chromedriverpath, chrome_options=chrome_options)
    return driver

if __name__ == "__main__":
    main(sys.argv[1:])
    
