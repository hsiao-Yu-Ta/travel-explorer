# Travel Explorer - Streamlit Cloud + iPhone
# Deploy: GitHub -> Streamlit Cloud
# Secrets: ANTHROPIC_API_KEY

import os, json, math, requests
import streamlit as st
import folium
from streamlit_folium import st_folium
from dataclasses import dataclass, asdict
from typing import List

def get_secret(key, default=""):
    try:    return st.secrets.get(key, os.getenv(key, default))
    except: return os.getenv(key, default)

ANTHROPIC_API_KEY = get_secret("ANTHROPIC_API_KEY")

@dataclass
class Spot:
    name: str
    lat: float
    lng: float
    category: str
    rating: float
    description: str
    tips: str
    hours: str
    region: str
    duration: int = 90

SPOTS_DB: List[Spot] = [
    Spot("Jiufen Old Street",25.1093,121.8442,"History",4.7,
         "A nostalgic mountain town with lantern-lit alleys, said to inspire Spirited Away.",
         "Visit after 4pm for smaller crowds. Bring an umbrella - cobblestones get slippery.",
         "All day (shops ~10:00-21:00)","Taiwan",120),
    Spot("Taroko National Park",24.1577,121.6218,"Nature",4.9,
         "Spectacular marble gorge with world-class hiking trails like Swallow Grotto.",
         "Check for typhoon closures. Zhuilu Old Trail requires advance permit.",
         "Open year-round, visitor center 08:00-17:00","Taiwan",300),
    Spot("Taipei 101",25.0338,121.5646,"Entertainment",4.5,
         "Taiwan landmark - 89F observatory overlooks the entire Taipei basin.",
         "Buy tickets online to skip queues. Clear days offer views to the coast.",
         "Observatory 09:00-22:00 (last entry 21:15)","Taiwan",120),
    Spot("Sun Moon Lake",23.8650,120.9170,"Nature",4.7,
         "Taiwan's largest alpine lake. Cycling around the lake is the top activity.",
         "Morning mist is magical. Cycling the full loop takes 3-4 hours.",
         "Open year-round","Taiwan",240),
    Spot("Alishan Forest",23.5116,120.8037,"Nature",4.8,
         "Famous for sunrise, sea of clouds, giant trees and forest railway.",
         "Book the sunrise train early. Cherry blossom season is March-April.",
         "Open year-round, arrive early","Taiwan",300),
    Spot("Kenting National Park",21.9500,120.8167,"Nature",4.6,
         "Taiwan's southernmost tropical coastal park with snorkeling and water sports.",
         "Summer northeast winds hit east coast - choose west coast spots. Use sunscreen.",
         "Open year-round","Taiwan",300),
    Spot("Shilin Night Market",25.0878,121.5241,"Food",4.5,
         "Taipei's largest night market - oyster omelette, giant fried chicken, sausages.",
         "Weekdays are less crowded. The underground food court is a must.",
         "~17:00-24:00","Taiwan",120),
    Spot("National Palace Museum",25.1023,121.5485,"History",4.8,
         "Nearly 700,000 Chinese artifacts. Jade Cabbage and Meat-shaped Stone are iconic.",
         "Fri-Sat open until 21:00. Audio guide recommended.",
         "Tue-Sun 08:30-18:30 (Fri-Sat until 21:00)","Taiwan",180),
    Spot("Chihkan Tower Tainan",23.0034,120.2032,"History",4.6,
         "Dutch-era fort built in 1653, one of Taiwan's most iconic historic buildings.",
         "Combine with Anping Fort and Eternal Golden Castle for a full heritage day.",
         "08:30-21:30","Taiwan",90),
    Spot("Fushimi Inari Shrine",34.9671,135.7727,"History",4.9,
         "Thousands of vermilion torii gates - one of Japan's most visited shrines.",
         "Go at 5-7am for best light and fewer crowds. Full walk takes 2-3 hours.",
         "Open 24 hours","Japan",150),
    Spot("Senso-ji Temple Tokyo",35.7147,139.7966,"History",4.7,
         "Tokyo's oldest temple with Nakamise shopping street full of traditional crafts.",
         "Early morning is best for photos. Sumida River views nearby are beautiful.",
         "Open year-round (main hall 06:00-17:00)","Japan",120),
    Spot("Tokyo Disneyland",35.6329,139.8804,"Entertainment",4.8,
         "One of the world's most popular Disney parks. Night parade is unmissable.",
         "Buy fast passes in advance. Weekdays have shorter queues.",
         "08:00-22:00 (seasonal variations)","Japan",480),
    Spot("Mount Fuji",35.3606,138.7274,"Nature",4.9,
         "Japan's highest peak at 3776m. Five Lakes area is beautiful year-round.",
         "Climbing season is July-August. Views from Shinkansen are stunning.",
         "Climbing season: early Jul to early Sep","Japan",240),
    Spot("Dotonbori Osaka",34.6687,135.5014,"Food",4.7,
         "Osaka's most vibrant food street - takoyaki, kushikatsu, ramen all here.",
         "Best at night when neon signs light up. Compare takoyaki from multiple stalls.",
         "All day (shops 11:00-23:00)","Japan",120),
    Spot("Gyeongbokgung Palace",37.5796,126.9770,"History",4.7,
         "Joseon Dynasty's main palace. Changing of the Guard is a daily highlight.",
         "Hanbok rental gives free or discounted entry. Guard ceremony: 10:00 and 14:00.",
         "Mar-May/Sep-Oct 09:00-18:00, extended summer hours","Korea",180),
    Spot("Myeongdong Seoul",37.5636,126.9869,"Shopping",4.5,
         "Seoul's busiest shopping street - K-beauty, fashion, street food all in one place.",
         "Get TAX REFUND receipts at eligible stores. Best in the evening.",
         "All day (shops ~10:00-23:00)","Korea",180),
    Spot("Hallasan Jeju",33.3617,126.5292,"Nature",4.8,
         "Korea's highest peak with unique volcanic landscape. Beautiful in all seasons.",
         "Check trail status before going. Autumn foliage October-November is stunning.",
         "Before sunrise to 2 hours before sunset","Korea",300),
    Spot("Eiffel Tower Paris",48.8584,2.2945,"History",4.8,
         "The world's most famous landmark. Light show every hour at night is spectacular.",
         "Book tickets 1-2 months ahead. Night light show lasts 5 minutes on the hour.",
         "09:00-24:00 (extended in summer)","France",180),
    Spot("Colosseum Rome",41.8902,12.4922,"History",4.8,
         "Built in 70-80 AD, one of the greatest architectural achievements of antiquity.",
         "Get combo ticket with Roman Forum. Avoid midday heat.",
         "09:00 to 1 hour before sunset","Italy",150),
    Spot("Sagrada Familia Barcelona",41.4036,2.1744,"History",4.9,
         "Gaudi's masterpiece under construction since 1882. Interior light effects are breathtaking.",
         "Must book online - often sells out on-site. Add tower ticket for city views.",
         "09:00-20:00 (seasonal variations)","Spain",150),
    Spot("Santorini Greece",36.3932,25.4615,"Nature",4.9,
         "Blue-domed white villages on the Aegean - Oia sunset is world-famous.",
         "Oia sunset draws huge crowds - arrive early for a good spot. Book July-Aug stays 6 months ahead.",
         "Open year-round","Greece",480),
    Spot("Central Park New York",40.7851,-73.9683,"Nature",4.8,
         "843-acre urban oasis in Manhattan. Strawberry Fields and Bethesda Fountain are must-sees.",
         "Autumn foliage October-November is stunning. Rent a bike to tour the whole park.",
         "Year-round 06:00-01:00","USA",180),
    Spot("Grand Canyon National Park",36.1069,-112.1129,"Nature",4.9,
         "Colorado River carved this breathtaking landscape over millions of years.",
         "Bring plenty of water in summer heat. Skywalk is at the West Rim separately.",
         "Open 24 hours year-round","USA",300),
    Spot("Statue of Liberty New York",40.6892,-74.0445,"History",4.7,
         "Symbol of American freedom on Liberty Island. Crown tickets sell out a year ahead.",
         "Buy ferry tickets online. Ferries from Battery Park Manhattan or New Jersey.",
         "Ferry 08:30-15:30 (last departure)","USA",180),
    Spot("Iceland Blue Lagoon",63.8800,-22.4550,"Nature",4.8,
         "Famous geothermal spa with milky-blue mineral-rich waters surrounded by lava fields.",
         "Book well in advance especially in summer. Visit at sunset for magical atmosphere.",
         "08:00-22:00 (hours vary by season)","Iceland",180),
    Spot("Reykjavik Iceland",64.1355,-21.8954,"History",4.7,
         "Iceland's colorful capital with Hallgrimskirkja church, street art and great seafood.",
         "Base for Northern Lights tours in winter. Midnight sun in summer is surreal.",
         "Open year-round","Iceland",240),
    Spot("Vatnajokull Glacier Iceland",64.4163,-16.9769,"Nature",4.9,
         "Europe's largest glacier with ice caves, glacier hikes and diamond beach nearby.",
         "Ice cave tours run November to March only. Book a certified guide - essential for safety.",
         "Tours depart from Jokulsarlon Glacier Lagoon","Iceland",300),
    Spot("Northern Lights Iceland",65.0000,-19.0000,"Nature",4.9,
         "Aurora borealis viewing - best from September to March away from city lights.",
         "Check aurora forecast app. Vik, Thingvellir and Snaefellsnes are top spots.",
         "Best September to March, clear dark nights","Iceland",180),
    Spot("Jokulsarlon Glacier Lagoon",64.0784,-16.2306,"Nature",4.9,
         "Stunning glacial lagoon with floating icebergs calving from Breidamerkurjokull glacier.",
         "Diamond Beach nearby has ice chunks on black sand - incredible photography.",
         "Open year-round, 24hrs in summer","Iceland",150),
]

