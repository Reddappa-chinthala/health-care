import re

from api_services import (
    get_disease_statistics,
    get_food_nutrition,
    compare_foods,
    search_medicine
)


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(message):

    text = message.lower()

    # Disease statistics
    disease_words = [
        "covid",
        "corona",
        "disease statistics",
        "disease cases",
        "cases in",
        "covid statistics"
    ]

    if any(word in text for word in disease_words):
        return "disease"

    # Food comparison
    comparison_words = [
        "compare",
        "comparison",
        "difference between",
        "vs",
        "versus"
    ]

    if any(word in text for word in comparison_words):
        return "comparison"

    # Medicine
    medicine_words = [
        "medicine",
        "medication",
        "drug",
        "tablet",
        "capsule",
        "medicine name",
        "standard name"
    ]

    if any(word in text for word in medicine_words):
        return "medicine"

    # Food nutrition
    food_words = [
        "nutrition",
        "nutritional",
        "protein",
        "calories",
        "carbohydrates",
        "carbs",
        "fat",
        "food"
    ]

    if any(word in text for word in food_words):
        return "food"

    return "general"


# ============================================================
# EXTRACT COUNTRY
# ============================================================

def extract_country(message):

    text = message.lower()

    countries = [
        "india",
        "usa",
        "united states",
        "uk",
        "united kingdom",
        "canada",
        "australia",
        "germany",
        "france",
        "italy",
        "japan",
        "china"
    ]

    for country in countries:

        if country in text:
            return country

    return "india"


# ============================================================
# DISEASE RESPONSE
# ============================================================

def disease_response(message):

    country = extract_country(message)

    data = get_disease_statistics(country)

    if "error" in data:
        return data["error"]

    response = f"""
### 🦠 COVID-19 Statistics — {data['country']}

- **Total Cases:** {data['cases']:,}
- **Today's Cases:** {data['today_cases']:,}
- **Total Deaths:** {data['deaths']:,}
- **Today's Deaths:** {data['today_deaths']:,}
- **Recovered:** {data['recovered']:,}
- **Active Cases:** {data['active']:,}
- **Critical Cases:** {data['critical']:,}
- **Population:** {data['population']:,}

*Source: Disease.sh*
"""

    return response


# ============================================================
# EXTRACT FOOD NAME
# ============================================================

def extract_food_name(message):

    text = message.lower()

    patterns = [
        r"nutrition of (.+)",
        r"nutritional value of (.+)",
        r"nutrients in (.+)",
        r"protein in (.+)",
        r"calories in (.+)",
        r"nutrition for (.+)",
        r"food (.+)"
    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:
            food = match.group(1)

            # Remove common words
            food = food.replace("100g", "")
            food = food.replace("100 grams", "")
            food = food.strip()

            return food

    return text


# ============================================================
# FOOD RESPONSE
# ============================================================

def food_response(message, api_key):

    food_name = extract_food_name(message)

    data = get_food_nutrition(
        food_name,
        api_key
    )

    if "error" in data:
        return data["error"]

    nutrients = data["nutrients"]

    response = f"""
### 🥗 Nutrition Information

**Food:** {data['food']}

| Nutrient | Amount |
|---|---:|
| Calories | {nutrients['Calories']} kcal |
| Protein | {nutrients['Protein']} g |
| Carbohydrates | {nutrients['Carbohydrates']} g |
| Fat | {nutrients['Fat']} g |
| Fiber | {nutrients['Fiber']} g |
| Sugar | {nutrients['Sugar']} g |

*Nutrition values are returned by USDA FoodData Central.*
"""

    return response


# ============================================================
# EXTRACT COMPARISON FOODS
# ============================================================

def extract_comparison_foods(message):

    text = message.lower()

    # Example:
    # compare rice and oats

    match = re.search(
        r"compare\s+(.+?)\s+(?:and|vs|versus)\s+(.+)",
        text
    )

    if match:
        return (
            match.group(1).strip(),
            match.group(2).strip()
        )

    match = re.search(
        r"difference between\s+(.+?)\s+and\s+(.+)",
        text
    )

    if match:
        return (
            match.group(1).strip(),
            match.group(2).strip()
        )

    return None, None


# ============================================================
# COMPARISON RESPONSE
# ============================================================

def comparison_response(message, api_key):

    food1, food2 = extract_comparison_foods(message)

    if not food1 or not food2:

        return """
Please enter the comparison like:

**Compare rice and oats**

or

**Compare apples and bananas**
"""

    data = compare_foods(
        food1,
        food2,
        api_key
    )

    if "error" in data:
        return data["error"]

    first = data["food1"]["nutrients"]
    second = data["food2"]["nutrients"]

    response = f"""
### 📊 Food Comparison

| Nutrient | {food1.title()} | {food2.title()} |
|---|---:|---:|
| Calories | {first['Calories']} kcal | {second['Calories']} kcal |
| Protein | {first['Protein']} g | {second['Protein']} g |
| Carbohydrates | {first['Carbohydrates']} g | {second['Carbohydrates']} g |
| Fat | {first['Fat']} g | {second['Fat']} g |
| Fiber | {first['Fiber']} g | {second['Fiber']} g |
| Sugar | {first['Sugar']} g | {second['Sugar']} g |

*Data source: USDA FoodData Central.*
"""

    return response


# ============================================================
# MEDICINE RESPONSE
# ============================================================

def medicine_response(message):

    text = message.lower()

    medicine = text

    remove_words = [
        "what is the standard name for",
        "what is the standard name of",
        "search medicine",
        "search medication",
        "medicine",
        "medication",
        "drug",
        "tablet",
        "capsule"
    ]

    for word in remove_words:
        medicine = medicine.replace(word, "")

    medicine = medicine.strip()

    if not medicine:

        return """
Please enter a medicine name.

Example:

**Search medicine paracetamol**
"""

    data = search_medicine(medicine)

    if isinstance(data, dict) and "error" in data:
        return data["error"]

    response = "### 💊 Standardized Medicine Information\n\n"

    for item in data:

        response += f"""
**Name:** {item['name']}  
**RxCUI:** {item['rxcui']}  
**Match Score:** {item['score']}

"""

    response += """
> This information is for terminology lookup only. It does not provide a prescription or treatment recommendation.
"""

    return response


# ============================================================
# MAIN CHATBOT FUNCTION
# ============================================================

def chatbot_response(message, api_key):

    intent = detect_intent(message)

    if intent == "disease":
        return disease_response(message)

    elif intent == "food":
        return food_response(
            message,
            api_key
        )

    elif intent == "comparison":
        return comparison_response(
            message,
            api_key
        )

    elif intent == "medicine":
        return medicine_response(message)

    else:

        return """
### 👋 Healthcare Research & Wellness Assistant

I can help you with:

🦠 **Disease statistics**

Example:
> Show COVID-19 statistics for India.

🥗 **Food nutrition**

Example:
> How much protein is in chickpeas?

💊 **Medicine terminology**

Example:
> Search medicine paracetamol.

📊 **Food comparison**

Example:
> Compare rice and oats.
"""