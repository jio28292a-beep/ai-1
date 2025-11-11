# streamlit_app.py
"""
MBTI Type by Country Visualizer
- 작동환경: Streamlit Cloud
- 데이터파일: countriesMBTI_16types.csv (같은 폴더에 위치)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -----------------------------
# Streamlit 기본 설정
# -----------------------------
st.set_page_config(page_title="MBTI Type by Country", layout="wide")
st.title("🌍 MBTI Type by Country Visualizer")
st.markdown("**MBTI 유형을 선택하면 전 세계 국가별 비율을 비교할 수 있습니다.**")

# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    df.columns = [c.strip() for c in df.columns]
    return df

df = load_data()

# -----------------------------
# MBTI 유형 선택
# -----------------------------
mbti_types = [col for col in df.columns if col != "Country"]
selected_type = st.selectbox("MBTI 유형을 선택하세요:", mbti_types, index=mbti_types.index("INFP") if "INFP" in mbti_types else 0)

# -----------------------------
# 선택된 유형 기준으로 정렬
# -----------------------------
df_sorted = df.sort_values(by=selected_type, ascending=False).reset_index(drop=True)

# -----------------------------
# 색상 설정
# -----------------------------
colors = []
max_country = df_sorted.loc[0, "Country"]

for country in df_sorted["Country"]:
    if country.lower() in ["south korea", "korea, republic of", "korea"]:
        colors.append("rgba(0, 102, 255, 0.9)")  # 한국: 파란색
    elif country == max_country:
        colors.append("rgba(255, 215, 0, 1)")    # 1등: 노랑색
    else:
        colors.append("rgba(150,150,150,0.6)")   # 나머지: 회색

# -----------------------------
# Plotly 그래프 생성
# -----------------------------
fig = go.Figure(
    data=[
        go.Bar(
            x=df_sorted["Country"],
            y=df_sorted[selected_type],
            marker_color=colors,
            text=[f"{v:.3f}" for v in df_sorted[selected_type]],
            textposition="outside",
            hovertemplate="국가: %{x}<br>비율: %{y:.3f}<extra></extra>",
        )
    ]
)

fig.update_layout(
    title=f"🌐 {selected_type} 비율이 높은 국가 순위",
    xaxis_title="국가",
    yaxis_title="비율",
    template="plotly_white",
    height=650,
    showlegend=False,
    xaxis_tickangle=-45,
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 데이터 테이블 표시
# -----------------------------
st
