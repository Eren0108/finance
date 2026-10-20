import re
from typing import List, Dict, Optional

# Keyword dictionary mapping categories to common transaction terms
CATEGORY_KEYWORDS = {
    "Food": [
        "swiggy", "zomato", "mcdonald", "burger", "pizza", "restaurant", "cafe",
        "coffee", "starbucks", "blinkit", "zepto", "instamart", "grocery", "groceries",
        "bigbasket", "dmart", "bakery", "sweets", "food", "snacks", "kfc", "domino",
        "subway", "chai", "dhabha", "hotel food", "dine", "eat", "barbeque"
    ],
    "Rent": [
        "rent", "landlord", "house rent", "lease", "maintenance", "society",
        "housing", "apartment rent", "flat maintenance", "pg accommodation"
    ],
    "Travel": [
        "uber", "ola", "rapido", "irctc", "flight", "indigo", "air india", "train",
        "metro", "fuel", "petrol", "diesel", "shell", "indian oil", "ioc", "hpcl",
        "bpcl", "taxi", "cab", "bus", "toll", "fastag", "yulu", "commute", "travel"
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "ajio", "zara", "h&m", "croma", "reliance digital",
        "retail", "clothing", "apparel", "mall", "ikea", "decathlon", "meesho", "nykaa",
        "store", "purchase", "shopping", "footwear", "electronics"
    ],
    "Bills": [
        "electricity", "power", "bescom", "tneb", "msedcl", "tatapower", "airtel",
        "jio", "vi", "vodafone", "broadband", "wifi", "water bill", "gas", "indane",
        "bharat gas", "lpg", "recharge", "mobile bill", "utility", "dth", "tata sky",
        "dish tv", "postpaid", "bill desk"
    ],
    "Health": [
        "pharmacy", "chemist", "apollo", "medplus", "pharmeasy", "1mg", "hospital",
        "clinic", "doctor", "lab", "pathology", "diagnostic", "dental", "dentist",
        "healthcare", "medicine", "wellness", "optical", "lenskart"
    ],
    "Entertainment": [
        "netflix", "spotify", "hotstar", "disney", "prime video", "bookmyshow",
        "pvr", "inox", "cinema", "theatre", "movie", "steam", "playstation", "xbox",
        "youtube", "gaming", "audible", "concert", "amusement"
    ],
    "Salary": [
        "salary", "payroll", "wage", "stipend", "direct deposit", "neft salary",
        "ach salary", "monthly payout", "bonus", "dividend"
    ]
}


def guess_category(description: str, category_names: Optional[List[str]] = None, default_category: str = "Other") -> str:
    """
    Given a description string and optional list of valid category names in DB,
    returns the best matching category name.
    """
    if not description:
        return default_category

    text = description.lower()
    
    # Check keyword categories
    for cat_name, keywords in CATEGORY_KEYWORDS.items():
        if category_names and cat_name not in category_names:
            continue
        for kw in keywords:
            # Word boundary or substring matching
            if re.search(r'\b' + re.escape(kw) + r'\b', text) or kw in text:
                return cat_name

    # If category_names contains "Other", return "Other", else first available
    if category_names:
        if default_category in category_names:
            return default_category
        return category_names[0]

    return default_category
