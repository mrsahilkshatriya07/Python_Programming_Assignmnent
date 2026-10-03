import os
import re
import sys
from bs4 import BeautifulSoup

def clean_price(price_str: str) -> float:
    """
    Extracts numeric values from a raw price string and converts to float.
    Example: "$1,299.00" or "INR 1299" -> 1299.0
    Returns -1.0 if no valid numeric price is found.
    """
    if not price_str:
        return -1.0
    # Remove currency symbols, commas, and whitespace, retaining numbers and decimal point
    cleaned = re.sub(r'[^\d.]', '', price_str)
    try:
        return float(cleaned)
    except ValueError:
        return -1.0

def clean_rating(rating_str: str) -> float:
    """
    Extracts rating score from strings like "4.8 out of 5" or "4.8".
    Returns -1.0 if invalid.
    """
    if not rating_str:
        return -1.0
    match = re.search(r'(\d+(?:\.\d+)?)', rating_str)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return -1.0
    return -1.0

def extract_products_from_html(file_path: str) -> list:
    """
    Parses a single HTML file and extracts (name, price, rating) tuples.
    Adapts to common HTML item container patterns or regex fallback.
    """
    products = []
    if not os.path.exists(file_path):
        return products

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    # Strategy 1: Look for standard product container cards/items
    containers = soup.find_all(class_=re.compile(r'product|item|card|listing', re.I))

    for container in containers:
        # Extract Product Name
        name_elem = container.find(class_=re.compile(r'title|name|header', re.I)) or container.find(['h1', 'h2', 'h3', 'h4', 'a'])
        # Extract Price
        price_elem = container.find(class_=re.compile(r'price|cost|amount', re.I))
        # Extract Rating
        rating_elem = container.find(class_=re.compile(r'rating|score|star', re.I))

        if name_elem and price_elem and rating_elem:
            name = name_elem.get_text(strip=True)
            price = clean_price(price_elem.get_text())
            rating = clean_rating(rating_elem.get_text())

            if name and price >= 0 and rating >= 0:
                products.append((name, price, rating))

    # Strategy 2: Fallback regex pattern matching if no structured containers found
    if not products:
        # Matches patterns like: Name: Python Book, Price: $499, Rating: 4.8
        regex_pattern = re.compile(
            r'(?:product|name)?\s*[:\-]?\s*([A-Za-z0-9\s]+?)\s*[,;\n|]'
            r'.*?(?:price)?\s*[:\-]?\s*([$\u20B9\xA3\xA5\d.,]+)'
            r'.*?(?:rating)?\s*[:\-]?\s*([\d.]{1,3})',
            re.IGNORECASE
        )
        for match in regex_pattern.finditer(content):
            raw_name, raw_price, raw_rating = match.groups()
            name = raw_name.strip()
            price = clean_price(raw_price)
            rating = clean_rating(raw_rating)

            if name and price >= 0 and rating >= 0:
                products.append((name, price, rating))

    return products

def rank_products(file_paths: list, k: int):
    """
    Extracts, deduplicates, and ranks products from multiple HTML files.
    Deduplication Policy: Keep the entry with the higher rating (or lower price if equal).
    Sort Order: Rating (Descending), Price (Ascending), Name (Ascending Lexicographically).
    """
    # Map product_name -> (price, rating)
    unique_products = {}

    for path in file_paths:
        extracted = extract_products_from_html(path)
        for name, price, rating in extracted:
            if name not in unique_products:
                unique_products[name] = (price, rating)
            else:
                existing_price, existing_rating = unique_products[name]
                # Keep better rating; break tie with lower price
                if (rating > existing_rating) or (rating == existing_rating and price < existing_price):
                    unique_products[name] = (price, rating)

    # Convert to list of tuples: (name, price, rating)
    product_list = [(name, price, rating) for name, (price, rating) in unique_products.items()]

    # Sort key rules:
    # 1. Rating descending: -rating
    # 2. Price ascending: price
    # 3. Name lexicographically ascending: name
    product_list.sort(key=lambda x: (-x[2], x[1], x[0]))

    # Print top K results
    top_k = product_list[:k]
    for name, price, rating in top_k:
        # Format integer prices cleanly (e.g., 499 instead of 499.0)
        formatted_price = int(price) if price.is_integer() else price
        formatted_rating = int(rating) if rating.is_integer() else rating
        print(f"{name} {formatted_price} {formatted_rating}")

if __name__ == "__main__":
    # Input handling
    try:
        first_line = sys.stdin.readline().split()
        if not first_line:
            sys.exit(0)
        
        p, k = int(first_line[0]), int(first_line[1])
        file_paths = [sys.stdin.readline().strip() for _ in range(p)]

        rank_products(file_paths, k)
    except Exception as e:
        print(f"Error parsing input: {e}", file=sys.stderr)
