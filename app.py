import streamlit as st
from functions import *
from scraper import *
import pandas as pd
import json
from datetime import datetime
import chromedriver_autoinstaller
import os
import zipfile
import requests

# chromedriver_autoinstaller.install()
# Set ChromeDriver installation directory to /tmp (or any other accessible directory)

# Check if ChromeDriver is already installed in /tmp, otherwise install it
def download_chromedriver(version="120"):
    # Set the download URL based on the version you want
    download_url = f"https://chromedriver.storage.googleapis.com/{version}.0.6099.24/chromedriver_linux64.zip"

    # Set the path to store the ChromeDriver
    driver_zip_path = "/tmp/chromedriver.zip"
    driver_extracted_path = "/tmp/chromedriver"

    # Download ChromeDriver zip
    response = requests.get(download_url)
    with open(driver_zip_path, "wb") as file:
        file.write(response.content)

    # Extract ChromeDriver
    with zipfile.ZipFile(driver_zip_path, "r") as zip_ref:
        zip_ref.extractall("/tmp/")

    # Make the chromedriver executable
    os.chmod(driver_extracted_path, 0o755)

    return driver_extracted_path

# Set the path for chromedriver in the /tmp directory
chromedriver_path = os.path.join("/tmp", "chromedriver")

# Check if chromedriver already exists, if not, download it
if not os.path.exists(chromedriver_path):
    chromedriver_path = download_chromedriver(version="120")


def show_download_data(result_df, state, city, formatted_date, sold):
    @st.cache_data
    def convert_df(df):
        return df.to_csv().encode("utf-8")

    st.dataframe(result_df)
    csv = convert_df(result_df)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name=f"zillow_listings_{state}{city if city is not None else ''}_{formatted_date}{'_sold' if sold else ''}.csv",
        mime="text/csv",
    )


def scrape(state, city, api_key, num_page, sold):
    date_now = datetime.now()
    formatted_date = date_now.strftime("%Y%m%d")
    # sold = False
    url = generate_zillow_url(state=state, city=city, page=1, sold_only=sold)
    if num_page is None:
        with st.spinner("Getting number of pages"):
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
    else:
        total_page = num_page
    st.text(f"Total page: {total_page}")

    final_data = []
    for page in range(1, total_page + 1):
        print("page:", page)
        url = generate_zillow_url(state=state, city=city, page=page, sold_only=sold)
        with st.spinner(f"Getting total elements in page {page}"):
            links = get_urls(url, api_key)
            total_link = len(links)
        st.write(f"Total elements on page {page}: {total_link}")
        progress_text = f"Scraping page {page}"
        my_bar = st.progress(0, text=progress_text)
        percent_complete = 0

        print("total properties:", total_link)
        for i, link in enumerate(links, 1):
            percent_complete += 1 / total_link
            my_bar.progress(percent_complete, text=progress_text)
            print(f"{i}/{total_link}")
            try:
                data = (
                    scrape_single_url(link)
                    if not sold
                    else scrape_single_url_sold(link)
                )
                if data["price"] is None and data["area"] is None:
                    data = (
                        scrape_single_url(link, scrapeops=True, api_key=api_key)
                        if not sold
                        else scrape_single_url_sold(
                            link, scrapeops=True, api_key=api_key
                        )
                    )
            except:
                print("scrape using scrapeops")
                data = (
                    scrape_single_url(link, scrapeops=True, api_key=api_key)
                    if not sold
                    else scrape_single_url_sold(link, scrapeops=True, api_key=api_key)
                )
            data["url"] = link
            final_data.append(data)
            final_df = pd.DataFrame(final_data)
            final_df.to_csv(
                f"zillow_listings_{state}{city if city is not None else ''}_{formatted_date}{'_sold' if sold else ''}.csv",
                index=False,
            )
        my_bar.empty()
        st.write(f"Page {page} completed")
    result_df = pd.DataFrame(final_data)
    return result_df

    # @st.cache_data
    # def convert_df(df):
    #     # IMPORTANT: Cache the conversion to prevent computation on every rerun
    #     return df.to_csv().encode("utf-8")

    # st.dataframe(result_df)
    # csv = convert_df(result_df)

    # st.download_button(
    #     label="Download data as CSV",
    #     data=csv,
    #     file_name=f"zillow_listings_{state}{city if city is not None else ''}_{formatted_date}{'_sold' if sold else ''}.csv",
    #     mime="text/csv",
    # )


