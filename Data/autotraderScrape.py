import re
import requests
import json
from bs4 import BeautifulSoup

# Get total listings
url = "https://www.autotrader.ca/cars/on/north%20york/?rcp=100&rcs=0&prx=100&prv=Ontario&loc=M2J%204X9&hprc=True&wcp=True&iosp=True&sts=New-Used&inMarket=basicSearch&mdl=Civic&make=Honda"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
total_listings = int(
    soup.find("span", id="sbCount").text.strip().replace(",", ""))

# All car listings
all_listings = []

# Extract all listings
for i in range(0, total_listings, 100):
    url = "https://www.autotrader.ca/cars/on/north%20york/?rcp=100&rcs={pageNum}&prx=100&prv=Ontario&loc=M2J%204X9&hprc=True&wcp=True&iosp=True&sts=New-Used&inMarket=basicSearch&mdl=Civic&make=Honda".format(
        pageNum=i)

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    listings = soup.find_all("div", class_="result-item-inner")

    count = 0
    for listing in listings:
        count += 1

        title = listing.find(
            "a", class_="result-title").find("span").text.strip()

        year = re.search('[0-9]+', title).group()

        mileage_unparsed = listing.find("div", class_="kms")
        if mileage_unparsed is not None:
            mileage = re.search(
                '[0-9]+(,[0-9]+)?', mileage_unparsed.text.strip()).group().replace(",", "")

        price = listing.find(
            "span", id="price-amount-value").text.strip().replace("$", "").replace(",", "")

        all_listings.append({"title": title, "year": year,
                            "mileage": mileage, "price": price})

# formatted json output file
output_json = json.dumps(
    {"total listings": total_listings, "contents": all_listings}, indent=2)

with open("all_listings.json", "w") as file:
    file.write(output_json)
