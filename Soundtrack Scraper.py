

# py script to scrape the soundtrack from a given tv show
# Tracks are pulled from each episode, ordered by season
# A Ridyard // 09.2024

from selenium import webdriver
from selenium.webdriver.common.by import By
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


def showAllClick():
    # each episode-page will show an abridged list of tracks; if there is a "show all" button, this function will click & expand the track listing
    try:
        showAllButt_xpath = '//p[@class="sc-jEACwC jpIqjk sc-hmdomO YqQqi"]'
        showAllButt = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, showAllButt_xpath)))
        browser.execute_script("arguments[0].click();", showAllButt)
    except:
        print("No 'Show All' button found, moving on.")


playlist = {}  # dict to hold each artist:song kv pair

# build the url from which we will scrape the soundtrack list
baseURL = 'https://www.tunefind.com/show/'
tvShow = input('Please enter a TV Show to search...').split()
tvShowClean = '-'.join(tvShow)  # replace whitespaces with '-' in url
builtUrl = baseURL + tvShowClean

# set browser object & open url
browser = webdriver.Firefox()
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
        
        # once inside the episode page, scrape the tracks
        showAllClick()  # Click "Show All" if present
                
        # pull song / artist elements from within a specific div element
        # avoids pulling additional / not required tracks that are duplicated around the page
        div_xpath = '//div[@class="sc-hBtRBD iUapDl"]'
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, div_xpath))) # Wait for the div to be present in the DOM

        # Locate the parent div element
        parent_div = browser.find_element(By.XPATH, div_xpath)

        # Now find a specific song(p) & artist(a/small) elements within the parent div
        song_elements = parent_div.find_elements(By.XPATH, './/p[@class="sc-jEACwC jpIqjk sc-hmdomO YqQqi sc-knuQbY dhEDwX"]')
        artist_elements = parent_div.find_elements(By.XPATH, './/a/small')
        
        # scrape song & artist into separate lists
        song_text = [song.text for song in song_elements]
        artist_text = [artist.text for artist in artist_elements]

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
