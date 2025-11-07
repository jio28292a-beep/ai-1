# app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# 페이지 설정
st.set_page_config(page_title="서울 인기 관광지 Top", layout="wide")
st.title("서울 외국인 인기 관광지 Top — Folium 지도")
st.markdown("외국인들이 좋아하는 서울 주요 관광지 Top을 지도에 표시합니다. 사이드바에서 표시 수와 지도 높이를 조정하세요.")

# 관광지 데이터 (Top 10)
places = [
    {"rank": 1, "name": "Gyeongbokgung Palace (경복궁)", "lat": 37.579617, "lon": 126.977041,
     "desc": "조선의 대표 궁궐로, 근정전·경회루 등 명소가 많습니다.",
     "url": "https://en.wikipedia.org/wiki/Gyeongbokgung"},
    {"rank": 2, "name": "Bukchon Hanok Village (북촌한옥마을)", "lat": 37.582604, "lon": 126.983029,
     "desc": "전통 한옥이 모여있는 골목길로 유명합니다.",
     "url": "https://en.wikipedia.org/wiki/Bukchon_Hanok_Village"},
    {"rank": 3, "name": "Myeongdong (명동 쇼핑거리)", "lat": 37.563756, "lon": 126.982389,
     "desc": "쇼핑과 길거리 음식의 중심지입니다.",
     "url": "https://en.wikipedia.org/wiki/Myeongdong"},
    {"rank": 4, "name": "N Seoul Tower / Namsan (N서울타워)", "lat": 37.5511694, "lon": 126.9882266,
     "desc": "서울 전경을 볼 수 있는 전망 명소입니다.",
     "url": "https://en.wikipedia.org/wiki/N_Seoul_Tower"},
    {"rank": 5, "name": "Hongdae (홍대)", "lat": 37.556230, "lon": 126.923587,
     "desc": "젊음의 거리로 예술과 음악, 밤문화가 활발한 곳입니다.",
     "url": "https://en.wikipedia.org/wiki/Hongdae"},
    {"rank": 6, "name": "Insadong (인사동)", "lat": 37.574025, "lon": 126.986152,
     "desc": "전통 공예품과 찻집이 많은 거리입니다.",
     "url": "https://en.wikipedia.org/wiki/Insadong"},
    {"rank": 7, "name": "Dongdaemun Design Plaza (DDP)", "lat": 37.566295, "lon": 127.009121,
     "desc": "현대적 건축과 디자인 전시가 유명한 장소입니다.",
     "url": "https://en.wikipedia.org/wiki/Dongdaemun_Design_Plaza"},
    {"rank": 8, "name": "Lotte World Tower (롯데월드타워)", "lat": 37.513078, "lon": 127.102663,
     "desc": "초고층 빌딩과 전망대, 쇼핑몰이 있는 곳입니다.",
     "url": "https://en.wikipedia.org/wiki/Lotte_World_Tower"},
    {"rank": 9, "name": "Changdeokgung Palace (창덕궁)", "lat": 37.579517, "lon": 126.991024,
     "desc": "유네스코 세계유산으로 지정된 궁궐입니다.",
     "url": "https://en.wikipedia.org/wiki/Changdeokgung"},
    {"rank": 10, "name": "Itaewon (이태원)", "lat": 37.534866, "lon": 126.994750,
     "desc": "다국적 음식과 외국인 친화적 상점이 많은 지역입니다.",
     "url": "https://en.wikipedia.org/wiki/Itaewon"},
]

# 사이드바: 표시 개수, 팝업, 높이
st.sidebar.header("지도 설정")
max_display = st.sidebar.slider("표시할 Top N", min_value=3, max_value=len(places), value=10)
show_popups = st.sidebar.checkbox("팝업에서 설명과 링크 표시", value=True)
map_height = st.sidebar.slider("지도 높이 (px)", min_value=400, max_value=1000, value=600)

# Folium 지도 생성 (서울 중심)
center = [37.5665, 126.9780]
m = folium.Map(location=center, zoom_start=12, control_scale=True)
cluster = MarkerCluster().add_to(m)

# 숫자 아이콘 함수 (간단한 HTML)
def number_icon_html(n):
    return (
        '<div style="width:34px;height:34px;line-height:34px;'
        'border-radius:17px;background:#2A9D8F;color:white;font-weight:bold;'
        'text-align:center;box-shadow:0 0 3px rgba(0,0,0,0.4);">'
        f'{n}</div>'
    )

# 마커 추가
for p in places[:max_display]:
    popup_html = f"<b>{p['rank']}. {p['name']}</b>"
    if show_popups:
        # 안전하게 문자열 결합 (작은 HTML)
        popup_html += "<br>" + p["desc"] + f"<br><a href='{p['url']}' target='_blank'>더보기</a>"
    popup = folium.Popup(popup_html, max_width=300)
    icon = folium.DivIcon(html=number_icon_html(p["rank"]))
    folium.Marker(location=[p["lat"], p["lon"]], popup=popup, icon=icon).add_to(cluster)

# 타일 레이어(명시적 URL + attribution으로 안전하게 추가)
folium.TileLayer("OpenStreetMap").add_to(m)
folium.TileLayer(
    tiles="https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg",
    attr="Map tiles by Stamen Design (CC BY 3.0) — Data © OpenStreetMap contributors",
    name="Stamen Terrain"
).add_to(m)
folium.LayerControl().add_to(m)

# Streamlit에 Folium 지도 표시
st.subheader(f"서울 관광지 Top {max_display}")
st.write("마커를 클릭하면 장소 설명과 링크가 표시됩니다.")
st_folium(m, width="100%", height=map_height)

# 목록 표시
st.subheader("표시된 관광지 목록")
for p in places[:max_display]:
    st.markdown(f"**{p['rank']}. [{p['name']}]({p['url']})** — {p['desc']}")

# requirements 파일 텍스트
requirements_text = (
    "streamlit>=1.20\n"
    "folium>=0.16\n"
    "streamlit-folium>=0.12.0\n"
)

# 다운로드 버튼 (사이드바)
st.sidebar.header("배포 파일")
st.sidebar.download_button("requirements.txt 다운로드", data=requirements_text, file_name="requirements.txt", mime="text/plain")
st.sidebar.code(requirements_text)
