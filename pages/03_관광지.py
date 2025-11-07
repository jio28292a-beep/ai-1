# app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium import Popup, Marker, Map, DivIcon
from folium.plugins import MarkerCluster

st.set_page_config(page_title="서울 인기 관광지 Top", layout="wide")

st.title("🌆 서울 외국인 인기 관광지 Top — Folium 지도")
st.markdown(
    """
    외국인들이 특히 좋아하는 **서울의 주요 관광지 Top 리스트**를 Folium 지도 위에 표시합니다.  
    👉 사이드바에서 표시 개수, 팝업 정보, 지도 높이 등을 조정할 수 있습니다.
    """
)

# 주요 관광지 데이터
places = [
    {"rank": 1, "name": "Gyeongbokgung Palace (경복궁)", "lat": 37.579617, "lon": 126.977041,
     "desc": "조선의 대표 궁궐로, 근정전·경회루 등 명소가 많습니다.",
     "url": "https://en.wikipedia.org/wiki/Gyeongbokgung"},
    {"rank": 2, "name": "Bukchon Hanok Village (북촌한옥마을)", "lat": 37.582604, "lon": 126.983029,
     "desc": "전통 한옥이 모여있는 아름다운 골목길로 유명합니다.",
     "url": "https://en.wikipedia.org/wiki/Bukchon_Hanok_Village"},
    {"rank": 3, "name": "Myeongdong (명동 쇼핑거리)", "lat": 37.563756, "lon": 126.982389,
     "desc": "쇼핑과 길거리 음식의 중심지입니다.",
     "url": "https://en.wikipedia.org/wiki/Myeongdong"},
    {"rank": 4, "name": "N Seoul Tower / Namsan (N서울타워)", "lat": 37.5511694, "lon": 126.9882266,
     "desc": "서울 전경을 한눈에 볼 수 있는 명소입니다.",
     "url": "https://en.wikipedia.org/wiki/N_Seoul_Tower"},
    {"rank": 5, "name": "Hongdae (홍대)", "lat": 37.556230, "lon": 126.923587,
     "desc": "젊음의 거리로 예술과 음악, 밤문화가 활발한 곳입니다.",
     "url": "https://en.wikipedia.org/wiki/Hongdae"},
    {"rank": 6,

