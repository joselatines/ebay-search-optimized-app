import re
import requests
from bs4 import BeautifulSoup


class Ebay:
    website = "https://www.ebay.com/sch/"
    all_products_list = []
    avg_product_price = None

    def search(self, user_search):
        query = self._format_product(user_search)
        response = requests.get(f"{self.website}{query}")
        content = response.content

        soup = BeautifulSoup(content, "html.parser")

        products_container = (
            soup.find("div", id="srp-river-results")
            .find("ul", class_="srp-results srp-list clearfix")
            .find_all()
        )

        all_products = []
        prices_list = []

        for product_li in products_container:
            price_li = product_li.find("span", class_="s-item__price")
            link_product_li = product_li.find("a", class_="s-item__link")
            title_container_product = product_li.find("div", class_="s-item__title")
            image_div = product_li.find(
                "div", class_="s-item__image-wrapper image-treatment"
            )

            if price_li and link_product_li and title_container_product and image_div:
                price_str = self._extract_first_price(price_li.get_text())
                price_float = self._format_price(price_str)

                link = link_product_li.get("href")
                title = title_container_product.find("span").get_text()
                image_uri = image_div.find("img").get("src")

                all_products.append(
                    {
                        "price": price_float,
                        "link": link,
                        "title": title,
                        "image_uri": image_uri,
                    }
                )
                prices_list.append(price_float)

        filtered_products = self._filter_products(
            all_products, prices_list, user_search
        )

        filtered_products.sort(key=self.get_price)

        self.all_products_list = filtered_products
        return filtered_products

    def get_avg_price(self):
        return round(self.avg_product_price)

    def _filter_products(self, all_products, prices_list, user_search) -> list:
        def filter_near_average(numbers: list[int], percentage=0.1):
            """This function takes a list of numbers and an optional percentage
            value as arguments. It calculates the average value of the numbers and
            determines a threshold value based on the given percentage value.
            It then returns a new list that only contains numbers that are within the
            threshold distance from the average value."""

            # in easy way: returns a list of prices that are near to the average base on the percentage

            avg = sum(numbers) / len(numbers)
            self.avg_product_price = avg
            threshold = avg * percentage
            return [num for num in numbers if abs(num - avg) < threshold]

        # numbers/prices that are near of average
        near_avg_prices = filter_near_average(prices_list)
        filtered_products = []

        def filter_products_by_price_and_title():
            filtered_products = []
            added_products = set()
            for product in all_products:
                price_is_in_avg_prices = product["price"] in near_avg_prices
                product_title_is_product_name = self.match_string(
                    product["title"], user_search
                )

                if price_is_in_avg_prices and product_title_is_product_name:
                    product_tuple = tuple(product.items())
                    if product_tuple not in added_products:  # checks if is unique
                        filtered_products.append(product)
                        added_products.add(product_tuple)

            return filtered_products

        filtered_products = filter_products_by_price_and_title()
        print("Products: ", len(all_products))
        print("Filtered products: ", len(filtered_products))
        return filtered_products

    @staticmethod
    def get_price(product):
        return product["price"]

    @staticmethod
    def match_string(match_str, target_str):
        match_str = match_str.lower()
        target_str = target_str.lower()
        # print(f"match_str: {match_str} - target: {target_str}")
        if match_str in target_str or target_str in match_str:
            return True
        else:
            return False

    @staticmethod
    def _extract_first_price(price_string) -> str:
        """splits a string containing prices separated by "a" or "o"
        using regular expression and returns the first price after
        removing any leading or trailing whitespace."""
        parts = re.split(r"a|o", price_string, flags=re.IGNORECASE)
        return parts[0].strip()

    @staticmethod
    def _format_price(price: str):
        try:
            # Remove any non-digit characters from the string
            clean_price = re.sub(r"[^\d.]", "", price)

            # Convert the cleaned string to a float
            float_price = float(clean_price)

            # Round the float to 2 decimal places
            rounded_price = round(float_price, 2)

            return rounded_price
        except (ValueError, TypeError):
            # Return None if the conversion fails
            return None

    @staticmethod
    def _format_product(product: str) -> str:
        return product.lower().replace(" ", "+")
