from flask import Flask, render_template, request
from scraper import scrape_apartments
import folium

app = Flask(__name__)

@app.route("/")
def home():
    filter_by = request.args.get("filter", None)
    borough = request.args.get("borough", "").lower()

    listings = scrape_apartments()

    if filter_by:
        listings = [l for l in listings if l["safety"] == filter_by]

    if borough:
        listings = [l for l in listings if borough in l["location"].lower()]

    return render_template("index.html", listings=listings, filter_by=filter_by, borough=borough)

@app.route("/map")
def map_view():
    listings = scrape_apartments()
    print(f"Total listings loaded for map: {len(listings)}")

    m = folium.Map(location=[40.75, -73.97], zoom_start=12)

    for listing in listings:
        # Safely get lat/lon
        lat = listing.get("lat")
        lon = listing.get("lon")

        # Skip if missing
        if lat is None or lon is None:
            print(f"Skipping listing (no coordinates): {listing['title']}")
            continue

        print(f"Placing pin: {listing['title']} at ({lat}, {lon})")

        # Marker color by safety
        color = (
            "green" if listing["safety"] == "Very Safe"
            else "orange" if listing["safety"] == "Moderate"
            else "red"
        )

        folium.Marker(
            location=[lat, lon],
            popup=f"<a href='{listing['link']}' target='_blank'>{listing['title']}</a><br>{listing['price']}<br>{listing['safety']}",
            icon=folium.Icon(color=color)
        ).add_to(m)

    from folium.plugins import HeatMap
    heat_data = [[l["lat"], l["lon"]] for l in listings if l["safety"] in ["Risky", "Avoid at Night"]]
    HeatMap(heat_data, radius=15).add_to(m)


    m.save("static/map.html")
    return render_template("map.html")

if __name__ == "__main__":
    app.run(debug=True)