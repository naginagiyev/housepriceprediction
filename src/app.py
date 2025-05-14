import folium
import streamlit as st
from predict import Predictor
from streamlit_folium import st_folium

model_path = "./models/model.pkl"
predictor = Predictor(model_path)

st.set_page_config(layout="wide", page_title="Flat Price Prediction")

if 'map_lat' not in st.session_state:
    st.session_state['map_lat'] = ""
if 'map_lon' not in st.session_state:
    st.session_state['map_lon'] = ""

def make_prediction():
    has_error = False

    try:
        lat_value = float(st.session_state.get("lat_input", ""))
        if not (40 <= lat_value <= 40.65):
            st.error(f"Latitude {lat_value} seems outside the expected range for Baku (40 - 40.65).")
            has_error = True
    except ValueError:
        st.error("Latitude must be a valid number.")
        has_error = True

    try:
        lon_value = float(st.session_state.get("lon_input", ""))
        if not (49.25 <= lon_value <= 50.5):
            st.error(f"Longitude {lon_value} seems outside the expected range for Baku (49.25 - 50.5).")
            has_error = True
    except ValueError:
        st.error("Longitude must be a valid number.")
        has_error = True

    try:
        area_value = float(st.session_state.get("area", ""))
        if area_value <= 0:
            st.error("Area must be greater than 0.")
            has_error = True
    except ValueError:
        st.error("Area must be a valid number.")
        has_error = True

    try:
        rooms_value = int(st.session_state.get("rooms", ""))
        if rooms_value <= 0:
            st.error("Rooms must be greater than 0.")
            has_error = True
    except ValueError:
        st.error("Rooms must be a valid integer.")
        has_error = True

    try:
        floor_value = int(st.session_state.get("floor", ""))
        if floor_value <= 0:
            st.error("Floor must be greater than 0.")
            has_error = True
    except ValueError:
        st.error("Floor must be a valid integer.")
        has_error = True

    try:
        max_floor_value = int(st.session_state.get("max_floor", ""))
        if max_floor_value <= 0:
            st.error("Max Floor must be greater than 0.")
            has_error = True
        elif floor_value and max_floor_value < floor_value:
            st.error("Max Floor must be greater than or equal to Floor.")
            has_error = True
    except ValueError:
        st.error("Max Floor must be a valid integer.")
        has_error = True

    if not has_error:
        input_data = {
            'address': st.session_state['district'],
            'latitude': lat_value,
            'longitude': lon_value,
            'area': area_value,
            'rooms': rooms_value,
            'floor': floor_value,
            'max_floor': max_floor_value,
            'category': st.session_state['category'],
            'repaired': st.session_state['repaired']
        }
        
        predicted_price = predictor.predict(input_data)

        lower_bound = round(predicted_price * (1 - 10 / 100))
        upper_bound = round(predicted_price * (1 + 10 / 100))

        st.success(f"💸 Qiymət: {round(predicted_price):,} AZN")
        st.success(f"📉 Təxmin edilən aralıq: {lower_bound:,} – {upper_bound:,} AZN")

col1, col2 = st.columns([4, 2])