ALL_REGIONS = sorted(set(s.region for s in SPOTS_DB))
ALL_CATS    = ["All", "Nature", "History", "Food", "Shopping", "Entertainment"]
CAT_ICON    = {"Nature":"nature","History":"landmark","Food":"food","Shopping":"shopping-bag","Entertainment":"star"}
CAT_EMOJI   = {"Nature":"green","History":"red","Food":"orange","Shopping":"purple","Entertainment":"blue"}

def rating_stars(r):
    if r >= 4.8: return "5.0 stars"
    if r >= 4.5: return "4.5 stars"
    if r >= 4.0: return "4.0 stars"
    return "3.5 stars"

def haversine(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2-lat1)
    dlng = math.radians(lng2-lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def nearest_order(spots):
    if not spots: return []
    result = [spots[0]]
    remaining = list(spots[1:])
    while remaining:
        last = result[-1]
        nearest = min(remaining, key=lambda s: haversine(last.lat, last.lng, s.lat, s.lng))
        result.append(nearest)
        remaining.remove(nearest)
    return result

def ai_search_spots(query):
    api_key = st.session_state.get("api_key_input", "") or ANTHROPIC_API_KEY
    if not api_key:
        st.info("Open sidebar (top-left) and enter your Anthropic API Key to enable AI search.")
        return []
    prompt = (
        "Search for tourist attractions in: " + query + "\n\n"
        "Return exactly 5 top attractions as a JSON array. Each item must have:\n"
        "name, lat, lng, category (one of: Nature/History/Food/Shopping/Entertainment), "
        "rating (3.5-5.0), description (English, 50-80 chars), "
        "tips (English, 30-50 chars), hours, region, duration (minutes as integer)\n\n"
        "Return ONLY the JSON array. No markdown, no explanation."
    )
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30,
        )
        rj = resp.json()
        if "error" in rj:
            st.warning("API Error: " + rj["error"].get("message", "Check your API Key"))
            return []
        content_list = rj.get("content", [])
        if not content_list:
            st.warning("Empty API response. Please try again.")
            return []
        text = content_list[0].get("text", "").strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        data = json.loads(text)
        return [Spot(**item) for item in data]
    except json.JSONDecodeError:
        st.warning("AI returned invalid format. Please try again.")
        return []
    except Exception as e:
        st.warning("AI search failed: " + str(e))
        return []

def make_map(spots, selected=None, center=None):
    if not spots:
        return folium.Map(location=[23.5, 121.0], zoom_start=7, tiles="CartoDB dark_matter")
    if center:
        clat, clng = center
    else:
        clat = sum(s.lat for s in spots) / len(spots)
        clng = sum(s.lng for s in spots) / len(spots)
    lat_range = max(s.lat for s in spots) - min(s.lat for s in spots)
    zoom = 14 if len(spots) == 1 else (10 if lat_range < 1 else (7 if lat_range < 5 else 5))
    m = folium.Map(location=[clat, clng], zoom_start=zoom, tiles="CartoDB dark_matter")
    if selected and len(selected) > 1:
        sel_spots = [s for s in spots if s.name in selected]
        ordered = nearest_order(sel_spots)
        coords = [[s.lat, s.lng] for s in ordered]
        folium.PolyLine(coords, color="#f0c040", weight=2.5, opacity=0.8, dash_array="8").add_to(m)
    for spot in spots:
        is_sel = selected and spot.name in selected
        color = CAT_EMOJI.get(spot.category, "gray")
        popup_html = (
            "<div style='font-family:sans-serif;min-width:180px'>"
            "<b style='font-size:14px'>" + spot.name + "</b><br>"
            "<span style='color:#888;font-size:11px'>" + spot.category + " | " + str(spot.rating) + " stars</span><br><br>"
            "<span style='font-size:12px'>" + spot.description + "</span><br><br>"
            "<div style='background:#f5f5f5;padding:6px;border-radius:4px;font-size:11px'>"
            "Tip: " + spot.tips + "</div><br>"
            "<span style='color:#888;font-size:11px'>Hours: " + spot.hours + "</span>"
            "</div>"
        )
        folium.Marker(
            [spot.lat, spot.lng],
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=("SELECTED: " if is_sel else "") + spot.name + " " + str(spot.rating),
            icon=folium.Icon(color=color, icon_color="white" if is_sel else "lightgray",
                             icon="star" if is_sel else "info-sign", prefix="glyphicon"),
        ).add_to(m)
    return m

def itinerary_card(spots, days):
    if not spots: return
    ordered = nearest_order(spots)
    total_mins = sum(s.duration for s in ordered)
    spots_per_day = math.ceil(len(ordered) / days)
    st.markdown(
        "<div style='border:1px solid #2d3a4a;border-radius:8px;padding:14px;background:#0d1117;margin-bottom:12px'>"
        "<div style='font-family:monospace;font-size:10px;color:#58697a;letter-spacing:.1em;margin-bottom:10px'>"
        "// Itinerary - " + str(len(ordered)) + " spots / " + str(days) + " days / ~" + str(total_mins//60) + "h total"
        "</div>",
        unsafe_allow_html=True
    )
    for day in range(days):
        day_spots = ordered[day*spots_per_day:(day+1)*spots_per_day]
        if not day_spots: continue
        day_mins = sum(s.duration for s in day_spots)
        st.markdown(
            "<div style='font-size:12px;color:#f0c040;font-weight:700;margin:10px 0 6px'>"
            "Day " + str(day+1) + " (~" + str(day_mins//60) + "h " + str(day_mins%60) + "m)"
            "</div>",
            unsafe_allow_html=True
        )
        for j, spot in enumerate(day_spots):
            dist = (" -> " + str(round(haversine(day_spots[j-1].lat, day_spots[j-1].lng, spot.lat, spot.lng), 1)) + "km") if j > 0 else ""
            st.markdown(
                "<div style='margin-bottom:8px;padding:8px;background:#141b24;border-radius:6px;"
                "border-left:3px solid #f0c040'>"
                "<div style='font-size:13px;font-weight:600;color:#e6edf3'>" + spot.name + "<span style='font-size:10px;color:#58697a;margin-left:6px'>" + dist + "</span></div>"
                "<div style='font-size:11px;color:#58697a'>" + str(spot.rating) + " stars | stay ~" + str(spot.duration) + " min</div>"
                "<div style='font-size:11px;color:#79c0ff;margin-top:3px'>Tip: " + spot.tips + "</div>"
                "</div>",
                unsafe_allow_html=True
            )
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Travel Explorer", page_icon="map",
                       layout="wide", initial_sidebar_state="collapsed")
    st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap');
  html,body,[class*="css"]{font-family:'Noto Sans TC',sans-serif !important;}
  .block-container{padding:0.8rem 0.7rem 3rem !important;max-width:100% !important;}
  #MainMenu,footer{visibility:hidden;}
  header[data-testid="stHeader"]{background:#080c10 !important;}
  .stButton>button{background:#0d1117 !important;color:#c9d1d9 !important;
    border:1px solid #2d3a4a !important;border-radius:6px !important;
    font-size:13px !important;width:100%;}
  .stButton>button:hover{border-color:#58697a !important;color:#e6edf3 !important;}
  section[data-testid="stSidebar"]{background:#0d1117 !important;border-right:1px solid #1c2333 !important;}
  .stTextInput>div>div>input,.stSelectbox>div>div{
    background:#0d1117 !important;border:1px solid #2d3a4a !important;
    color:#c9d1d9 !important;font-size:13px !important;}
  .main{padding-bottom:env(safe-area-inset-bottom) !important;}
</style>
""", unsafe_allow_html=True)

    if "my_list" not in st.session_state:     st.session_state["my_list"] = []
    if "ai_spots" not in st.session_state:    st.session_state["ai_spots"] = []
    if "search_done" not in st.session_state: st.session_state["search_done"] = False

    st.markdown('<h2 style="font-family:monospace;font-size:16px;color:#e6edf3;margin:0;padding:6px 0">Travel Explorer</h2>', unsafe_allow_html=True)

    col_s, col_b = st.columns([4, 1])
    with col_s:
        query = st.text_input("", placeholder="Search: Iceland, Kyoto, Kenting...", label_visibility="collapsed")
    with col_b:
        search_btn = st.button("Search", use_container_width=True)

    col_r, col_c = st.columns(2)
    with col_r:
        region_filter = st.selectbox("Region", ["All"] + ALL_REGIONS, label_visibility="collapsed")
    with col_c:
        cat_filter = st.selectbox("Category", ALL_CATS, label_visibility="collapsed")

    if search_btn and query:
        with st.spinner("AI searching for spots in " + query + "..."):
            ai_results = ai_search_spots(query)
            if ai_results:
                st.session_state["ai_spots"] = ai_results
                st.session_state["search_done"] = True
                st.success("Found " + str(len(ai_results)) + " spots!")
            else:
                st.info("No AI results. Showing built-in database. Set ANTHROPIC_API_KEY to enable AI search.")

    all_spots = SPOTS_DB + st.session_state["ai_spots"]
    filtered = all_spots
    if region_filter != "All":
        filtered = [s for s in filtered if s.region == region_filter]
    if cat_filter != "All":
        filtered = [s for s in filtered if s.category == cat_filter]
    if query and not st.session_state["search_done"]:
        q = query.lower()
        filtered = [s for s in filtered if q in s.name.lower() or q in s.region.lower() or q in s.description.lower()]

    st.markdown('<p style="font-family:monospace;font-size:10px;color:#58697a;letter-spacing:.1em;margin:12px 0 6px">// Map (click markers for details)</p>', unsafe_allow_html=True)
    my_names = [s.name for s in st.session_state["my_list"]]
    m = make_map(filtered if filtered else all_spots, selected=my_names)
    st_folium(m, width="100%", height=380, returned_objects=["last_object_clicked"])

    st.markdown('<p style="font-family:monospace;font-size:10px;color:#58697a;letter-spacing:.1em;margin:14px 0 8px">// Spots (' + str(len(filtered)) + ')</p>', unsafe_allow_html=True)

    display_spots = filtered if filtered else all_spots
    for spot in display_spots:
        in_list = spot.name in my_names
        with st.expander(spot.name + "  " + str(spot.rating) + " stars  " + ("SAVED" if in_list else ""), expanded=False):
            st.markdown(
                "<div style='font-size:13px;color:#c9d1d9;line-height:1.8'>"
                "<div style='margin-bottom:8px'>" + spot.description + "</div>"
                "<div style='background:#141b24;padding:8px 10px;border-radius:6px;margin-bottom:8px'>"
                "<span style='color:#79c0ff'>Tip</span>: " + spot.tips + "</div>"
                "<div style='font-size:11px;color:#58697a'>"
                "Hours: " + spot.hours + " | Stay: " + str(spot.duration) + " min | Region: " + spot.region
                + "</div></div>",
                unsafe_allow_html=True
            )
            col1, col2 = st.columns(2)
            with col1:
                if in_list:
                    if st.button("Remove from itinerary", key="rm_" + spot.name):
                        st.session_state["my_list"] = [s for s in st.session_state["my_list"] if s.name != spot.name]
                        st.rerun()
                else:
                    if st.button("+ Add to itinerary", key="add_" + spot.name):
                        st.session_state["my_list"].append(spot)
                        st.rerun()

    my_list = st.session_state["my_list"]
    if my_list:
        st.markdown('<p style="font-family:monospace;font-size:10px;color:#f0c040;letter-spacing:.1em;margin:16px 0 8px">// My Itinerary</p>', unsafe_allow_html=True)
        days = st.slider("Number of days", 1, 7, min(3, len(my_list)), key="days_slider")
        itinerary_card(my_list, days)
        st.markdown('<p style="font-family:monospace;font-size:10px;color:#58697a;letter-spacing:.1em;margin:8px 0 6px">// Route Map</p>', unsafe_allow_html=True)
        route_map = make_map(my_list, selected=[s.name for s in my_list])
        st_folium(route_map, width="100%", height=320, key="route_map")
        if st.button("Clear itinerary"):
            st.session_state["my_list"] = []
            st.rerun()

    with st.sidebar:
        st.markdown("### Settings")
        ak = st.text_input(
            "Anthropic API Key",
            value=st.session_state.get("api_key_input", ANTHROPIC_API_KEY),
            type="password",
            placeholder="Enable AI search",
            key="api_key_input"
        )
        if ak:
            st.success("Key set - search any destination!")
        st.markdown("---")
        st.markdown("""
**How to use:**
- Search any city/region
- Click map markers for details
- Add spots to your itinerary
- Adjust days to split the plan
- Route map shows optimal order

**Categories:**
- Nature
- History
- Food
- Shopping
- Entertainment
""")

    st.markdown('<p style="font-family:monospace;font-size:10px;color:#2d3a4a;margin-top:16px">v2 | Built-in DB + Claude AI search</p>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
