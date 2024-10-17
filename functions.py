import pandas as pd
import numpy as np
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import random
from fake_useragent import UserAgent
from seleniumwire import webdriver as wd
import urllib.parse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import os
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.firefox.options import Options
# from webdriver_manager.firefox import GeckoDriverManager

def generate_zillow_url(state, city=None, page=1, sold_only=False):
    # Base URL for either city-state or state-level search
    if city:
        base_url = "https://www.zillow.com/{city}-{state}/land/"
    else:
        base_url = "https://www.zillow.com/{state}/land/"

    # URL parameters (similar to your original version)
    query_params = {
        "pagination": {"currentPage": page},  # Dynamic pagination
        "isMapVisible": False,  # Set this to False to hide the map
        "mapBounds": {
            "west": -97.28451920751954,  # Example map bounds (adjust for different states/cities)
            "east": -96.27034379248047,
            "south": 32.514457732222695,
            "north": 33.120363697939986,
        },
        "usersSearchTerm": f"{city + ' ' if city else ''}{state}",  # Dynamic city and state input
        # Removed the 'regionSelection' to let Zillow automatically determine the region based on search term
        "filterState": {
            "sort": {"value": "globalrelevanceex"},
            "ah": {"value": True},  # Example filters for land
            "sf": {"value": False},
            "tow": {"value": False},
            "mf": {"value": False},
            "con": {"value": False},
            "apa": {"value": False},
            "manu": {"value": False},
            "apco": {"value": False},
            "rs": {
                "value": sold_only
            },  # Sold only filter (True for sold, False otherwise)
            "fsba": {"value": False},  # Other filters (can adjust as needed)
            "fsbo": {"value": False},
            "nc": {"value": False},
            "cmsn": {"value": False},
            "auc": {"value": False},
            "fore": {"value": False},
        },
        "isListVisible": True,  # Ensure list view is visible
        "mapZoom": 11,
    }

    # URL encoding the query parameters
    encoded_query_params = urllib.parse.quote(str(query_params))

    # Format city and state for the URL path
    if city:
        city_state_path = base_url.format(
            city=city.lower().replace(" ", "-"), state=state.lower()
        )
    else:
        city_state_path = base_url.format(state=state.lower())

    # Complete URL
    complete_url = f"{city_state_path}?searchQueryState={encoded_query_params}"

    return complete_url


def get_soup1(url):
    
    # options = uc.ChromeOptions()
    options = Options
    # options.add_argument('--headless')  # Run in headless mode (no GUI)
    options.add_argument('--no-sandbox')  # Bypass OS security model
    options.add_argument('--disable-dev-shm-usage')  # Disable shared memory
    options.add_argument('--disable-gpu')  # Disable GPU (since there's no display)
    options.add_argument('--remote-debugging-port=9222')  # Enable remote debugging (needed in headless)
    options.add_argument('--disable-software-rasterizer')  #
    driver = wd.Chrome(options=options, service=Service(ChromeDriverManager().install()))

    # options = Options()
    # options.add_argument('--no-sandbox')  # Bypass OS security model
    # options.add_argument('--disable-dev-shm-usage')  # Disable shared memory
    # options.add_argument('--disable-gpu')  # Disable GPU (for headless)
    
    # Uncomment the line below if you want to run in headless mode (for cloud environments)
    # options.add_argument('--headless')  

    # Automatically download and install the correct version of GeckoDriver
    # driver = wd.Firefox(service=Service(GeckoDriverManager().install()), options=options)

    try:
        driver.get(url)
        # Click the button without waiting for it to be clickable
        try:
            show_more_button = driver.find_element(
                By.CLASS_NAME,
                "StyledTextButton-c11n-8-100-1__sc-1nwmfqo-0.hcHpXi.expando-icon",
            )
            show_more_button.click()
        except Exception as e:
            pass

        # Get the updated page source after clicking the button
        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")
        return soup

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        driver.quit()


