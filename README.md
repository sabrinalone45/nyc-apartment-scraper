# NYC Apartment Scraper
This project is a web-based tool that scrapes real-time NYC apartment listings from Craigslist and analyzes their neighborhood safety based on recent crime data from the NYC Open Data portal. The goal is to help users make informed rental decisions by providing safety labels and map visualizations based on crime proximity.

# Project Overview
Renting in New York City can be overwhelming, especially when safety is a concern. This project uses a combination of real apartment listing data and publicly available crime data to evaluate the safety of rental locations.

# The project includes:
- A scraper that collects Craigslist apartment listings and geocodes them.
- A crime data fetcher that pulls recent NYC incident reports via the Socrata API.
- A safety scoring system based on proximity of listings to crime locations.
- A Flask web app that displays listings with safety labels and a map view.

# Features
Safety Assessment:
- Fetches 10,000 recent NYC crime reports (last 12 months).
- Calculates the number of crimes within 0.25 miles of each listing.
- Labels listings as Very Safe, Moderate, Risky, or Avoid at Night using scoring thresholds.
  
Craigslist Listing Scraper:
- Extracts apartment title, price, location, and posting link.
- Geocodes locations using OpenStreetMap's Nominatim API.
- Caches geocoding results to speed up future runs.
  
Interactive Web App:
- Built with Flask and Folium for map visualization.
- Filter listings by safety level or borough.
- Heatmap of riskier locations based on apartment geocoordinates.

# Known Issues and Future Improvements
Inconsistent Safety Labels:
- Safety labels may vary across refreshes due to dynamic listings and localized percentile scoring.
- Future fix: Use borough-level scoring and static thresholds instead of batch-based percentiles.

Price Showing as “N/A”:
- Some listings fail to match price data from the HTML card.
- Future fix: Improve mapping logic between parsed title text and card data or fallback to more robust scraping methods.

Map Labeling Accuracy:
- Markers on the map sometimes don’t match current filter selections or safety labels.
- Future fix: Ensure listings and map filters share consistent data and logic.

Borough Filter Display Bug:
- Although the filter works, the dropdown always reverts to “All Boroughs” upon reload.
- Future fix: Persist filter selection state in the template view.

Limited Listing Locations:
- Currently, only a small sample of NYC neighborhoods are shown.
- Future fix: Broaden the search radius or paginate to show more listings.

# Usage Instructions
Run the App Locally
Clone the repository

git clone https://github.com/sabrinalone45/nyc-apartment-scraper.git  

cd nyc-apartment-scraper

Install dependencies

pip install -r requirements.txt

Run the app

python app.py

View in browser

Navigate to http://127.0.0.1:5000/ in your browser.

File Structure
nyc-apartment-scraper/
├── app.py                  # Flask web server
├── scraper.py              # Listing scraper and crime data fetcher
├── templates/
│   ├── index.html          # Main listing page
│   └── map.html            # Map view page
├── static/
│   └── map.html            # Generated folium map
├── geocache.csv            # Stores cached geocoding results
├── requirements.txt        # Python package dependencies
└── README.md

# Technologies Used
- Python (Requests, Pandas, NumPy)
- BeautifulSoup for HTML parsing
- Socrata API for NYC crime data
- Geopy and OpenStreetMap Nominatim for geocoding
- Flask for the web application
- Folium for map rendering and heatmaps

# License
This project is for educational and demonstration purposes only.

# Author
Sabrina Lone, Mathematics and Computer Science Undergraduate Student
