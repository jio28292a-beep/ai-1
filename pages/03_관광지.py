# app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# ------------------------------------------------
# 기본 설정
# ------------------------------------------------
st.set_page_config(page_title="서울 관광지도 (외국인 인기 TOP)", layout="wide")
st.title("🌏 외국인들이 좋아하는 서울 주요 관광지 지도")
st.markdown("""
서울을 방문하는 외국인들이 가장 많이 찾는 명소들을 **Folium 지도**로 시각화했습니다.  
지도에서 관광지를 클릭하면 하단에 자세한 정보가 표시됩니다.
""")

# ------------------------------------------------
# 데이터 정의
# ------------------------------------------------
places = [
    {
        "rank": 1,
        "name": "Gyeongbokgung Palace (경복궁)",
        "lat": 37.579617, "lon": 126.977041,
        "desc": "조선의 법궁으로, 근정전과 경회루 등 고궁 건축의 정수를 보여줍니다.",
        "reason": "한국 전통 궁궐 문화와 역사를 대표하며, 외국인들이 한복 체험과 함께 즐겨 방문합니다.",
        "station": "경복궁역 (3호선)",
        "url": "https://en.wikipedia.org/wiki/Gyeongbokgung"
    },
    {
        "rank": 2,
        "name": "Bukchon Hanok Village (북촌한옥마을)",
        "lat": 37.582604, "lon": 126.983029,
        "desc": "조선시대 양반가 한옥이 보존된 전통마을입니다.",
        "reason": "전통 한옥 거리와 함께 인스타그램 인기 명소로 알려져 있습니다.",
        "station": "안국역 (3호선)",
        "url": "https://en.wikipedia.org/wiki/Bukchon_Hanok_Village"
    },
    {
        "rank": 3,
        "name": "Myeongdong (명동 쇼핑거리)",
        "lat": 37.563756, "lon": 126.982389,
        "desc": "서울의 대표적인 쇼핑 거리로 화장품, 의류, 음식이 가득합니다.",
        "reason": "한류 화장품 브랜드와 길거리 음식으로 외국인 쇼핑 명소로 유명합니다.",
        "station": "명동역 (4호선)",
        "url": "https://en.wikipedia.org/wiki/Myeongdong"
    },
    {
        "rank": 4,
        "name": "N Seoul Tower (N서울타워)",
        "lat": 37.5511694, "lon": 126.9882266,
        "desc": "남산 정상에 위치한 서울의 랜드마크 전망탑입니다.",
        "reason": "서울 전경을 한눈에 볼 수 있고 ‘사랑의 자물쇠’ 명소로 유명합니다.",
        "station": "명동역 (4호선) / 충무로역 (3·4호선)",
        "url": "https://en.wikipedia.org/wiki/N_Seoul_Tower"
    },
    {
        "rank": 5,
        "name": "Hongdae (홍대)",
        "lat": 37.556230, "lon": 126.923587,
        "desc": "홍익대학교 인근 예술 거리로 젊음과 자유분위기로 가득합니다.",
        "reason": "라이브 클럽, 스트리트 공연, 개성 있는 카페 문화로 외국인에게 인기입니다.",
        "station": "홍대입구역 (2호선·공항철도)",
        "url": "https://en.wikipedia.org/wiki/Hongdae"
    },
    {
        "rank": 6,
        "name": "Insadong (인사동)",
        "lat": 37.574025, "lon": 126.986152,
        "desc": "전통 찻집, 공예품점이 많은 한국문화 거리입니다.",
        "reason": "전통과 현대가 공존하며, 외국인들이 한국적인 기념품을 구매하기 좋습니다.",
        "station": "안국역 (3호선)",
        "url": "https://en.wikipedia.org/wiki/Insadong"
    },
    {
        "rank": 7,
        "name": "Dongdaemun Design Plaza (DDP)",
        "lat": 37.566295, "lon": 127.009121,
        "desc": "자하 하디드가 설계한 미래형 디자인 랜드마크입니다.",
        "reason": "패션쇼, 전시, 야경 명소로 외국인 사진 명소로도 인기가 많습니다.",
        "station": "동대문역사문화공원역 (2·4·5호선)",
        "url": "https://en.wikipedia.org/wiki/Dongdaemun_Design_Plaza"
    },
    {
        "rank": 8,
        "name": "Lotte World Tower (롯데월드타워)",
        "lat": 37.513078, "lon": 127.102663,
        "desc": "123층 초고층 건물로 서울 스카이 전망대가 유명합니다.",
        "reason": "세계 5위 높이의 타워로 서울의 스카이라인을 대표합니다.",
        "station": "잠실역 (2호선·8호선)",
        "url": "https://en.wikipedia.org/wiki/Lotte_World_Tower"
    },
    {
        "rank": 9,
        "name": "Changdeokgung Palace (창덕궁)",
        "lat": 37.579517, "lon": 126.991024,
        "desc": "유네스코 세계유산으로 지정된 아름다운 궁궐입니다.",
        "reason": "자연과 조화된 후원(비원)으로 유명하며 외국인 가이드 투어 명소입니다.",
        "station": "안국역 (3호선)",
        "url": "https://en.wikipedia.org/wiki/Changdeokgung"
    },
    {
        "rank": 10,
        "name": "Itaewon (이태원)",
        "lat": 37.534866, "lon": 126.994750,
        "desc": "다국적 문화가 공존하는 서울의 대표 외국인 거리입니다.",
        "reason": "세계 각국의 음식과 바, 클럽으로 외국인 친화적인 분위기입니다.",
        "station": "이태원역 (6호선)",
        "url": "https://en.wikipedia.org/wiki/Itaewon"
    },
]