def interceptor(request):
    allowed_domains = [
        "zillow.com",
        "zillowstatic.com",
        "zg-api.com",
    ]  # Add any other necessary domains here
    # Extract the domain from the request URL
    request_url = request.url

    # Allow only if the request domain is in the allowed domains
    if not any(domain in request_url for domain in allowed_domains):
        request.abort()  # Abort the request if it's not in the allowed domains

    if request.path.endswith((".png", ".jpg", ".gif")):
        request.abort()

    # Stopping CSS from being requested
    if request.path.endswith(".css"):
        request.abort()

    # Stopping fonts from being requested
    if (
        "fonts." in request.path
    ):  # For example: fonts.googleapis.com or fonts.gstatic.com
        request.abort()


def get_soup_scrapeops(url, api_key):
    print("scraping using scrapeops")
    # SCRAPEOPS_API_KEY = "b03194c3-7b9a-43f8-8fbf-909ff75f3097"
    SCRAPEOPS_API_KEY = api_key

    ## Define ScrapeOps Proxy Port Endpoint
    proxy_options = {
        "proxy": {
            "http": f"http://scrapeops.headless_browser_mode=true:{SCRAPEOPS_API_KEY}@proxy.scrapeops.io:5353",
            "https": f"http://scrapeops.headless_browser_mode=true:{SCRAPEOPS_API_KEY}@proxy.scrapeops.io:5353",
            "no_proxy": "localhost:127.0.0.1",
        }
    }
    
    # option = uc.ChromeOptions()
    option = Options
    # option.add_argument('--headless')  # Run in headless mode (no GUI)
    option.add_argument('--no-sandbox')  # Bypass OS security model
    option.add_argument('--disable-dev-shm-usage')  # Disable shared memory
    option.add_argument('--disable-gpu')  # Disable GPU (since there's no display)
    option.add_argument('--remote-debugging-port=9222')  # Enable remote debugging (needed in headless)
    option.add_argument('--disable-software-rasterizer')  
    driver = wd.Chrome(seleniumwire_options=proxy_options, options=option, service=Service(ChromeDriverManager().install()))
    # driver = uc.Chrome(seleniumwire_options=proxy_options, options=option, use_subprocess=False, service=Service(os.path.join("/tmp", "chromedriver")))
    # driver = uc.Chrome(seleniumwire_options=proxy_options, use_subprocess=False, service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))
    driver.request_interceptor = interceptor
    try:
        driver.get(url)

        # Click the button without waiting for it to be clickable
        try:
            show_more_button = driver.find_element(
                By.CLASS_NAME,
                "StyledTextButton-c11n-8-100-1__sc-1nwmfqo-0.hcHpXi.expando-icon",
            )

            show_more_button.click()
        except Exception as e:
            pass

        # Get the updated page source after clicking the button
        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")

        return soup

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        driver.quit()





def get_price(soup):
    try:
        price = float(
            soup.find("span", {"data-testid": "price"})
            .text.replace("$", "")
            .replace(",", "")
        )
        return price
    except:
        # print('Fail to fetch price')
        return None


def get_status(soup):
    try:
        status = soup.find("span", {"data-testid": "home-status"}).text
        return status
    except:
        # print('Fail to fetch status')
        return "For Sale"


# def get_basic_data(soup):
#     try:
#         vals = soup.findAll('span', {'data-testid': 'bed-bath-sqft-text__value'})
#         vals = [val.text for val in vals]

#         units = soup.findAll('span', {'data-testid': 'bed-bath-sqft-text__description'})
#         units = [unit.text for unit in units]
#         data_dict = dict(zip(units, vals))

#         if 'sqft' in data_dict:
#             data_dict['sqft'] = float(data_dict['sqft'].replace(',', ''))

#         return data_dict
#     except:
#         print('Fail to fetch basic data')
#         return {}


def get_area(soup):
    try:
        area = float(
            soup.findAll("div", {"data-testid": "bed-bath-sqft-fact-container"})[-1]
            .find("span")
            .text.replace(",", "")
        )
        area_unit = (
            soup.findAll("div", {"data-testid": "bed-bath-sqft-fact-container"})[-1]
            .findAll("span")[-1]
            .text
        )

        if area_unit == "Square Feet":
            area /= 43560

        return np.round(area, 2)
    except:
        # print('Fail to fetch area')
        return None


