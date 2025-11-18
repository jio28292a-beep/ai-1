import streamlit as st
import pandas as pd
import plotly.express as px
import os

def load_data():
    csv_path = os.path.join('..', 'subway.csv')
    return pd.read_csv(csv_path, encoding='cp949')

def main():
    st.title("지하철 승하차 데이터 분석 (2025년 10월)")

    df = load_data()
    df['총승하차'] = df['승차총승객수'] + df['하차총승객수']

    # 날짜 선택
    dates = sorted(df['사용일자'].unique())
    선택날짜 = st.selectbox("날짜 선택", dates)

    # 노선 선택
    lines = sorted(df['노선명'].unique())
    선택노선 = st.selectbox("노선 선택", lines)

    # 필터링
    filtered = df[(df['사용일자'] == 선택날짜) & (df['노선명'] == 선택노선)]
    filtered = filtered.sort_values('총승하차', ascending=False)

    if filtered.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
        return

    # 색상 설정: 1등 하늘색, 이후 노란색 그라데이션
    colors = ['skyblue'] + [f'rgba(255, 255, {50 + i*8}, 1)' for i in range(len(filtered)-1)]

    fig = px.bar(
        filtered,
        x='역명',
        y='총승하차',
        title=f"{선택날짜} / {선택노선} 승하차 Top 역",
    )

    fig.update_traces(marker_color=colors)
    fig.update_layout(xaxis_title="역명", yaxis_title="총승하차")

    st.plotly_chart(fig, use_container_width=True)

if __name__ == '__main__':
    main()
