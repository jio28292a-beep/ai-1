import streamlit as st
import pandas as pd
import plotly.express as px
import os

@st.experimental_singleton
def load_data():
    csv_path = os.path.join('..', 'subway.csv')
    # 한글 인코딩이 CP949인 경우가 많아 명시
    df = pd.read_csv(csv_path, encoding='cp949')
    # 사용일자가 정수(예: 20251001)로 되어있을 수 있어서 문자열로 변환
    df['사용일자'] = df['사용일자'].astype(str)
    # 총승하차 칼럼 추가
    df['총승하차'] = df['승차총승객수'] + df['하차총승객수']
    return df


def make_yellow_gradient(n):
    """노란색에서 점점 연해지는(밝아지는) 그라데이션을 rgba 문자열 리스트로 반환한다.
    첫 색은 제외하고(1등은 하늘색) 나머지 n-1개를 생성한다.
    """
    if n <= 1:
        return []
    # start(진한 노랑), end(연한 노랑)
    start = (255, 200, 0)
    end = (255, 245, 160)
    colors = []
    steps = n - 1
    for i in range(steps):
        t = i / max(1, steps - 1)
        r = int(start[0] + (end[0] - start[0]) * t)
        g = int(start[1] + (end[1] - start[1]) * t)
        b = int(start[2] + (end[2] - start[2]) * t)
        colors.append(f'rgba({r}, {g}, {b}, 1)')
    return colors


def main():
    st.set_page_config(page_title='지하철 승하차 Top 바', layout='wide')
    st.title('지하철 승하차 데이터 — 2025년 10월 (Streamlit / Plotly)')

    try:
        df = load_data()
    except FileNotFoundError:
        st.error('상위 폴더에 subway.csv 파일이 없습니다. pages 폴더 바로 위에 subway.csv 를 놓아주세요.')
        return
    except Exception as e:
        st.exception(e)
        return

    # 2025년 10월에 해당하는 날짜만 선택지로 제공
    oct_dates = sorted([d for d in df['사용일자'].unique() if d.startswith('202510')])
    if not oct_dates:
        st.warning('데이터에 2025년 10월(202510**) 항목이 없습니다.')
        return

    col1, col2 = st.columns([1, 1])
    with col1:
        선택날짜 = st.selectbox('2025년 10월 날짜 선택', oct_dates)
    with col2:
        lines = sorted(df['노선명'].unique())
        선택노선 = st.selectbox('호선(노선) 선택', lines)

    # 필터
    filtered = df[(df['사용일자'] == 선택날짜) & (df['노선명'] == 선택노선)].copy()
    if filtered.empty:
        st.warning('선택한 날짜와 호선에 해당하는 데이터가 없습니다.')
        return

    # 역별로 합산(혹시 여러행이 있을 경우 대비)
    agg = filtered.groupby('역명', as_index=False)['총승하차'].sum()
    agg = agg.sort_values('총승하차', ascending=False)

    # 색상: 1등 하늘색, 나머지는 노랑 그라데이션
    n = len(agg)
    colors = []
    if n >= 1:
        colors.append('rgba(135, 206, 235, 1)')  # skyblue for 1st
    colors += make_yellow_gradient(n)
    # colors 길이가 n 인지 보장
    colors = colors[:n]

    # Plotly 바 차트
    fig = px.bar(
        agg,
        x='역명',
        y='총승하차',
        text='총승하차',
        title=f"{선택날짜} — {선택노선} 역별 총승하차 순위",
        labels={'총승하차': '총승하차(승차+하차)', '역명': '역명'},
    )

    # 막대색 지정
    fig.update_traces(marker_color=colors, hovertemplate='<b>%{x}</b><br>총승하차: %{y}<extra></extra>')

    # x축 역명은 내림차순(총승하차 기준)으로 표시되도록 설정
    fig.update_layout(
        xaxis={'categoryorder': 'array', 'categoryarray': agg['역명'].tolist()},
        yaxis=dict(title='총승하차(명)', tick0=0, dtick=100),
        margin=dict(l=40, r=20, t=60, b=120),
        bargap=0.15,
    )

    st.plotly_chart(fig, use_container_width=True)

    # 표 형태로도 보여주기
    with st.expander('상세 데이터 (역별)'):
        st.dataframe(agg.reset_index(drop=True))

    st.markdown('---')
    st.markdown('**설치해야 할 패키지 (requirements.txt)**')
    st.code('''streamlit
pandas
plotly''')


if __name__ == '__main__':
    main()