def get_address(soup):
    try:
        address = soup.title.text.split("|")[0].strip()
        return address
    except:
        # print('Fail to fetch address')
        return None


def get_description(soup):
    try:
        description = soup.find(
            "div", {"class": "Text-c11n-8-100-2__sc-aiai24-0 sc-jsTgWu bSfDch drqkiS"}
        ).text
        return description
    except:
        # print('Fail to fetch description')
        return None


def get_listing_stats(soup):
    try:
        result = {}
        listing_stats = soup.find(
            "dl",
            {"class": "styles__StyledOverviewStats-fshdp-8-100-2__sc-1x11gd9-0 dMQsJk"},
        ).findChildren()
        listing_stats = [stat.text for stat in listing_stats]
        listing_stats = list(dict.fromkeys(listing_stats))
        listing_stats = [s for s in listing_stats if s != "|"]

        days_on_zillow_idx = listing_stats.index("on Zillow") - 1
        days_on_zillow = int(listing_stats[days_on_zillow_idx].split()[0])

        views_idx = listing_stats.index("views") - 1
        views = int(listing_stats[views_idx].replace(",", ""))

        saves_idx = (
            listing_stats.index("saves" if "saves" in listing_stats else "save") - 1
        )
        saves = int(listing_stats[saves_idx])

        result["days_on_zillow"] = days_on_zillow
        result["views"] = views
        result["saves"] = saves

        return result
    except:
        # print('Fail to fetch listing stats')
        return {}


def get_hoa(soup):
    try:
        categories = soup.findAll("div", {"data-testid": "category-group"})
        for category in categories:
            if category.find("h3").text == "Community & HOA":
                fact_categories = category.findAll(
                    "div", {"data-testid": "fact-category"}
                )
                for fact_category in fact_categories:
                    if fact_category.find("h6").text == "HOA":
                        hoa = fact_category.find("span").text.split(":")[-1].strip()
                        return hoa
        return None
    except:
        # print('Fail to fetch HOA')
        return None


def get_subdivision(soup):
    try:
        categories = soup.findAll("div", {"data-testid": "category-group"})
        for category in categories:
            if category.find("h3").text == "Community & HOA":
                fact_categories = category.findAll(
                    "div", {"data-testid": "fact-category"}
                )
                for fact_category in fact_categories:
                    if fact_category.find("h6").text == "Community":
                        spans = fact_category.findAll("span")
                        for span in spans:
                            if span.text.split(":")[0] == "Subdivision":
                                subdivision = span.text.split(":")[-1].strip()
                                return subdivision
        print("Subdivision data unavailable")
        return None
    except:
        # print('Fail to fetch division')
        return None


def get_sewer(soup):
    try:
        categories = soup.findAll("div", {"data-testid": "category-group"})
        for category in categories:
            if category.find("h3").text == "Utilities & green energy":
                fact_category = category.find("div", {"data-testid": "fact-category"})
                spans = fact_category.findAll("span")
                for span in spans:
                    if span.text.split(":")[0] == "Sewer":
                        sewer = span.text.split(":")[-1].strip()
                        return sewer
        # print('Sewer data unavailable')
        return None
    except:
        # print('Fail to fetch sewer')
        return None


def get_water(soup):
    try:
        categories = soup.findAll("div", {"data-testid": "category-group"})
        for category in categories:
            if category.find("h3").text == "Utilities & green energy":
                fact_category = category.find("div", {"data-testid": "fact-category"})
                spans = fact_category.findAll("span")
                for span in spans:
                    if span.text.split(":")[0] == "Water":
                        water = span.text.split(":")[-1].strip()
                        return water
        # print('Water data unavailable')
        return None
    except:
        print("Fail to fetch water")
        return None


def get_utilities(soup):
    try:
        categories = soup.findAll("div", {"data-testid": "category-group"})
        for category in categories:
            if category.find("h3").text == "Utilities & green energy":
                fact_category = category.find("div", {"data-testid": "fact-category"})
                spans = fact_category.findAll("span")
                for span in spans:
                    if span.text.split(":")[0] == "Utilities for property":
                        utilities = span.text.split(":")[-1].strip()
                        return utilities
        # print('Utilities data unavailable')
        return None
    except:
        print("Fail to fetch utilities")
        return None


