from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import datetime
import re

# initiating chrome webdriver
driver = webdriver.Chrome()
driver.get("https://www.sothebys.com/en/results?from=&to=&f2=00000164-609b-d1db-a5e6-e9ff01230000&f2=00000164-609b-d1db-a5e6-e9ff08ab0000&q=")

# initiating csv file using append
csv_file = open('sothebys7.csv', 'a+', encoding='utf-8', newline='')
writer = csv.writer(csv_file)

# tracking time scraping started
start_time = datetime.datetime.now()

# scroll page function
def scroll_page_end(scroll_count, scroll_pause):
    count = 0
    while (True and count < scroll_count):
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        count += 1
        # Wait to load page
        time.sleep(scroll_pause)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # Wait to load page
            time.sleep(scroll_pause)
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            # check if the page height has remained the same
            if new_height == last_height:
                # if so, you are done
                break
            # if not, move on to the next loop
            else:
                last_height = new_height
                continue

# driver gets page which contains infinite scroll, scroll_page_end(times_scrolled, time_pause)
scroll_page_end(10, 0.7)
print('='*50)
print('Reaching the end of auctions list')
print('='*50)

# assign list of auctions URL to auctions_list
auctions = driver.find_elements_by_xpath('//li[@class="SearchModule-results-item"]')
print(f'length of auctions list: {len(auctions)}')

# filter auctions list that contains "view results" ONLY, filter out "view works" which doesn't contain any content
auctions_list = []
for auction in auctions:
    view_text = auction.find_element_by_xpath('.//div[@class="Card-info-ctaActions"]').text
    if (view_text.lower() == 'view results'):
        auctions_list.append(auction.find_element_by_xpath('.//div[@class="Card-info-aside"]/a').get_attribute('href'))
auction_url_length = len(auctions_list)
# print for debugging (to remove)
print('='*50)
print(f'length of filtered auctions list: {auction_url_length}')
print('='*50)
print(f'links from the auctions list: {auctions_list[:10]}')
print('='*50)

