import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

st.set_page_config(page_title="인구 연령별 분석", layout="wide")

st.title("📊 행정구역별 연령 인구 꺾은선 그래프")

# 파일 업로드 또는 기본 파일 불러오기
uploaded_file = st.file_uploader("인구 데이터를 업로드하세요 (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    st.info("예시로 population.csv 파일을 사용할 수 있습니다. 파일을 업로드해주세요.")
    st.stop()

# '행정구역' 컬럼 확인
if "행정구역" not in df.columns:
    st.error("❌ '행정구역' 컬럼이 없습니다. CSV 파일을 확인해주세요.")
    st.stop()

# 가로형 → 세로형 변환 (wide → long)
age_pattern = r"(\d{4}년\d{1,2}월)_(남|여|계)_(\d+세|연령구간인구수|총인구수|100세 이상)"
age_cols = [c for c in df.columns if re.match(age_pattern, c)]

if not age_cols:
    st.error("❌ 연령 관련 컬럼명이 예상 형식과 다릅니다. (예: 2025년10월_남_30세)")
    st.stop()

melted = df.melt(
    id_vars=["행정구역"],
    value_vars=age_cols,
    var_name="기준",
    value_name="인구수"
)

# 컬럼명에서 성별과 나이 추출
melted[["기간", "성별", "나이"]] = melted["기준"].str.extract(age_pattern)
melted["나이"] = melted["나이"].replace("100세 이상", "100").str.replace("세", "").astype(int)
melted["인구수"] = (
    melted["인구수"]
    .astype(str)
    .str.replace(",", "")
    .astype(float)
)

# 행정구역 선택
region = st.selectbox("📍 행정구역을 선택하세요", sorted(melted["행정구역"].unique()))

# 선택된 지역 데이터 필터링
filtered = melted[(melted["행정구역"] == region) & (melted["성별"] == "계")]

# 그래프 생성
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=filtered["나이"],
        y=filtered["인구수"],
        mode="lines+markers",
        line=dict(color="black", width=2),
        marker=dict(size=5)
    )
)

# 그래프 스타일 설정
fig.update_layout(
    title=f"{region} 연령별 인구 분포",
    xaxis_title="나이 (세)",
    yaxis_title="인구수 (명)",
    plot_bgcolor="lightgray",
    xaxis=dict(dtick=10, tick0=0, showgrid=True, gridcolor="white"),
    yaxis=dict(dtick=100, showgrid=True, gridcolor="white"),
    margin=dict(l=40, r=40, t=80, b=40)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("데이터 예시: 통계청 행정구역별 연령 인구 (CSV 형식)")