def get_listing_date(soup):
    try:
        table = soup.find(
            "table",
            {
                "class": "StyledTableComponents__StyledTable-fshdp-8-100-2__sc-shu7eb-2 jaWGxh"
            },
        )
        rows = table.find_all("tr")
        rows_data = []
        for row in rows:
            try:
                cells = row.find_all("td")
                date = cells[0].text.strip()
                event = cells[1].text.strip()
                price = cells[2].text.strip()
                rows_data.append([date, event, price])
            except:
                continue
        listing_history = pd.DataFrame(rows_data, columns=["date", "event", "price"])
        listing_history["date"] = pd.to_datetime(
            listing_history["date"], format="%m/%d/%Y"
        )
        listing_date = listing_history["date"].min().strftime("%Y-%m-%d")
        return listing_date
    except:
        print("Listing date not available")
        return None


def get_last_page(soup):
    try:
        total_items = int(
            soup.find("span", {"class": "result-count"})
            .text.split()[0]
            .replace(",", "")
        )
        total_page = int(total_items / 40)
        return total_page
    except:
        print("Error to get last page")
        return 3


def get_listing_agent(soup):
    try:
        listing_agent = soup.find(
            "p", {"data-testid": "attribution-LISTING_AGENT"}
        ).text
        return listing_agent
    except:
        return None


def get_listing_agency(soup):
    try:
        listing_agency = soup.find("p", {"data-testid": "attribution-BROKER"}).text
        return listing_agency
    except:
        return None



def get_urls(url, api_key):
    print("Scraping using ScrapeOps with slow scrolling")
    SCRAPEOPS_API_KEY = api_key

    ## Define ScrapeOps Proxy Port Endpoint
    proxy_options = {
        "proxy": {
            "http": f"http://scrapeops.headless_browser_mode=true:{SCRAPEOPS_API_KEY}@proxy.scrapeops.io:5353",
            "https": f"http://scrapeops.headless_browser_mode=true:{SCRAPEOPS_API_KEY}@proxy.scrapeops.io:5353",
            "no_proxy": "localhost:127.0.0.1",
        }
    }

    # driver_path = "/usr/local/bin/chromedriver"
    # service = Service(executable_path=driver_path)
    # service = Service(ChromeDriverManager().install())

    # options = Options()
    # options.add_argument('--no-sandbox')  # Bypass OS security model
    # options.add_argument('--disable-dev-shm-usage')  # Disable shared memory
    # options.add_argument('--disable-gpu')  # Disable GPU (since there's no display)


    # # Use selenium-wire's WebDriver with Firefox and proxy options
    # driver = wd.Firefox(
    #     seleniumwire_options=proxy_options,
    #     options=options,
    #     service=Service(GeckoDriverManager().install())
    # )

    # Chrome options to ensure proper rendering
    # option = uc.ChromeOptions()
    option = Options
    # option.add_argument('--headless')  # Run in headless mode (no GUI)
    option.add_argument('--no-sandbox')  # Bypass OS security model
    option.add_argument('--disable-dev-shm-usage')  # Disable shared memory
    option.add_argument('--disable-gpu')  # Disable GPU (since there's no display)
    option.add_argument('--remote-debugging-port=9222')  # Enable remote debugging (needed in headless)
    option.add_argument('--disable-software-rasterizer')  #
    # option.add_argument("--window-size=1000,800")  # Set window size to 1200x800

    # # Initialize the WebDriver with proxy options
    driver = wd.Chrome(seleniumwire_options=proxy_options, options=option, service=Service(ChromeDriverManager().install()))
    # driver = uc.Chrome(seleniumwire_options=proxy_options, options=option, use_subprocess=False, service=Service(os.path.join("/tmp", "chromedriver")))
    # driver = uc.Chrome(seleniumwire_options=proxy_options, use_subprocess=False)
    driver.set_window_size(1000, 800)  # Set window size directly

    # Optional: Interceptor to modify requests (if needed)
    driver.request_interceptor = interceptor

    try:
        driver.get(url)

        # Wait for the initial page to load by waiting for a key element (e.g., pagination or footer)
        wait = WebDriverWait(driver, 30)
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".search-pagination"))
        )  # Adjust this selector based on your page

        # SCROLLING LOOP: Slow scrolling with pauses
        SCROLL_PAUSE_TIME = 10  # Pause time between scrolls in seconds
        SCROLL_PIXELS = 500  # Number of pixels to scroll each time

        last_height = driver.execute_script(
            "return document.body.scrollHeight"
        )  # Get initial scroll height

        while True:
            # Scroll down by a fixed number of pixels (e.g., 500 pixels)
            driver.execute_script(f"window.scrollBy(0, {SCROLL_PIXELS});")

            # Wait for new content to load
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height after scrolling
            new_height = driver.execute_script("return document.body.scrollHeight")

            # If the page height hasn't increased, we've reached the bottom
            if new_height == last_height:
                break

            last_height = new_height  # Update the last scroll height to the new height

        # After scrolling is complete and all content is loaded, get the rendered page source
        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")

        # Now that the full page is loaded, scrape all desired 'li' elements with the specific class
        li_elements = soup.find_all(
            "li",
            class_="ListItem-c11n-8-105-0__sc-13rwu5a-0 StyledListCardWrapper-srp-8-105-0__sc-wtsrtn-0 gpgmwS cXzrsE",
        )  # Replace with your target class
        links = [
            link.find("a").get("href")
            for link in li_elements
            if link.find("a") is not None
        ]
        links = [link for link in links if "homedetails" in link]

        print(f"Scraped {len(links)} urls")
        return links

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        driver.quit()


