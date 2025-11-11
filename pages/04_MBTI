# streamlit_app.py
"""
Countries MBTI Visualizer
- 작동환경: Streamlit Cloud
- 데이터파일: countriesMBTI_16types.csv (같은 폴더에 위치)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# -----------------------------
# Streamlit 기본 설정
# -----------------------------
st.set_page_config(page_title="Countries MBTI Visualizer", layout="wide")
st.title("🌍 Countries MBTI Visualizer")
st.markdown("**각 나라의 MBTI 분포를 인터랙티브하게 탐색해보세요!**")

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
# 국가 선택 UI
# -----------------------------
countries = df["Country"].tolist()
selected_country = st.selectbox("국가를 선택하세요:", countries, index=0)

# -----------------------------
# 선택된 국가 데이터 처리
# -----------------------------
country_row = df[df["Country"] == selected_country].iloc[0]
mbti_values = country_row[1:]  # 첫 번째 열(Country) 제외
mbti_types = mbti_values.index.tolist()
values = mbti_values.values

# -----------------------------
# 1등 MBTI 구하기
# -----------------------------
max_idx = values.argmax()
colors = ["#1f77b4"] * len(values)  # 기본 파란색
colors = [f"rgba(31,119,180,{0.3 + 0.7*(v/max(values))})" for v in values]
colors[max_idx] = "rgba(255,0,0,0.9)"  # 1등은 빨간색

# -----------------------------
# Plotly 그래프 (막대그래프)
# -----------------------------
fig = go.Figure(
    data=[
        go.Bar(
            x=mbti_types,
            y=values,
            marker_color=colors,
            text=[f"{v:.3f}" for v in values],
            textposition="outside",
            hovertemplate="MBTI: %{x}<br>비율: %{y:.3f}<extra></extra>",
        )
    ]
)

fig.update_layout(
    title=f"🇨🇳 {selected_country}의 MBTI 비율",
    xaxis_title="MBTI 유형",
    yaxis_title="비율",
    yaxis=dict(range=[0, max(values)*1.2]),
    template="plotly_white",
    showlegend=False,
    height=600,
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 데이터 테이블 표시
# -----------------------------
st.markdown("### 📊 세부 데이터")
st.dataframe(
    pd.DataFrame({"MBTI": mbti_types, "비율": values}).sort_values("비율", ascending=False).reset_index(drop=True),
    hide_index=True,
    use_container_width=True,
)

# -----------------------------
# 전체 평균 MBTI 그래프 (참고용)
# -----------------------------
st.markdown("---")
st.markdown("### 🌎 전체 평균 MBTI 분포")

avg_values = df.drop(columns=["Country"]).mean().sort_values(ascending=False)
fig_avg = px.bar(
    x=avg_values.index,
    y=avg_values.values,
    color=avg_values.values,
    color_continuous_scale="Blues",
    labels={"x": "MBTI 유형", "y": "평균 비율"},
    title="전 세계 평균 MBTI 비율",
)
fig_avg.update_traces(text=[f"{v:.3f}" for v in avg_values.values], textposition="outside")
st.plotly_chart(fig_avg, use_container_width=True)

# -----------------------------
# CSV 다운로드 버튼
# -----------------------------
st.download_button(
    label="📥 전체 데이터 다운로드 (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="countriesMBTI_16types.csv",
    mime="text/csv",
)
