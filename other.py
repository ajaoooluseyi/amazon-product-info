import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://www.amazon.in"
PRODUCTS_PER_PAGE = 48
MAX_PAGES = 20
MAX_PRODUCTS = 200


def scrape_products():
    products = []
    count = 0

    for page in range(1, MAX_PAGES + 1):
        url = f"https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        results = soup.find_all("div", {"data-component-type": "s-search-result"})
        for result in results:
            if count >= MAX_PRODUCTS:
                break

            product_url = BASE_URL + result.find(
                "a", class_="a-link-normal s-no-outline"
            ).get("href")
            product_name = result.find(
                "span", class_="a-size-medium a-color-base a-text-normal"
            ).text.strip()
            product_price = result.find("span", class_="a-offscreen").text.strip()
            rating = result.find("span", class_="a-icon-alt").text.strip()
            review_count = result.find(
                "span", {"class": "a-size-base", "dir": "auto"}
            ).text.strip()

            # Scrape additional information from product URL
            additional_info = scrape_product_details(product_url)

            product = {
                "Product URL": product_url,
                "Product Name": product_name,
                "Product Price": product_price,
                "Rating": rating,
                "Number of Reviews": review_count,
                "Description": additional_info["description"],
                "ASIN": additional_info["asin"],
                "Product Description": additional_info["product_description"],
                "Manufacturer": additional_info["manufacturer"],
            }
            products.append(product)

            count += 1
            print(f"Scraped product {count}/{MAX_PRODUCTS}: {product_name}")

        if count >= MAX_PRODUCTS:
            break

    return products


def scrape_product_details(product_url):
    response = requests.get(product_url)
    soup = BeautifulSoup(response.content, "html.parser")

    description = (
        soup.find("h2", text="Product description").find_next("div").text.strip()
    )
    asin = soup.find("th", text="ASIN").find_next("td").text.strip()
    product_description = (
        soup.find("h2", text="Product description")
        .find_next("div")
        .find_next("p")
        .text.strip()
    )
    manufacturer = soup.find("th", text="Manufacturer").find_next("td").text.strip()

    return {
        "description": description,
        "asin": asin,
        "product_description": product_description,
        "manufacturer": manufacturer,
    }


# Example usage
scraped_products = scrape_products()

# Export data to CSV
df = pd.DataFrame(scraped_products)
df.to_csv("product_data.csv", index=False)

print("Scraping completed. Data exported to product_data.csv.")
