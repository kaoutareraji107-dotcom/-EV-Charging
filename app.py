import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from streamlit_folium import st_folium
import folium
import sqlite3
from datetime import datetime
from engine import *

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------

st.set_page_config(
    page_title="EV Charging Smart Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# DATABASE
# ----------------------------------------------------

init_db()

# ----------------------------------------------------
# SESSION
# ----------------------------------------------------

defaults = {
    "registered": False,
    "first_name": "",
    "last_name": "",
    "email": "",
    "country": "Morocco",
    "city": "",
    "theme": "Dark",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ----------------------------------------------------
# CSS
# ----------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght=300;500;700&display=swap');

html, body, [class*="css"]{
font-family:Poppins;
}

.stApp{
background:linear-gradient(135deg, #0F172A, #111827, #1E293B);
color:white;
}

section[data-testid="stSidebar"]{
background:#111827;
border-right:1px solid #374151;
}

h1,h2,h3,h4{
color:#F472B6;
}

div[data-testid="stMetric"]{
background:#1E293B;
padding:20px;
border-radius:18px;
border:1px solid #374151;
box-shadow:0px 0px 20px rgba(255,255,255,.05);
}

.stButton>button{
background:#EC4899;
color:white;
border:none;
border-radius:15px;
padding:12px;
font-weight:bold;
width:100%;
}

.stButton>button:hover{
background:#DB2777;
}

input{
border-radius:12px !important;
}

div[data-baseweb="select"]{
border-radius:12px;
}

hr{
border:1px solid #374151;
}

.block-container{
padding-top:2rem;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# HEADER
# ----------------------------------------------------

st.markdown("""
<h1 style='text-align:center;font-size:42px;'>
⚡ EV Charging Smart Assistant
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center;color:#9CA3AF;font-size:18px;'>
Smart Charging • AI • Battery Analytics • Energy Saving
</div>
""", unsafe_allow_html=True)

st.write("")

# ----------------------------------------------------
# REGISTRATION PAGE OR MAIN APPLICATION
# ----------------------------------------------------

if not st.session_state.registered:
    st.markdown("## 👤 Registration")

    with st.form("register"):
        c1, c2 = st.columns(2)
        with c1:
            first = st.text_input("First Name")
            last = st.text_input("Last Name")
            email = st.text_input("Email")
        with c2:
            country = st.text_input("Country", value="Morocco")
            city = st.text_input("City")

        agree = st.checkbox("I agree to save my information")
        register = st.form_submit_button("Create Account")

        if register:
            if not agree:
                st.error("Please accept the terms.")
            elif "" in [first, last, email, city]:
                st.warning("Please fill all fields.")
            else:
                save_user_data(first, last, email, country, city)

                st.session_state.registered = True
                st.session_state.first_name = first
                st.session_state.last_name = last
                st.session_state.email = email
                st.session_state.country = country
                st.session_state.city = city

                st.success("Registration completed successfully.")
                st.rerun()
                
    st.stop()

else:
    # ============================================================
    # MAIN APPLICATION
    # ============================================================

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3202/3202926.png", width=120)

        st.markdown(
            f"""
            ### Welcome
            **{st.session_state.first_name} {st.session_state.last_name}**

            📧 {st.session_state.email}
            📍 {st.session_state.city}
            """
        )

        st.write("---")

        selected = option_menu(
            menu_title="Navigation",
            options=["Dashboard", "EV Calculator", "Charging Stations", "History"],
            icons=["speedometer2", "battery-charging", "geo-alt-fill", "clock-history"],
            menu_icon="ev-front",
            default_index=0,
            styles={
                "container": {"padding": "0px", "background-color": "#111827"},
                "icon": {"color": "#F472B6", "font-size": "18px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "4px", "--hover-color": "#1E293B"},
                "nav-link-selected": {"background-color": "#EC4899"}
            }
        )

    # ============================================================
    # DASHBOARD
    # ============================================================
    if selected == "Dashboard":
        st.title("📊 Dashboard")
        st.write("")

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Users", "152", "+12")
        with c2: st.metric("Calculations", "489", "+28")
        with c3: st.metric("Money Saved", "18,250 DH", "+920 DH")
        with c4: st.metric("CO₂ Saved", "4.8 Tons", "+120 Kg")

        st.write("")
        left, right = st.columns([2, 1])

        with left:
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
            savings = [120, 180, 260, 300, 420, 510, 690, 830]
            df = pd.DataFrame({"Month": months, "Savings": savings})
            fig = px.line(df, x="Month", y="Savings", markers=True, title="Monthly Savings")
            fig.update_layout(template="plotly_dark", height=420)
            st.plotly_chart(fig, use_container_width=True)

        with right:
            battery = 92
            fig2 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=battery,
                title={"text": "Battery Health"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "lime"},
                    "steps": [
                        {"range": [0, 40], "color": "red"},
                        {"range": [40, 70], "color": "orange"},
                        {"range": [70, 100], "color": "green"}
                    ]
                }
            ))
            fig2.update_layout(template="plotly_dark", height=420)
            st.plotly_chart(fig2, use_container_width=True)

        st.write("")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("### 🔋 Battery\n\nBattery Status\n\nExcellent\n\nHealth : 92%\n\nTemperature : 28°C")
        with col2:
            st.success("### 💰 Energy\n\nBest Charging Time\n\n22:00 → 06:00\n\nEstimated Saving\n\n35 DH")
        with col3:
            st.warning("### ⚡ AI Recommendation\n\nCharge after 10 PM\n\nAvoid charging to 100%\n\nKeep battery between\n\n20% and 80%")

    # ============================================================
    # EV CALCULATOR
    # ============================================================
    elif selected == "EV Calculator":
        st.title("⚡ EV Savings Calculator")
        st.write("Compare your fuel car with an electric vehicle.")

        col1, col2 = st.columns(2)
        with col1:
            fuel_price = st.number_input("Fuel Price (DH/L)", min_value=5.0, max_value=30.0, value=14.0, step=0.1)
            fuel_consumption = st.number_input("Fuel Consumption (L / 100 km)", min_value=1.0, max_value=20.0, value=6.5, step=0.1)
            monthly_distance = st.number_input("Monthly Distance (km)", min_value=100, max_value=10000, value=1200, step=100)
        with col2:
            electricity_price = st.number_input("Electricity Price (DH / kWh)", min_value=0.50, max_value=5.00, value=1.40, step=0.05)
            ev_consumption = st.number_input("EV Consumption (kWh / 100 km)", min_value=5.0, max_value=40.0, value=16.0, step=0.5)
            battery_capacity = st.number_input("Battery Capacity (kWh)", min_value=20, max_value=150, value=60)

        st.write("")

        calculate_clicked = st.button("Calculate Savings")

        if calculate_clicked:
            result = calculate_ev_savings(fuel_price, fuel_consumption, electricity_price, ev_consumption, monthly_distance)
            st.session_state.last_result = result
            save_calculation(
                st.session_state.email,
                fuel_price,
                fuel_consumption,
                electricity_price,
                ev_consumption,
                monthly_distance,
                result
            )

        if "last_result" in st.session_state:
            result = st.session_state.last_result
            st.success("Calculation completed successfully!")

            m1, m2, m3, m4 = st.columns(4)
            with m1: st.metric("Fuel Cost", f"{result['fuel_cost']:.2f} DH")
            with m2: st.metric("EV Cost", f"{result['ev_cost']:.2f} DH")
            with m3: st.metric("Monthly Saving", f"{result['monthly_saving']:.2f} DH")
            with m4: st.metric("Yearly Saving", f"{result['yearly_saving']:.2f} DH")

            st.write("---")
            c1, c2 = st.columns(2)
            with c1:
                labels = ["Fuel Cost", "EV Cost"]
                values = [result["fuel_cost"], result["ev_cost"]]
                fig = px.bar(x=labels, y=values, text=values, title="Monthly Cost Comparison")
                fig.update_layout(template="plotly_dark", height=450)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                fig2 = px.pie(names=["Savings", "EV Cost"], values=[result["monthly_saving"], result["ev_cost"]], hole=0.55, title="Monthly Distribution")
                fig2.update_layout(template="plotly_dark", height=450)
                st.plotly_chart(fig2, use_container_width=True)

            st.write("---")
            co2 = result["co2_saved"]
            st.success(f"🌱 Estimated CO₂ reduction: {co2:.1f} kg/month")

            battery_range = battery_capacity / ev_consumption * 100
            st.info(f"🔋 Estimated driving range: {battery_range:.0f} km")

            if result["monthly_saving"] > 500:
                recommendation = """
### 🤖 AI Recommendation
✅ Switching to an EV is highly beneficial.
• Excellent monthly savings.
• Lower maintenance costs.
• Significant CO₂ reduction.
• Consider charging between 22:00 and 06:00 for additional savings.
"""
            else:
                recommendation = """
### 🤖 AI Recommendation
The EV is still more economical than a fuel vehicle.
You can increase your savings by:
• Charging during off-peak hours.
• Maintaining tire pressure.
• Driving smoothly.
• Avoiding unnecessary battery charging to 100%.
"""
            st.markdown(recommendation)
            st.write("---")
            
            pdf_data = generate_pdf_report(
                st.session_state.first_name,
                st.session_state.last_name,
                st.session_state.email,
                st.session_state.city,
                result
            )

            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_data,
                file_name=f"EV_Report_{st.session_state.first_name}.pdf",
                mime="application/pdf"
            )

    # ============================================================
    # CHARGING STATIONS (هنا زدت ليك الخريطة اللي كانت ناقصاك)
    # ============================================================
    elif selected == "Charging Stations":
        st.title("🗺️ EV Charging Stations in Morocco")
        st.write("اكتشف محطات الشحن الكهربائي المتوفرة في مختلف المدن المغربية.")

        stations_data = [
            {"name": "Tesla Supercharger - Agadir", "lat": 30.3919, "lon": -9.5971, "city": "Agadir", "type": "Tesla Fast Charger"},
            {"name": "Porsche Destination Charging - Agadir", "lat": 30.4080, "lon": -9.5991, "city": "Agadir", "type": "Type 2 (11kW)"},
            {"name": "TotalEnergies Station - Chichaoua", "lat": 31.4871, "lon": -8.6550, "city": "Chichaoua", "type": "CCS Combo 2"},
            {"name": "Fast Charger TotalEnergies - Casablanca", "lat": 33.5731, "lon": -7.5898, "city": "Casablanca", "type": "Fast Charger 50kW"},
            {"name": "Afriquia EV Station - Rabat Road", "lat": 33.9716, "lon": -6.8498, "city": "Rabat", "type": "Type 2 / CCS"},
            {"name": "Marrakech Plaza EV Charger", "lat": 31.6295, "lon": -7.9811, "city": "Marrakech", "type": "Type 2 (22kW)"},
            {"name": "Tanger Med EV Charging", "lat": 35.7595, "lon": -5.8340, "city": "Tangier", "type": "Fast Charger"}
        ]

        df_stations = pd.DataFrame(stations_data)
        cities = ["الكل"] + list(df_stations["city"].unique())
        selected_city = st.selectbox("📍 فلتر حسب المدينة:", cities)

        if selected_city != "الكل":
            df_filtered = df_stations[df_stations["city"] == selected_city]
        else:
            df_filtered = df_stations

        # إنشاء الخريطة متمركزة على المغرب بديكور مظلم متناسق
        m = folium.Map(location=[31.7917, -7.0926], zoom_start=6, tiles="CartoDB dark_matter")

        for index, row in df_filtered.iterrows():
            popup_text = f"<b>{row['name']}</b><br>City: {row['city']}<br>Type: {row['type']}"
            folium.Marker(
                location=[row["lat"], row["lon"]],
                popup=popup_text,
                tooltip=row["name"],
                icon=folium.Icon(color="pink", icon="flash", prefix="fa")
            ).add_to(m)

        st_folium(m, width="100%", height=500)
        
        st.write("")
        st.markdown("### 📋 تفاصيل المحطات المتوفرة:")
        st.dataframe(df_filtered[["name", "city", "type"]], use_container_width=True)

    # ============================================================
    # HISTORY (وهنا صفحة الأرشيف نتاع الحسابات)
    # ============================================================
    elif selected == "History":
        st.title("⏳ Calculation History")
        st.write("أرشيف جميع العمليات الحسابية التي قمت بها سابقاً.")
        
        df_history = get_history(st.session_state.email)
        if not df_history.empty:
            st.dataframe(df_history, use_container_width=True)
        else:
            st.info("No calculations found in your history yet.")
