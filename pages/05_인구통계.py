import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from io import StringIO

st.set_page_config(page_title="행정구역별 연령 인구 분석", layout="wide")
st.title("📈 행정구역별 연령 인구 꺾은선 그래프 (Streamlit)")

st.markdown(
    "업로드한 CSV에서 `행정구역` 열을 기준으로 나머지 열(예: `2025년10월_남_30세`)을 자동으로 파싱하여 "
    "선그래프로 표시합니다. 업로드하지 않으면 데모 데이터를 생성할 수 있습니다."
)

# 파일 업로드
uploaded_file = st.file_uploader("CSV 파일 업로드 (encoding: UTF-8 권장)", type=["csv"])

# 데모 데이터 생성 버튼(업로드가 없을 때)
if uploaded_file is None:
    if st.button("데모 데이터 생성해서 앱 실행"):
        # 간단한 데모: 5개 행정구, 나이 0~100, 성별 '계'만
        rows = []
        regions = ["종로구", "중구", "강남구", "송파구", "은평구"]
        period = "2025년10월"
        for r in regions:
            row = {"행정구역": r}
            for age in range(0, 101):
                colname = f"{period}_계_{age}세" if age < 100 else f"{period}_계_100세 이상"
                # 임의의 값: 정규분포 + 지역별 보정
                import numpy as np
                base = max(0, int(2000 * np.exp(-((age-40)/30)**2) + np.random.randint(-50,50) + regions.index(r)*50))
                if age == 0:
                    base = max(100, int(base/4))
                row[colname] = base
            rows.append(row)
        demo_df = pd.DataFrame(rows)
        csv_buffer = StringIO()
        demo_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        uploaded_file = csv_buffer  # treat as uploaded
        st.success("데모 데이터 생성 완료. 아래에서 행정구역 선택하세요.")
    else:
        st.info("CSV를 업로드하거나, '데모 데이터 생성해서 앱 실행' 버튼을 눌러 테스트하세요.")
        st.stop()

# 읽기 (안전하게)
try:
    df = pd.read_csv(uploaded_file, dtype=str)  # 처음엔 문자열로 읽어 유연성 확보
except Exception as e:
    st.error(f"CSV 읽기 오류: {e}")
    st.stop()

if "행정구역" not in df.columns:
    st.error("CSV에 '행정구역' 컬럼이 필요합니다. 컬럼명이 정확한지 확인해주세요.")
    st.stop()

# 처리 대상 컬럼: '행정구역' 제외한 모든 컬럼
value_columns = [c for c in df.columns if c != "행정구역"]
if not value_columns:
    st.error("행정구역 외에 분석할 연령/성별 칼럼이 없습니다.")
    st.stop()

# 유연한 컬럼명 파싱 패턴
# 가능한 형태 예시:
# - 2025년10월_남_30세
# - 2025-10_계_100세 이상
# - 2025.10_여_2세
# - 남_30세 (기간 없음)
# 정규식 그룹: (period optional)_(gender)_(age or '100세 이상' or '100세이상')
col_parse_regex = re.compile(
    r"""(?ix)                                   # ignorecase, verbose
    (?:(?P<period>[\d]{4}[-년\.]?\d{1,2}월?)[_\-\.]?)?  # optional period like 2025년10월 or 2025-10
    (?P<gender>남|여|계|M|F|Total)?[_\-\.]?
    (?P<age>\d{1,3}\s*세\s*이상|\d{1,3}\s*세|\d{1,3}|100세이상|100세\+|100\+)
    """
)

parsed_rows = []
unparsed_cols = []

for col in value_columns:
    m = col_parse_regex.search(col)
    if not m:
        # try a simpler fallback: look for digits (age) at end
        simple = re.search(r"(\d{1,3})(?=\D*$)", col)
        if simple:
            age = simple.group(1)
            parsed_rows.append({
                "orig_col": col,
                "period": None,
                "gender": "계",
                "age_raw": age
            })
        else:
            unparsed_cols.append(col)
    else:
        period = m.group("period") or None
        gender = m.group("gender") or "계"
        age_raw = m.group("age")
        parsed_rows.append({
            "orig_col": col,
            "period": period,
            "gender": gender,
            "age_raw": age_raw
        })

# Warn about any totally unparsed columns but continue
if unparsed_cols:
    st.warning(f"다음 칼럼은 자동 파싱 규칙에 맞지 않아 기본 '계' 및 숫자 추출 시도 후 진행됩니다: {unparsed_cols[:5]}{('...' if len(unparsed_cols)>5 else '')}")

# Build a long-form DataFrame
long_dfs = []
for p in parsed_rows:
    col = p["orig_col"]
    # take column values, with 행정구역 alongside
    tmp = df[["행정구역", col]].copy()
    tmp = tmp.rename(columns={col: "value"})
    tmp["orig_col"] = col
    tmp["period"] = p["period"]
    tmp["gender"] = p["gender"]
    tmp["age_raw"] = p["age_raw"]
    long_dfs.append(tmp)

long = pd.concat(long_dfs, ignore_index=True)