# def scrape_sale(state, city, api_key, num_page):
#     sold = True
#     date_now = datetime.now()
#     formatted_date = date_now.strftime("%Y%m%d")
#     url = generate_zillow_url(state=state, city=city, page=1, sold_only=sold)
#     if num_page is None:
#         with st.spinner("Getting number of pages"):
#             try:
#                 soup = get_soup1(url)
#                 total_page = get_last_page(soup)

#                 if "denied" in soup.title.text:
#                     soup = get_soup_scrapeops(url, api_key)
#                     total_page = get_last_page(soup)

#             except:
#                 soup = get_soup_scrapeops(url, api_key)
#                 total_page = get_last_page(soup)

#             print(f"Scraping {total_page} page")
#     else:
#         total_page = num_page
#     st.text(f"Total page: {total_page}")

#     final_data = []
#     for page in range(1, total_page + 1):
#         print("page:", page)
#         url = generate_zillow_url(state=state, city=city, page=page, sold_only=sold)
#         with st.spinner(f"Getting total elements in page {page}"):
#             links = get_urls(url, api_key)
#             total_link = len(links)
#         st.write(f"Total elements on page {page}: {total_link}")
#         progress_text = f"Scraping page {page}"
#         my_bar = st.progress(0, text=progress_text)
#         percent_complete = 0

#         print("total properties:", total_link)
#         for i, link in enumerate(links, 1):
#             percent_complete += 1 / total_link
#             my_bar.progress(percent_complete, text=progress_text)
#             print(f"{i}/{total_link}")
#             try:
#                 data = scrape_single_url(link)
#                 if data["price"] is None and data["area"] is None:
#                     data = scrape_single_url(link, scrapeops=True, api_key=api_key)
#             except:
#                 print("scrape using scrapeops")
#                 data = scrape_single_url(link, scrapeops=True, api_key=api_key)
#             data["url"] = link
#             final_data.append(data)
#             final_df = pd.DataFrame(final_data)
#             final_df.to_csv(
#                 f"zillow_listings_{state}{city if city is not None else ''}_{formatted_date}{'_sold' if sold else ''}.csv",
#                 index=False,
#             )
#         my_bar.empty()
#         st.write(f"Page {page} completed")
#     result_df = pd.DataFrame(final_data)

#     @st.cache_data
#     def convert_df(df):
#         # IMPORTANT: Cache the conversion to prevent computation on every rerun
#         return df.to_csv().encode("utf-8")

#     st.dataframe(result_df)
#     csv = convert_df(result_df)

#     st.download_button(
#         label="Download data as CSV",
#         data=csv,
#         file_name=f"zillow_listings_{state}{city if city is not None else ''}_{formatted_date}{'_sold' if sold else ''}.csv",
#         mime="text/csv",
#     )


with open("config.json", "r") as file:
    config = json.load(file)

api_key = config.get("api_key")

st.title("Zillow Scraper")
land_status = st.selectbox("Choose land status", ["For Sale", "Sold", "All"])

col1, col2 = st.columns(2)
with col1:
    state = st.text_input("State Code", placeholder="example: TX")
with col2:
    city = st.text_input("City Name", placeholder="optional")

num_page = None
page_prefer = st.radio("Choose number of page to scrape", ["All", "Custom"])
if page_prefer == "Custom":
    col1, col2, col3 = st.columns(3)
    with col1:
        num_page = st.number_input("Number of page to scrape", min_value=1, step=1)


btn = st.button("Start Scraping")
date_now = datetime.now()
formatted_date = date_now.strftime("%Y%m%d")
if btn:
    if state.strip() == "":
        st.warning("Please input state code")
    elif land_status == []:
        st.warning("Please input land status")
    else:
        st.write("Scraping data...")
        if land_status == "For Sale":
            st.info("Scraping Sale Data")
            sale_df = scrape(state, city, api_key, num_page, sold=False)
            show_download_data(sale_df, state, city, formatted_date, sold=False)
        elif land_status == "Sold":
            st.info("Scraping Sold Data")
            sold_df = scrape(state, city, api_key, num_page, sold=True)
            show_download_data(sold_df, state, city, formatted_date, sold=True)
        elif land_status == "All":
            st.info("Scraping Sale and Sold Data")
            sale_df = scrape(state, city, api_key, num_page, sold=False)
            sold_df = scrape(state, city, api_key, num_page, sold=True)
            merged_df = pd.concat([sale_df, sold_df])
            show_download_data(merged_df, state, city, formatted_date, sold=False)

        # scrape_sale(state, city, api_key, num_page)
