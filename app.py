import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# ----------------------------------
#   Page config
# ----------------------------------
st.set_page_config(
    page_title="TaxiFare Predictor 3000",
    page_icon="🚕",
    layout="centered",
)

# ----------------------------------
#   Title
# ----------------------------------
st.title("🚕 TaxiFare Predictor 3000")

st.markdown("""

Get a prediction of your taxi fare!
""")

# ----------------------------------
#   GEOCODING function ..merci stack overflow
# ----------------------------------
def geocode(address: str):
    """
    geocoding using Nominatim (OpenStreetMap).
    Returns (lat, lon) or None if not found.
    """
    if not address:
        return None

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "taxifare-streamlit-demo"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()
        if not data:
            return None
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return lat, lon
    except Exception:
        return None


# ----------------------------------
#   Inputs: addresses
# ----------------------------------
st.subheader("📍 Pickup & Dropoff")

col_pick, col_drop = st.columns(2)

with col_pick:
    pickup_address = st.text_input(
        "Pickup address",
        value="Times Square, New York"
    )

with col_drop:
    dropoff_address = st.text_input(
        "Dropoff address",
        value="JFK Airport, New York"
    )

# ----------------------------------
#   Inputs: date / time / passengers
# ----------------------------------
st.subheader("🕒 Schedule & passengers")

col_date, col_time, col_pass = st.columns([2, 2, 1])

with col_date:
    pickup_date = st.date_input("Pickup date")

with col_time:
    pickup_time = st.time_input("Pickup time")

with col_pass:
    passenger_count = st.number_input(
        "Passengers",
        min_value=1,
        max_value=8,
        value=1
    )

# Combine into datetime
pickup_datetime = datetime.combine(pickup_date, pickup_time)

# ----------------------------------
#   API URL (replace by your own if needed)
# ----------------------------------
API_URL = "https://taxifare.lewagon.ai/predict"

# ----------------------------------
#   Prediction
# ----------------------------------
st.markdown("---")
if st.button("🔮 Predict fare"):

    # 1) Geocode pickup & dropoff
    pickup_coords = geocode(pickup_address)
    dropoff_coords = geocode(dropoff_address)

    if not pickup_coords:
        st.error("Could not locate the pickup address. Try to be more precise.")
    elif not dropoff_coords:
        st.error("Could not locate the dropoff address. Try to be more precise.")
    else:
        pickup_lat, pickup_lon = pickup_coords
        dropoff_lat, dropoff_lon = dropoff_coords

        # 2) Params for API
        params = {
            "pickup_datetime": pickup_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "pickup_longitude": pickup_lon,
            "pickup_latitude": pickup_lat,
            "dropoff_longitude": dropoff_lon,
            "dropoff_latitude": dropoff_lat,
            "passenger_count": passenger_count,
        }

        # Call prediction API
        response = requests.get(API_URL, params=params)

        if response.status_code == 200:
            fare = response.json().get("fare")
            st.subheader("💰 Estimated fare")
            st.success(f"${fare:.2f}")
        else:
            st.error("❌ API error — please check the server or your parameters.")
            st.stop()

        # MAP rendering:

        st.markdown("### Route preview")

        route_df = pd.DataFrame(
            {'latitude': [pickup_lat, dropoff_lat],
             'longitude':[pickup_lon, dropoff_lon],
             'color': ["#4DF527", '#FF0000' ]}
        )

        st.caption("🟢 Pickup (origin)   |   🔴 Destination (dropoff)")
        st.map(route_df, zoom=11, size=50, color="color", use_container_width=True)
