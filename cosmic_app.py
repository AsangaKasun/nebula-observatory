import streamlit as st
import streamlit.components.v1 as components
import feedparser
from google import genai
from google.genai import types
from PIL import Image
import urllib.request
import json
import asyncio
import edge_tts
import hashlib
import re
import os
import base64
import requests


def get_live_weather(lat=51.70, lon=-0.03):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        res = requests.get(url, timeout=5).json()
        cw = res["current_weather"]
        return f"{cw['temperature']}°C (Wind: {cw['windspeed']} km/h)"
    except Exception:
        return "Unavailable"


# ==========================================
# 1. PAGE SETUP & LOCAL FOLDER
# ==========================================
st.set_page_config(
    page_title="NEBULA | Deep Space & UAP Observatory",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOCAL_VAULT_DIR = "pentagon_videos"
os.makedirs(LOCAL_VAULT_DIR, exist_ok=True)

st.markdown("""
<style>
/* Sidebar Mic එක කුඩා රවුම් බොත්තමක් පමණක් කිරීම */
[data-testid="stSidebar"] [data-testid="stAudioInput"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    margin-top: -8px !important;
}
[data-testid="stSidebar"] [data-testid="stAudioInput"] > div {
    background: radial-gradient(circle, #0f172a 0%, #040608 100%) !important;
    border: 1.5px solid #38bdf8 !important;
    border-radius: 50px !important;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.45) !important;
    padding: 4px 14px !important;
    width: fit-content !important;
    max-width: 140px !important;
    justify-content: center !important;
}
[data-testid="stSidebar"] [data-testid="stAudioInput"] canvas,
[data-testid="stSidebar"] [data-testid="stAudioInput"] [data-testid="stAudioInputWaveform"],
[data-testid="stSidebar"] [data-testid="stAudioInput"] span,
[data-testid="stSidebar"] [data-testid="stAudioInput"] button:nth-of-type(n+2) {
    display: none !important;
}
[data-testid="stSidebar"] [data-testid="stAudioInput"] button:first-of-type {
    color: #38bdf8 !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CLEAN THEME (ORBITRON + INTER + VERTICAL HUD BUBBLE TABS)
# ==========================================
# ==========================================
# 2. CLEAN THEME (ORBITRON + INTER + VERTICAL HUD BUBBLE TABS)
# ==========================================
st.markdown("""
<style> @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Orbitron:wght@600;700;900&display=swap'); .stApp { background-color: #040608; background-image: linear-gradient(180deg, rgba(4, 6, 8, 0.74) 0%, rgba(4, 6, 8, 0.86) 55%, rgba(4, 6, 8, 0.96) 100%), radial-gradient(circle at 65% 30%, rgba(31, 99, 155, 0.22) 0%, transparent 55%), url("https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=2072&q=85"); background-size: cover; background-position: center top; background-attachment: fixed; color: #E2E8F0 !important; font-family: 'Inter', sans-serif; } header[data-testid="stHeader"] { background-color: rgba(4, 6, 8, 0.65) !important; backdrop-filter: blur(10px); border-bottom: 1px solid rgba(76, 154, 187, 0.18); } .block-container { padding-top: 2.2rem !important; } h1, h2, h3, h4, h1 *, h2 *, h3 *, h4 *, [data-testid="stHeading"] * { font-family: 'Orbitron', sans-serif !important; letter-spacing: 1px !important; color: #FFFFFF !important; } [data-testid="stSidebar"] { background: rgba(4, 6, 8, 0.92) !important; backdrop-filter: blur(16px); border-right: 1px solid rgba(76, 154, 187, 0.22); } [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { font-family: 'Inter', sans-serif !important; color: #E2E8F0 !important; } [data-testid="stIconMaterial"] { font-family: 'Material Symbols Rounded' !important; } [data-testid="stSidebar"] div[data-baseweb="select"] * { color: #040608 !important; } .sidebar-nebula-banner { font-family: 'Orbitron', sans-serif !important; font-size: 22px !important; font-weight: 900 !important; color: #39ff14 !important; letter-spacing: 3.5px; text-align: center; padding: 10px 8px; margin-bottom: 12px; background: linear-gradient(135deg, rgba(18, 53, 88, 0.35) 0%, rgba(4, 6, 8, 0.85) 100%); border: 1px solid rgba(57, 255, 20, 0.45); border-bottom: 2px solid #39ff14; border-radius: 8px; text-shadow: 0 0 12px rgba(57, 255, 20, 0.85), 0 0 24px rgba(57, 255, 20, 0.45); box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5), inset 0 0 10px rgba(57, 255, 20, 0.15); } .main-hero-header { font-family: 'Orbitron', sans-serif !important; font-size: 21px !important; font-weight: 700 !important; color: #E2E8F0 !important; letter-spacing: 2.5px; text-transform: uppercase; padding: 6px 2px 12px 2px; margin-bottom: 14px; background: transparent !important; border-bottom: 1px solid rgba(76, 154, 187, 0.35); text-shadow: 0 0 10px rgba(76, 154, 187, 0.35); } [data-testid="stMetric"] { background: linear-gradient(135deg, rgba(18, 53, 88, 0.38) 0%, rgba(4, 6, 8, 0.72) 100%) !important; backdrop-filter: blur(14px); border: 1px solid rgba(57, 255, 20, 0.3); border-left: 3px solid #39ff14; padding: 14px 18px; border-radius: 8px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45); transition: all 0.25s ease; } [data-testid="stMetric"]:hover { border-color: #39ff14; box-shadow: 0 0 18px rgba(57, 255, 20, 0.35); background: linear-gradient(135deg, rgba(31, 99, 155, 0.42) 0%, rgba(4, 6, 8, 0.78) 100%) !important; } [data-testid="stMetricLabel"] p { font-family: 'Orbitron', sans-serif !important; color: #AFC1CD !important; font-size: 11px !important; font-weight: 600 !important; letter-spacing: 1.2px; text-transform: uppercase; } [data-testid="stMetricValue"] div { font-family: 'Orbitron', sans-serif !important; color: #39ff14 !important; text-shadow: 0 0 10px rgba(57, 255, 20, 0.65); font-size: 17px !important; font-weight: 700 !important; letter-spacing: 1px; margin-top: 4px; } [data-testid="stMetricDelta"] { background-color: transparent !important; padding: 2px 0px !important; color: #39ff14 !important; } [data-testid="stMetricDelta"] > div { font-family: 'Orbitron', sans-serif !important; color: #39ff14 !important; text-shadow: 0 0 8px rgba(57, 255, 20, 0.5); font-size: 11px !important; font-weight: 600 !important; letter-spacing: 0.8px; } [data-testid="stMetricDelta"] svg { fill: #39ff14 !important; } .stButton > button { font-family: 'Inter', sans-serif !important; font-size: 14px !important; font-weight: 600 !important; background: rgba(18, 53, 88, 0.28) !important; color: #E2E8F0 !important; border: 1px solid rgba(175, 193, 205, 0.3) !important; border-radius: 6px !important; transition: all 0.22s ease !important; } .stButton > button:hover { background: rgba(31, 99, 155, 0.48) !important; border-color: #4C9ABB !important; box-shadow: 0 0 16px rgba(76, 154, 187, 0.45) !important; } div[data-testid="stHorizontalBlock"]:has(.nebula-nav-anchor) > div[data-testid="stColumn"]:first-child { padding-right: 0px !important; } div[data-testid="stHorizontalBlock"]:has(.nebula-nav-anchor) > div[data-testid="stColumn"]:first-child .stButton > button[kind="secondary"] { font-family: 'Orbitron', sans-serif !important; font-size: 12px !important; font-weight: 600 !important; letter-spacing: 0.6px !important; justify-content: flex-start !important; text-align: left !important; padding: 13px 16px !important; margin-bottom: 4px !important; background: linear-gradient(135deg, rgba(10, 18, 32, 0.78) 0%, rgba(4, 6, 8, 0.88) 100%) !important; color: #CBD5E1 !important; border: 1px solid rgba(76, 154, 187, 0.25) !important; border-left: 3px solid rgba(76, 154, 187, 0.45) !important; border-radius: 12px !important; } div[data-testid="stHorizontalBlock"]:has(.nebula-nav-anchor) > div[data-testid="stColumn"]:first-child .stButton > button[kind="secondary"]:hover { background: linear-gradient(90deg, rgba(31, 99, 155, 0.42) 0%, rgba(10, 18, 32, 0.9) 100%) !important; border-color: #38bdf8 !important; color: #FFFFFF !important; transform: translateX(3px); } div[data-testid="stHorizontalBlock"]:has(.nebula-nav-anchor) > div[data-testid="stColumn"]:first-child .stButton > button[kind="primary"] { font-family: 'Orbitron', sans-serif !important; font-size: 12.5px !important; font-weight: 700 !important; letter-spacing: 0.7px !important; justify-content: flex-start !important; text-align: left !important; padding: 15px 18px !important; margin-bottom: 4px !important; background: linear-gradient(90deg, rgba(56, 189, 248, 0.32) 0%, rgba(18, 53, 88, 0.92) 70%, rgba(12, 24, 44, 0.98) 100%) !important; color: #FFFFFF !important; border: 1.5px solid #38bdf8 !important; border-left: 5px solid #38bdf8 !important; border-radius: 16px 6px 6px 16px !important; box-shadow: 0 0 22px rgba(56, 189, 248, 0.45), inset 0 0 12px rgba(56, 189, 248, 0.25) !important; text-shadow: 0 0 10px rgba(56, 189, 248, 0.8) !important; } div[data-testid="stHorizontalBlock"]:has(.nebula-nav-anchor) > div[data-testid="stColumn"]:nth-child(2) [data-testid="stVerticalBlockBorderWrapper"] { background: linear-gradient(155deg, rgba(11, 21, 38, 0.86) 0%, rgba(4, 6, 8, 0.94) 100%) !important; backdrop-filter: blur(18px) !important; border: 1.5px solid rgba(56, 189, 248, 0.55) !important; border-top: 3px solid #38bdf8 !important; border-radius: 18px !important; padding: 24px 26px !important; min-height: 540px !important; box-shadow: 0 12px 36px rgba(0, 0, 0, 0.65), 0 0 28px rgba(56, 189, 248, 0.18), inset 0 0 24px rgba(18, 53, 88, 0.35) !important; } .active-bubble-header { display: flex; align-items: center; justify-content: space-between; background: linear-gradient(90deg, rgba(56, 189, 248, 0.22) 0%, rgba(18, 53, 88, 0.35) 60%, transparent 100%); border: 1px solid rgba(56, 189, 248, 0.4); border-left: 4px solid #38bdf8; border-radius: 10px; padding: 8px 14px; margin-bottom: 16px; } .active-bubble-title { font-family: 'Orbitron', sans-serif !important; font-size: 13px !important; font-weight: 700 !important; color: #38bdf8 !important; letter-spacing: 1.2px; text-shadow: 0 0 10px rgba(56, 189, 248, 0.6); } .active-bubble-pill { font-family: 'Orbitron', sans-serif !important; font-size: 10px !important; font-weight: 700 !important; color: #39ff14 !important; background: rgba(57, 255, 20, 0.12); border: 1px solid rgba(57, 255, 20, 0.45); padding: 3px 10px; border-radius: 20px; } div[data-testid="stHorizontalBlock"]:has(.nebula-nav-anchor) > div[data-testid="stColumn"]:nth-child(2) .stButton > button[kind="primary"] { background: linear-gradient(135deg, rgba(56, 189, 248, 0.35), rgba(18, 53, 88, 0.85)) !important; border: 1.5px solid #38bdf8 !important; color: #FFFFFF !important; box-shadow: 0 0 14px rgba(56, 189, 248, 0.4) !important; } .report-box { font-family: 'Inter', sans-serif !important; background: rgba(4, 6, 8, 0.82); backdrop-filter: blur(16px); border: 1px solid rgba(175, 193, 205, 0.2); border-left: 3px solid #4C9ABB; padding: 24px; border-radius: 10px; margin-top: 12px; color: #E2E8F0 !important; font-size: 15.5px; line-height: 1.85; } .pursue-banner { background: rgba(18, 53, 88, 0.28); border: 1px solid rgba(76, 154, 187, 0.35); border-radius: 8px; padding: 12px 16px; margin-bottom: 14px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 10px; } .dossier-card { background: linear-gradient(145deg, rgba(18, 53, 88, 0.35), rgba(4, 6, 8, 0.85)); backdrop-filter: blur(14px); border: 1px solid rgba(175, 193, 205, 0.22); border-top: 2px solid #4C9ABB; border-radius: 10px; padding: 20px; margin-bottom: 12px; } .dossier-badge { display: inline-block; font-family: 'Orbitron', sans-serif !important; font-size: 10px; font-weight: 700; color: #4C9ABB !important; border: 1px solid rgba(76, 154, 187, 0.5); background: rgba(18, 53, 88, 0.4); padding: 3px 9px; border-radius: 4px; margin-bottom: 8px; } .jetaudio-deck { background: linear-gradient(145deg, #0d1520, #040608); border: 1px solid rgba(76, 154, 187, 0.45); border-radius: 8px; padding: 10px; margin-bottom: 8px; } .jetaudio-brand { font-family: 'Orbitron', sans-serif !important; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; color: #AFC1CD !important; display: flex; justify-content: space-between; margin-bottom: 6px; } .vfd-screen { background-color: #020508; border: 1px solid #123558; border-radius: 4px; padding: 8px 10px; } .vfd-title { font-family: 'Orbitron', sans-serif !important; color: #4C9ABB !important; font-size: 11px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; } .vfd-meta { font-family: 'Inter', sans-serif !important; color: #94A3B8 !important; font-size: 11px; margin-top: 4px; display: flex; justify-content: space-between; } </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. GEMINI AI ENGINE & PENTAGON DATABASE
# ==========================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = ""

client = genai.Client(api_key=api_key)

models_to_try = [
    "gemini-3.1-flash-lite",
    "gemma-4-31b-it",
    "gemini-3.6-flash",
    "gemini-3.5-flash"
]

PENTAGON_BATCHES = {
    "Release 01": {
        "date": "MAY 8, 2026",
        "doc_bundle": "1.2 GB (160+ Records)",
        "vid_bundle": "1.3 GB",
        "agencies": ["DOW / DoD", "AARO"],
        "url": "https://www.war.gov/ufo/",
        "records": [
            {
                "id": "NAVAIR-FLIR1",
                "title": "USS Nimitz 'Tic-Tac' FLIR1 Targeting Pod Video (2004)",
                "agency": "DOW / DoD",
                "type": "Video",
                "video_url": "https://www.youtube.com/watch?v=6rWOtrke0HY",
                "detail": "Official ATFLIR infrared footage captured by Navy F/A-18F pilots off San Diego showing a wingless white oblong object executing instantaneous acceleration."
            },
            {
                "id": "NAVAIR-GIMBAL",
                "title": "East Coast 'GIMBAL' Rotating Aerial Object Video (2015)",
                "agency": "DOW / DoD",
                "type": "Video",
                "video_url": "https://www.youtube.com/watch?v=QKHg-dgKOHs",
                "detail": "Infrared sensor footage showing an anomalous craft flying against 120-knot winds and rotating mid-air with zero visible exhaust plume."
            },
            {
                "id": "NAVAIR-GOFAST",
                "title": "Atlantic 'GOFAST' High-Speed Low-Altitude Object Video (2015)",
                "agency": "DOW / DoD",
                "type": "Video",
                "video_url": "https://www.youtube.com/watch?v=wxVRg7LLaQA",
                "detail": "Raytheon AN/ASQ-228 ATFLIR lock on a cold, fast-moving spherical object skimming above the Atlantic Ocean surface."
            },
            {
                "id": "PURSUE-R01-DOC01",
                "title": "Historical Project Sign / Grudge & 1946–1963 Incident Summaries",
                "agency": "AARO",
                "type": "Document",
                "video_url": "",
                "detail": "Declassified Box 7 incident checklists, witness statements, and early Cold War aerospace defense reports."
            }
        ]
    },
    "Release 02": {
        "date": "MAY 22, 2026",
        "doc_bundle": "70.1 MB",
        "vid_bundle": "5.6 GB",
        "agencies": ["CIA", "DOW / DoD", "ODNI"],
        "url": "https://www.war.gov/ufo/",
        "records": [
            {
                "id": "AARO-EUCOM-IR",
                "title": "AARO Unresolved European Infrared Sensor Clips (PR-011 to PR-018)",
                "agency": "DOW / DoD",
                "type": "Video",
                "video_url": "https://www.youtube.com/watch?v=TCLKbR_jbkA",
                "detail": "Official infrared video clips submitted by U.S. European Command showing distinct thermal contrast objects moving across military targeting fields."
            },
            {
                "id": "AARO-ME-ORB",
                "title": "Middle East Metallic Spherical Orb (MQ-9 Reaper Sensor Video)",
                "agency": "DOW / DoD",
                "type": "Video",
                "video_url": "https://www.youtube.com/watch?v=4bGTkcoIq9k",
                "detail": "Declassified MQ-9 drone footage presented by AARO Director Dr. Sean Kirkpatrick showing an unresolved metallic sphere flying through an active conflict zone."
            },
            {
                "id": "PURSUE-R02-DOC01",
                "title": "CIA, Department of Energy (DOE) & ODNI Intelligence Assessments",
                "agency": "CIA",
                "type": "Document",
                "video_url": "",
                "detail": "Inter-agency intelligence memoranda evaluating anomalous aerial objects near sensitive installations."
            }
        ]
    },
    "Release 03": {
        "date": "JUNE 12, 2026",
        "doc_bundle": "826 MB (53 PDFs)",
        "vid_bundle": "4.6 GB (6 Videos)",
        "agencies": ["FBI", "CIA", "NASA", "DOW / DoD"],
        "url": "https://www.war.gov/ufo/",
        "records": [
            {
                "id": "CENTCOM-JELLYFISH",
                "title": "Iraq 'Jellyfish' Multi-Lobed UAP Thermal Tracking Footage",
                "agency": "DOW / DoD",
                "type": "Video",
                "video_url": "https://www.youtube.com/watch?v=nb45rXZX6Yw",
                "detail": "Military electro-optical/infrared tracking video showing an irregular multi-lobed object moving silently over a joint operations base."
            },
            {
                "id": "DHS-AGUADILLA",
                "title": "Aguadilla, Puerto Rico Thermal Transmedium Object Video",
                "agency": "FBI",
                "type": "Video",
                "video_url": "https://www.youtube.com/watch?v=c1qiZ_L8wX4",
                "detail": "Airborne thermal camera footage capturing an object traveling over land, entering the ocean without slowing, and splitting into two distinct signatures."
            },
            {
                "id": "DOW-UAP-D081",
                "title": "Western US Event (Oct 2023) & Cheyenne Mountain (Feb 2022)",
                "agency": "NASA",
                "type": "Document",
                "video_url": "",
                "detail": "Includes NASA legacy records, 1950–2008 CIA historical batch, and Western US sensor reconstructions."
            }
        ]
    },
    "Release 04": {
        "date": "JULY 10, 2026",
        "doc_bundle": "227 MB (40 Records)",
        "vid_bundle": "1.4 GB",
        "agencies": ["NASA", "DOW / DoD", "AARO"],
        "url": "https://www.war.gov/ufo/",
        "records": [
            {
                "id": "AARO-SOUTHASIA-2023",
                "title": "South Asia Fly-By Sensor Video (MQ-9 Infrared Pod)",
                "agency": "AARO",
                "type": "Video",
                "video_url": "https://www.youtube.com/watch?v=8Y691c4-zN0",
                "detail": "Official AARO release showing a high-speed object passing directly beneath an MQ-9 sensor field with a distinct thermal trail."
            },
            {
                "id": "PURSUE-R04-DOC01",
                "title": "NASA Orbital Imagery & Historical Intelligence Records",
                "agency": "NASA",
                "type": "Document",
                "video_url": "",
                "detail": "Mixed-era release combining NASA imagery logs with declassified Cold War intelligence cables."
            }
        ]
    },
    "Release 05": {
        "date": "AUGUST 7, 2026",
        "doc_bundle": "130 MB (41 Records)",
        "vid_bundle": "1.3 GB",
        "agencies": ["FBI", "CIA", "DOW / DoD"],
        "url": "https://www.war.gov/ufo/",
        "records": [
            {
                "id": "PURSUE-R05-VID01",
                "title": "Orbs & Triangular UAP Military Tracking Compilation",
                "agency": "DOW / DoD",
                "type": "Video",
                "video_url": "https://www.youtube.com/watch?v=dees3BDXHCg",
                "detail": "Fifth Pentagon release highlighting spherical orbs and triangular craft captured on military electro-optical sensors."
            },
            {
                "id": "PURSUE-R05-DOC01",
                "title": "Eight FBI Witness Forms & State Department / CIA Memos",
                "agency": "FBI",
                "type": "Document",
                "video_url": "",
                "detail": "Includes 8 FBI witness interview forms and multi-agency records spanning 1950 to 2026."
            }
        ]
    },
    "Release 06": {
        "date": "SEPTEMBER 18, 2026",
        "doc_bundle": "2.23 GB (55 PDFs)",
        "vid_bundle": "1.4 GB (15 Videos)",
        "agencies": ["DOW / DoD", "AARO"],
        "url": "https://www.war.gov/ufo/",
        "records": [
            {
                "id": "PURSUE-R06-TREMONTON",
                "title": "1952 Tremonton, Utah Restored Navy Analysis Film",
                "agency": "AARO",
                "type": "Video",
                "video_url": "https://www.youtube.com/watch?v=8Y691c4-zN0",
                "detail": "Includes a restored copy of the famous July 1952 Tremonton, Utah color film analyzed by U.S. Navy photo-interpreters alongside 14 military clips."
            },
            {
                "id": "PURSUE-R06-DOC01",
                "title": "AAWSAP Technical Studies & Advanced Aerospace Physics Papers",
                "agency": "DOW / DoD",
                "type": "Document",
                "video_url": "",
                "detail": "Extensive 2.23 GB document bundle covering AAWSAP research papers on propulsion, wormholes, and sensor anomalies."
            }
        ]
    },
    "Release 07": {
        "date": "OCTOBER 23, 2026",
        "doc_bundle": "325 MB (28 PDFs)",
        "vid_bundle": "No Videos in Release 07",
        "agencies": ["DOW / DoD", "FBI"],
        "url": "https://www.war.gov/ufo/",
        "records": [
            {
                "id": "DOW-UAP-D176",
                "title": "2026 Matte-Black Triangular Craft Over Sensitive Site (FBI-UAP-D043)",
                "agency": "FBI",
                "type": "Document",
                "video_url": "",
                "detail": "Two federal special agents observed a silent 13–15 ft matte-black triangle climb 300 ft, hover for 20 seconds, and accelerate at jet speed. (Pentagon released 28 PDFs and 0 videos in Batch 7)."
            },
            {
                "id": "DOW-UAP-D155",
                "title": "1957 Saudi Arabia B-52 Gunnery Scope Detection & Roswell Account",
                "agency": "DOW / DoD",
                "type": "Document",
                "video_url": "",
                "detail": "Air Intelligence Report on a B-52 crew tracking an unknown object over Saudi Arabia, plus Walter Haut's 2002 Roswell statement."
            }
        ]
    },
    "Release 08": {
        "date": "NOVEMBER 20, 2026",
        "doc_bundle": "296 MB (40 PDFs)",
        "vid_bundle": "29 MB (3 Videos)",
        "agencies": ["DOW / DoD", "CIA", "AARO"],
        "url": "https://www.war.gov/ufo/",
        "records": [
            {
                "id": "PURSUE-R08-VID01",
                "title": "Middle East Naval Vessel Anomalous Object Videos (2020, 2023 & 2026)",
                "agency": "DOW / DoD",
                "type": "Video",
                "video_url": "https://www.youtube.com/watch?v=245MswcvKeg",
                "detail": "Latest eighth tranche release: 3 declassified videos showing anomalous objects operating near a U.S. Naval vessel in the Middle East."
            },
            {
                "id": "PURSUE-R08-DOC01",
                "title": "Radar Track Analyses, 1952 CIA Evaluation & 1957 Martha's Vineyard Sketch",
                "agency": "CIA",
                "type": "Document",
                "video_url": "",
                "detail": "40 PDF documents including radar track telemetry, 1952 CIA flying saucer evaluations, and a 1957 sighting sketch off Woods Hole, MA."
            }
        ]
    }
}

# ==========================================
# 4. SESSION STATE & HELPER FUNCTIONS
# ==========================================
if "active_main_tab" not in st.session_state:
    st.session_state.active_main_tab = 0
if "active_uap_batch" not in st.session_state:
    st.session_state.active_uap_batch = "Release 01"
if "nebula_reply" not in st.session_state:
    st.session_state.nebula_reply = ""
    st.session_state.nebula_model = ""
if "last_nebula_cmd" not in st.session_state:
    st.session_state.last_nebula_cmd = ""
if "live_report" not in st.session_state:
    st.session_state.live_report = ""
    st.session_state.live_model = ""
if "research_answer" not in st.session_state:
    st.session_state.research_answer = ""
    st.session_state.research_model = ""
if "uap_briefing" not in st.session_state:
    st.session_state.uap_briefing = ""
    st.session_state.uap_model = ""
if "jwst_analysis" not in st.session_state:
    st.session_state.jwst_analysis = ""
    st.session_state.jwst_model = ""
if "vision_analysis" not in st.session_state:
    st.session_state.vision_analysis = ""
    st.session_state.vision_model = ""
if "pdf_analysis" not in st.session_state:
    st.session_state.pdf_analysis = ""
    st.session_state.pdf_model = ""
if "iss_analysis" not in st.session_state:
    st.session_state.iss_analysis = ""
    st.session_state.iss_model = ""
if "active_audio" not in st.session_state:
    st.session_state.active_audio = ""
    st.session_state.track_name = "NO TRACK LOADED"
    st.session_state.track_lang = "STANDBY"


def ask_ai(prompt_content):
    live_weather = get_live_weather()
    weather_context = (
        f"[System Context: User is located in Cuffley/Cheshunt, UK. "
        f"Current live local weather is {live_weather}. "
        f"Always use this exact live reading when asked about temperature or weather.]\n\n"
    )

    if isinstance(prompt_content, list):
        final_prompt = [weather_context] + prompt_content
    else:
        final_prompt = weather_context + str(prompt_content)

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=final_prompt
            )
            return response.text, model_name
        except Exception:
            continue
    return "All AI servers are currently busy. Please try again shortly.", "None"


async def create_voice(text, voice_code, filename):
    clean_text = re.sub(r'[*#_`()\[\]-]', ' ', text)
    clean_text = re.sub(r'[^\w\s.,?!\u0D80-\u0DFF]', '', clean_text)
    rate_speed = "-8%" if "si-LK" in voice_code else "-3%"
    communicate = edge_tts.Communicate(clean_text, voice_code, rate=rate_speed)
    await communicate.save(filename)


def generate_audio_file(text, voice_code, filename):
    asyncio.run(create_voice(text, voice_code, filename))


def fetch_json_safe(url):
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "NEBULA-Observatory/1.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def fetch_and_generate_live_report(current_lang, count, voice_code):
    rss_urls = [
        "https://www.nasa.gov/news-release/feed/",
        "https://www.space.com/feeds/all"
    ]
    latest_news = ""
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:count]:
            latest_news += f"- {entry.title}: {entry.summary[:200]}\n"

    if current_lang == "English":
        prompt = f"""
        You are NEBULA, an expert female AI researcher in astrophysics, cosmic paradoxes, and UAP phenomena.
        Analyze the following latest space news and write a compelling, structured report in English:
        {latest_news}
1. Highlight the 3 most intriguing discoveries and explain their significance clearly.
2. Provide a scientific analysis of how these findings connect to Cosmic Paradoxes (like the Fermi Paradox or Dark Matter) or UAP/extraterrestrial research.
        """
    else:
        prompt = f"""
        ඔබ නෙබියුලා නම් වූ තාරකා විද්‍යාව, විශ්වීය පැරඩොක්ස් සහ හඳුනා නොගත් පියාසර වස්තූන් පිළිබඳ විශේෂඥ පර්යේෂණ පද්ධතියයි.
        පහත පුවත් විශ්ලේෂණය කර සිංහලෙන් වාර්තාවක් සකසන්න:
        {latest_news}
1. වඩාත්ම කුතුහලය දනවන සොයාගැනීම් 3ක් පැහැදිලි කරන්න.
2. මේවා ෆර්මි පැරඩොක්ස්, අඳුරු පදාර්ථ හෝ පිටසක්වල ජීවය සෙවීමේ ගවේෂණ සමඟ සම්බන්ධ වන ආකාරය විග්‍රහ කරන්න.
        
        වැදගත් නීතියක්: කිසිම ඉංග්‍රීසි අකුරක් (A-Z) හෝ වරහන් භාවිතා නොකරන්න. NASA, UAP, SpaceX වැනි සියලුම විද්‍යාත්මක සහ ආයතනික නම් 'නාසා', 'යූ ඒ පී', 'ස්පේස් එක්ස්' ලෙස සිංහල අකුරෙන්ම උච්චාරණය වන පරිදි පමණක් ලියන්න.
        """
    report, used_model = ask_ai(prompt)
    st.session_state.live_report = report
    st.session_state.live_model = used_model

    if used_model != "None":
        generate_audio_file(report, voice_code, "live_report.mp3")
        st.session_state.active_audio = "live_report.mp3"
        st.session_state.track_name = "LIVE_NEBULA_REPORT.MP3"
        st.session_state.track_lang = "EN-UK" if current_lang == "English" else "SI-LK"


