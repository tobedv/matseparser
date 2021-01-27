import requests
import logging
import os
import json
from collections import defaultdict

category_tree_url = "https://mat.se/api/product/getCategoryTree"
category_details_url = "https://mat.se/api/product/listByCategory"

logging.basicConfig(level=20)
logger = logging.getLogger()


def get_json_data(url, params=None):
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data


def get_categories() -> dict:
    logger.info("Fetching categories")
    return get_json_data(category_tree_url)


def get_category_products(category_id: str) -> list:
    logger.info(f"Fetching category id: {category_id}")
    return get_json_data(category_details_url, params={"categoryId": category_id})


def find_best_selling_products(product_list: list, amount_of_objects=5) -> list:
    sorted_list = sorted(
        product_list, key=lambda product: product["soldCount"], reverse=True
    )
    return sorted_list[:amount_of_objects]


def calculate_percentage_country_specific_products(
    product_list: list, country_code="SE"
) -> float:
    total_count = len(product_list)
    country_specific_count = 0
    for product in product_list:
        if product["countryOfOrigin"] == country_code:
            country_specific_count += 1
    return country_specific_count / total_count


def get_category_statistics(categories: dict) -> dict:
    result_dict = {}
    for category in categories["subCategories"]:
        products_in_category = get_category_products(str(category["id"]))
        result_dict[category["name"]] = {
            "product_count": category["count"],
            "top_5_products": find_best_selling_products(
                product_list=products_in_category
            ),
            "percentage_swedish": calculate_percentage_country_specific_products(
                product_list=products_in_category
            ),
        }
        logger.info(f"Proccessed {category['id']}: {category['name']}")
    return result_dict


def group_statistics_per_deliverable(result_dict: dict) -> dict:
    grouped_dict = defaultdict(dict)
    for category_name, statistics in result_dict.items():
        grouped_dict["number_of_products"][category_name] = statistics["product_count"]
        grouped_dict["top_5_products"][category_name] = statistics["top_5_products"]
        grouped_dict["percentage_swedish"][category_name] = statistics[
            "percentage_swedish"
        ]
    logger.info("Grouped objects per deliverable")
    return grouped_dict


def save_result_to_json_files(
    grouped_statistics_per_deliverable: dict, root_path="/tmp"
) -> None:
    for name, items in grouped_statistics_per_deliverable.items():
        full_file_path = os.path.join(root_path, f"{name}.json")
        with open(full_file_path, "w+") as f:
            json.dump(items, f)
        logger.info(f"Wrote result of: {name} to {full_file_path}")


def main(root_path="/tmp"):
    categories = get_categories()
    per_category_statistics = get_category_statistics(categories)
    grouped_statistics_per_deliverable = group_statistics_per_deliverable(
        per_category_statistics
    )
    save_result_to_json_files(grouped_statistics_per_deliverable, root_path=root_path)


if __name__ == "__main__":
    main()
