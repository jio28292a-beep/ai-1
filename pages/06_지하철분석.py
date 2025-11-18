import os
import pandas as pd
import streamlit as st
import plotly.express as px

# -------------------------
# 1) CSV 자동 탐색 함수
# -------------------------
def find_csv(filename="subway.csv"):
    candidate_paths = [
        os.path.join('.', filename),
        os.path.join('..', filename),
        os.path.join('..', '..', filename),
        os.path.join('pages', filename),
        os.path.join('/', 'app', filename),
        os.path.join('/mount', 'src', filename),
    ]

    # 기본 경로 탐색
    for path in candidate_paths:
        if os.path.exists(path):
            return path

    # 전체 파일 시스템 탐색
    for root, dirs, files in os.walk('/'):
        if filename in files:
            return os.path.join(root, filename)

    return None


# -------------------------
# 2) CSV 로드
# -------------------------
csv_path = find_csv()

st.title("🚇 2025년 10월 지하철 역 승·하차 분석")
st.write("CSV 파일 자동 탐색 기능 포함됨")

if csv_path is None:
    st.error("❌ subway.csv 파일을 찾을 수 없습니다.\nStreamlit Cloud 파일 위치를 확인하세요.")
    st.stop()
else:
    st.success(f"📁 CSV 파일 로드 성공: `{csv_path}`")

    df = pd.read_csv(csv_path, encoding="utf-8", engine="python")

# -------------------------
# 데이터 전처리
# -------------------------
df["합계"] = df["승차총승객수"] + df["하차총승객수"]
df["날짜"] = pd.to_datetime(df["날짜"])

# -------------------------
# 3) 사용자 선택 UI
# -------------------------
st.subheader("📌 날짜와 호선 선택")

# 2025년 10월만 필터
df_oct = df[df["날짜"].dt.month == 10]

선택_날짜 = st.date_input(
    "날짜 선택 (2025년 10월 중 하루)",
    value=df_oct["날짜"].iloc[0].date(),
    min_value=df_oct["날짜"].min().date(),
    max_value=df_oct["날짜"].max().date(),
)

호선_list = sorted(df["호선"].unique())
선택_호선 = st.selectbox("호선 선택", 호선_list)

# -------------------------
# 4) 선택된 조건 필터링
# -------------------------
df_filtered = df_oct[
    (df_oct["날짜"].dt.date == 선택_날짜)
    & (df_oct["호선"] == 선택_호선)
]

if df_filtered.empty:
    st.warning("⚠ 선택한 날짜와 호선에 해당하는 데이터가 없습니다.")
    st.stop()

# -------------------------
# 5) 승·하차 합계 기준 정렬
# -------------------------
df_sorted = df_filtered.sort_values("합계", ascending=False)

# 색상 그라데이션 (1등=하늘색, 나머지=노란색→옅어짐)
colors = ["skyblue"] + [f"rgba(255, 230, 100, {1 - i/len(df_sorted)})" for i in range(1, len(df_sorted)+1)]

# -------------------------
# 6) Plotly 그래프 생성
# -------------------------
fig = px.bar(
    df_sorted,
    x="역명",
    y="합계",
    title=f"🚇 {선택_날짜} / {선택_호선} 승·하차 총합 Top 역",
)

fig.update_traces(marker_color=colors)
fig.update_layout(
    xaxis_title="역명",
    yaxis_title="승·하차 총합",
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# 데이터 테이블 출력
# -------------------------
st.subheader("📄 데이터 확인")
st.dataframe(df_sorted)
