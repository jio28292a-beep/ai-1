import streamlit as st
import pandas as pd
import plotly.express as px

st.title("🚇 2025년 서울 지하철 승하차 분석")

# CSV 파일 읽기
try:
    df = pd.read_csv('../subway.csv', encoding='cp949')
except Exception as e:
    st.error("❌ CSV 파일을 불러오지 못했습니다. 경로를 다시 확인하세요.")
    st.stop()

# 날짜 선택 (2025년 10월만 필터링)
df['날짜'] = pd.to_datetime(df['날짜'])
df_oct = df[df['날짜'].dt.month == 10]

select_date = st.date_input("📅 날짜 선택 (2025년 10월)", value=df_oct['날짜'].min())
select_line = st.selectbox("🚉 호선 선택", sorted(df['호선'].unique()))

# 선택된 조건 필터링
filtered = df_oct[(df_oct['날짜'] == pd.to_datetime(select_date)) &
                   (df_oct['호선'] == select_line)]

if filtered.empty:
    st.warning("⚠ 선택한 조건에 해당되는 데이터가 없습니다.")
    st.stop()

# 승하차 총합 계산
filtered['총승객'] = filtered['승차총승객수'] + filtered['하차총승객수']

# 승객수 높은 순 정렬
filtered = filtered.sort_values('총승객', ascending=False)

# 색상 처리 (1등 하늘색 / 나머지 노란 → 연한 노란 그라데이션)
colors = ["#87CEFA"]  # 1등 하늘색
yellow = 255
step = 8

for i in range(1, len(filtered)):
    # 노란색을 점점 연하게
    yellow_value = max(180, 255 - i * step)
    color_hex = f'#FFFF{yellow_value:02X}'
    colors.append(color_hex)

# 인터랙티브 Plotly 그래프
fig = px.bar(
    filtered,
    x="역명",
    y="총승객",
    title=f"📊 {select_date} {select_line} 승하차 총합 상위역",
)

fig.update_traces(marker_color=colors)

fig.update_layout(
    xaxis_title="역명",
    yaxis_title="총 승객수",
    template="simple_white"
)

st.plotly_chart(fig, use_container_width=True)

st.dataframe(filtered[['역명', '승차총승객수', '하차총승객수', '총승객']])
