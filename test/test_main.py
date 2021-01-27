import os
import sys
import pytest
import requests_mock
import json
import tempfile

module_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(module_dir, "../src/"))
import main

categories_test_data = os.path.join(module_dir, "test_data", "getCategoryTree.json")
products_test_data = os.path.join(
    module_dir, "test_data", "listByCategory-1469-slim.json"
)


@pytest.fixture
def category_tree():
    with open(categories_test_data) as f:
        test_data = json.load(f)
    return test_data


@pytest.fixture
def product_data():
    with open(products_test_data) as f:
        test_data = json.load(f)
    return test_data


def test_get_json_data(category_tree):
    with requests_mock.Mocker() as m:
        m.get(main.category_tree_url, json=category_tree)
        result = main.get_json_data(main.category_tree_url)
        assert result == category_tree


def test_get_categories(category_tree):
    with requests_mock.Mocker() as m:
        m.get(main.category_tree_url, json=category_tree)
        result = main.get_categories()
        assert result == category_tree


def test_get_category_products(product_data):
    with requests_mock.Mocker() as m:
        m.get(main.category_details_url, json=product_data)
        result = main.get_category_products("123")
        assert result == product_data


def test_find_best_selling_products(product_data):
    expected_result = [
        {"countryOfOrigin": "SE", "id": 7, "soldCount": 7},
        {"countryOfOrigin": "UK", "id": 6, "soldCount": 6},
        {"countryOfOrigin": "DE", "id": 5, "soldCount": 5},
        {"countryOfOrigin": "DE", "id": 4, "soldCount": 4},
        {"countryOfOrigin": "SE", "id": 3, "soldCount": 3},
    ]
    assert main.find_best_selling_products(product_data) == expected_result


def test_calculate_percentage_country_specific_products(product_data):
    expected_resut = 0.57
    assert pytest.approx(
        main.calculate_percentage_country_specific_products(product_data),
        expected_resut,
    )


def test_get_category_statistics(category_tree, product_data):
    category_tree["subCategories"] = category_tree["subCategories"][:1]
    main.get_category_products = lambda *args, **kwargs: product_data
    main.find_best_selling_products = lambda *args, **kwargs: [
        {"countryOfOrigin": "SE", "id": 7, "soldCount": 7},
        {"countryOfOrigin": "UK", "id": 6, "soldCount": 6},
        {"countryOfOrigin": "DE", "id": 5, "soldCount": 5},
        {"countryOfOrigin": "DE", "id": 4, "soldCount": 4},
        {"countryOfOrigin": "SE", "id": 3, "soldCount": 3},
    ]
    main.calculate_percentage_country_specific_products = lambda *args, **kwargs: 0.57

    expected_result = {
        "Bageri": {
            "percentage_swedish": 0.57,
            "product_count": 574,
            "top_5_products": [
                {"countryOfOrigin": "SE", "id": 7, "soldCount": 7},
                {"countryOfOrigin": "UK", "id": 6, "soldCount": 6},
                {"countryOfOrigin": "DE", "id": 5, "soldCount": 5},
                {"countryOfOrigin": "DE", "id": 4, "soldCount": 4},
                {"countryOfOrigin": "SE", "id": 3, "soldCount": 3},
            ],
        },
    }

    assert main.get_category_statistics(category_tree) == expected_result


def test_group_statistics_per_deliverable():
    result_dict = {
        "Bageri": {
            "percentage_swedish": 0.57,
            "product_count": 574,
            "top_5_products": [
                {"countryOfOrigin": "SE", "id": 7, "soldCount": 7},
                {"countryOfOrigin": "UK", "id": 6, "soldCount": 6},
                {"countryOfOrigin": "DE", "id": 5, "soldCount": 5},
                {"countryOfOrigin": "DE", "id": 4, "soldCount": 4},
                {"countryOfOrigin": "SE", "id": 3, "soldCount": 3},
            ],
        },
    }

    expected_result = {
        "number_of_products": {"Bageri": 574},
        "percentage_swedish": {"Bageri": 0.57},
        "top_5_products": {
            "Bageri": [
                {"countryOfOrigin": "SE", "id": 7, "soldCount": 7},
                {"countryOfOrigin": "UK", "id": 6, "soldCount": 6},
                {"countryOfOrigin": "DE", "id": 5, "soldCount": 5},
                {"countryOfOrigin": "DE", "id": 4, "soldCount": 4},
                {"countryOfOrigin": "SE", "id": 3, "soldCount": 3},
            ]
        },
    }

    assert main.group_statistics_per_deliverable(result_dict) == expected_result


def test_save_result_to_json_files():
    grouped_statistics_per_deliverable = {
        "number_of_products": {"Bageri": 574},
        "percentage_swedish": {"Bageri": 0.57},
        "top_5_products": {
            "Bageri": [
                {"countryOfOrigin": "SE", "id": 7, "soldCount": 7},
                {"countryOfOrigin": "UK", "id": 6, "soldCount": 6},
                {"countryOfOrigin": "DE", "id": 5, "soldCount": 5},
                {"countryOfOrigin": "DE", "id": 4, "soldCount": 4},
                {"countryOfOrigin": "SE", "id": 3, "soldCount": 3},
            ]
        },
    }

    with tempfile.TemporaryDirectory() as tmp_path:
        main.save_result_to_json_files(
            grouped_statistics_per_deliverable, root_path=tmp_path
        )

        with open(os.path.join(tmp_path, "number_of_products.json")) as f:
            loaded_nop = json.load(f)
            expected_nop = {"Bageri": 574}
            assert loaded_nop == expected_nop

        with open(os.path.join(tmp_path, "percentage_swedish.json")) as f:
            loaded_pct = json.load(f)
            expected_pct = {"Bageri": 0.57}
            assert loaded_pct == expected_pct

        with open(os.path.join(tmp_path, "top_5_products.json")) as f:
            loaded_top = json.load(f)
            expected_top = {
                "Bageri": [
                    {"countryOfOrigin": "SE", "id": 7, "soldCount": 7},
                    {"countryOfOrigin": "UK", "id": 6, "soldCount": 6},
                    {"countryOfOrigin": "DE", "id": 5, "soldCount": 5},
                    {"countryOfOrigin": "DE", "id": 4, "soldCount": 4},
                    {"countryOfOrigin": "SE", "id": 3, "soldCount": 3},
                ]
            }
            assert loaded_top == expected_top


def test_main(category_tree, product_data):
    category_tree["subCategories"] = category_tree["subCategories"][:1]
    with requests_mock.Mocker() as m:
        m.get(main.category_tree_url, json=category_tree)
        m.get(main.category_details_url, json=product_data)
        with tempfile.TemporaryDirectory() as tmp_path:
            main.main(root_path=tmp_path)
            assert os.path.exists(os.path.join(tmp_path, "number_of_products.json"))
            assert os.path.exists(os.path.join(tmp_path, "percentage_swedish.json"))
            assert os.path.exists(os.path.join(tmp_path, "top_5_products.json"))
