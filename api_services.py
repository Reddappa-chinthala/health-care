import os

import requests
from dotenv import load_dotenv


# ============================================================
# API CONFIGURATION
# ============================================================

load_dotenv()

DISEASE_API = "https://disease.sh/v3/covid-19"
USDA_API = "https://api.nal.usda.gov/fdc/v1"
USDA_API_KEY = os.getenv("USDA_API_KEY", "DEMO_KEY")
RXNORM_API = "https://rxnav.nlm.nih.gov/REST"


# ============================================================
# 1. DISEASE STATISTICS
# ============================================================

def get_disease_statistics(country):
    """
    Get COVID-19 statistics for a country using disease.sh
    """

    url = f"{DISEASE_API}/countries/{country}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return {
                "error": f"Unable to retrieve data. HTTP {response.status_code}"
            }

        data = response.json()

        return {
            "country": data.get("country"),
            "cases": data.get("cases"),
            "today_cases": data.get("todayCases"),
            "deaths": data.get("deaths"),
            "today_deaths": data.get("todayDeaths"),
            "recovered": data.get("recovered"),
            "active": data.get("active"),
            "critical": data.get("critical"),
            "population": data.get("population")
        }

    except requests.exceptions.RequestException as e:
        return {
            "error": f"API connection error: {str(e)}"
        }


# ============================================================
# 2. USDA FOOD SEARCH
# ============================================================

def search_food(food_name, api_key=USDA_API_KEY):
    """
    Search USDA FoodData Central for a food.
    """

    url = f"{USDA_API}/foods/search"

    params = {
        "api_key": api_key,
        "query": food_name,
        "pageSize": 5
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return {
                "error": f"USDA API error: HTTP {response.status_code}"
            }

        data = response.json()

        foods = data.get("foods", [])

        if not foods:
            return {
                "error": f"No food found for '{food_name}'."
            }

        return foods

    except requests.exceptions.RequestException as e:
        return {
            "error": f"USDA API connection error: {str(e)}"
        }


# ============================================================
# 3. GET FOOD DETAILS
# ============================================================

def get_food_details(fdc_id, api_key=USDA_API_KEY):
    """
    Get detailed nutrition information for a food.
    """

    url = f"{USDA_API}/food/{fdc_id}"

    params = {
        "api_key": api_key
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return {
                "error": f"USDA API error: HTTP {response.status_code}"
            }

        return response.json()

    except requests.exceptions.RequestException as e:
        return {
            "error": f"USDA API connection error: {str(e)}"
        }


# ============================================================
# 4. EXTRACT IMPORTANT NUTRIENTS
# ============================================================

def extract_nutrients(food_data):
    """
    Extract commonly used nutrients from USDA response.
    """

    nutrients = {
        "Calories": 0,
        "Protein": 0,
        "Carbohydrates": 0,
        "Fat": 0,
        "Fiber": 0,
        "Sugar": 0
    }

    for item in food_data.get("foodNutrients", []):

        nutrient = item.get("nutrient", {})

        name = nutrient.get("name", "")
        value = item.get("amount", 0)
        unit = nutrient.get("unitName", "")

        if value is None:
            value = 0

        if "Energy" in name and "kcal" in unit.lower():
            nutrients["Calories"] = value

        elif name == "Protein":
            nutrients["Protein"] = value

        elif "Carbohydrate" in name:
            nutrients["Carbohydrates"] = value

        elif name == "Total lipid (fat)":
            nutrients["Fat"] = value

        elif "Fiber" in name:
            nutrients["Fiber"] = value

        elif "Sugars, Total" in name:
            nutrients["Sugar"] = value

    return nutrients


# ============================================================
# 5. SEARCH NUTRITION
# ============================================================

def get_food_nutrition(food_name, api_key=USDA_API_KEY):
    """
    Search for a food and return nutrition information.
    """

    search_result = search_food(food_name, api_key)

    if isinstance(search_result, dict) and "error" in search_result:
        return search_result

    first_food = search_result[0]

    fdc_id = first_food.get("fdcId")
    description = first_food.get("description", food_name)

    details = get_food_details(fdc_id, api_key)

    if isinstance(details, dict) and "error" in details:
        return details

    nutrients = extract_nutrients(details)

    return {
        "food": description,
        "fdc_id": fdc_id,
        "nutrients": nutrients
    }


# ============================================================
# 6. FOOD COMPARISON
# ============================================================

def compare_foods(food1, food2, api_key=USDA_API_KEY):
    """
    Compare two foods using USDA nutrition information.
    """

    first = get_food_nutrition(food1, api_key)
    second = get_food_nutrition(food2, api_key)

    if "error" in first:
        return first

    if "error" in second:
        return second

    return {
        "food1": first,
        "food2": second
    }


# ============================================================
# 7. RXNORM MEDICINE SEARCH
# ============================================================

def search_medicine(medicine_name):
    """
    Search RxNorm for standardized medication terminology.
    """

    url = f"{RXNORM_API}/approximateTerm.json"

    params = {
        "term": medicine_name,
        "maxEntries": 5
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return {
                "error": f"RxNorm API error: HTTP {response.status_code}"
            }

        data = response.json()

        candidates = (
            data
            .get("approximateGroup", {})
            .get("candidate", [])
        )

        if not candidates:
            return {
                "error": f"No standardized medicine information found for '{medicine_name}'."
            }

        results = []

        for item in candidates:

            results.append({
                "rxcui": item.get("rxcui"),
                "name": item.get("name"),
                "score": item.get("score")
            })

        return results

    except requests.exceptions.RequestException as e:
        return {
            "error": f"RxNorm API connection error: {str(e)}"
        }