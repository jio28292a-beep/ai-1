import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from io import StringIO
import numpy as np

st.set_page_config(page_title="행정구역별 연령 인구 분석", layout="wide")

st.title("📊 행정구역별 인구 데이터 분석 대시보드")

# 파일 업로드
uploaded_file = st.file_uploader("CSV 파일 업로드 (UTF-8 권장)", type=["csv"])

# 데모 데이터 생성 버튼
if uploaded_file is None:
    if st.button("데모 데이터 생성하기"):
        regions = ["종로구", "중구", "강남구", "송파구", "은평구", "노원구", "광진구"]
        rows = []
        for region in regions:
            row = {"행정구역": region}
            for age in range(0, 101):
                col = f"2025년10월_계_{age if age < 100 else '100세 이상'}세"
                value = max(0, int(2000 * np.exp(-((age-40)/25)**2) + np.random.randint(-100,100)))
                row[col] = value + regions.index(region)*50
            rows.append(row)
        demo_df = pd.DataFrame(rows)
        csv_buf = StringIO()
        demo_df.to_csv(csv_buf, index=False)
        csv_buf.seek(0)
        uploaded_file = csv_buf
        st.success("데모 데이터 생성 완료! 아래 탭에서 확인하세요.")
    else:
        st.info("CSV를 업로드하거나 '데모 데이터 생성하기' 버튼을 눌러주세요.")
        st.stop()

# CSV 읽기
try:
    df = pd.read_csv(uploaded_file, dtype=str)
except Exception as e:
    st.error(f"CSV 읽기 오류: {e}")
    st.stop()

if "행정구역" not in df.columns:
    st.error("❌ '행정구역' 컬럼이 없습니다.")
    st.stop()

# === 공통 데이터 정제 로직 ===
value_cols = [c for c in df.columns if c != "행정구역"]
col_pattern = re.compile(r"(?P<year>\d{4})년?(?P<month>\d{1,2})?월?_?(?P<gender>남|여|계)?_?(?P<age>\d{1,3}|100세 이상)")

parsed = []
for c in value_cols:
    m = col_pattern.search(c)
    if m:
        age = m.group("age")
        if "100" in age:
            age = "100"
        else:
            age = re.sub(r"세", "", age)
        gender = m.group("gender") if m.group("gender") else "계"
        parsed.append({"col": c, "age": int(age), "gender": gender})
    else:
        parsed.append({"col": c, "age": None, "gender": "계"})

melted = []
for p in parsed:
    temp = df[["행정구역", p["col"]]].copy()
    temp["나이"] = p["age"]
    temp["성별"] = p["gender"]
    temp["인구수"] = temp[p["col"]].replace(",", "", regex=True).astype(float)
    melted.append(temp[["행정구역", "나이", "성별", "인구수"]])

data = pd.concat(melted, ignore_index=True)
data = data.dropna(subset=["나이"])
data["나이"] = data["나이"].astype(int)

# === Streamlit Tabs ===
tab1, tab2 = st.tabs(["📈 연령별 꺾은선그래프", "🏙️ 연령대별 인구 TOP 구 분석"])

# ---------------- TAB 1 -----------------
with tab1:
    st.subheader("행정구별 연령 인구 꺾은선그래프")

    region = st.selectbox("행정구를 선택하세요", sorted(data["행정구역"].unique()))
    filtered = data[(data["행정구역"] == region) & (data["성별"] == "계")].groupby("나이")["인구수"].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=filtered["나이"],
            y=filtered["인구수"],
            mode="lines+markers",
            line=dict(color="black", width=2),
            marker=dict(size=6)
        )
    )
    fig.update_layout(
        title=f"{region} 연령별 인구 분포",
        xaxis_title="나이 (세)",
        yaxis_title="인구수 (명)",
        plot_bgcolor="lightgray",
        xaxis=dict(dtick=10, showgrid=True, gridcolor="white"),
        yaxis=dict(dtick=100, showgrid=True, gridcolor="white"),
        margin=dict(l=40, r=40, t=80, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- TAB 2 -----------------
with tab2:
    st.subheader("연령대별 인구 TOP 행정구 분석")

    # 연령대 선택 (0대 ~ 90대)
    age_group = st.selectbox("연령대를 선택하세요", [f"{i}대" for i in range(0, 100, 10)])
    start_age = int(age_group.replace("대", ""))
    end_age = start_age + 9

    # 선택된 연령대 인구 합산
    age_filtered = data[
        (data["성별"] == "계") &
        (data["나이"].between(start_age, end_age))
    ]
    grouped = age_filtered.groupby("행정구역")["인구수"].sum().reset_index()
    grouped = grouped.sort_values("인구수", ascending=False)

    # 그래프
    fig2 = go.Figure()
    fig2.add_trace(
        go.Bar(
            x=grouped["행정구역"],
            y=grouped["인구수"],
            marker=dict(color="darkslategray"),
        )
    )
    fig2.update_layout(
        title=f"{age_group} 인구가 가장 많은 행정구",
        xaxis_title="행정구역",
        yaxis_title="인구수 (명)",
        plot_bgcolor="lightgray",
        yaxis=dict(dtick=100, showgrid=True, gridcolor="white"),
        xaxis=dict(showgrid=False),
        margin=dict(l=40, r=40, t=80, b=80)
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(grouped.head(10).rename(columns={"행정구역": "행정구", "인구수": "인구수"}))