def get_county(soup):
    try:
        breadcrumbs = soup.find("ul", {"class": "footer-breadcrumbs"}).findChildren()
        for breadcrumb in breadcrumbs:
            if "county" in breadcrumb.text.lower():
                return breadcrumb.text
    except:
        return None


def get_details(soup):

    final_data = {}

    final_data["price"] = get_price(soup)
    final_data["status"] = get_status(soup)
    # final_data.update(get_basic_data(soup))
    final_data["area"] = get_area(soup)
    final_data["address"] = get_address(soup)
    final_data["description"] = get_description(soup)
    final_data.update(get_listing_stats(soup))
    final_data["hoa"] = get_hoa(soup)
    final_data["subdivison"] = get_subdivision(soup)
    final_data["sewer"] = get_sewer(soup)
    final_data["water"] = get_water(soup)
    final_data["utilities"] = get_utilities(soup)
    final_data["listing_date"] = get_listing_date(soup)
    final_data["listing_agent"] = get_listing_agent(soup)
    final_data["listing_agency"] = get_listing_agency(soup)
    final_data["county"] = get_county(soup)

    try:
        final_data["price_per_acre"] = np.round(
            final_data["price"] / final_data["area"]
        )
    except:
        final_data["price_per_acre"] = np.nan

    try:
        street, city, code = final_data["address"].split(",")
        final_data["street"] = street
        final_data["city"] = city
        final_data["code"] = code
    except:
        pass

    return final_data


def scrape_single_url(url, scrapeops=False, api_key=None):
    # soup = get_soup1(url)
    if not scrapeops:
        soup = get_soup1(url)
    else:
        soup = get_soup_scrapeops(url, api_key)
    data = get_details(soup)
    return data


# ===========================
# SOLD PROPERTIES FUNCTION


def get_area_sold(soup):
    try:
        area = soup.find("span", {"data-testid": "bed-bath-beyond"}).text.lower()
        if "square" in area:
            area = np.round(
                float(area.lower().split("square")[0].strip().replace(",", "")) / 43560,
                2,
            )
        else:
            area = float(area.split()[0])
        return area
    except:
        return None


def get_address_sold(soup):
    try:
        address = soup.find(
            "h1", {"class": "Text-c11n-8-99-3__sc-aiai24-0 dFxMdJ"}
        ).text.replace("\xa0", " ")
        return address
    except:
        return None


