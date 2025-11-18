# pages/10_subway_analysis.py
import os
import io
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title='지하철 승하차 Top 바', layout='wide')

# ----------------------------
# 파일 탐색 (간단/안전)
# ----------------------------
def find_csv(filename="subway.csv"):
    # 자주 쓰이는 후보 경로를 먼저 체크 (압축 탐색을 피하기 위해 루트 전체탐색은 선택적으로 사용)
    candidates = [
        os.path.join('.', filename),
        os.path.join('pages', filename),
        os.path.join('..', filename),
        os.path.join('..', '..', filename),
        os.path.join('/', 'app', filename),
        os.path.join('/mount', 'src', filename),
    ]
    for p in candidates:
        try:
            if os.path.exists(p):
                return p
        except Exception:
            pass
    # 필요하면 루트에서 재귀 탐색 (주석 처리: 느릴 수 있음 — 문제 시 주석 해제해서 사용)
    # for root, dirs, files in os.walk('/'):
    #     if filename in files:
    #         return os.path.join(root, filename)
    return None

# ----------------------------
# 안전한 CSV 로더: 다양한 인코딩 시도
# ----------------------------
def safe_read_csv(path):
    """
    여러 인코딩을 시도해서 DataFrame을 반환.
    성공 시 (df, used_encoding) 를 반환.
    실패하면 예외를 던짐.
    """
    encodings_to_try = ["utf-8", "cp949", "euc-kr", "iso-8859-1", "latin1"]
    last_exc = None

    # 1) pandas 직접 시도 (일반적)
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(path, encoding=enc, engine="python", low_memory=False)
            return df, enc
        except UnicodeDecodeError as e:
            last_exc = e
            continue
        except Exception as e:
            # 어떤 파일 포맷 문제(구분자 등)일 수 있으니 기록하고 계속 시도
            last_exc = e
            continue

    # 2) 파일을 바이너리로 열어 직접 디코딩 시도 (errors='replace' 포함)
    try:
        with open(path, "rb") as f:
            raw = f.read()
        for enc in encodings_to_try:
            try:
                text = raw.decode(enc)
                df = pd.read_csv(io.StringIO(text), engine="python", low_memory=False)
                return df, enc + " (decoded via bytes)"
            except Exception as e:
                last_exc = e
                continue
        # 3) 최후의 수단: latin1으로 강제로 디코드(모든 바이트를 매핑) — 데이터 일부 깨질 수 있음
        try:
            text = raw.decode("latin1")
            df = pd.read_csv(io.StringIO(text), engine="python", low_memory=False)
            return df, "latin1 (fallback)"
        except Exception as e:
            last_exc = e
    except Exception as e:
        last_exc = e

    # 전부 실패
    raise RuntimeError(f"CSV 읽기 실패: {last_exc}")

# ----------------------------
# 컬럼명 정규화 (유연하게 처리)
# ----------------------------
def normalize_columns(df):
    # trim whitespace
    df.columns = [str(c).strip() for c in df.columns]
    # 간단한 매핑: 가능한 컬럼 이름들에 대해 통일된 이름으로 변경
    mapping = {}
    cols = df.columns.tolist()

    # 사용일자
    for candidate in ["사용일자", "날짜", "date", "일자"]:
        if candidate in cols:
            mapping[candidate] = "사용일자"
            break

    # 노선명 / 호선
    for candidate in ["노선명", "호선", "line", "노선"]:
        if candidate in cols:
            mapping[candidate] = "노선명"
            break

    # 역명
    for candidate in ["역명", "역", "station", "역사명"]:
        if candidate in cols:
            mapping[candidate] = "역명"
            break

    # 승하차 컬럼
    for candidate in ["승차총승객수", "승차", "승차수", "승차총"]:
        if candidate in cols:
            mapping[candidate] = "승차총승객수"
            break
    for candidate in ["하차총승객수", "하차", "하차수", "하차총"]:
        if candidate in cols:
            mapping[candidate] = "하차총승객수"
            break

    df = df.rename(columns=mapping)
    return df

