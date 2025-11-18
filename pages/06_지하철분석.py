import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -----------------------
# 데이터 로드 (안전한 인코딩 시도, 캐시)
# -----------------------
@st.cache_data
def load_data():
    csv_path = os.path.join('..', 'subway.csv')  # pages 폴더 기준 상위
    # 인코딩 여러가지 시도
    for enc in ('utf-8', 'cp949', 'euc-kr'):
        try:
            df = pd.read_csv(csv_path, encoding=enc)
            break
        except Exception:
            df = None
    if df is None:
        raise FileNotFoundError(f"파일을 열 수 없습니다: {csv_path} (utf-8/cp949/euc-kr 모두 실패)")

    # 컬럼명 공백제거
    df.columns = [c.strip() for c in df.columns]

    # 사용일자 문자열화(정수로 되어있을 가능성)
    if '사용일자' not in df.columns:
        raise KeyError("CSV에 '사용일자' 컬럼이 없습니다.")
    df['사용일자'] = df['사용일자'].astype(str)

    # 승/하차 컬럼 확인 및 숫자형 변환
    for col in ('승차총승객수', '하차총승객수'):
        if col not in df.columns:
            raise KeyError(f"CSV에 '{col}' 컬럼이 없습니다.")
        # 숫자형으로 변환 (콤마, 공백 제거)
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(',', '', regex=False)
            .str.strip()
            .replace({'': '0', 'nan': '0'})
        )
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 총승하차 컬럼
    df['총승하차'] = df['승차총승객수'] + df['하차총승객수']

    # 노선명/역명 공백제거
    if '노선명' in df.columns:
        df['노선명'] = df['노선명'].astype(str).str.strip()
    if '역명' in df.columns:
        df['역명'] = df['역명'].astype(str).str.strip()

    return df

# -----------------------
# 색상 그라데이션 생성
# -----------------------
def make_yellow_gradient(n):
    """첫 항목 제외(1등 하늘색)하고 나머지 n-1개 노랑 -> 연한 노랑 그라데이션 반환."""
    if n <= 1:
        return []
    start = (255, 200, 0)
    end = (255, 245, 160)
    steps = n - 1
    colors = []
    # steps可能 =1 일 때도 작동
    for i in range(steps):
        t = 0 if steps == 1 else i / (steps - 1)
        r = int(round(start[0] + (end[0] - start[0]) * t))
        g = int(round(start[1] + (end[1] - start[1]) * t))
        b = int(round(start[2] + (end[2] - start[2]) * t))
        colors.append(f'rgba({r}, {g}, {b}, 1)')
    return colors

# -----------------------
# 메인
# -----------------------
def main():
    st.set_page_config(page_title='지하철 승하차 Top 바', layout='wide')
    st.title('지하철 승하차 데이터 — 2025년 10월 (Streamlit / Plotly)')

    # 데이터 로드 안전하게 처리
    try:
        df = load_data()
    except FileNotFoundError as e:
        st.error(str(e))
        st.info("pages 폴더 위(상위)에 subway.csv 파일을 올려두었는지 확인하세요.")
        return
    except KeyError as e:
        st.error(f"컬럼 문제: {e}")
        return
    except Exception as e:
        st.exception(e)
        return

    # 2025년 10월 날짜 목록
    oct_dates = sorted([d for d in df['사용일자'].unique() if d.startswith('202510')])
    if not oct_dates:
        st.warning('데이터에 2025년 10월(202510**) 항목이 없습니다.')
        return

    # UI: 날짜, 노선 선택
    col1, col2 = st.columns([1, 1])
    with col1:
        selected_date = st.selectbox('2025년 10월 날짜 선택', oct_dates)
    with col2:
        lines = sorted(df['노선명'].unique())
        selected_line = st.selectbox('호선(노선) 선택', lines)

    # 필터링
    filtered = df[(df['사용일자'] == selected_date) & (df['노선명'] == selected_line)].copy()
    if filtered.empty:
        st.warning('선택한 날짜와 호선에 해당하는 데이터가 없습니다.')
        return

    # 역별 합산(안전)
    agg = filtered.groupby('역명', as_index=False)['총승하차'].sum()
    agg = agg.sort_values('총승하차', ascending=False)

    # 색상 생성 (1등 하늘색)
    n = len(agg)
    colors = []
    if n >= 1:
        colors.append('rgba(135, 206, 235, 1)')  # skyblue
    colors += make_yellow_gradient(n)
    colors = colors[:n]

    # Plotly 그래프 (텍스트에 천단위 콤마)
    fig = px.bar(
        agg,
        x='역명',
        y='총승하차',
        text='총승하차',
        title=f"{selected_date} — {selected_line} 역별 총승하차 순위",
        labels={'총승하차': '총승하차(승차+하차)', '역명': '역명'},
    )

    # 텍스트 포맷, 색상, 호버
    fig.update_traces(
        marker=dict(color=colors, line=dict(width=0)),
        texttemplate='%{text:,}',
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>총승하차: %{y:,}<extra></extra>'
    )

    # x축 카테고리 순서(총승하차 내림차순)
    fig.update_layout(
        xaxis={'categoryorder': 'array', 'categoryarray': agg['역명'].tolist()},
        yaxis=dict(title='총승하차(명)', tick0=0, dtick=100),
        margin=dict(l=40, r=20, t=70, b=130),
        bargap=0.12,
    )

    st.plotly_chart(fig, use_container_width=True)

    # 표로 보기
    with st.expander('상세 데이터 (역별)'):
        st.dataframe(agg.reset_index(drop=True).assign(총승하차=lambda d: d['총승하차'].map(lambda x: f"{x:,}")))

    st.markdown('---')
    st.markdown('**설치해야 할 패키지 (requirements.txt)**')
    st.code('''streamlit
pandas
plotly''')

if __name__ == '__main__':
    main()