# 숫자 정리: 쉼표 제거, 공백 제거, 비숫자 -> NaN
def to_numeric_safe(x):
    if pd.isna(x):
        return pd.NA
    s = str(x)
    s = s.replace(",", "").strip()
    # remove any non-digit except + and space
    s = re.sub(r"[^\d\-+\.\s]", "", s)
    try:
        return pd.to_numeric(s, errors="coerce")
    except:
        return pd.NA

long["value_num"] = long["value"].apply(to_numeric_safe)

# 나이 정규화: "100세 이상" 등 처리, 숫자만 추출
def normalize_age(age_raw):
    if pd.isna(age_raw):
        return None
    s = str(age_raw)
    s = s.strip()
    # 대표적인 표현 처리
    if re.search(r"(100|100세|100\+|100세이상|100세 이상)", s):
        return 100
    # 숫자 추출
    m = re.search(r"(\d{1,3})", s)
    if m:
        return int(m.group(1))
    return None

long["age"] = long["age_raw"].apply(normalize_age)

# 집계: 행정구역, period(optional), gender, age별 합산 (value_num)
agg = (
    long.groupby(["행정구역", "period", "gender", "age"], dropna=False, as_index=False)
    .agg({"value_num": "sum"})
)

# 사용자가 선택할 수 있도록 행정구역 목록 제공
regions = sorted(agg["행정구역"].dropna().unique().tolist())
if not regions:
    st.error("유효한 '행정구역' 값이 없습니다.")
    st.stop()

region = st.selectbox("행정구역을 선택하세요", regions)

# 성별 선택(기본 '계' 권장)
genders = sorted(agg["gender"].dropna().unique().tolist())
if "계" in genders:
    default_gender = "계"
else:
    default_gender = genders[0]
gender_sel = st.selectbox("성별 선택", genders, index=genders.index(default_gender))

# (선택적) 기간 선택: 제공되는 period 중 선택 or 전체
periods = sorted([p for p in agg["period"].dropna().unique().tolist() if p is not None])
period_sel = None
if periods:
    periods_display = ["전체"] + periods
    p_choice = st.selectbox("기간 선택 (선택하지 않으면 전체)", periods_display)
    if p_choice != "전체":
        period_sel = p_choice

# 필터링
mask = (agg["행정구역"] == region) & (agg["gender"] == gender_sel)
if period_sel:
    mask = mask & (agg["period"] == period_sel)

filtered = agg[mask].copy()

# 나이별로 정렬 및 누락된 나이 채우기 (0~100)
if filtered.empty:
    st.warning("선택한 조건에 맞는 데이터가 없습니다. 다른 성별/기간을 선택해 보세요.")
    st.stop()

# ensure ages 0..100 present
ages_full = list(range(0, 101))
filtered = filtered.set_index("age").reindex(ages_full, fill_value=0).reset_index()
filtered = filtered.rename(columns={"index": "age"}).rename(columns={"value_num": "population", "age": "age"})
# after reindex, 'age' is int in index; ensure column names
if "population" not in filtered.columns:
    # if earlier grouping used 'age' column name
    filtered = filtered.rename(columns={"value_num": "population"})

# ensure correct columns
if "population" not in filtered.columns or "age" not in filtered.columns:
    st.error("데이터 전처리에서 예상치 못한 문제가 발생했습니다.")
    st.stop()

# 그래프: Plotly 꺾은선
fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=filtered["age"],
        y=filtered["population"],
        mode="lines+markers",
        line=dict(color="black", width=2),
        marker=dict(size=6),
        name=f"{region} ({gender_sel})"
    )
)

# 레이아웃: 회색 배경, x축 10단위, y축 100단위
# y축 tick interval guessed from max value to set reasonable dtick if needed
max_pop = int(filtered["population"].max() if pd.notna(filtered["population"].max()) else 0)
# set y dtick = 100 but if max_pop small, adjust to 10/50 accordingly
y_dtick = 100
if max_pop <= 500:
    y_dtick = 50
if max_pop <= 200:
    y_dtick = 20
if max_pop <= 100:
    y_dtick = 10

fig.update_layout(
    title=f"{region} - 연령별 인구 (성별: {gender_sel}{', 기간: ' + period_sel if period_sel else ''})",
    xaxis_title="나이 (세)",
    yaxis_title="인구수 (명)",
    plot_bgcolor="lightgray",
    paper_bgcolor="white",
    margin=dict(l=60, r=20, t=80, b=60),
)

fig.update_xaxes(
    dtick=10,
    tick0=0,
    showgrid=True,
    gridcolor="white",
    zeroline=False,
    range=[0, 100]
)

fig.update_yaxes(
    dtick=y_dtick,
    showgrid=True,
    gridcolor="white",
    zeroline=False,
    tickformat=",d"
)

st.plotly_chart(fig, use_container_width=True)

# 하단: 선택한 데이터 테이블(간단히)
with st.expander("선택된 데이터(나이, 인구수) 보기"):
    st.dataframe(filtered[["age", "population"]].rename(columns={"age": "나이", "population": "인구수"}))

st.markdown("---")
st.caption("앱이 자동으로 칼럼명을 파싱하여 동작합니다. 예상과 다른 컬럼명이 있다면 CSV 샘플(상위 몇 개 헤더)을 보여주시면 더 맞춤 수정해드릴게요.")
