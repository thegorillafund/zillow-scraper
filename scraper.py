import pandas as pd
from functions import *
import json
from datetime import datetime


def scrape_sale(state, city, api_key):
    date_now = datetime.now()
    formatted_date = date_now.strftime("%Y%m%d")
    sold = False
    url = generate_zillow_url(state=state, city=city, page=1, sold_only=sold)
    try:
        soup = get_soup1(url)
        total_page = get_last_page(soup)

        if "denied" in soup.title.text:
            soup = get_soup_scrapeops(url, api_key)
            total_page = get_last_page(soup)

    except:
        soup = get_soup_scrapeops(url, api_key)
        total_page = get_last_page(soup)

    print(f"Scraping {total_page} page")
    final_data = []
    for page in range(1, total_page + 1):
        print("page:", page)
        url = generate_zillow_url(state=state, city=city, page=page, sold_only=sold)
        # try:
        #     soup = get_soup1(url)
        #     if "denied" in soup.title.text:
        #         soup = get_soup_scrapeops(url, api_key)
        # except:
        #     soup = get_soup_scrapeops(url, api_key)

        # links = soup.findAll(
        #     "li",
        #     {
        #         "class": "ListItem-c11n-8-105-0__sc-13rwu5a-0 StyledListCardWrapper-srp-8-105-0__sc-wtsrtn-0 gpgmwS cXzrsE"
        #     },
        # )
        # links = [link.find("a").get("href") for link in links if link.find("a") is not None]

        links = get_urls(url, api_key)
        total_link = len(links)
        print("total properties:", total_link)
        for i, link in enumerate(links, 1):
            print(f"{i}/{total_link}")
            try:
                data = scrape_single_url(link)
                if data["price"] is None and data["area"] is None:
                    data = scrape_single_url(link, scrapeops=True, api_key=api_key)
            except:
                print("scrape using scrapeops")
                data = scrape_single_url(link, scrapeops=True, api_key=api_key)
            data["url"] = link
            final_data.append(data)
            final_df = pd.DataFrame(final_data)
            final_df.to_csv(
                f"zillow_listings_{state}{city if city is not None else ''}_{formatted_date}{'_sold' if sold else ''}.csv",
                index=False,
            )


def scrape_sold(state, city, api_key):
    date_now = datetime.now()
    formatted_date = date_now.strftime("%Y%m%d")
    sold = True
    url = generate_zillow_url(state=state, city=city, page=1, sold_only=sold)
    try:
        soup = get_soup1(url)
        total_page = get_last_page(soup)

        if "denied" in soup.title.text:
            soup = get_soup_scrapeops(url, api_key)
            total_page = get_last_page(soup)

    except:
        soup = get_soup_scrapeops(url, api_key)
        total_page = get_last_page(soup)

    print(f"Scraping {total_page} page")
    final_data = []
    for page in range(1, total_page + 1):
        print("page:", page)
        url = generate_zillow_url(state=state, city=city, page=page, sold_only=sold)

        links = get_urls(url, api_key)
        total_link = len(links)
        print("total properties:", total_link)
        for i, link in enumerate(links, 1):
            print(f"{i}/{total_link}")
            try:
                data = scrape_single_url_sold(link)
                if data["price"] is None and data["area"] is None:
                    data = scrape_single_url_sold(link, scrapeops=True, api_key=api_key)
            except:
                print("scrape using scrapeops")
                data = scrape_single_url_sold(link, scrapeops=True, api_key=api_key)
            data["url"] = link
            final_data.append(data)
            final_df = pd.DataFrame(final_data)
            final_df.to_csv(
                f"zillow_listings_{state}{city if city is not None else ''}_{formatted_date}{'_sold' if sold else ''}.csv",
                index=False,
            )


if __name__ == "__main__":
    date_now = datetime.now()
    formatted_date = date_now.strftime("%Y%m%d")

    with open("config.json", "r") as file:
        config = json.load(file)

    city = config.get("city")
    state = config.get("state")
    sold = config.get("sold")
    api_key = config.get("api_key")

    scrape_sale(state, city, api_key)