# ==========================================
# 5. SIDEBAR & HANDS-FREE N.E.B.U.L.A. CORE
# ==========================================

with st.sidebar:
    st.markdown('<div class="sidebar-nebula-banner">N.E.B.U.L.A.</div>',
                unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=500&q=80",
             use_container_width=True)
    lang = st.radio("🌐 Language / භාෂාව",
                    ["English", "සිංහල"], horizontal=True)
    st.divider()

if lang == "English":
    ui = {
        "m1_label": "📡 Live Data Feeds", "m1_val": "NASA + JWST + NOAA", "m1_delta": "All Systems Online",
        "m2_label": "🧠 AI Core Status", "m2_val": "NEBULA + Vision + PDF", "m2_delta": "4 Models Ready",
        "m3_label": "🎙️ Audio Deck", "m3_val": "Hands-Free Wake", "m3_delta": "English Female Voice",
        "sidebar_title": "🎛️ Mission Control",
        "slider_label": "Articles per source:",
        "preset_title": "⚡ Quick Research Topics",
        "preset_label": "Select a topic:",
        "presets": [
            "Custom (Write my own query)",
            "The Fermi Paradox and the Great Filter",
            "Pentagon UAP Reports and Physics Anomalies",
            "Dark Matter and Multiverse Theories",
            "The Mystery of Interstellar Object Oumuamua"
        ],
        "tab1": "📡 Live Cosmic Report",
        "tab2": "🔭 James Webb Live",
        "tab3": "🗂️ Pentagon UAP Vault",
        "tab4": "🔬 Visual Evidence Lab",
        "tab5": "📄 Dossier Reader",
        "tab6": "🛰️ ISS & Space Weather",
        "tab7": "🧠 Deep Research",
        "t1_sub": "Latest NASA & Space.com Intelligence",
        "t1_btn": "🚀 Generate Cosmic Report & Audio",
        "t1_spin": "Gathering data, analyzing & synthesizing voice...",
        "jwst_sub": "James Webb Space Telescope — Live L2 Feed & Infrared Imagery",
        "jwst_select": "Select Latest JWST Observation / Discovery:",
        "jwst_btn": "🎙️ Analyze JWST Discovery & Synthesize Audio",
        "jwst_spin": "Decoding JWST infrared telemetry & generating voice...",
        "uap_sub": "PURSUE Declassified UAP Releases (Batch 01 – 08)",
        "uap_filter_type": "Filter by File Type:",
        "uap_filter_agency": "Filter by Agency:",
        "uap_select": "Select Record in this Release:",
        "uap_btn": "🎙️ Generate AI Forensic Briefing & Audio",
        "uap_spin": "Analyzing Pentagon UAP dossier & synthesizing voice...",
        "uap_live_title": "📡 Live Pentagon / WAR.GOV Disclosure Feed",
        "vis_sub": "Multimodal Visual Evidence & Anomaly Lab",
        "vis_upload": "Upload a UAP sighting photo, video frame, or deep-space image (JPG, PNG, WEBP):",
        "vis_mode": "Select Forensic Analysis Mode:",
        "vis_modes": [
            "UAP / Aerial Anomaly Forensics (Shape, Lighting, Flight Dynamics & Conventional Explanations)",
            "Deep Space / Astrophotography Breakdown (Celestial Objects, Spectra & Cosmic Context)",
            "Custom Visual Investigation (Ask my own question about this image)"
        ],
        "vis_custom_q": "Specific question about this image:",
        "vis_btn": "🔬 Run AI Visual Forensics & Synthesize Audio",
        "vis_spin": "Scanning visual telemetry, lighting anomalies & generating voice...",
        "pdf_sub": "Declassified PDF & Research Dossier Reader",
        "pdf_source": "Choose PDF Document Source:",
        "pdf_sources": [
            "Upload a PDF Document (WAR.GOV Dossier / Research Paper)",
            "Select PDF from Local Vault (pentagon_videos folder)"
        ],
        "pdf_upload": "Upload PDF file (Max 25MB):",
        "pdf_vault_sel": "Select PDF from pentagon_videos:",
        "pdf_no_vault": "No PDF files found in 'pentagon_videos' folder yet. Place extracted WAR.GOV PDFs there or upload one above.",
        "pdf_mode": "Select Document Analysis Mode:",
        "pdf_modes": [
            "Executive Intelligence Briefing (Key Findings, Dates, Witnesses & Anomalies)",
            "Technical & Physics Telemetry Extraction (Radar, Speed, Altitude & Sensor Data)",
            "Custom Dossier Interrogation (Ask a specific question about this PDF)"
        ],
        "pdf_custom_q": "Specific question about this PDF:",
        "pdf_btn": "📄 Decode Dossier & Synthesize Audio",
        "pdf_spin": "Reading declassified pages, extracting telemetry & generating voice...",
        "iss_sub": "Live ISS Orbital Radar & NOAA Solar Storm Telemetry",
        "iss_refresh": "🔄 Refresh Live Telemetry",
        "iss_btn": "🎙️ Generate AI Orbital & Space Weather Briefing",
        "iss_spin": "Analyzing ISS coordinates, solar wind & geomagnetic conditions...",
        "t2_sub": "UAP Phenomena & Cosmic Paradox Explorer",
        "t2_input": "Your research question:",
        "t2_placeholder": "e.g., Explain the Great Filter and its implications for human civilization...",
        "t2_btn": "🔍 Analyze & Synthesize Audio",
        "t2_spin": "Researching deep space data & generating audio...",
        "t2_warn": "Please enter a research question first.",
        "model_tag": "Model used:"
    }
    active_voice = "en-GB-SoniaNeural"