# iterate through each auction url, open page with chrome webdriver, and assign all auction items for each auction
# create flag to detect if this is the first time of writing, if so, csv write will write column headers
times_written = 0
for auction_link in auctions_list:
    driver.get(auction_link)
    # below blocks uses try, except find xpath elements for the assigned names
    try:
        auction_name = driver.find_element_by_xpath('//div[@class="css-sg3wyi"]//h1').text
    except Exception as e:
        auction_name = ''
        print(type(e), e)
    try: 
        auction_time_loc = driver.find_element_by_xpath('//div[@class="css-2lny4p"]').text
    except Exception as e:
        auction_time_loc = ''
        print(type(e), e)
    # print for debugging (to remove)
    print('='*50)
    print(f'current auction name is {auction_name}')
    print('='*50)
    print(f'current auction time and location was {auction_time_loc}')
    print('='*50)

    # starts scrolling to the bottom of page, click on "load more" if present
    auction_items_list = []
    while True:
        try:
            time.sleep(.5)
            scroll_page_end(10, 0.5)
            load_more = driver.find_element_by_xpath('//div[@class="css-al9y2g"]')
            load_more.click()
        except Exception as e:
            print(type(e), e)
            break
        
    # find all auction items url and assign to auction_items_list
    auction_items_list = driver.find_elements_by_xpath('//div[@class="css-1up9enl"]')
    items_in_auction = len(auction_items_list)
    print('='*50)
    print(f'this auction has {items_in_auction} items')
    print('='*50)
    print(f'list of items on each auction url: {auction_items_list[:10]}')
    print('='*50)

    auction_items_url = []
    for item in auction_items_list:
        auction_items_url.append(item.find_element_by_xpath('.//a[@class="css-1um49bp row"]').get_attribute('href'))
    print('='*50)
    print(f'length of auction items url list: {len(auction_items_url)}')
    print('='*50)
    print(f'preview of auction items url list {auction_items_url[:10]}')
    print('='*50)

    # iterate through each auction item's url to access html tags
    for index, auction_item_url in enumerate(auction_items_url):
        print('='*50)
        print(f'currently scraping index number {index} of auction_item {auction_item_url}')
        driver.get(auction_item_url)
        # scroll down page, locate and expand on element "condition"
        while True:
            try:
                time.sleep(0.5)
                scroll_page_end(2, 0.7)
                driver.find_element_by_xpath('//h2[@aria-label="Open-Condition ReportSection"]').click()
            except Exception as e:
                print(type(e), e)
                break

        # storing scraped items to dictionary
        auction_dict = {}
        auction_dict['auction_item_url'] = auction_item_url
        auction_dict['auction_name'] = auction_name
        auction_dict['auction_time_loc'] = auction_time_loc
        auction_dict['items_in_auction'] = items_in_auction

        # below blocks uses try, except find xpath elements for the assigned names
        try:
            auction_dict['artwork'] = driver.find_element_by_xpath('//div[@class="css-19m7kbw"]/h1').text
        except Exception as e:
            print(type(e), e)
            auction_dict['artwork'] = ''
        try:
            auction_dict['estimate'] = driver.find_element_by_xpath('//*[@id="__next"]/div/div[3]/div/div/div/div[2]/div[4]/div/div[3]/div[2]/div/p').text
        except Exception as e:
            print(type(e), e)
            auction_dict['estimate'] = ''
        try:
            auction_dict['lot'] = driver.find_element_by_xpath('//div[@class="css-oj38t7"]/span[1]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['lot'] = ''
        try:
            auction_dict['price'] = driver.find_element_by_xpath('//div[@class="css-oj38t7"]/span[2]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['price'] = ''
        try:
            auction_dict['currency'] = driver.find_element_by_xpath('//div[@class="css-oj38t7"]/span[3]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['currency'] = ''
        try:
            auction_dict['image_link'] = driver.find_element_by_xpath('//img[@class="css-1hvlv6i"]').get_attribute('srcset').split()[0]
        except Exception as e:
            print(type(e), e)
            auction_dict['image_link'] = ''        
        try:
            auction_dict['bid'] = driver.find_element_by_xpath('//*[@id="__next"]/div/div[3]/div/div/div/div[2]/div[4]/div/div[3]/div[3]/span').text
        except Exception as e:
            print(type(e), e)
            auction_dict['bid'] = ''
        
        # extracting xpath elements which contain artist details and assigning them to a list called tags
        # save each section's text into a list for future use
        tags = driver.find_elements_by_xpath('//div[@class="css-8cpbw4"]')

        for i, tag in enumerate(tags):
            auction_dict[f'tag{i+1}'] = tag.text

        move_down_1 = 0
        try:
            if (re.search('\W*((?i)property(?i)|(?i)collection(?i))\W*',tags[0].find_element_by_xpath('.//div[@class="css-xs9w33"]/p[1]').text) != None):
                move_down_1 = 1
        except Exception as e:
            print(type(e), e)

        try:
            auction_dict['artist'] = tags[0].find_element_by_xpath(f'.//div[@class="css-xs9w33"]/p[{1 + move_down_1}]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['artist'] = ''

        try:
            auction_dict['year_born'] = tags[0].find_element_by_xpath(f'.//div[@class="css-xs9w33"]/p[{2 + move_down_1}]').text   
        except Exception as e:
            print(type(e), e)
            auction_dict['year_born'] = ''
        
        try:
            auction_dict['title']= tags[0].find_element_by_xpath(f'.//div[@class="css-xs9w33"]/p[{3 + move_down_1}]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['title'] = ''
        
        move_down_2 = 0
        try:
            if (re.search('\W*((?i)signed(?i)|(?i)signature(?i)|(?i)sign(?i)|(?i)glass(?i)|(?i)parts(?i)|(?i)plaster(?i)|(?i)mount(?i)|(?i)mounted(?i)|(?i)titled(?i)|(?i)dated)(?i)\W*',tags[0].find_element_by_xpath(f'.//div[@class="css-xs9w33"]/p[{5 + add_zero}]').text) != None):
                move_down_2 = 1
                auction_dict['signed']= tags[0].find_element_by_xpath(f'.//div[@class="css-xs9w33"]/p[{5 + move_down_1}]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['signed']= ''

        try:
            auction_dict['material'] = tags[0].find_element_by_xpath(f'.//div[@class="css-xs9w33"]/p[{5+move_down_1+move_down_2}]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['material'] = ''

        try:
            auction_dict['size'] = tags[0].find_element_by_xpath(f'.//div[@class="css-xs9w33"]/p[{6+move_down_1+move_down_2}]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['size'] = ''

        try:
            auction_dict['year_produced'] = tags[0].find_element_by_xpath(f'.//div[@class="css-xs9w33"]/p[{7+move_down_1+move_down_2}]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['year_produced'] = ''           

        try:
            auction_dict['condition'] = tags[1].find_element_by_xpath('.//div[@class="css-xs9w33"]/p[3]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['condition'] = ''

        try:
            auction_dict['provenance1'] = tags[-1].find_element_by_xpath('.//div[@class="css-xs9w33"]/p[1]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['provenance1'] = ''

        try:
            auction_dict['provenance2'] = tags[-1].find_element_by_xpath('.//div[@class="css-xs9w33"]/p[2]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['provenance2'] = ''

        try:
            auction_dict['provenance3'] = tags[-1].find_element_by_xpath('.//div[@class="css-xs9w33"]/p[3]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['provenance3'] = ''
        
        try:
            auction_dict['provenance4'] = tags[-1].find_element_by_xpath('.//div[@class="css-xs9w33"]/p[4]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['provenance4'] = ''

        try:
            auction_dict['provenance5'] = tags[-1].find_element_by_xpath('.//div[@class="css-xs9w33"]/p[5]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['provenance5'] = ''

        try:
            auction_dict['provenance6'] = tags[-1].find_element_by_xpath('.//div[@class="css-xs9w33"]/p[6]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['provenance6'] = ''

        try:
            auction_dict['provenance7'] = tags[-1].find_element_by_xpath('.//div[@class="css-xs9w33"]/p[7]').text
        except Exception as e:
            print(type(e), e)
            auction_dict['provenance7'] = ''

        print(f'here\'s the auction dictionary: {auction_dict}')
        if times_written == 0:
            writer.writerow(auction_dict.keys())
        times_written += 1

        writer.writerow(auction_dict.values())
        print(f'written {times_written} rows')
        
    print('='*50)
    print(f'done scraping index number {index} of auction_item {auction_item_url}')

end_time = datetime.datetime.now()
elapsed_time = end_time - start_time
print(f'Statistics:')
print('='*50)
print(f'Elapsed run time: {elapsed_time} seconds')

driver.close()