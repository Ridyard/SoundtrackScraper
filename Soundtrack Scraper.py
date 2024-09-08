

# py script to scrape the soundtrack from a given tv show
# Tracks are pulled from each episode, ordered by season
# A Ridyard // 09.2024

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def handleCookies():
    # Called when navigating to new browser instance or web page; clear the "cookies" pop-up
    # Wait for the cookies "AGREE" button to be present and clickable
    agree_button_xpath = '//button[span[text()="AGREE"]]'
    try:
        agree_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, agree_button_xpath)))
        agree_button.click()  # Click the "AGREE" button
    except:
        print("No cookies popup found.")


def findGivenElements(xpath_in):
    # accepts an xpath argument & returns a list of corresponding elements 
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, xpath_in)))
    return browser.find_elements(By.XPATH, xpath_in)


def showAllClick(parent_div_in):
    # each episode-page will show an abridged list of tracks; if there is a "show all" button, this function will click & expand the track listing
    try:
        showAllButt_xpath = '//p[@class="sc-jEACwC jpIqjk sc-hmdomO YqQqi"]'
        showAllButt = parent_div_in.find_element(By.XPATH, showAllButt_xpath)
        browser.execute_script("arguments[0].scrollIntoView(true);", showAllButt)
        browser.execute_script("arguments[0].click();", showAllButt)
        # print("'show all' button clicked")
    except Exception as e:
        print(f"No 'Show All' button found or issue with clicking: {str(e)}")



playlist = {}  # dict to hold each artist:song kv pair

# Headless Firefox configuration
options = Options()
options.headless = True  # Enable headless mode / True = don't show browser

# build the url from which we will scrape the soundtrack list
baseURL = 'https://www.tunefind.com/show/'
tvShow = input('Please enter a TV Show to search...').split()
tvShowClean = '-'.join(tvShow)  # replace whitespaces with '-' in url
builtUrl = baseURL + tvShowClean

# set browser object & open url
browser = webdriver.Firefox(options = options) # Use options when initializing the WebDriver
browser.get(builtUrl)
handleCookies()

# xpath of the show's seasons
season_element_xpath = '//h4[@class="sc-fUnMCh ImNYE sc-hmdomO ifqyAa"]'
season_elements = findGivenElements(season_element_xpath)

# choose the season to pull track listing from
if len(season_elements) > 1:
    currChoice = int(input(f'Scrape the soundtrack for which season?\n1-{str(len(season_elements))} \n'))
else:
    print(f'scraping soundtrack for {" ".join(tvShow)} season 1')
    currChoice = 1

# Click into the corresponding season link
browser.execute_script("arguments[0].click();", season_elements[currChoice-1])

# xpath of "episode" elements within each season
episode_element_xpath = '//h4[@class="sc-fUnMCh ImNYE sc-hmdomO ifqyAa"]'
episode_elements = findGivenElements(episode_element_xpath)

for j in range(len(episode_elements)):

    # Re-fetch the elements after each navigation to avoid stale element exception
    episode_elements = findGivenElements(episode_element_xpath)
    episode = episode_elements[j]
    
    print(f"Navigating to episode: {episode.text}")
    
    # Try to click the episode link
    try:
        browser.execute_script("arguments[0].click();", episode)  # click into each episode
        
        # pull song / artist elements from within a specific div element
        # avoids pulling additional / not required tracks that are duplicated around the page
        div_xpath = '//div[@class="sc-hBtRBD iUapDl"]'
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, div_xpath))) # Wait for the div to be present in the DOM
        
        # Locate the parent div element
        parent_div = browser.find_element(By.XPATH, div_xpath)

        # the "show all tracks" button is located within the parent_div, hence why we pass the parent_div as an argument
        # this function call is inconsistent when we don't use the parent_div, ie we just search for the "show all tracks" button xpath
        showAllClick(parent_div)  # Click "Show All" if present

        # once inside the episode page, scrape the tracks
        # Now find a specific song(p) & artist(a/small) elements within the parent div
        song_elements = parent_div.find_elements(By.XPATH, './/p[@class="sc-jEACwC jpIqjk sc-hmdomO YqQqi sc-knuQbY dhEDwX"]')
        artist_elements = parent_div.find_elements(By.XPATH, ".//div[contains(@class, 'ant-row') and contains(@class, 'sc-ERObt') and contains(@class, 'fRngQV')]") # this will pull the full artist list for each track, ie if there are multiple contributors

        # scrape song & artist into separate lists
        song_text = [song.text for song in song_elements]
        artist_text = [artist.text.replace('\n', '') for artist in artist_elements] # if there are multiple artists, this line will remove the /n separator 

        playlist.update(dict(zip(song_text, artist_text))) # combine the song with the corresponding artist

        # After scraping, navigate back to the season episode list
        browser.back()

    except Exception as e:
        print(f"Could not navigate to episode: {episode.text}, error: {str(e)}")

# Close the browser once scraping is complete
browser.quit()

for k,v in playlist.items():
    print(k + " : " + v)
print(f"playlist length: {len(playlist)}")