else:
    ui = {
        "m1_label": "📡 සජීවී දත්ත මූලාශ්‍ර", "m1_val": "NASA + JWST + NOAA", "m1_delta": "සියල්ල සක්‍රීයයි",
        "m2_label": "🧠 AI පද්ධතිය", "m2_val": "NEBULA + Vision + PDF", "m2_delta": "මොඩල් 4ක් සූදානම්",
        "m3_label": "🎙️ හඬ පද්ධතිය", "m3_val": "Hands-Free Wake", "m3_delta": "සිංහල කාන්තා හඬ",
        "sidebar_title": "🎛️ පාලක පුවරුව",
        "slider_label": "එක් අඩවියකින් ගන්නා පුවත් ගණන:",
        "preset_title": "⚡ ඉක්මන් මාතෘකා",
        "preset_label": "මාතෘකාවක් තෝරන්න:",
        "presets": [
            "Custom (මගේ ප්‍රශ්නයක් ලියමි)",
            "ෆර්මි පැරඩොක්ස් සහ ග්‍රේට් ෆිල්ටර් න්‍යාය",
            "පෙන්ටගනයේ යූ ඒ පී වාර්තා සහ භෞතික විද්‍යාව",
            "අඳුරු පදාර්ථ සහ සමාන්තර විශ්ව",
            "ඔමුවමුවා අන්තර් තාරකා වස්තුවේ අභිරහස"
        ],
        "tab1": "📡 සජීවී විශ්වීය වාර්තාව",
        "tab2": "🔭 ජේම්ස් වෙබ් සජීවී දත්ත",
        "tab3": "🗂️ පෙන්ටගන UAP ලිපිගොනු",
        "tab4": "🔬 දෘශ්‍ය සාක්ෂි විද්‍යාගාරය",
        "tab5": "📄 ලිපිගොනු කියවනය",
        "tab6": "🛰️ ISS සහ අභ්‍යවකාශ කාලගුණය",
        "tab7": "🧠 ගැඹුරු පර්යේෂණ",
        "t1_sub": "අද දවසේ නාසා සහ Space.com දත්ත විශ්ලේෂණය",
        "t1_btn": "🚀 නවතම වාර්තාව සහ හඬපටය සකසන්න",
        "t1_spin": """දත්ත රැස් කර විශ්ලේෂණය කර හඬපටය සකසමින්...""",
        "jwst_sub": "ජේම්ස් වෙබ් අභ්‍යවකාශ දුරේක්ෂය — සජීවී දත්ත සහ අධෝරක්ත සොයාගැනීම්",
        "jwst_select": "නවතම ජේම්ස් වෙබ් සොයාගැනීමක් තෝරන්න:",
        "jwst_btn": "🎙️ ජේම්ස් වෙබ් දත්ත විශ්ලේෂණය සහ හඬපටය",
        "jwst_spin": """ජේම්ස් වෙබ් අධෝරක්ත දත්ත විශ්ලේෂණය කර හඬපටය සකසමින්...""",
        "uap_sub": "නිල පෙන්ටගන PURSUE UAP නිකුතු (Release 01 – 08)",
        "uap_filter_type": "ගොනු වර්ගය අනුව පෙරන්න:",
        "uap_filter_agency": "ආයතනය අනුව පෙරන්න:",
        "uap_select": "මෙම කොටසේ ඇති වාර්තාවක් තෝරන්න:",
        "uap_btn": "🎙️ AI විශ්ලේෂණය සහ හඬපටය සකසන්න",
        "uap_spin": """පෙන්ටගන UAP ලිපිගොනුව විශ්ලේෂණය කර හඬපටය සකසමින්...""",
        "uap_live_title": "📡 සජීවී පෙන්ටගන UAP නිකුතු පුවත්",
        "vis_sub": "දෘශ්‍ය සාක්ෂි සහ අසාමාන්‍ය ඡායාරූප විශ්ලේෂණ විද්‍යාගාරය",
        "vis_upload": "UAP ඡායාරූපයක්, වීඩියෝ රාමුවක් හෝ අභ්‍යවකාශ ඡායාරූපයක් තෝරන්න (JPG, PNG, WEBP):",
        "vis_mode": "විශ්ලේෂණ ක්‍රමය තෝරන්න:",
        "vis_modes": [
            "UAP / අහසේ අසාමාන්‍ය වස්තූන් පරීක්ෂාව (හැඩය, ආලෝකය සහ විද්‍යාත්මක පැහැදිලි කිරීම්)",
            "ගැඹුරු අභ්‍යවකාශ ඡායාරූප විශ්ලේෂණය (තාරකා, මන්දාකිණි සහ විශ්වීය පසුබිම)",
            "මගේ විශේෂ ප්‍රශ්නයක් ඇසීම (Custom Visual Investigation)"
        ],
        "vis_custom_q": "මෙම ඡායාරූපය ගැන ඔබේ ප්‍රශ්නය:",
        "vis_btn": "🔬 ඡායාරූපය විශ්ලේෂණය කර හඬපටය සකසන්න",
        "vis_spin": """ඡායාරූපයේ දත්ත පරීක්ෂා කර හඬපටය සකසමින්...""",
        "pdf_sub": "රහස්‍යභාවය ඉවත් කළ PDF සහ පර්යේෂණ ලිපිගොනු කියවනය",
        "pdf_source": "PDF ලේඛනය ලබාගන්නා ආකාරය තෝරන්න:",
        "pdf_sources": [
            "නව PDF ගොනුවක් Upload කරන්න (WAR.GOV Dossier / Research Paper)",
            "pentagon_videos ෆෝල්ඩරයේ ඇති PDF ගොනුවක් තෝරන්න"
        ],
        "pdf_upload": "PDF ගොනුව තෝරන්න (Max 25MB):",
        "pdf_vault_sel": "pentagon_videos ෆෝල්ඩරයේ ඇති PDF ගොනුව:",
        "pdf_no_vault": "pentagon_videos ෆෝල්ඩරයේ තවම PDF ගොනු නැත. WAR.GOV වෙතින් ගත් PDF එතැනට දමන්න හෝ ඉහතින් Upload කරන්න.",
        "pdf_mode": "ලේඛන විශ්ලේෂණ ක්‍රමය තෝරන්න:",
        "pdf_modes": [
            "ප්‍රධාන බුද්ධි වාර්තා සාරාංශය (Executive Intelligence Briefing)",
            "තාක්ෂණික සහ රේඩාර් දත්ත විශ්ලේෂණය (Technical & Physics Telemetry)",
            "මගේ විශේෂ ප්‍රශ්නයක් ඇසීම (Custom Dossier Interrogation)"
        ],
        "pdf_custom_q": "මෙම PDF ලේඛනය ගැන ඔබේ ප්‍රශ්නය:",
        "pdf_btn": "📄 ලිපිගොනුව කියවා හඬපටය සකසන්න",
        "pdf_spin": """ලිපිගොනුවේ පිටු කියවා විශ්ලේෂණය කර හඬපටය සකසමින්...""",
        "iss_sub": "ජාත්‍යන්තර අභ්‍යවකාශ මධ්‍යස්ථානය (ISS) සහ NOAA සූර්ය කුණාටු රේඩාර් පද්ධතිය",
        "iss_refresh": "🔄 සජීවී දත්ත අලුත් කරන්න",
        "iss_btn": "🎙️ ISS සහ අභ්‍යවකාශ කාලගුණ වාර්තාව (හඬපටය සමඟ)",
        "iss_spin": """ISS පිහිටීම සහ සූර්ය කුණාටු දත්ත විශ්ලේෂණය කරමින්...""",
        "t2_sub": "යූ ඒ පී සිදුවීම් සහ විශ්වීය පැරඩොක්ස් ගවේෂකයා",
        "t2_input": "ඔබේ පර්යේෂණ ප්‍රශ්නය:",
        "t2_placeholder": """උදා: ග්‍රේට් ෆිල්ටර් න්‍යාය සහ අපේ ශිෂ්ටාචාරයේ අනාගතය ගැන පැහැදිලි කරන්න...""",
        "t2_btn": "🔍 විශ්ලේෂණය සහ හඬපටය සකසන්න",
        "t2_spin": """දත්ත ගවේෂණය කර හඬපටය සකසමින්...""",
        "t2_warn": "කරුණාකර පළමුව ප්‍රශ්නයක් ඇතුළත් කරන්න.",
        "model_tag": "භාවිතා කළ මොඩල් එක:"
    }
    active_voice = "si-LK-ThiliniNeural"