# ------------------------------------------------
# 사이드바 옵션
# ------------------------------------------------
st.sidebar.header("🗺 지도 옵션")
max_display = st.sidebar.slider("표시할 관광지 개수", 3, len(places), 10)
map_height = st.sidebar.slider("지도 높이 (px)", 400, 1000, 650)

# ------------------------------------------------
# 지도 생성
# ------------------------------------------------
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12, control_scale=True)
cluster = MarkerCluster().add_to(m)

def marker_icon_html(rank):
    colors = ["#E63946", "#F4A261", "#2A9D8F", "#1D3557", "#8ECAE6"]
    color = colors[(rank - 1) % len(colors)]
    return f"""
    <div style="
        width:36px; height:36px; line-height:36px;
        border-radius:18px;
        background:{color};
        color:white; font-weight:bold; text-align:center;
        font-size:16px; box-shadow:0 0 5px rgba(0,0,0,0.4);
        ">{rank}</div>
    """

# 마커 추가
for p in places[:max_display]:
    popup_html = f"<b>{p['rank']}. {p['name']}</b>"
    folium.Marker(
        location=[p["lat"], p["lon"]],
        popup=popup_html,
        tooltip=p["name"],
        icon=folium.DivIcon(html=marker_icon_html(p["rank"]))
    ).add_to(cluster)

# 타일 추가
folium.TileLayer("OpenStreetMap").add_to(m)
folium.TileLayer(
    tiles="https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg",
    attr="Map tiles by Stamen Design (CC BY 3.0) — Data © OpenStreetMap contributors",
    name="Stamen Terrain"
).add_to(m)
folium.LayerControl().add_to(m)

# ------------------------------------------------
# Streamlit 지도 출력
# ------------------------------------------------
st.markdown("### 🗺 관광지 지도 (마커를 클릭해보세요)")
map_data = st_folium(m, width="100%", height=map_height)

# ------------------------------------------------
# 마커 클릭 시 하단 정보 표시
# ------------------------------------------------
clicked_info = None
if map_data and map_data.get("last_object_clicked_popup"):
    clicked_text = map_data["last_object_clicked_popup"]
    for p in places:
        if p["name"] in clicked_text:
            clicked_info = p
            break

st.markdown("---")
if clicked_info:
    st.markdown(f"## 📍 {clicked_info['rank']}. {clicked_info['name']}")
    st.markdown(f"🏛 {clicked_info['desc']}")
    st.markdown(f"⭐ {clicked_info['reason']}")
    st.markdown(f"🚇 가장 가까운 지하철역: **{clicked_info['station']}**")
    st.markdown(f"[🔗 자세히 보기]({clicked_info['url']})")
else:
    st.info("👆 지도의 마커를 클릭하면 해당 관광지의 상세 설명이 여기에 표시됩니다.")

# ------------------------------------------------
# requirements.txt 다운로드 버튼
# ------------------------------------------------
requirements_text = "streamlit>=1.20\nfolium>=0.16\nstreamlit-folium>=0.12.0\n"
st.sidebar.header("📦 배포 파일")
st.sidebar.download_button("requirements.txt 다운로드", data=requirements_text, file_name="requirements.txt", mime="text/plain")
st.sidebar.code(requirements_text)
