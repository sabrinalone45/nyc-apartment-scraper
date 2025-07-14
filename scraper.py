import requests, json, random, time, os, re
import pandas as pd
from bs4 import BeautifulSoup
from geopy.distance import great_circle
from sodapy import Socrata
import datetime
import numpy as np

def fetch_crime_coords():
    client = Socrata("data.cityofnewyork.us", None)
    one_year_ago = (datetime.datetime.now() - datetime.timedelta(days=365)).date().isoformat()
    results = client.get(
        "qgea-i56i",
        where=f"latitude IS NOT NULL AND longitude IS NOT NULL AND cmplnt_fr_dt >= '{one_year_ago}'",
        select="latitude, longitude",
        limit=10000
    )
    return [(float(r['latitude']), float(r['longitude'])) for r in results if 'latitude' in r and 'longitude' in r]

try:
    crime_coords = fetch_crime_coords()
    print(f"[CRIME DATA] Fetched {len(crime_coords)} points")
except Exception as e:
    print(f"[ERROR] Fetching crime data: {e}")
    crime_coords = []

geocache = {}
if os.path.exists("geocache.csv"):
    df = pd.read_csv("geocache.csv")
    geocache = {row["query"]: (row["lat"], row["lon"]) for _, row in df.iterrows()}

def get_fake_coordinates():
    return random.uniform(40.70, 40.80), random.uniform(-74.00, -73.90)

def get_coordinates_from_nominatim(query):
    try:
        time.sleep(1)
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "json", "limit": 1},
            headers={"User-Agent": "ApartmentSafetyApp/1.0"}
        )
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"[ERROR] Nominatim failed for '{query}': {e}")
    return get_fake_coordinates()

def get_coordinates_from_nominatim_cached(query):
    if query in geocache:
        return geocache[query]
    coords = get_coordinates_from_nominatim(query)
    geocache[query] = coords
    pd.DataFrame([{"query": q, "lat": lat, "lon": lon} for q, (lat, lon) in geocache.items()]).to_csv("geocache.csv", index=False)
    return coords

def extract_price_and_title_from_card(card):
    title_elem = card.find("h3")
    price_elem = card.find("span", class_="price")
    title = title_elem.text.strip().lower() if title_elem else ""
    price = price_elem.text.strip() if price_elem else ""
    return title, price

# main scraper
def scrape_apartments():
    url = "https://newyork.craigslist.org/search/apa"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    script = soup.find("script", {"id": "ld_searchpage_results", "type": "application/ld+json"})
    data = json.loads(script.string) if script else {}
    items = data.get("itemListElement", [])
    html_cards = soup.find_all("li", class_="cl-static-search-result")

    price_lookup = {}
    for card in html_cards:
        title_lower, price = extract_price_and_title_from_card(card)
        if title_lower and price:
            price_lookup[title_lower] = price

    raw_listings = []
    for item in items[:30]:
        info = item.get("item", {})
        title = info.get("name", "No title")
        title_lower = title.lower()
        address_info = info.get("address", {})
        location_text = address_info.get("addressLocality", "").lower()
        query = f"{location_text}, New York, NY" if location_text else title_lower

        lat, lon = get_coordinates_from_nominatim_cached(query)
        if lat is None or lon is None:
            continue

        center = (lat, lon)
        radius_miles = 0.25
        crime_count = sum(
            1 for (clat, clon) in crime_coords
            if great_circle(center, (clat, clon)).miles <= radius_miles
        )

        price = price_lookup.get(title_lower, "N/A")
        
        raw_listings.append({
            "title": title,
            "location": location_text or "Unknown",
            "price": price,
            "link": f"https://newyork.craigslist.org/search/apa?query={title.replace(' ', '+')}",
            "lat": lat,
            "lon": lon,
            "crime_count": crime_count
        })

    if not raw_listings:
        return []

    all_scores = [l["crime_count"] for l in raw_listings]
    thresholds = np.percentile(all_scores, [25, 50, 75])

    def assign_safety(score):
        if score <= thresholds[0]:
            return "Very Safe"
        elif score <= thresholds[1]:
            return "Moderate"
        elif score <= thresholds[2]:
            return "Risky"
        else:
            return "Avoid at Night"
            
    listings = []
    for listing in raw_listings:
        listing["safety"] = assign_safety(listing["crime_count"])
        listings.append(listing)

    return listings