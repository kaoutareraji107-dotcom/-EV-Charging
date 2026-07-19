import sqlite3
import pandas as pd
from datetime import datetime
from io import BytesIO 

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

# =====================================================
# DATABASE NAME
# =====================================================
DB_NAME = "database.db"

# =====================================================
# CONNECT DATABASE
# =====================================================
def connect_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

# =====================================================
# CREATE TABLES
# =====================================================
def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        email TEXT UNIQUE,
        country TEXT,
        city TEXT,
        created_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calculations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        fuel_price REAL,
        fuel_consumption REAL,
        electricity_price REAL,
        ev_consumption REAL,
        distance REAL,
        fuel_cost REAL,
        ev_cost REAL,
        monthly_saving REAL,
        yearly_saving REAL,
        co2_saved REAL,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

# =====================================================
# SAVE USER
# =====================================================
def save_user_data(first_name, last_name, email, country, city):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT OR IGNORE INTO users(
            first_name,
            last_name,
            email,
            country,
            city,
            created_at
        )
        VALUES(?,?,?,?,?,?)
        """, (
            first_name,
            last_name,
            email,
            country,
            city,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))
        conn.commit()
    finally:
        conn.close()

# =====================================================
# GET ALL USERS
# =====================================================
def get_all_users():
    conn = connect_db()
    df = pd.read_sql("SELECT * FROM users", conn)
    conn.close()
    return df

# =====================================================
# EV SAVINGS CALCULATOR
# =====================================================
def calculate_ev_savings(fuel_price, fuel_consumption, electricity_price, ev_consumption, monthly_distance):
    fuel_cost = (monthly_distance / 100) * fuel_consumption * fuel_price
    ev_cost = (monthly_distance / 100) * ev_consumption * electricity_price
    
    monthly_saving = fuel_cost - ev_cost
    yearly_saving = monthly_saving * 12
    co2_saved = (monthly_distance / 100) * fuel_consumption * 2.31

    return {
        "fuel_cost": round(fuel_cost, 2),
        "ev_cost": round(ev_cost, 2),
        "monthly_saving": round(monthly_saving, 2),
        "yearly_saving": round(yearly_saving, 2),
        "co2_saved": round(co2_saved, 2)
    }

# =====================================================
# SAVE CALCULATION
# =====================================================
def save_calculation(email, fuel_price, fuel_consumption, electricity_price, ev_consumption, distance, result):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO calculations(
        email,
        fuel_price,
        fuel_consumption,
        electricity_price,
        ev_consumption,
        distance,
        fuel_cost,
        ev_cost,
        monthly_saving,
        yearly_saving,
        co2_saved,
        created_at
    )
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        email,
        fuel_price,
        fuel_consumption,
        electricity_price,
        ev_consumption,
        distance,
        result["fuel_cost"],
        result["ev_cost"],
        result["monthly_saving"],
        result["yearly_saving"],
        result["co2_saved"],
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()
    conn.close()

# =====================================================
# HISTORY
# =====================================================
def get_history(email):
    conn = connect_db()
    df = pd.read_sql(
        """
        SELECT *
        FROM calculations
        WHERE email=?
        ORDER BY id DESC
        """,
        conn,
        params=(email,)
    )
    conn.close()
    return df

# =====================================================
# PDF REPORT
# =====================================================
def generate_pdf_report(first_name, last_name, email, city, result):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph(
        "<b><font size=22 color='darkblue'>EV Charging Smart Assistant</font></b>",
        styles["Title"]
    )
    elements.append(title)
    elements.append(Spacer(1, 20))

    subtitle = Paragraph(
        "<b>Smart Energy Report</b>",
        styles["Heading2"]
    )
    elements.append(subtitle)
    elements.append(Spacer(1, 15))

    info = [
        ["Name", f"{first_name} {last_name}"],
        ["Email", email],
        ["City", city]
    ]

    table = Table(info)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.lightblue),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 25))

    elements.append(
        Paragraph(
            "<b>Calculation Results</b>",
            styles["Heading2"]
        )
    )

    result_table = [
        ["Fuel Cost", f"{result['fuel_cost']} DH"],
        ["EV Cost", f"{result['ev_cost']} DH"],
        ["Monthly Saving", f"{result['monthly_saving']} DH"],
        ["Yearly Saving", f"{result['yearly_saving']} DH"],
        ["CO₂ Saved", f"{result['co2_saved']} Kg"]
    ]

    t = Table(result_table)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgreen),
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    recommendation = Paragraph(
        "<b>AI Recommendation</b><br/>"
        "Charge your EV during off-peak hours (22:00 - 06:00).<br/>"
        "Keep battery between 20% and 80% for longer battery life.",
        styles["BodyText"]
    )
    elements.append(recommendation)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf
