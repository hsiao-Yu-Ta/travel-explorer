# Travel Explorer - Streamlit Cloud + iPhone Version

# Features: Built-in DB + Claude AI search + Folium map + Auto itinerary

# Deploy: GitHub -> Streamlit Cloud | Secrets: ANTHROPIC_API_KEY

import os, json, math, datetime, requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import folium
from streamlit_folium import st_folium
from dataclasses import dataclass, field, asdict
from typing import List

# ── Secrets ───────────────────────────────────────────────

def get_secret(key, default=””):
try:    return st.secrets.get(key, os.getenv(key, default))
except: return os.getenv(key, default)

ANTHROPIC_API_KEY = get_secret(“ANTHROPIC_API_KEY”)

# ════════════════════════════════════════════════

# 資料結構

# ════════════════════════════════════════════════

@dataclass
class Spot:
name: str
lat: float
lng: float
category: str       # 自然景觀 / 歷史文化 / 美食 / 購物 / 娛樂
rating: float       # 1-5
description: str
tips: str           # 旅遊小提示
hours: str          # 開放時間
region: str         # 所屬地區
duration: int = 90  # 建議停留分鐘數

# ════════════════════════════════════════════════

# 內建景點資料庫

# ════════════════════════════════════════════════

SPOTS_DB: List[Spot] = [
# ── 台灣 ──────────────────────────────────────────────
Spot(“九份老街”,25.1093,121.8442,“歷史文化”,4.7,
“充滿懷舊氛圍的山城老街，以《千與千尋》取景地聞名，夜晚燈籠點亮格外迷人。”,
“下午4點後人潮漸少，建議傍晚前往欣賞夜景。雨天記得帶傘，石板路濕滑。”,
“全天開放（商店約10:00-21:00）”,“台灣”,120),
Spot(“太魯閣國家公園”,24.1577,121.6218,“自然景觀”,4.9,
“壯觀的大理石峽谷地形，燕子口步道、錐麓古道等健行路線聞名全球。”,
“颱風季節注意封路公告。錐麓古道需提前申請入山許可。”,
“全年開放，遊客中心08:00-17:00”,“台灣”,300),
Spot(“台北101”,25.0338,121.5646,“娛樂”,4.5,
“台灣地標性建築，89樓觀景台可俯瞰整個台北盆地，購物中心有精品與美食。”,
“購買網路預售票可省排隊時間。晴天能遠眺淡水河出海口。”,
“觀景台09:00-22:00（最後入場21:15）”,“台灣”,120),
Spot(“日月潭”,23.8650,120.9170,“自然景觀”,4.7,
“台灣最大的高山湖泊，環湖騎自行車是最受歡迎的活動，湖光山色四季皆美。”,
“清晨的湖面薄霧最美。租自行車環湖約需3-4小時。”,
“全年開放”,“台灣”,240),
Spot(“阿里山國家森林遊樂區”,23.5116,120.8037,“自然景觀”,4.8,
“以日出、雲海、神木、小火車聞名，春季賞櫻花更是人氣爆棚。”,
“清晨搭小火車看日出需提前訂票。春季（3-4月）是賞花旺季。”,
“全年開放，建議早上入園”,“台灣”,300),
Spot(“墾丁國家公園”,21.9500,120.8167,“自然景觀”,4.6,
“台灣最南端的熱帶海洋公園，白沙灣、船帆石等景點，浮潛與水上活動豐富。”,
“夏季（6-8月）東北季風強，建議選擇西海岸景點。防曬必備。”,
“全年開放”,“台灣”,300),
Spot(“士林夜市”,25.0878,121.5241,“美食”,4.5,
“台北最大夜市，蚵仔煎、大雞排、士林大香腸等必吃美食應有盡有。”,
“周末人潮洶湧，建議平日或早點前往。地下美食區是必去重點。”,
“約17:00-24:00”,“台灣”,120),
Spot(“故宮博物院”,25.1023,121.5485,“歷史文化”,4.8,
“收藏中華文物近70萬件，翠玉白菜、肉形石是必看鎮館之寶。”,
“週五六延長至21:00。建議租語音導覽。”,
“週二至週日 08:30-18:30（週五六至21:00）”,“台灣”,180),
Spot(“平溪天燈”,25.0256,121.7382,“歷史文化”,4.6,
“每逢元宵節放天燈的傳統民俗，平溪老街也有各式懷舊小吃與老建築。”,
“元宵節（農曆正月十五）天燈節人潮最多。平日也有天燈可放。”,
“全天開放”,“台灣”,150),
Spot(“台南赤崁樓”,23.0034,120.2032,“歷史文化”,4.6,
“建於1653年的荷蘭時代城堡，台灣最具代表性的歷史建築之一，周邊小吃林立。”,
“結合周邊安平古堡、億載金城規劃一日古蹟遊。”,
“08:30-21:30”,“台灣”,90),

```
# ── 日本 ──────────────────────────────────────────────
Spot("京都伏見稻荷大社",34.9671,135.7727,"歷史文化",4.9,
     "以數千座朱紅色鳥居聞名全球，是日本最受歡迎的神社之一。",
     "清晨5-7點光線最美且人少。全程走完約2-3小時。",
     "全年24小時開放","日本",150),
Spot("東京淺草寺",35.7147,139.7966,"歷史文化",4.7,
     "東京最古老的寺廟，仲見世商店街有各式傳統工藝品與點心。",
     "清晨人少最適合拍照。周邊的隅田川夜景也很美。",
     "全年開放（寺院06:00-17:00）","日本",120),
Spot("東京迪士尼樂園",35.6329,139.8804,"娛樂",4.8,
     "全球最受歡迎的迪士尼樂園之一，夜間遊行與煙火秀是必看節目。",
     "提前購買快速通關票。平日人潮較少。",
     "08:00-22:00（依季節調整）","日本",480),
Spot("富士山",35.3606,138.7274,"自然景觀",4.9,
     "日本最高峰（3776m），登山季7-8月，周邊五湖地區四季皆美。",
     "登山需提前規劃體力與裝備。從新幹線或湖邊拍富士山最美。",
     "登山季7月上旬-9月上旬","日本",240),
Spot("大阪道頓堀",34.6687,135.5014,"美食",4.7,
     "大阪最熱鬧的美食街，章魚燒、串炸、拉麵密集，格力高跑者看板是地標。",
     "晚上霓虹燈亮起氣氛最佳。記得嘗試各家的章魚燒比較。",
     "全天（商店11:00-23:00）","日本",120),

# ── 韓國 ──────────────────────────────────────────────
Spot("首爾景福宮",37.5796,126.9770,"歷史文化",4.7,
     "朝鮮王朝的正宮，換崗儀式是每日必看景點，周邊仁寺洞文化街值得逛。",
     "穿韓服入場可享優惠或免費。換崗儀式時間：10:00/14:00。",
     "3-5月/9-10月 09:00-18:00，夏季延長","韓國",180),
Spot("首爾明洞",37.5636,126.9869,"購物",4.5,
     "首爾最繁華的購物街，美妝、服飾、街頭小吃全部聚集，是購物天堂。",
     "退稅商店記得索取TAX REFUND收據。晚上逛街最熱鬧。",
     "全天（商店約10:00-23:00）","韓國",180),
Spot("濟州島漢拏山",33.3617,126.5292,"自然景觀",4.8,
     "韓國最高峰，火山地形形成獨特的自然景觀，登山步道四季各有美景。",
     "提前確認步道開放狀態。秋季紅葉（10-11月）最美。",
     "日出前30分鐘-日落前2小時","韓國",300),

# ── 歐洲 ──────────────────────────────────────────────
Spot("巴黎艾菲爾鐵塔",48.8584,2.2945,"歷史文化",4.8,
     "世界最著名地標之一，夜晚整點的燈光秀令人震撼，從戰神廣場拍攝最美。",
     "提前1-2個月網路訂票。頂層需另購票。夜晚燈光秀每整點持續5分鐘。",
     "09:00-24:00（夏季延長）","法國",180),
Spot("羅馬競技場",41.8902,12.4922,"歷史文化",4.8,
     "建於西元70-80年的古羅馬圓形競技場，是古代世界最偉大的建築成就之一。",
     "建議搭配羅馬廣場、帕拉丁諾山丘套票。避開正中午的烈日。",
     "09:00-日落前1小時","義大利",150),
Spot("巴塞隆納聖家堂",41.4036,2.1744,"歷史文化",4.9,
     "高第設計的曠世傑作，自1882年動工至今仍未完成，內部光影效果絕美。",
     "必須提前網路訂票，現場常售罄。加購塔樓門票可俯瞰市區。",
     "09:00-20:00（依季節調整）","西班牙",150),
Spot("希臘聖托里尼",36.3932,25.4615,"自然景觀",4.9,
     "藍頂白牆的愛琴海小島，伊亞村的日落被譽為全球最美，是蜜月勝地首選。",
     "伊亞日落人潮極多，建議提早佔位。旺季（7-8月）住宿需提前半年訂。",
     "全年開放","希臘",480),

# ── 美洲 ──────────────────────────────────────────────
Spot("紐約中央公園",40.7851,-73.9683,"自然景觀",4.8,
     "紐約市中心的843英畝城市綠洲，四季各有風情，草莓園、貝塞斯達噴泉是必訪景點。",
     "秋季（10-11月）紅葉最美。租自行車環遊全園約需2-3小時。",
     "全年06:00-01:00","美國",180),
Spot("大峽谷國家公園",36.1069,-112.1129,"自然景觀",4.9,
     "科羅拉多河侵蝕數百萬年造就的壯觀地貌，南緣全年開放，日出日落最震撼。",
     "夏季極熱，帶足水分。玻璃橋（大峽谷西緣）需另外前往。",
     "全年24小時開放","美國",300),
Spot("紐約自由女神像",40.6892,-74.0445,"歷史文化",4.7,
     "美國自由的象徵，搭渡輪前往自由島，皇冠需提前一年預訂門票。",
     "渡輪票需提前網路購買。從曼哈頓砲台公園或紐澤西都有渡輪。",
     "渡輪 08:30-15:30（最後班次）","美國",180),
```

]

# ════════════════════════════════════════════════

# 工具函數

# ════════════════════════════════════════════════

ALL_REGIONS  = sorted(set(s.region for s in SPOTS_DB))
ALL_CATS     = [“全部”, “自然景觀”, “歷史文化”, “美食”, “購物”, “娛樂”]
CAT_ICON     = {“自然景觀”:“🌿”,“歷史文化”:“🏛️”,“美食”:“🍜”,“購物”:“🛍️”,“娛樂”:“🎡”}
CAT_COLOR    = {“自然景觀”:“green”,“歷史文化”:“red”,“美食”:“orange”,“購物”:“purple”,“娛樂”:“blue”}
STAR_RATINGS = {5:“⭐⭐⭐⭐⭐”, 4.5:“⭐⭐⭐⭐½”, 4:“⭐⭐⭐⭐”, 3.5:“⭐⭐⭐½”}

def rating_stars(r):
if r >= 4.8: return “⭐⭐⭐⭐⭐”
if r >= 4.5: return “⭐⭐⭐⭐½”
if r >= 4.0: return “⭐⭐⭐⭐”
return “⭐⭐⭐½”

def haversine(lat1, lng1, lat2, lng2):
“”“計算兩點距離（公里）”””
R = 6371
dlat = math.radians(lat2-lat1); dlng = math.radians(lng2-lng1)
a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlng/2)**2
return R * 2 * math.asin(math.sqrt(a))

def nearest_order(spots: List[Spot]) -> List[Spot]:
“”“貪婪最近鄰演算法排出最佳動線”””
if not spots: return []
result = [spots[0]]; remaining = spots[1:]
while remaining:
last = result[-1]
nearest = min(remaining, key=lambda s: haversine(last.lat, last.lng, s.lat, s.lng))
result.append(nearest); remaining.remove(nearest)
return result

# ════════════════════════════════════════════════

# Claude AI 景點搜尋

# ════════════════════════════════════════════════

def ai_search_spots(query: str) -> List[Spot]:
“”“用 Claude API 即時搜尋景點，回傳結構化資料”””
# ★ 修正：優先讀 session_state（側邊欄輸入），再讀 Secrets
api_key = st.session_state.get(“api_key_input”, “”) or ANTHROPIC_API_KEY
if not api_key:
st.info(“請點左上角 ☰ 展開側邊欄，填入 Anthropic API Key 後再搜尋。”)
return []
prompt = f””“使用者想搜尋「{query}」的旅遊景點。

請回傳該地區最值得造訪的5個景點，格式為 JSON 陣列，每個景點包含以下欄位：

- name: 景點中文名稱
- lat: 緯度（數字）
- lng: 經度（數字）
- category: 類型（只能是：自然景觀/歷史文化/美食/購物/娛樂 其中之一）
- rating: 評分（3.5-5.0 的數字）
- description: 景點介紹（50-80字）
- tips: 旅遊小提示（30-50字）
- hours: 開放時間
- region: 所在國家或地區
- duration: 建議停留分鐘數（數字）

只回傳 JSON 陣列，不要其他任何文字或 markdown。”””
try:
resp = requests.post(
“https://api.anthropic.com/v1/messages”,
headers={“x-api-key”: api_key,
“anthropic-version”: “2023-06-01”,
“content-type”: “application/json”},
json={“model”: “claude-haiku-4-5-20251001”,
“max_tokens”: 2000,
“messages”: [{“role”: “user”, “content”: prompt}]},
timeout=30,
)
resp_json = resp.json()
# 檢查 API 錯誤（Key 無效、額度不足等）
if “error” in resp_json:
st.warning(f”API 錯誤：{resp_json[‘error’].get(‘message’,‘請確認 API Key 是否正確’)}”)
return []
# 安全取出文字
content_list = resp_json.get(“content”, [])
if not content_list:
st.warning(f”API 回應異常，請稍後再試”)
return []
text = content_list[0].get(“text”, “”).strip()
# 清理 markdown 標記
if “`" in text: text = text.split("`”)[1]
if text.startswith(“json”): text = text[4:]
text = text.strip()
data = json.loads(text)
return [Spot(**item) for item in data]
except json.JSONDecodeError:
st.warning(“AI 回傳格式錯誤，請再試一次”)
return []
except Exception as e:
st.warning(f”AI 搜尋失敗：{e}”)
return []

# ════════════════════════════════════════════════

# 地圖產生

# ════════════════════════════════════════════════

def make_map(spots: List[Spot], selected: List[str] = None, center=None) -> folium.Map:
if not spots:
return folium.Map(location=[23.5, 121.0], zoom_start=7, tiles=“CartoDB dark_matter”)

```
if center:
    clat, clng = center
else:
    clat = sum(s.lat for s in spots) / len(spots)
    clng = sum(s.lng for s in spots) / len(spots)

# 自動縮放
if len(spots) == 1:
    zoom = 14
else:
    lat_range = max(s.lat for s in spots) - min(s.lat for s in spots)
    zoom = 10 if lat_range < 1 else (7 if lat_range < 5 else 5)

m = folium.Map(location=[clat, clng], zoom_start=zoom, tiles="CartoDB dark_matter")

# 行程路線
if selected and len(selected) > 1:
    sel_spots = [s for s in spots if s.name in selected]
    ordered = nearest_order(sel_spots)
    coords = [[s.lat, s.lng] for s in ordered]
    folium.PolyLine(coords, color="#f0c040", weight=2.5,
                    opacity=0.8, dash_array="8").add_to(m)

# 景點標記
for i, spot in enumerate(spots):
    is_selected = selected and spot.name in selected
    color = CAT_COLOR.get(spot.category, "gray")
    icon_color = "white" if is_selected else "lightgray"

    popup_html = f"""
```

<div style="font-family:sans-serif;min-width:180px;max-width:220px">
  <div style="font-weight:700;font-size:14px;margin-bottom:4px">{spot.name}</div>
  <div style="font-size:11px;color:#888;margin-bottom:6px">
    {CAT_ICON.get(spot.category,'')} {spot.category} ｜ {rating_stars(spot.rating)}
  </div>
  <div style="font-size:12px;color:#333;margin-bottom:6px;line-height:1.5">{spot.description}</div>
  <div style="font-size:11px;color:#666;background:#f5f5f5;padding:6px;border-radius:4px">
    💡 {spot.tips}
  </div>
  <div style="font-size:11px;color:#888;margin-top:6px">🕐 {spot.hours}</div>
</div>"""

```
    folium.Marker(
        [spot.lat, spot.lng],
        popup=folium.Popup(popup_html, max_width=240),
        tooltip=f"{'✅ ' if is_selected else ''}{spot.name} {rating_stars(spot.rating)}",
        icon=folium.Icon(color=color, icon_color=icon_color,
                         icon="star" if is_selected else "info-sign", prefix="glyphicon"),
    ).add_to(m)

    # 行程編號
    if is_selected:
        ordered = nearest_order([s for s in spots if s.name in selected])
        idx = next((i for i, s in enumerate(ordered) if s.name == spot.name), None)
        if idx is not None:
            folium.Marker(
                [spot.lat + 0.003, spot.lng],
                icon=folium.DivIcon(
                    html=f'<div style="background:#f0c040;color:#000;font-weight:700;'
                         f'font-size:12px;padding:2px 6px;border-radius:10px;'
                         f'white-space:nowrap">Day {idx+1}</div>',
                    icon_size=(50, 24), icon_anchor=(25, 0),
                )
            ).add_to(m)
return m
```

# ════════════════════════════════════════════════

# 行程卡片

# ════════════════════════════════════════════════

def itinerary_card(spots: List[Spot], days: int):
if not spots: return
ordered = nearest_order(spots)
total_mins = sum(s.duration for s in ordered)
spots_per_day = math.ceil(len(ordered) / days)

```
st.markdown(f"""
```

<div style="border:1px solid #2d3a4a;border-radius:8px;padding:14px;background:#0d1117;margin-bottom:12px">
  <div style="font-family:monospace;font-size:10px;color:#58697a;letter-spacing:.1em;margin-bottom:10px">
    // 建議行程 — {len(ordered)} 個景點 ／ {days} 天 ／ 預估總時間 {total_mins//60} 小時</div>
""", unsafe_allow_html=True)

```
for day in range(days):
    day_spots = ordered[day*spots_per_day:(day+1)*spots_per_day]
    if not day_spots: continue
    day_mins = sum(s.duration for s in day_spots)
    st.markdown(f'<div style="font-size:12px;color:#f0c040;font-weight:700;margin:10px 0 6px">▸ 第 {day+1} 天（約 {day_mins//60} 小時 {day_mins%60} 分）</div>', unsafe_allow_html=True)
    for j, spot in enumerate(day_spots):
        icon = CAT_ICON.get(spot.category, "📍")
        dist = f"→ {haversine(day_spots[j-1].lat,day_spots[j-1].lng,spot.lat,spot.lng):.1f}km" if j > 0 else ""
        st.markdown(f"""
```

<div style="display:flex;gap:10px;align-items:flex-start;margin-bottom:8px;
            padding:8px;background:#141b24;border-radius:6px;border-left:3px solid {
            CAT_COLOR.get(spot.category,'gray') if spot.category != '歷史文化' else '#dc3545'}">
  <div style="font-size:18px;flex-shrink:0">{icon}</div>
  <div style="flex:1">
    <div style="font-size:13px;font-weight:600;color:#e6edf3">{spot.name}
      <span style="font-size:10px;color:#58697a;margin-left:6px">{dist}</span></div>
    <div style="font-size:11px;color:#58697a">{rating_stars(spot.rating)} ｜ 建議停留 {spot.duration} 分鐘</div>
    <div style="font-size:11px;color:#79c0ff;margin-top:3px">💡 {spot.tips}</div>
  </div>
</div>""", unsafe_allow_html=True)

```
st.markdown("</div>", unsafe_allow_html=True)
```

# ════════════════════════════════════════════════

# 主程式

# ════════════════════════════════════════════════

def main():
st.set_page_config(page_title=“旅遊探索器”, page_icon=“🗺️”,
layout=“wide”, initial_sidebar_state=“collapsed”)

```
st.markdown("""
```

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
  .stMultiSelect>div>div{background:#0d1117 !important;border:1px solid #2d3a4a !important;}
  .stCheckbox>label{font-size:13px !important;color:#c9d1d9 !important;}
  .main{padding-bottom:env(safe-area-inset-bottom) !important;}
  div[data-testid="stExpander"]{background:#0d1117;border:1px solid #1c2333;border-radius:8px;}
</style>

“””, unsafe_allow_html=True)

```
# ── 初始化 session_state ───────────────────────────────
if "my_list" not in st.session_state:    st.session_state["my_list"] = []
if "ai_spots" not in st.session_state:   st.session_state["ai_spots"] = []
if "search_done" not in st.session_state: st.session_state["search_done"] = False

# ── 頂部標題 ───────────────────────────────────────────
st.markdown('<h2 style="font-family:monospace;font-size:16px;color:#e6edf3;margin:0;padding:6px 0">🗺️ 旅遊景點探索器</h2>', unsafe_allow_html=True)

# ── 搜尋列 ─────────────────────────────────────────────
col_s, col_b = st.columns([4, 1])
with col_s:
    query = st.text_input("", placeholder="搜尋地點，例如：沖繩、巴黎、花蓮…",
                          label_visibility="collapsed")
with col_b:
    search_btn = st.button("🔍 搜尋", use_container_width=True)

# ── 地區 & 類型篩選 ────────────────────────────────────
col_r, col_c = st.columns(2)
with col_r:
    region_filter = st.selectbox("地區", ["全部"] + ALL_REGIONS,
                                 label_visibility="collapsed")
with col_c:
    cat_filter = st.selectbox("類型", ALL_CATS,
                              label_visibility="collapsed")

# ── 執行搜尋 ───────────────────────────────────────────
if search_btn and query:
    with st.spinner(f"AI 正在搜尋「{query}」的景點…"):
        ai_results = ai_search_spots(query)
        if ai_results:
            st.session_state["ai_spots"] = ai_results
            st.session_state["search_done"] = True
            st.success(f"找到 {len(ai_results)} 個景點！")
        else:
            st.info("未取得 AI 結果，顯示內建資料庫景點。請設定 ANTHROPIC_API_KEY 以啟用 AI 搜尋。")

# ── 合併景點清單 ───────────────────────────────────────
all_spots = SPOTS_DB + st.session_state["ai_spots"]

# 套用篩選
filtered = all_spots
if region_filter != "全部":
    filtered = [s for s in filtered if s.region == region_filter]
if cat_filter != "全部":
    filtered = [s for s in filtered if s.category == cat_filter]
if query and not st.session_state["search_done"]:
    filtered = [s for s in filtered if
                query.lower() in s.name.lower() or
                query.lower() in s.region.lower() or
                query.lower() in s.description.lower()]

# ── 主地圖 ─────────────────────────────────────────────
st.markdown('<p style="font-family:monospace;font-size:10px;color:#58697a;letter-spacing:.1em;margin:12px 0 6px">// 景點地圖（點標記查看詳情）</p>', unsafe_allow_html=True)

my_names = [s.name for s in st.session_state["my_list"]]
m = make_map(filtered if filtered else all_spots, selected=my_names)
map_result = st_folium(m, width="100%", height=380, returned_objects=["last_object_clicked"])

# ── 景點卡片清單 ───────────────────────────────────────
st.markdown(f'<p style="font-family:monospace;font-size:10px;color:#58697a;letter-spacing:.1em;margin:14px 0 8px">// 景點清單（{len(filtered)} 個）</p>', unsafe_allow_html=True)

display_spots = filtered if filtered else all_spots
for spot in display_spots:
    in_list = spot.name in my_names
    border_color = "#39d353" if in_list else "#1c2333"
    with st.expander(
        f"{CAT_ICON.get(spot.category,'')} {spot.name}  {rating_stars(spot.rating)}  {'✅' if in_list else ''}",
        expanded=False
    ):
        st.markdown(f"""
```

<div style="font-size:13px;color:#c9d1d9;line-height:1.8">
  <div style="margin-bottom:8px">{spot.description}</div>
  <div style="background:#141b24;padding:8px 10px;border-radius:6px;margin-bottom:8px">
    <span style="color:#79c0ff">💡 小提示</span><br>{spot.tips}
  </div>
  <div style="font-size:11px;color:#58697a">
    🕐 {spot.hours}　⏱ 建議停留 {spot.duration} 分鐘　📍 {spot.region}
  </div>
</div>""", unsafe_allow_html=True)

```
        col1, col2 = st.columns(2)
        with col1:
            if in_list:
                if st.button("❌ 從行程移除", key=f"rm_{spot.name}"):
                    st.session_state["my_list"] = [
                        s for s in st.session_state["my_list"] if s.name != spot.name]
                    st.rerun()
            else:
                if st.button("➕ 加入我的行程", key=f"add_{spot.name}"):
                    st.session_state["my_list"].append(spot)
                    st.rerun()

# ── 我的行程 ───────────────────────────────────────────
my_list = st.session_state["my_list"]
if my_list:
    st.markdown('<p style="font-family:monospace;font-size:10px;color:#f0c040;letter-spacing:.1em;margin:16px 0 8px">// 我的行程清單</p>', unsafe_allow_html=True)

    days = st.slider("行程天數", 1, 7, min(3, len(my_list)), key="days_slider")

    itinerary_card(my_list, days)

    # 行程地圖
    st.markdown('<p style="font-family:monospace;font-size:10px;color:#58697a;letter-spacing:.1em;margin:8px 0 6px">// 行程路線地圖</p>', unsafe_allow_html=True)
    route_map = make_map(my_list, selected=[s.name for s in my_list])
    st_folium(route_map, width="100%", height=320, key="route_map")

    if st.button("🗑️ 清空行程"):
        st.session_state["my_list"] = []
        st.rerun()

# ── 側邊欄 ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ 設定")
    # ★ 修正：用 session_state 儲存，搜尋時直接讀取
    ak = st.text_input("Anthropic API Key",
                        value=st.session_state.get("api_key_input", ANTHROPIC_API_KEY),
                        type="password", placeholder="啟用 AI 即時搜尋",
                        key="api_key_input")
    if ak:
        st.success("✅ Key 已設定，直接搜尋即可")
    st.markdown("---")
    st.markdown("""<div style="font-size:11px;color:#3a4a5a;line-height:2">
```

<b style="color:#58697a">功能說明</b><br>
🔍 輸入地名用 AI 搜尋<br>
📍 地圖點標記看詳情<br>
➕ 加入景點到行程<br>
🗺️ 自動規劃最佳動線<br>
📅 調整行程天數分配<br><br>
<b style="color:#58697a">景點類型</b><br>
🌿 自然景觀<br>
🏛️ 歷史文化<br>
🍜 美食<br>
🛍️ 購物<br>
🎡 娛樂

</div>""", unsafe_allow_html=True)

```
st.markdown('<p style="font-family:monospace;font-size:10px;color:#2d3a4a;margin-top:16px">v1 ｜ 內建資料庫 + Claude AI 即時搜尋</p>', unsafe_allow_html=True)
```

if **name** == “**main**”:
main()