def get_sold_date(soup):
    try:
        sold_date = datetime.strptime(
            soup.find(
                "span",
                {
                    "class": "Text-c11n-8-99-3__sc-aiai24-0 hdp__sc-ym74hh-0 dFxMdJ lmzVzR"
                },
            )
            .text.split("on")[-1]
            .split("Zestimate")[0]
            .strip(),
            "%m/%d/%y",
        ).strftime("%Y-%m-%d")
        return sold_date
    except:
        return None


def get_price_sold(soup):
    try:
        price = (
            soup.find("span", {"class": "Text-c11n-8-99-3__sc-aiai24-0 dFhjAe"})
            .text.replace(",", "")
            .replace("$", "")
        )
        return price
    except:
        return None


def get_listing_agent_sold(soup):
    try:
        listing_agent = soup.find(
            "p", {"data-testid": "attribution-LISTING_AGENT"}
        ).text
        return listing_agent
    except:
        return None


def get_listing_agency_sold(soup):
    try:
        listing_agency = soup.find("p", {"data-testid": "attribution-BROKER"}).text
        return listing_agency
    except:
        return None


def get_listing_date_sold(soup):
    try:
        table = soup.find(
            "table",
            {"class": "StyledTableComponents__StyledTable-sc-f00yqe-2 kNXiqz"},
        )

        rows = table.find_all("tr")
        rows_data = []
        for row in rows:
            try:
                cells = row.find_all("td")
                date = cells[0].text.strip()
                event = cells[1].text.strip()
                price = cells[2].text.strip()
                rows_data.append([date, event, price])
            except:
                continue
        listing_history = pd.DataFrame(rows_data, columns=["date", "event", "price"])
        listing_history["date"] = pd.to_datetime(
            listing_history["date"], format="%m/%d/%Y"
        )

        listing_date = (
            listing_history.loc[listing_history.event == "Listed for sale"]["date"]
            .min()
            .strftime("%Y-%m-%d")
        )
        return listing_date
    except:
        return None


def get_info_sold(soup):
    try:
        items = soup.findAll(
            "li", {"class": "ListItem-c11n-8-99-3__sc-13rwu5a-0 bPtGxh"}
        )
        sewer, water, utilities = None, None, None
        for item in items:
            splitted = item.text.split(":")
            if "sewer" in splitted[0].lower():
                sewer = splitted[-1]
            if "water" in splitted[0].lower():
                water = splitted[-1]
            if "utilities" in splitted[0].lower():
                utilities = splitted[-1]
        return {"sewer": sewer, "water": water, "utilities": utilities}
    except:
        return None


def get_description_sold(soup):
    try:
        description = soup.find(
            "div", {"class": "Text-c11n-8-99-3__sc-aiai24-0 sc-cjibBx dFxMdJ feUIjT"}
        ).text
        return description
    except:
        return None


def get_county_sold(soup):
    try:
        breadcrumbs = soup.find("ul", {"class": "ds-breadcrumbs"}).findChildren()
        for breadcrumb in breadcrumbs:
            if "county" in breadcrumb.text.lower():
                return breadcrumb.text
    except:
        return None


def get_details_sold(soup):
    final_data = {}
    final_data["price"] = get_price_sold(soup)
    final_data["status"] = "Sold"
    final_data["area"] = get_area_sold(soup)
    final_data["address"] = get_address_sold(soup)
    final_data["description"] = get_description_sold(soup)
    final_data.update(get_info_sold(soup))
    final_data["listing_date"] = get_listing_date_sold(soup)
    final_data["listing_agent"] = get_listing_agent_sold(soup)
    final_data["county"] = get_county_sold(soup)
    final_data["listing_agency"] = get_listing_agency_sold(soup)
    final_data['sold_date'] = get_sold_date(soup)
    try:
        final_data["price_per_acre"] = np.round(
            final_data["price"] / final_data["area"]
        )
    except:
        final_data["price_per_acre"] = np.nan
    try:
        street, city, code = final_data["address"].split(",")
        final_data["street"] = street
        final_data["city"] = city
        final_data["code"] = code
    except:
        pass

    return final_data


def scrape_single_url_sold(url, scrapeops=False, api_key=None):
    # soup = get_soup1(url)
    if not scrapeops:
        soup = get_soup1(url)
    else:
        soup = get_soup_scrapeops(url, api_key)
    data = get_details_sold(soup)
    return data