with col1:
    st.markdown("<h1 style='text-align: left; font-size: 2.5em; margin-bottom: 0.25em;'>Model Inference</h1>", unsafe_allow_html=True)
    
    default_lat = st.session_state.get('map_lat', '')
    default_lon = st.session_state.get('map_lon', '')
    
    lat_col, lon_col = st.columns(2)
    latitude = lat_col.text_input("Latitude", value=default_lat, key="lat_input")
    longitude = lon_col.text_input("Longitude", value=default_lon, key="lon_input")

    district_options = sorted([
        "Nəriman Nərimanov M.", "Əhmədli M.", "Neftçilər M.", "8 Noyabr M.", "Yeni Günəşli Q.",
        "Qaraçuxur Q.", "Elmlər Akademiyası M.", "Memar Əcəmi M.", "Masazır Q.", "Nardaran Q.",
        "Həzi Aslanov M.", "Gənclik M.", "Sahil M.", "Şah İsmayıl Xətai M.", "28 May M.",
        "8-ci Mikrorayon Q.", "Xalqlar Dostluğu M.", "Xətai R.", "Nəsimi M.", "Dərnəgül M.",
        "Biləcəri Q.", "Binəqədi Q.", "İnşaatçılar M.", "Nərimanov R.", "Yeni Yasamal Q.",
        "Qara Qarayev M.", "Nəsimi R.", "Həzi Aslanov Q.", "Yasamal R.", "Azadlıq Prospekti M.",
        "Səbail R.", "Nizami M.", "Yasamal Q.", "Əhmədli Q.", "İçəri Şəhər M.", "Ağ Şəhər Q.",
        "Badamdar Q.", "Bayıl Q.", "20 Yanvar M.", "Nizami R.", "Bakıxanov Q.", "Avtovağzal M.",
        "Şıxov Q.", "Günəşli Q.", "Massiv A Q.", "Məmmədli Q.", "Köhnə Günəşli Q.", "Binəqədi R.",
        "Sabunçu R.", "9-cu Mikrorayon Q.", "Hövsan Q.", "Abşeron R.", "Koroğlu M.",
        "3-cü Mikrorayon Q.", "6-cı Mikrorayon Q.", "8-ci Kilometr Q.", "Buzovna Q.",
        "5-ci Mikrorayon Q.", "Əmircan Q.", "Zığ Q.", "Xutor Q.", "7-ci Mikrorayon Q.",
        "Lökbatan Q.", "Ceyranbatan Q.", "Mərdəkan Q.", "Massiv D Q.", "Kubinka Q.",
        "Müşfiqabad Q.", "Bakmil M.", "Binə Q.", "Suraxanı R.", "Saray Q.", "Xəzər R.",
        "4-cü Mikrorayon Q.", "20-ci Sahə Q.", "Mehdiabad Q.", "Suraxanı Q.", "Massiv V Q.",
        "Xocəsən Q.", "Massiv G Q.", "Böyükşor Q.", "M.Ə.Rəsulzadə Q.", "NZS Q.", "Xocəsən M.",
        "Sulutəpə Q.", "Yeni Suraxanı Q.", "Ulduz M.", "Bibiheybət Q.", "Massiv B Q.",
        "Yeni Ramana Q.", "1-ci Mikrorayon Q.", "Novxanı Q.", "Sabunçu Q.", "Şüvəlan Q.",
        "Maştağa Q.", "Ramana Q.", "Görədil Q.", "Bülbülə Q.", "Qaradağ R.", "Sahil Q.",
        "Keşlə Q.", "Zabrat Q.", "Xırdalan", "2-ci Alatava Q.", "Pirallahı R.",
        "Hökməli Q.", "28 May Q.", "2-ci Mikrorayon Q."
    ])
    district = st.selectbox("District", options=district_options, key="district")

    rooms_col, area_col = st.columns(2)
    rooms = rooms_col.text_input("Rooms", key="rooms")
    area = area_col.text_input("Area", key="area")

    floor_col, max_floor_col = st.columns(2)
    floor = floor_col.text_input("Floor", key="floor")
    max_floor = max_floor_col.text_input("Max Floor", key="max_floor")

    category_col, situation_col = st.columns(2)
    category_selection = category_col.radio("Category", options=["Old Building", "New Building"], horizontal=True)
    st.session_state["category"] = 0 if category_selection == "Old Building" else 1

    situation_selection = situation_col.radio("Situation", options=["Not Repaired", "Repaired"], horizontal=True)
    st.session_state["repaired"] = 0 if situation_selection == "Not Repaired" else 1

    if st.button("🚀 Predict", use_container_width=True):
        make_prediction()

with col2:
    st.markdown("<div style='margin-top: 64px'></div>", unsafe_allow_html=True)
    st.subheader("🗺️ Map")
    m = folium.Map(location=[40.4093, 49.8671], zoom_start=10, tiles="OpenStreetMap")
    m.add_child(folium.LatLngPopup())

    map_data = st_folium(m, width=360, height=360)

    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]

        if lat != st.session_state.get('map_lat') or lon != st.session_state.get('map_lon'):
            st.session_state['map_lat'] = lat
            st.session_state['map_lon'] = lon
            st.rerun()