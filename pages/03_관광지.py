# app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium import Popup, Marker, Map, DivIcon
from folium.plugins import MarkerCluster

st.set_page_config(page_title="서울 인기 관광지 Top - 지도", layout="wide")

st.title("서울 외국인 인기 관광지 Top — Folium 지도")
st.markdown(
    "외국인들이 특히 좋아하는 서울의 주요 관광지들을 **Top** 순서로 지도에 표시합니다. "
    "사이드바에서 표시 개수 조정과 정보 토글이 가능합니다."
)

# 주요 관광지 데이터 (이 순서가 랭킹: 1이 최고)
places = [
    {
        "rank": 1,
        "name": "Gyeongbokgung Palace (경복궁)",
        "lat": 37.579617,
        "lon": 126.977041,
        "desc": "조선의 대표적 궁궐. 근정전, 경회루 등 역사적 명소.",
        "url": "https://en.wikipedia.org/wiki/Gyeongbokgung"
    },
    {
        "rank": 2,
        "name": "Bukchon Hanok Village (북촌한옥마을)",
        "lat": 37.582604,
        "lon": 126.983029,
        "desc": "전통 한옥이 모여있는 골목 풍경으로 유명합니다.",
        "url": "https://en.wikipedia.org/wiki/Bukchon_Hanok_Village"
    },
    {
        "rank": 3,
        "name": "Myeongdong (명동 쇼핑거리)",
        "lat": 37.563756,
        "lon": 126.982389,
        "desc": "쇼핑과 길거리 음식의 중심지. 외국인 쇼핑객이 많습니다.",
        "url": "https://en.wikipedia.org/wiki/Myeongdong"
    },
    {
        "rank": 4,
        "name": "N Seoul Tower / Namsan (N서울타워/남산)",
        "lat": 37.5511694,
        "lon": 126.9882266,
        "desc": "서울 전경을 볼 수 있는 전망 명소. '사랑의 자물쇠'로도 유명.",
        "url": "https://en.wikipedia.org/wiki/N_Seoul_Tower"
    },
    {
        "rank": 5,
        "name": "Hongdae (홍대)",
        "lat": 37.556230,
        "lon": 126.923587,
        "desc": "젊음의 거리, 인디문화, 밤문화가 발달한 지역.",
        "url": "https://en.wikipedia.org/wiki/Hongdae"
    },
    {
        "rank": 6,
        "name": "Insadong (인사동)",
        "lat": 37.574025,
        "lon": 126.986152,
        "desc": "한국 전통문화 상품과 찻집이 많은 거리.",
        "url": "https://en.wikipedia.org/wiki/Insadong"
    },
    {
        "rank": 7,
        "name": "Dongdaemun Design Plaza (동대문DDP)",
        "lat": 37.566295,
        "lon": 127.009121,
        "desc": "현대적 건축과 야간 조명, 패션타운으로 유명.",
        "url": "https://en.wikipedia.org/wiki/Dongdaemun_Design_Plaza"
    },
    {
        "rank": 8,
        "name": "Lotte World Tower (롯데월드타워 / 잠실)",
        "lat": 37.513078,
        "lon": 127.102663,
        "desc": "한국에서 손꼽히는 초고층 건물과 전망대, 쇼핑몰.",
        "url": "https://en.wikipedia.org/wiki/Lotte_World_Tower"
    },
    {
        "rank": 9,
        "name": "Changdeokgung Palace (창덕궁)",
        "lat": 37.579517,
        "lon": 126.991024,
        "desc": "유네스코 세계유산에 등록된 궁궐. 비원(후원)이 유명.",
        "url": "https://en.wikipedia.org/wiki/Changdeokgung"
    },
    {
        "rank": 10,
        "name": "Itaewon (이태원)",
        "lat": 37.534866,
        "lon": 126.994750,
        "desc": "다국적 음식과 외국인 친화적 거리로 유명한 지역.",
        "url": "https://en.wikipedia.org/wiki/Itaewon"
    }
]

# 사이드바 컨트롤
st.sidebar.header("지도 설정")
max_display = st.sidebar.slider("표시할 Top N", min_value=3, max_value=len(places), value=10)
show_popups = st.sidebar.checkbox("자세한 팝업(설명+링크) 표시", value=True)
map_height = st.sidebar.slider("지도 높이 (px)", min_value=400, max_value=1000, value=600)

# 지도 생성 (서울 중심)
center_lat = 37.5665
center_lon = 126.9780
m = Map(location=[center_lat, center_lon], zoom_start=12, control_scale=True)

# 마커 클러스터 추가
cluster = MarkerCluster().add_to(m)

# Function: 숫자 아이콘(원형)
def number_icon_html(n):
    # 스타일: 원형 배경 + 숫자
    return f"""
    <div style="
        display:inline-block;
        width:34px;
        height:34px;
        line-height:34px;
        border-radius:17px;
        background:#2A9D8F;
        color:white;
        text-align:center;
        font-weight:bold;
        box-shadow: 0 0 3px rgba(0,0,0,0.6);
        ">
        {n}
    </div>
    """

# 장소 추가
for p in places[:max_display]:
    popup_html = f"<b>{p['rank']}. {p['name']}</b>"
    if show_popups:
        popup_html += f"<br>{p['desc']}<br><a href='{p['url']}' target='_blank'>더보기</a>"
    popup = Popup(popup_html, max_width=300)
    icon = DivIcon(html=number_icon_html(p['rank']))
    Marker(location=[p['lat'], p['lon']], popup=popup, icon=icon).add_to(cluster)

# 레이어 컨트롤(기본 타일 변경 가능)
folium.TileLayer('OpenStreetMap').add_to(m)
folium.TileLayer('CartoDB positron').add_to(m)
folium.TileLayer('Stamen Terrain').add_to(m)
folium.LayerControl().add_to(m)

# Streamlit에 지도 표시
st.subheader(f"서울 관광지 Top {max_display} (Folium)")
st.write("지도에서 마커를 클릭하면 장소 정보를 확인할 수 있습니다.")
map_data = st_folium(m, width="100%", height=map_height)

# 장소 목록 표시
st.subheader("표시된 장소 목록")
for p in places[:max_display]:
    st.markdown(f"**{p['rank']}. {p['name']}**  — {p['desc']}  ([더보기]({p['url']}))")

# requirements.txt 내용 표시 및 다운로드 버튼
requirements_text = """streamlit>=1.20
folium>=0.12
streamlit-folium>=0.12.0
"""

st.sidebar.header("파일/배포 도움")
st.sidebar.markdown(
    "앱을 배포하려면 `app.py`와 아래 `requirements.txt` 파일을 동일한 GitHub repo에 넣고 "
    "Streamlit Cloud에 연결하세요."
)
st.sidebar.download_button("requirements.txt 다운로드", data=requirements_text, file_name="requirements.txt", mime="text/plain")

st.sidebar.markdown("**requirements.txt 내용 미리보기:**")
st.sidebar.code(requirements_text, language="text")