# ----------------------------
# 메인
# ----------------------------
def main():
    st.title("🚇 지하철 승하차 데이터 — 자동 인코딩 처리")
    st.write("subway.csv를 자동 탐색하고 여러 인코딩을 시도하여 안전하게 로드합니다.")

    csv_path = find_csv()
    if csv_path is None:
        st.error("❌ subway.csv 파일을 찾을 수 없습니다. 프로젝트 루트(또는 pages 상위)에 올려주세요.")
        st.stop()

    st.info(f"🔎 CSV 경로: `{csv_path}` — 인코딩을 자동으로 시도합니다.")

    try:
        df, used_enc = safe_read_csv(csv_path)
        st.success(f"✅ CSV 로드 성공 (사용 인코딩: {used_enc})")
    except Exception as e:
        st.error("❌ CSV 파일을 읽는 데 실패했습니다.")
        st.exception(e)
        st.stop()

    # 컬럼 정규화
    df = normalize_columns(df)

    # 필수 컬럼 체크
    required = ["사용일자", "노선명", "역명", "승차총승객수", "하차총승객수"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"데이터에 필요한 컬럼이 없습니다: {missing}\n(현재 컬럼: {df.columns.tolist()})")
        st.stop()

    # 숫자형 변환 (콤마 제거 등)
    for col in ["승차총승객수", "하차총승객수"]:
        df[col] = df[col].astype(str).str.replace(",", "", regex=False).str.strip()
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 사용일자 문자열로 통일 (예: '20251001' 또는 '2025-10-01' 등)
    df['사용일자'] = df['사용일자'].astype(str).str.strip()

    # 총승하차 컬럼
    df['총승하차'] = df['승차총승객수'] + df['하차총승객수']

    # 2025년 10월 데이터만 사용 (사용일자가 '20251001' 형태일 경우, startswith로 처리)
    oct_mask = df['사용일자'].str.startswith('202510')
    df_oct = df[oct_mask].copy()

    if df_oct.empty:
        st.warning("데이터에 2025년 10월(202510**) 항목이 없습니다. 사용일자 포맷을 확인하세요.")
        st.write("현재 사용된 사용일자 샘플:", df['사용일자'].unique()[:10].tolist())
        st.stop()

    # 날짜 선택 UI (문자열 목록 사용)
    oct_dates = sorted(df_oct['사용일자'].unique())
    selected_date = st.selectbox("2025년 10월 날짜 선택", oct_dates)

    # 노선 선택 UI
    lines = sorted(df_oct['노선명'].unique())
    selected_line = st.selectbox("호선(노선) 선택", lines)

    # 필터링
    filtered = df_oct[(df_oct['사용일자'] == selected_date) & (df_oct['노선명'] == selected_line)].copy()
    if filtered.empty:
        st.warning("선택한 날짜와 호선에 해당하는 데이터가 없습니다.")
        st.stop()

    # 역별 집계(혹시 중복 행이 있으면 합산)
    agg = filtered.groupby('역명', as_index=False)['총승하차'].sum()
    agg = agg.sort_values('총승하차', ascending=False)

    # 색상: 1등 하늘색, 나머지 노랑->연한노랑 그라데이션
    n = len(agg)
    # 안전 처리
    def make_yellow_gradient(n):
        if n <= 1:
            return []
        start = (255, 200, 0)
        end = (255, 245, 160)
        steps = n - 1
        colors = []
        for i in range(steps):
            t = 0 if steps == 1 else i / (steps - 1)
            r = int(round(start[0] + (end[0] - start[0]) * t))
            g = int(round(start[1] + (end[1] - start[1]) * t))
            b = int(round(start[2] + (end[2] - start[2]) * t))
            colors.append(f'rgba({r}, {g}, {b}, 1)')
        return colors

    colors = []
    if n >= 1:
        colors.append('rgba(135, 206, 235, 1)')
    colors += make_yellow_gradient(n)
    colors = colors[:n]

    # Plotly 그래프
    fig = px.bar(
        agg,
        x='역명',
        y='총승하차',
        text='총승하차',
        title=f"{selected_date} — {selected_line} 역별 총승하차 순위",
        labels={'총승하차': '총승하차(승차+하차)', '역명': '역명'},
    )

    fig.update_traces(
        marker=dict(color=colors, line=dict(width=0)),
        texttemplate='%{text:,}',
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>총승하차: %{y:,}<extra></extra>'
    )

    fig.update_layout(
        xaxis={'categoryorder': 'array', 'categoryarray': agg['역명'].tolist()},
        yaxis=dict(title='총승하차(명)', tick0=0, dtick=100),
        margin=dict(l=40, r=20, t=70, b=130),
        bargap=0.12,
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("상세 데이터 (역별)"):
        st.dataframe(agg.reset_index(drop=True).assign(총승하차=lambda d: d['총승하차'].map(lambda x: f"{x:,}")))

    st.markdown("---")
    st.markdown("**requirements.txt** 예시:")
    st.code("streamlit\npandas\nplotly")

if __name__ == "__main__":
    main()