with st.sidebar:
    status_badge = "● READY" if st.session_state.active_audio else "○ IDLE"
    st.markdown(f"""
        <div class="jetaudio-deck">
            <div class="jetaudio-brand">
                <span>JET-NEBULA DECK</span>
                <span>{status_badge}</span>
            </div>
            <div class="vfd-screen">
                <div class="vfd-title">▶ {st.session_state.track_name}</div>
                <div class="vfd-meta">
                    <span>24kHz • FEMALE NEURAL</span>
                    <span>{st.session_state.track_lang}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.active_audio and os.path.exists(st.session_state.active_audio):
        st.audio(st.session_state.active_audio,
                 format="audio/mp3", autoplay=True)

    st.divider()

    nebula_img_src = "https://upload.wikimedia.org/wikipedia/commons/b/b1/NGC7293_%282004%29.jpg"
    if os.path.exists("nebula_eye.jpg"):
        with open("nebula_eye.jpg", "rb") as img_f:
            b64_str = base64.b64encode(img_f.read()).decode("utf-8")
            nebula_img_src = f"data:image/jpeg;base64,{b64_str}"

    is_speaking = "true" if st.session_state.track_name == "NEBULA_VOICE_LINK.MP3" else "false"
    nebula_status = "N.E.B.U.L.A. • SPEAKING" if is_speaking == "true" else "N.E.B.U.L.A. • ONLINE"
    orb_anim_speed = "14s" if is_speaking == "true" else "38s"
    pulse_anim_speed = "1.1s" if is_speaking == "true" else "4.2s"

    components.html(f"""
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            background: transparent;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: 'Orbitron', sans-serif;
            overflow: hidden;
        }}
        .nebula-viewport {{
            position: relative;
            width: 190px;
            height: 190px;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: coreBreathe {pulse_anim_speed} infinite ease-in-out;
            -webkit-mask-image: radial-gradient(circle at center, black 42%, rgba(0,0,0,0.65) 56%, transparent 71%);
            mask-image: radial-gradient(circle at center, black 42%, rgba(0,0,0,0.65) 56%, transparent 71%);
        }}
        .nebula-img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            animation: nebulaSwirl {orb_anim_speed} linear infinite;
            filter: saturate(1.3) contrast(1.12);
        }}
        .nebula-label {{
            color: #38bdf8;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1.8px;
            margin-top: 2px;
            text-align: center;
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.85);
        }}
        @keyframes nebulaSwirl {{
            0% {{ transform: rotate(0deg) scale(1.06); }}
            50% {{ transform: rotate(180deg) scale(1.18); }}
            100% {{ transform: rotate(360deg) scale(1.06); }}
        }}
        @keyframes coreBreathe {{
            0%, 100% {{ transform: scale(0.96); filter: brightness(0.95); }}
            50% {{ transform: scale(1.05); filter: brightness(1.28); }}
        }}
    </style>
    <div class="nebula-viewport">
        <img class="nebula-img" src="{nebula_img_src}" alt="Nebula Core">
    </div>
    <div class="nebula-label">{nebula_status}</div>
    """, height=215)

    voice_cmd = st.audio_input(
        "🎙️ Tap Mic & Speak" if lang == "English" else "🎙️ මයික් ඔබා කතා කරන්න",
        key="sidebar_nebula_mic",
        label_visibility="collapsed"
    )

    if voice_cmd is not None:
        audio_bytes = voice_cmd.read()
        current_hash = hashlib.md5(audio_bytes).hexdigest()

        if current_hash != st.session_state.last_nebula_cmd and len(audio_bytes) > 800:
            st.session_state.last_nebula_cmd = current_hash
            with st.spinner("N.E.B.U.L.A. thinking..." if lang == "English" else "නෙබියුලා සවන් දෙමින්..."):
                if lang == "English":
                    j_prompt = """
                    You are N.E.B.U.L.A., the intelligent female AI core of the NEBULA Deep Space & UAP Observatory.
                    Listen to the Commander's voice command in the attached audio and respond directly, warmly, and intelligently as N.E.B.U.L.A.
                    Keep your spoken response crisp, authoritative, and under 90 words.
                    """
                else:
                    j_prompt = """
                    ඔබ නෙබියුලා අභ්‍යවකාශ සහ යූ ඒ පී පර්යේෂණ මධ්‍යස්ථානයේ උසස් බුද්ධිමත් සහායිකාව වන නෙබියුලා ය.
                    පරිශීලකයාගේ හඬ පණිවිඩයට සවන් දී, ඉතා බුද්ධිමත්ව, ආචාරශීලීව සහ කෙටියෙන් සිංහලෙන් පිළිතුරු දෙන්න.
                    වැදගත් නීතියක්: කිසිම ඉංග්‍රීසි අකුරක් (A-Z) හෝ වරහන් භාවිතා නොකරන්න. සියලුම විද්‍යාත්මක නම් සිංහල අකුරෙන්ම උච්චාරණය වන පරිදි පමණක් ලියන්න.
                    """
                audio_part = types.Part.from_bytes(
                    data=audio_bytes, mime_type="audio/wav")
                j_reply, j_used_model = ask_ai([j_prompt, audio_part])
                st.session_state.nebula_reply = j_reply
                st.session_state.nebula_model = j_used_model

                if j_used_model != "None":
                    generate_audio_file(
                        j_reply, active_voice, "nebula_response.mp3")
                    st.session_state.active_audio = "nebula_response.mp3"
                    st.session_state.track_name = "NEBULA_VOICE_LINK.MP3"
                    st.session_state.track_lang = "EN-UK" if lang == "English" else "SI-LK"
                    st.rerun()

    if st.session_state.nebula_reply:
        with st.expander("💬 N.E.B.U.L.A. Transcript", expanded=True):
            st.caption(f"Core: `{st.session_state.nebula_model}`")
            st.write(st.session_state.nebula_reply)

    st.divider()
    st.header(ui["sidebar_title"])
    news_count = st.slider(
        ui["slider_label"], min_value=2, max_value=10, value=5)

    st.divider()
    st.subheader(ui["preset_title"])
    preset_topic = st.selectbox(ui["preset_label"], ui["presets"])

# ==========================================
# 6. MAIN DASHBOARD HEADER, HUD & VERTICAL BUBBLE TABS
# ==========================================
st.markdown('<div class="main-hero-header">DEEP SPACE & UAP OBSERVATORY</div>',
            unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label=ui["m1_label"], value=ui["m1_val"], delta=ui["m1_delta"])
with col2:
    st.metric(label=ui["m2_label"], value=ui["m2_val"], delta=ui["m2_delta"])
with col3:
    st.metric(label=ui["m3_label"], value=ui["m3_val"], delta=ui["m3_delta"])

st.write("")

tab_labels = [
    ui["tab1"], ui["tab2"], ui["tab3"], ui["tab4"], ui["tab5"], ui["tab6"], ui["tab7"]
]

# Left Column: Vertical Tab Heads (Parallel to Sidebar)
# Right Column: Connected Square HUD Bubble Frame Pane
nav_col, content_col = st.columns([1.2, 3.8], gap="small")

with nav_col:
    st.markdown('<div class="nebula-nav-anchor"></div>',
                unsafe_allow_html=True)
    for idx, label in enumerate(tab_labels):
        is_active = (st.session_state.active_main_tab == idx)
        btn_display = f"{label}  ▸" if is_active else label
        if st.button(
            btn_display,
            key=f"vertical_tab_btn_{idx}",
            type="primary" if is_active else "secondary",
            use_container_width=True
        ):
            st.session_state.active_main_tab = idx
            st.rerun()

with content_col:
    active_idx = st.session_state.active_main_tab
    with st.container(border=True):
        st.markdown(f"""
            <div class="active-bubble-header">
                <span class="active-bubble-title">{tab_labels[active_idx]}</span>
                <span class="active-bubble-pill">● MODULE 0{active_idx + 1} ACTIVE</span>
            </div>
        """, unsafe_allow_html=True)

        # TAB 1: Live Cosmic Report
        if active_idx == 0:
            st.subheader(ui["t1_sub"])

            if st.button(ui["t1_btn"], use_container_width=True):
                with st.spinner(ui["t1_spin"]):
                    fetch_and_generate_live_report(
                        lang, news_count, active_voice)
                    st.rerun()

            if st.session_state.live_report:
                st.success(
                    f"✅ {ui['model_tag']} `{st.session_state.live_model}`")
                st.markdown(
                    f'<div class="report-box">{st.session_state.live_report}</div>', unsafe_allow_html=True)

        # TAB 2: James Webb Live Feed & L2 Telemetry
        elif active_idx == 1:
            st.subheader(ui["jwst_sub"])

            st.markdown("""
                <div class="pursue-banner">
                    <div>
                        <span class="dossier-badge">JWST TELEMETRY • SUN-EARTH L2 HALO ORBIT • ACTIVE</span>
                        <div style="font-size:13px; color:#AFC1CD;">
                            <b>DISTANCE:</b> ~1,500,000 km from Earth &nbsp;|&nbsp;
                            <b>PRIMARY MIRROR:</b> 6.5m Gold-Coated Beryllium &nbsp;|&nbsp;
                            <b>INSTRUMENTS:</b> NIRCam • NIRSpec • MIRI • FGS/NIRISS
                        </div>
                    </div>
                    <div>
                        <a href="https://webb.nasa.gov/content/webbLaunch/whereIsWebb.html" target="_blank" style="color:#4C9ABB; text-decoration:none; font-weight:bold; font-size:13px; margin-right:14px;">
                            🛰️ Live L2 Position ↗
                        </a>
                        <a href="https://www.stsci.edu/jwst/science-execution/observing-schedules" target="_blank" style="color:#4C9ABB; text-decoration:none; font-weight:bold; font-size:13px;">
                            🎯 Live Target Schedule ↗
                        </a>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            jwst_entries = []
            for j_url in ["https://www.nasa.gov/missions/webb/feed/", "https://esawebb.org/feed/"]:
                parsed = feedparser.parse(j_url)
                for item in parsed.entries[:6]:
                    img_url = ""
                    if "media_content" in item and item.media_content:
                        img_url = item.media_content[0].get("url", "")
                    elif "enclosures" in item and item.enclosures:
                        img_url = item.enclosures[0].get("href", "")
                    jwst_entries.append({
                        "title": item.title,
                        "link": item.link,
                        "published": item.get("published", "Latest Release")[:16],
                        "summary": re.sub(r'<[^>]+>', '', item.get("summary", ""))[:450],
                        "image": img_url
                    })

            if jwst_entries:
                jwst_titles = [
                    f"{e['title']} ({e['published']})" for e in jwst_entries]
                chosen_jwst_label = st.selectbox(
                    ui["jwst_select"], jwst_titles)
                chosen_jwst = jwst_entries[jwst_titles.index(
                    chosen_jwst_label)]

                j_col1, j_col2 = st.columns([3, 2])
                with j_col1:
                    st.markdown(f"""
                        <div class="dossier-card">
                            <div class="dossier-badge">JWST INFRARED RELEASE • {chosen_jwst['published']}</div>
                            <h4 style="color:#FFFFFF; margin:4px 0 8px 0;">{chosen_jwst['title']}</h4>
                            <p style="color:#E2E8F0; line-height:1.65;">{chosen_jwst['summary']}...</p>
                            <a href="{chosen_jwst['link']}" target="_blank" style="color:#4C9ABB; text-decoration:none; font-weight:bold; font-size:13px;">
                                🔭 View Full High-Res Infrared Plate on NASA / ESA Webb ↗
                            </a>
                        </div>
                    """, unsafe_allow_html=True)
                with j_col2:
                    if chosen_jwst["image"]:
                        st.image(
                            chosen_jwst["image"], caption=chosen_jwst["title"], use_container_width=True)
                    else:
                        st.image("https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?w=800&q=80",
                                 caption="Deep Space Infrared Sector", use_container_width=True)

                if st.button(ui["jwst_btn"], use_container_width=True):
                    with st.spinner(ui["jwst_spin"]):
                        if lang == "English":
                            jwst_prompt = f"""
                            You are NEBULA, an astrophysics intelligence core analyzing James Webb Space Telescope (JWST) telemetry.
                            Analyze this latest JWST observation/discovery in clear, engaging English:
                            Title: {chosen_jwst['title']}
                            Details: {chosen_jwst['summary']}
                            Explain: 1) What JWST's infrared instruments revealed, 2) Why this challenges or advances our understanding of the early universe, exoplanets, or dark matter.
                            """
                        else:
                            jwst_prompt = f"""
                            ඔබ නාසා ආයතනයේ ජේම්ස් වෙබ් අභ්‍යවකාශ දුරේක්ෂයේ අධෝරක්ත දත්ත විශ්ලේෂණය කරන නෙබියුලා පද්ධතියයි.
                            පහත නවතම ජේම්ස් වෙබ් සොයාගැනීම පිළිබඳව සිංහලෙන් පැහැදිලි විශ්ලේෂණයක් ලබා දෙන්න:
                            මාතෘකාව: {chosen_jwst['title']}
                            විස්තරය: {chosen_jwst['summary']}
                            
                            වැදගත් නීතියක්: කිසිම ඉංග්‍රීසි අකුරක් (A-Z) හෝ වරහන් භාවිතා නොකරන්න. NASA, JWST, NIRCam වැනි සියලුම නම් 'නාසා', 'ජේම්ස් වෙබ්', 'නියර් කැම්' ලෙස සිංහල අකුරෙන්ම උච්චාරණය වන පරිදි පමණක් ලියන්න.
                            """
                        j_ans, j_mod = ask_ai(jwst_prompt)
                        st.session_state.jwst_analysis = j_ans
                        st.session_state.jwst_model = j_mod

                        if j_mod != "None":
                            generate_audio_file(
                                j_ans, active_voice, "jwst_live.mp3")
                            st.session_state.active_audio = "jwst_live.mp3"
                            st.session_state.track_name = "JWST_INFRARED.MP3"
                            st.session_state.track_lang = "EN-UK" if lang == "English" else "SI-LK"
                            st.rerun()

                if st.session_state.jwst_analysis:
                    st.success(
                        f"✅ {ui['model_tag']} `{st.session_state.jwst_model}`")
                    st.markdown(
                        f'<div class="report-box">{st.session_state.jwst_analysis}</div>', unsafe_allow_html=True)

                st.divider()
                st.markdown("#### 🛰️ Latest JWST Telemetry & Discovery Stream")
                for item in jwst_entries[:5]:
                    st.markdown(
                        f"• [{item['title']}]({item['link']}) — <span style='color:#999999; font-size:12px;'>{item['published']}</span>", unsafe_allow_html=True)
            else:
                st.warning(
                    "Unable to reach NASA/ESA Webb RSS feed right now. Check your internet connection.")

        # TAB 3: Pentagon UAP Vault (Release 01 to 08 Selector Grid + Auto-Sync Local Folder)
        elif active_idx == 2:
            st.subheader(ui["uap_sub"])

            f_col1, f_col2 = st.columns(2)
            with f_col1:
                media_filter = st.selectbox(ui["uap_filter_type"], [
                                            "All", "Video", "Document"])
            with f_col2:
                agency_filter = st.selectbox(ui["uap_filter_agency"], [
                                             "All", "DOW / DoD", "CIA", "FBI", "NASA", "AARO"])

            batch_keys = list(PENTAGON_BATCHES.keys())
            r_row1 = st.columns(4)
            r_row2 = st.columns(4)
            for b_i, b_key in enumerate(batch_keys):
                target_col = r_row1[b_i] if b_i < 4 else r_row2[b_i - 4]
                with target_col:
                    if st.button(
                        b_key,
                        key=f"uap_rel_btn_{b_key}",
                        type="primary" if st.session_state.active_uap_batch == b_key else "secondary",
                        use_container_width=True
                    ):
                        st.session_state.active_uap_batch = b_key
                        st.rerun()

            batch_name = st.session_state.active_uap_batch
            b_data = PENTAGON_BATCHES[batch_name]

            st.markdown(f"""
                <div class="pursue-banner" style="margin-top:10px;">
                    <div>
                        <span class="dossier-badge">PURSUE • {batch_name.upper()} • {b_data['date']}</span>
                        <div style="font-size:13px; color:#AFC1CD;">
                            <b>AGENCIES:</b> {', '.join(b_data['agencies'])} &nbsp;|&nbsp;
                            <b>DOCS:</b> {b_data['doc_bundle']} &nbsp;|&nbsp;
                            <b>VIDEOS:</b> {b_data['vid_bundle']}
                        </div>
                    </div>
                    <a href="{b_data['url']}" target="_blank" style="color:#4C9ABB; text-decoration:none; font-weight:bold; font-size:13px;">
                        🔗 WAR.GOV/UFO Portal ↗
                    </a>
                </div>
            """, unsafe_allow_html=True)

            filtered_records = [
                r for r in b_data["records"]
                if (media_filter == "All" or r["type"] == media_filter)
                and (agency_filter == "All" or r["agency"] == agency_filter)
            ]

            if not filtered_records:
                st.info(
                    f"No '{media_filter}' records from '{agency_filter}' in {batch_name}. Switch filters to 'All' to view available files.")
            else:
                record_titles = [
                    f"[{r['type'].upper()}] {r['id']} — {r['title']}" for r in filtered_records]
                chosen_label = st.selectbox(
                    ui["uap_select"], record_titles, key=f"sel_{batch_name}")
                chosen_record = filtered_records[record_titles.index(
                    chosen_label)]

                st.markdown(f"""
                    <div class="dossier-card">
                        <div class="dossier-badge">{chosen_record['id']} • {chosen_record['agency']} • {chosen_record['type'].upper()}</div>
                        <h4 style="color:#FFFFFF; margin:4px 0 8px 0;">{chosen_record['title']}</h4>
                        <p style="color:#E2E8F0; line-height:1.6;">{chosen_record['detail']}</p>
                    </div>
                """, unsafe_allow_html=True)

                if chosen_record.get("video_url"):
                    st.video(chosen_record["video_url"])
                else:
                    dl_col1, dl_col2 = st.columns(2)
                    with dl_col1:
                        st.link_button(
                            f"⬇️ Download {batch_name} Documents ({b_data['doc_bundle']})",
                            "https://www.war.gov/ufo/?type=.pdf",
                            use_container_width=True
                        )
                    with dl_col2:
                        st.link_button(
                            "📂 Open Sample Declassified PDF (Release 01)",
                            "https://www.war.gov/medialink/ufo/release_1/65_hs1-834228961_62-hq-83894_section_5.pdf",
                            use_container_width=True
                        )

                if st.button(ui["uap_btn"], key=f"btn_{batch_name}", use_container_width=True):
                    with st.spinner(ui["uap_spin"]):
                        if lang == "English":
                            uap_prompt = f"""
                            You are NEBULA, an intelligence and aerospace physics analyst examining declassified Pentagon PURSUE UAP records.
                            Provide a detailed forensic briefing in English on this official file:
                            Release: {batch_name} ({b_data['date']})
                            Record ID: {chosen_record['id']} ({chosen_record['agency']})
                            Title: {chosen_record['title']}
                            Details: {chosen_record['detail']}
                            Include: 1) Key observable anomalies, 2) Conventional vs. non-conventional hypotheses, and 3) Significance within the 2026 UAP disclosures.
                            """
                        else:
                            uap_prompt = f"""
                            ඔබ පෙන්ටගනයේ රහස්‍යභාවය ඉවත් කළ යූ ඒ පී ලිපිගොනු විශ්ලේෂණය කරන නෙබියුලා පද්ධතියයි.
                            පහත නිල වාර්තාව පිළිබඳව සිංහලෙන් ගැඹුරු විශ්ලේෂණයක් ලබා දෙන්න:
                            කොටස: {batch_name} ({b_data['date']})
                            වාර්තා අංකය: {chosen_record['id']}
                            මාතෘකාව: {chosen_record['title']}
                            විස්තරය: {chosen_record['detail']}
                            
                            වැදගත් නීතියක්: කිසිම ඉංග්‍රීසි අකුරක් (A-Z) හෝ වරහන් භාවිතා නොකරන්න. සියලුම ඉංග්‍රීසි විද්‍යාත්මක නම් සහ ආයතන නම් සිංහල අකුරෙන්ම උච්චාරණය වන පරිදි පමණක් ලියන්න.
                            """
                        briefing, used_model = ask_ai(uap_prompt)
                        st.session_state.uap_briefing = briefing
                        st.session_state.uap_model = used_model

                        if used_model != "None":
                            generate_audio_file(
                                briefing, active_voice, "pentagon_uap.mp3")
                            st.session_state.active_audio = "pentagon_uap.mp3"
                            st.session_state.track_name = f"{chosen_record['id']}.MP3"
                            st.session_state.track_lang = "EN-UK" if lang == "English" else "SI-LK"
                            st.rerun()

            st.divider()
            st.markdown(
                "#### 📂 Auto-Sync Local Pentagon Vault (`pentagon_videos`)")
            local_files = sorted([
                f for f in os.listdir(LOCAL_VAULT_DIR)
                if f.lower().endswith((".mp4", ".mov", ".webm", ".mkv", ".pdf"))
            ])

            if local_files:
                selected_local = st.selectbox(
                    "Select extracted WAR.GOV/UFO file from your local folder:", local_files, key="local_vault_sel")
                local_path = os.path.join(LOCAL_VAULT_DIR, selected_local)
                if selected_local.lower().endswith(".pdf"):
                    with open(local_path, "rb") as pdf_f:
                        st.download_button(
                            f"⬇️ Open / Save {selected_local}", pdf_f, file_name=selected_local)
                else:
                    st.video(local_path)
            else:
                st.info(
                    "💡 WAR.GOV/UFO වෙතින් Download කළ ZIP ගොනු Extract කර pentagon_videos ෆෝල්ඩරයට දැමූ විගස ඒවා ඉබේම මෙතැනට එකතු වී Play වනු ඇත.")

            if st.session_state.uap_briefing:
                st.success(
                    f"✅ {ui['model_tag']} `{st.session_state.uap_model}`")
                st.markdown(
                    f'<div class="report-box">{st.session_state.uap_briefing}</div>', unsafe_allow_html=True)

            st.divider()
            st.markdown(f"#### {ui['uap_live_title']}")
            uap_feed = feedparser.parse(
                "https://news.google.com/rss/search?q=Pentagon+UAP+OR+WAR.GOV+UFO+files&hl=en-US&gl=US&ceid=US:en")
            for entry in uap_feed.entries[:4]:
                st.markdown(
                    f"• [{entry.title}]({entry.link}) — <span style='color:#999999; font-size:12px;'>{entry.published[:16]}</span>", unsafe_allow_html=True)

        # TAB 4: Multimodal Visual Evidence Lab
        elif active_idx == 3:
            st.subheader(ui["vis_sub"])

            uploaded_img = st.file_uploader(
                ui["vis_upload"], type=["jpg", "jpeg", "png", "webp"])

            if uploaded_img is not None:
                pil_img = Image.open(uploaded_img)
                v_col1, v_col2 = st.columns([2, 3])

                with v_col1:
                    st.image(
                        pil_img, caption=f"Evidence File: {uploaded_img.name}", use_container_width=True)

                with v_col2:
                    selected_mode = st.selectbox(
                        ui["vis_mode"], ui["vis_modes"])
                    custom_vis_query = ""
                    if selected_mode == ui["vis_modes"][2]:
                        custom_vis_query = st.text_input(
                            ui["vis_custom_q"], placeholder="e.g., Analyze the light trail and elevation angle of this object...")

                    if st.button(ui["vis_btn"], use_container_width=True):
                        with st.spinner(ui["vis_spin"]):
                            if lang == "English":
                                if selected_mode == ui["vis_modes"][0]:
                                    v_prompt = """
                                    You are NEBULA, an aerospace image analyst and UAP forensic investigator. Examine this uploaded image carefully and provide a structured report:
1. Visual Telemetry & Morphology: Describe the object's shape, surface illumination, shadows, motion blur, and atmospheric interaction.
2. Conventional vs. Anomalous Assessment: Evaluate prosaic explanations (lens flare, drones, balloons, satellites, atmospheric optics) versus genuinely anomalous flight/optical characteristics.
3. Forensic Conclusion: Summarize confidence levels and what additional sensor data would confirm its nature.
                                    """
                                elif selected_mode == ui["vis_modes"][1]:
                                    v_prompt = """
                                    You are NEBULA, an observational astrophysicist. Analyze this space/astronomy image in detail:
1. Identify celestial structures, nebulae, star clusters, or planetary features visible.
2. Explain the wavelengths/colors, physical processes, and cosmic significance of what is shown.
                                    """
                                else:
                                    v_prompt = f"You are NEBULA, an astrophysics and UAP visual forensics expert. Answer this question about the uploaded image clearly and scientifically:\n\n{custom_vis_query or 'Analyze everything notable in this image.'}"
                            else:
                                if selected_mode == ui["vis_modes"][0]:
                                    v_prompt = """
                                    ඔබ අභ්‍යවකාශ සහ හඳුනා නොගත් පියාසර වස්තූන් පිළිබඳ ඡායාරූප විශ්ලේෂණය කරන නෙබියුලා පද්ධතියයි. මෙම ඡායාරූපය පරීක්ෂා කර සිංහලෙන් වාර්තාවක් සකසන්න:
1. වස්තුවේ හැඩය, ආලෝකය, සෙවණැලි සහ චලන ලක්ෂණ විස්තර කරන්න.
2. මෙය සාමාන්‍ය ඩ්‍රෝන යානයක්, බැලූනයක්, කාච දෝෂයක් හෝ වායුගෝලීය සංසිද්ධියක් විය හැකිද, නැතහොත් අසාමාන්‍ය ලක්ෂණ පෙන්වයිද යන්න විග්‍රහ කරන්න.
                                    
                                    වැදගත් නීතියක්: කිසිම ඉංග්‍රීසි අකුරක් (A-Z) හෝ වරහන් භාවිතා නොකරන්න. සියලුම විද්‍යාත්මක නම් සිංහල අකුරෙන්ම උච්චාරණය වන පරිදි පමණක් ලියන්න.
                                    """
                                elif selected_mode == ui["vis_modes"][1]:
                                    v_prompt = """
                                    ඔබ නෙබියුලා තාරකා විද්‍යා විශ්ලේෂකයායි. මෙම අභ්‍යවකාශ ඡායාරූපයේ පෙනෙන තාරකා, නිහාරිකා හෝ ග්‍රහලෝක ව්‍යුහයන් සහ ඒවායේ විද්‍යාත්මක වැදගත්කම සිංහලෙන් පැහැදිලි කරන්න.
                                    වැදගත් නීතියක්: කිසිම ඉංග්‍රීසි අකුරක් (A-Z) හෝ වරහන් භාවිතා නොකරන්න.
                                    """
                                else:
                                    v_prompt = f"""
                                    ඔබ නෙබියුලා දෘශ්‍ය සාක්ෂි විශ්ලේෂකයායි. මෙම ඡායාරූපය පරීක්ෂා කර පහත ප්‍රශ්නයට සිංහලෙන් පිළිතුරු දෙන්න.
                                    වැදගත් නීතියක්: කිසිම ඉංග්‍රීසි අකුරක් (A-Z) හෝ වරහන් භාවිතා නොකරන්න.
                                    
                                    ප්‍රශ්නය: {custom_vis_query or 'මෙම ඡායාරූපයේ ඇති විශේෂ ලක්ෂණ විස්තර කරන්න.'}
                                    """

                            vis_ans, vis_mod = ask_ai([v_prompt, pil_img])
                            st.session_state.vision_analysis = vis_ans
                            st.session_state.vision_model = vis_mod

                            if vis_mod != "None":
                                generate_audio_file(
                                    vis_ans, active_voice, "visual_evidence.mp3")
                                st.session_state.active_audio = "visual_evidence.mp3"
                                st.session_state.track_name = "VISUAL_FORENSICS.MP3"
                                st.session_state.track_lang = "EN-UK" if lang == "English" else "SI-LK"
                                st.rerun()

                if st.session_state.vision_analysis:
                    st.success(
                        f"✅ {ui['model_tag']} `{st.session_state.vision_model}`")
                    st.markdown(
                        f'<div class="report-box">{st.session_state.vision_analysis}</div>', unsafe_allow_html=True)

        # TAB 5: Declassified PDF & Research Dossier Reader
        elif active_idx == 4:
            st.subheader(ui["pdf_sub"])

            pdf_source_choice = st.radio(
                ui["pdf_source"], ui["pdf_sources"], horizontal=True)
            pdf_bytes = None
            pdf_display_name = ""

            if pdf_source_choice == ui["pdf_sources"][0]:
                uploaded_pdf = st.file_uploader(ui["pdf_upload"], type=["pdf"])
                if uploaded_pdf is not None:
                    pdf_bytes = uploaded_pdf.read()
                    pdf_display_name = uploaded_pdf.name
            else:
                vault_pdfs = sorted([f for f in os.listdir(
                    LOCAL_VAULT_DIR) if f.lower().endswith(".pdf")])
                if vault_pdfs:
                    chosen_vault_pdf = st.selectbox(
                        ui["pdf_vault_sel"], vault_pdfs)
                    vault_pdf_path = os.path.join(
                        LOCAL_VAULT_DIR, chosen_vault_pdf)
                    with open(vault_pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    pdf_display_name = chosen_vault_pdf
                else:
                    st.info(ui["pdf_no_vault"])

            if pdf_bytes is not None:
                st.markdown(f"""
                    <div class="pursue-banner">
                        <div>
                            <span class="dossier-badge">DOSSIER LOADED • READY FOR AI EXTRACTION</span>
                            <div style="font-size:13px; color:#AFC1CD;">
                                <b>FILE:</b> {pdf_display_name} &nbsp;|&nbsp;
                                <b>SIZE:</b> {round(len(pdf_bytes) / 1024, 1)} KB
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                selected_pdf_mode = st.selectbox(
                    ui["pdf_mode"], ui["pdf_modes"])
                custom_pdf_query = ""
                if selected_pdf_mode == ui["pdf_modes"][2]:
                    custom_pdf_query = st.text_input(
                        ui["pdf_custom_q"], placeholder="e.g., Extract all radar altitudes, dates, and witness statements...")

                if st.button(ui["pdf_btn"], use_container_width=True):
                    with st.spinner(ui["pdf_spin"]):
                        if lang == "English":
                            if selected_pdf_mode == ui["pdf_modes"][0]:
                                p_prompt = """
                                You are NEBULA, an intelligence analyst examining a declassified UAP dossier or scientific paper.
                                Read this PDF carefully and provide a structured Executive Briefing:
1. Document Classification & Origin: Agency, date, location, and primary subject.
2. Key Findings & Witness/Sensor Evidence: Summarize the core events, observations, and conclusions.
3. Anomalous Significance: Highlight anything unexplained or scientifically notable.
                                """
                            elif selected_pdf_mode == ui["pdf_modes"][1]:
                                p_prompt = """
                                You are NEBULA, an aerospace telemetry and physics specialist. Extract all quantitative and technical details from this PDF:
1. Sensor types (radar, FLIR, electro-optical, visual), altitudes, speeds, headings, and durations.
2. Environmental conditions and physical anomalies recorded in the document.
                                """
                            else:
                                p_prompt = f"You are NEBULA, an intelligence and astrophysics analyst. Answer this specific question based strictly on the attached PDF document:\n\n{custom_pdf_query or 'Summarize the most important points in this document.'}"
                        else:
                            if selected_pdf_mode == ui["pdf_modes"][0]:
                                p_prompt = """
                                ඔබ පෙන්ටගනයේ රහස්‍යභාවය ඉවත් කළ ලිපිගොනු සහ විද්‍යාත්මක වාර්තා විශ්ලේෂණය කරන නෙබියුලා පද්ධතියයි. මෙම PDF ලේඛනය කියවා සිංහලෙන් පැහැදිලි සාරාංශයක් සකසන්න:
1. ලේඛනය අයත් ආයතනය, දිනය, ස්ථානය සහ ප්‍රධාන මාතෘකාව.
2. සිදුවීමේ ප්‍රධාන කරුණු, සාක්ෂි සහ නිගමන.
3. විද්‍යාත්මකව අසාමාන්‍ය හෝ වැදගත් කරුණු.
                                
                                වැදගත් නීතියක්: කිසිම ඉංග්‍රීසි අකුරක් (A-Z) හෝ වරහන් භාවිතා නොකරන්න. සියලුම විද්‍යාත්මක නම් සහ ආයතන නම් සිංහල අකුරෙන්ම උච්චාරණය වන පරිදි පමණක් ලියන්න.
                                """
                            elif selected_pdf_mode == ui["pdf_modes"][1]:
                                p_prompt = """
                                ඔබ නෙබියුලා රේඩාර් දත්ත විශ්ලේෂකයායි. මෙම PDF ලේඛනයේ ඇති රේඩාර් දත්ත, වේගය, උස, කාලය සහ භෞතික ලක්ෂණ සිංහලෙන් පැහැදිලි කරන්න.
                                වැදගත් නීතියක්: කිසිම ඉංග්‍රීසි අකුරක් (A-Z) හෝ වරහන් භාවිතා නොකරන්න.
                                """
                            else:
                                p_prompt = f"""
                                ඔබ නෙබියුලා පර්යේෂණ විශ්ලේෂකයායි. මෙම PDF ලේඛනය ඇසුරින් පහත ප්‍රශ්නයට සිංහලෙන් පිළිතුරු දෙන්න.
                                වැදගත් නීතියක්: කිසිම ඉංග්‍රීසි අකුරක් (A-Z) හෝ වරහන් භාවිතා නොකරන්න.
                                
                                ප්‍රශ්නය: {custom_pdf_query or 'මෙම ලේඛනයේ ඇති වැදගත්ම කරුණු සාරාංශ කරන්න.'}
                                """

                        pdf_part = types.Part.from_bytes(
                            data=pdf_bytes, mime_type="application/pdf")
                        pdf_ans, pdf_mod = ask_ai([p_prompt, pdf_part])
                        st.session_state.pdf_analysis = pdf_ans
                        st.session_state.pdf_model = pdf_mod

                        if pdf_mod != "None":
                            generate_audio_file(
                                pdf_ans, active_voice, "dossier_briefing.mp3")
                            st.session_state.active_audio = "dossier_briefing.mp3"
                            st.session_state.track_name = "DOSSIER_BRIEF.MP3"
                            st.session_state.track_lang = "EN-UK" if lang == "English" else "SI-LK"
                            st.rerun()

            if st.session_state.pdf_analysis:
                st.success(
                    f"✅ {ui['model_tag']} `{st.session_state.pdf_model}`")
                st.markdown(
                    f'<div class="report-box">{st.session_state.pdf_analysis}</div>', unsafe_allow_html=True)

        # TAB 6: Live ISS & Space Weather Radar
        elif active_idx == 5:
            st.subheader(ui["iss_sub"])

            if st.button(ui["iss_refresh"]):
                st.rerun()

            iss_data = fetch_json_safe(
                "https://api.wheretheiss.at/v1/satellites/25544")
            kp_data = fetch_json_safe(
                "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json")
            sw_alerts = fetch_json_safe(
                "https://services.swpc.noaa.gov/products/alerts.json")

            current_kp = "N/A"
            storm_status = "Nominal"
            if kp_data and len(kp_data) > 0:
                latest_kp_row = kp_data[-1]
                if isinstance(latest_kp_row, dict):
                    current_kp = latest_kp_row.get(
                        "Kp") or latest_kp_row.get("kp") or "N/A"
                elif isinstance(latest_kp_row, list) and len(latest_kp_row) > 1:
                    current_kp = latest_kp_row[1]
                try:
                    kp_val = float(current_kp)
                    if kp_val >= 5.0:
                        storm_status = f"G{int(kp_val - 4)} Geomagnetic Storm"
                    elif kp_val >= 4.0:
                        storm_status = "Active Solar Wind"
                    else:
                        storm_status = "Quiet Magnetosphere"
                except Exception:
                    storm_status = "Active Monitoring"

            if iss_data:
                lat = round(float(iss_data.get("latitude", 0)), 4)
                lon = round(float(iss_data.get("longitude", 0)), 4)
                alt = round(float(iss_data.get("altitude", 418)), 1)
                vel = round(float(iss_data.get("velocity", 27580)), 0)
                vis = str(iss_data.get("visibility", "daylight")).upper()

                st.markdown(f"""
                    <div class="pursue-banner">
                        <div>
                            <span class="dossier-badge">ISS ORBITAL TELEMETRY • NORAD ID 25544 • {vis}</span>
                            <div style="font-size:13px; color:#AFC1CD;">
                                <b>COORDINATES:</b> {lat}° LAT, {lon}° LON &nbsp;|&nbsp;
                                <b>ALTITUDE:</b> {alt} km &nbsp;|&nbsp;
                                <b>VELOCITY:</b> {int(vel):,} km/h &nbsp;|&nbsp;
                                <b>NOAA Kp-INDEX:</b> {current_kp} ({storm_status})
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                st.map([{"lat": lat, "lon": lon}], zoom=2)

                if st.button(ui["iss_btn"], use_container_width=True):
                    with st.spinner(ui["iss_spin"]):
                        latest_alert_txt = sw_alerts[0].get(
                            "message", "")[:350] if sw_alerts else "No active severe solar storm alerts."
                        if lang == "English":
                            iss_prompt = f"""
                            You are NEBULA, an orbital flight director and heliophysics analyst at Mission Control.
                            Provide a live tactical briefing in English based on these real-time telemetry readings:
- ISS Position: Latitude {lat}, Longitude {lon}, Altitude {alt} km, Velocity {int(vel)} km/h ({vis}).
- NOAA Geomagnetic Kp-Index: {current_kp} ({storm_status}).
- Latest NOAA Space Weather Bulletin: {latest_alert_txt}
                            Explain: 1) What geographic region or ocean the ISS is currently flying over, and 2) What the current Kp-index means for satellite communications, GPS, and Northern/Southern Lights (Aurora) visibility.
                            """
                        else:
                            iss_prompt = f"""
                            ඔබ නෙබියුලා මෙහෙයුම් මධ්‍යස්ථානයේ කක්ෂීය සහ සූර්ය කාලගුණ විශ්ලේෂකයායි.
                            පහත සජීවී දත්ත ඇසුරින් සිංහලෙන් පැහැදිලි වාර්තාවක් ලබා දෙන්න:
- ජාත්‍යන්තර අභ්‍යවකාශ මධ්‍යස්ථානයේ පිහිටීම: අක්ෂාංශ {lat}, දේශාංශ {lon}, උස කිලෝමීටර් {alt}, වේගය පැයට කිලෝමීටර් {int(vel)}.
- සූර්ය කුණාටු දර්ශකය: {current_kp} ({storm_status}).
- නවතම සූර්ය කාලගුණ පණිවිඩය: {latest_alert_txt}
                            
                            වැදගත් නීතියක්: කිසිම ඉංග්‍රීසි අකුරක් (A-Z) හෝ වරහන් භාවිතා නොකරන්න. සියලුම විද්‍යාත්මක නම් සහ ස්ථාන නම් සිංහල අකුරෙන්ම උච්චාරණය වන පරිදි පමණක් ලියන්න.
                            """
                        i_ans, i_mod = ask_ai(iss_prompt)
                        st.session_state.iss_analysis = i_ans
                        st.session_state.iss_model = i_mod

                        if i_mod != "None":
                            generate_audio_file(i_ans, active_voice,
                                                "iss_space_weather.mp3")
                            st.session_state.active_audio = "iss_space_weather.mp3"
                            st.session_state.track_name = "ISS_SPACE_RADAR.MP3"
                            st.session_state.track_lang = "EN-UK" if lang == "English" else "SI-LK"
                            st.rerun()
            else:
                st.warning(
                    "Unable to reach live ISS orbital telemetry API right now. Please try refreshing.")

            if st.session_state.iss_analysis:
                st.success(
                    f"✅ {ui['model_tag']} `{st.session_state.iss_model}`")
                st.markdown(
                    f'<div class="report-box">{st.session_state.iss_analysis}</div>', unsafe_allow_html=True)

            if sw_alerts:
                st.divider()
                st.markdown("#### ☀️ Live NOAA Space Weather Bulletins")
                for alert in sw_alerts[:3]:
                    issue_time = alert.get("issue_datetime", "")[:16]
                    msg_lines = [line.strip() for line in alert.get(
                        "message", "").splitlines() if line.strip()]
                    headline = next((l for l in msg_lines if "ALERT:" in l or "WARNING:" in l or "WATCH:" in l or "SUMMARY:" in l),
                                    msg_lines[0] if msg_lines else "NOAA Space Weather Update")
                    st.markdown(f"""
                        <div class="dossier-card">
                            <div class="dossier-badge">NOAA SWPC • {issue_time} UTC</div>
                            <div style="color:#E2E8F0; font-size:14px;">{headline}</div>
                        </div>
                    """, unsafe_allow_html=True)

        # TAB 7: Deep Research
        elif active_idx == 6:
            st.subheader(ui["t2_sub"])
            is_custom = preset_topic.startswith("Custom")
            if is_custom:
                default_text = ""
            elif lang == "English":
                default_text = f"""Provide a deep, scientifically grounded analysis of {preset_topic}, including current theories and unresolved mysteries."""
            else:
                default_text = f"""{preset_topic} පිළිබඳව නවීන විද්‍යාත්මක සාක්ෂි සහ නොවිසඳුණු අභිරහස් ඇසුරින් ගැඹුරු පැහැදිලි කිරීමක් ලබා දෙන්න."""

            user_query = st.text_area(
                ui["t2_input"], value=default_text, height=120, placeholder=ui["t2_placeholder"])

            if st.button(ui["t2_btn"], use_container_width=True):
                if user_query:
                    with st.spinner(ui["t2_spin"]):
                        if lang == "English":
                            custom_prompt = f"""You are NEBULA, an astrophysics and UAP expert. Provide a deep, clear, scientifically rigorous explanation in English for:\n\n{user_query}"""
                        else:
                            custom_prompt = f"""
                            ඔබ තාරකා විද්‍යා හා විශ්වීය අභිරහස් පිළිබඳ විශේෂඥ නෙබියුලා පද්ධතියයි. පහත ප්‍රශ්නයට ගැඹුරු, විද්‍යාත්මක නමුත් සරල සිංහල පැහැදිලි කිරීමක් දෙන්න.
                            වැදගත් නීතියක්: කිසිම ඉංග්‍රීසි අකුරක් (A-Z) හෝ වරහන් භාවිතා නොකරන්න. සියලුම ඉංග්‍රීසි විද්‍යාත්මක නම් සිංහල අකුරෙන්ම උච්චාරණය වන පරිදි පමණක් ලියන්න.
                            
                            ප්‍රශ්නය: {user_query}
                            """
                        answer, used_model = ask_ai(custom_prompt)
                        st.session_state.research_answer = answer
                        st.session_state.research_model = used_model

                        if used_model != "None":
                            generate_audio_file(
                                answer, active_voice, "research_answer.mp3")
                            st.session_state.active_audio = "research_answer.mp3"
                            st.session_state.track_name = "DEEP_RESEARCH.MP3"
                            st.session_state.track_lang = "EN-UK" if lang == "English" else "SI-LK"
                            st.rerun()
                else:
                    st.warning(ui["t2_warn"])

            if st.session_state.research_answer:
                st.info(
                    f"🧠 {ui['model_tag']} `{st.session_state.research_model}`")
                st.markdown(
                    f'<div class="report-box">{st.session_state.research_answer}</div>', unsafe_allow_html=True)
