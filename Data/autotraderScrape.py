import re
import time
import requests
import json
from bs4 import BeautifulSoup

# URL PARAMS
# rcp = display number (set to max to reduce # of requests)
DISPLAY_NUM = 100
# rcs = starting entry (0 = page 1; 100 = page 2...)
# srt = 35 (default sorting), this shouldn't matter
SORT_VALUE = 35
# prx = search radius (-1 = national)
NATION_WIDE = -1
# loc = postal code (currently set to CN tower)
POSTAL_CODE = "M5V3L9"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0"}


def get_url(brand, model, page_num):
    return (f"https://www.autotrader.ca/cars/{brand}/{model}/?rcp={DISPLAY_NUM}"
            f"&rcs={page_num * 100}&srt={SORT_VALUE}&prx={NATION_WIDE}&loc={POSTAL_CODE}")


# Get total listings for a brand model nationwide
def get_total_listings(brand, model):
    url = get_url(brand, model, page_num=0)
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    return int(soup.find("span", id="sbCount").text.strip().replace(",", ""))


# list of cars to scrape
cars_to_scrape = {
    "honda": ["civic", "accord"]
}


def main():
    # Scrape all cars listed in cars_to_scrape
    for brand in cars_to_scrape:
        for model in cars_to_scrape[brand]:
            # All car listings
            all_listings = []

            total_listings = get_total_listings(brand, model)
            total_pages = int(total_listings / 100)

            # Extract all listings
            print(f"Extracting nation wide car data for {brand} {model}...")
            start_inner = time.perf_counter()
            empty_page_count = 0
            for page_num in range(0, total_pages):
                print(f"On page number {page_num}")
                url = get_url(brand, model, page_num)

                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, "html.parser")

                # listings_container is a container containing all listings
                listings_container = soup.find("div", id="SearchListings")

                # Failed to acquire listings container, request failed
                if listings_container is None:
                    print("Request blocked by Autotrader, cannot scrape this page")
                    empty_page_count += 1
                    continue

                copy_flag = False
                # Iterate through the listings
                for child_element in listings_container.findChildren("div", recursive=False):
                    # Get classes of child element
                    child_element_classes = child_element.get("class")

                    # Only set copy_flag to true if we are going through the 'all listings' section
                    if (child_element_classes is not None and "listingHeadingNewSRP" in child_element_classes):
                        copy_flag = ("All Listings" in child_element.find(
                            "span").text.strip())

                    # Only copy when copy_flag is on, ex. We are going through all listings, not ads
                    if (copy_flag and child_element_classes is not None and "result-item" in child_element_classes):
                        title = child_element.find(
                            "a", class_="result-title").find("span").text.strip()

                        year = re.search('[0-9]+', title).group()

                        mileage_unparsed = child_element.find(
                            "div", class_="kms")
                        if mileage_unparsed is not None:
                            mileage = re.search(
                                '[0-9]+(,[0-9]+)?', mileage_unparsed.text.strip()).group().replace(",", "")

                        price = child_element.find(
                            "span", id="price-amount-value").text.strip().replace("$", "").replace(",", "")

                        all_listings.append({"title": title, "year": year,
                                            "mileage": mileage, "price": price})
                # chill down for a bit, so we don't get blocked by the Autotrader server
                time.sleep(5)

            end_inner = time.perf_counter()
            print(f"Omitted {empty_page_count} pages due to blocked request")
            print(
                f"Extraction complete for {brand} {model}, took {end_inner - start_inner:0.4f} seconds, outputting to JSON...")

            # formatted json output file
            output_json = json.dumps(
                {"total listings": total_listings, "contents": all_listings}, indent=2)

            with open(f"./Data/output/{brand}_{model}.json", "w") as file:
                file.write(output_json)


if __name__ == "__main__":
    start = time.perf_counter()
    main()
    end = time.perf_counter()
    print(f"Extraction complete. Took {end - start:0.4f} seconds")
