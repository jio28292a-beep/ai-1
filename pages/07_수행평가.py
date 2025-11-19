# pages/1_멸종위기종_등급별_순위.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 설정 및 데이터 로드 ---
st.set_page_config(
    page_title="멸종위기종 등급별 순위 분석",
    layout="wide"
)

# 데이터 파일 경로 설정 (루트 폴더에 있다고 가정)
CSV_FILE_PATH = 'endangered.csv'

@st.cache_data
def load_data(path):
    """CSV 파일을 로드하고 캐싱합니다."""
    try:
        # 파일 인코딩 문제 해결을 위해 'cp949' 또는 'euc-kr' 시도
        df = pd.read_csv(path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(path, encoding='cp949')
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding='euc-kr')
    
    # '등급'과 '분류군' 컬럼의 결측값을 처리 (필요시)
    df = df.dropna(subset=['등급', '분류군']).copy()
    return df

df = load_data(CSV_FILE_PATH)

# --- Streamlit 앱 시작 ---
st.title("멸종위기 야생생물 등급별 분포 분석 🐘🌿")
st.markdown("""
이 앱은 'endangered.csv' 파일의 데이터를 사용하여 **멸종위기 등급**별로 **분류군**의 개체 수 순위를 분석하고 인터랙티브한 막대 그래프를 시각화합니다.
""")

# --- 사용자 입력 (등급 선택) ---
# 데이터프레임의 고유한 등급을 가져옵니다.
available_grades = sorted(df['등급'].unique().tolist())
selected_grade = st.sidebar.selectbox(
    "1️⃣ 멸종위기 등급 선택",
    available_grades,
    index=0,  # 기본값으로 첫 번째 등급 선택
    help="분석할 멸종위기 등급(I급, II급 등)을 선택하세요."
)

# --- 데이터 처리 ---
# 1. 선택된 등급으로 필터링
filtered_df = df[df['등급'] == selected_grade]

# 2. 분류군(예: 포유류, 식물)별 개체 수 집계
if not filtered_df.empty:
    ranking_data = filtered_df['분류군'].value_counts().reset_index()
    ranking_data.columns = ['분류군', '개체수']
    
    # 순위를 개체수 내림차순으로 정렬
    ranking_data = ranking_data.sort_values(by='개체수', ascending=False)
    
    st.subheader(f"선택 등급: **{selected_grade}급** 분류군별 개체 수 순위")
    st.dataframe(ranking_data, use_container_width=True, hide_index=True)
    
    # --- Plotly 그래프 생성 ---
    
    # 3. 색상 설정: 1등은 파란색, 나머지는 노란색 계열 그라데이션
    # 개체수가 가장 많은 분류군(1등)을 찾습니다.
    if not ranking_data.empty:
        top_category = ranking_data.iloc[0]['분류군']
        
        # 색상 리스트 생성
        # 1등은 지정된 파란색, 나머지는 노란색 계열의 색상 스케일 적용
        color_map = {
            category: '#1f77b4' if category == top_category else 
                      px.colors.sequential.YlOrRd[i % (len(px.colors.sequential.YlOrRd) - 1) + 1] 
            for i, category in enumerate(ranking_data['분류군'])
        }
        
        # 1등 색상을 명확하게 파란색으로 지정하고, 나머지는 노란색 계열로
        color_discrete_map = {
            category: ('#1f77b4' if category == top_category else '#FFD700')
            for category in ranking_data['분류군']
        }
        # Plotly Express를 사용하여 막대 그래프 생성
        fig = px.bar(
            ranking_data, 
            x='분류군', 
            y='개체수',
            title=f"'{selected_grade}'급 멸종위기종의 분류군별 개체 수",
            color='분류군', # '분류군'을 기준으로 색상을 나눕니다.
            color_discrete_map=color_discrete_map,
            labels={'분류군': '분류군 (Taxonomy)', '개체수': '멸종위기 종 개체수'},
            template='plotly_white' # 깔끔한 템플릿 사용
        )
        
        # 4. 그래프 레이아웃 커스터마이징
        fig.update_traces(marker_line_width=0)
        fig.update_layout(
            xaxis_title="분류군",
            yaxis_title="멸종위기 종 개체수",
            # 1등을 강조하는 주석 추가
            annotations=[
                dict(
                    x=top_category,
                    y=ranking_data.iloc[0]['개체수'],
                    text=f"🥇 1위 ({ranking_data.iloc[0]['개체수']}종)",
                    showarrow=True,
                    arrowhead=7,
                    ax=0,
                    ay=-40
                )
            ]
        )
        
        # 5. Streamlit에 Plotly 그래프 표시
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning(f"선택하신 등급 '{selected_grade}'에 해당하는 데이터가 없습니다.")

else:
    st.error("데이터프레임 로드에 문제가 있거나, 선택하신 등급의 데이터가 없습니다.")

# --- 코드 설명 ---
st.markdown("""
<br>

## 💡 코드 설명 및 배포 안내

1.  **데이터 로드 (`@st.cache_data`)**: CSV 파일을 로드하고 Streamlit의 캐싱 기능을 사용해 데이터 로딩 속도를 최적화했습니다. (Streamlit Cloud 환경에서는 **루트 폴더**에 `endangered.csv` 파일이 있어야 합니다.)
2.  **사용자 입력 (`st.sidebar.selectbox`)**: `등급` 컬럼의 고유값을 드롭다운 메뉴로 만들어 사용자 친화적인 인터페이스를 구성했습니다.
3.  **데이터 처리**: 선택된 등급으로 데이터를 **필터링**한 후, `분류군`별로 `value_counts()`를 사용하여 개체 수를 집계하고 순위를 매겼습니다.
4.  **Plotly 시각화**:
    * `plotly.express`의 `bar` 함수를 사용하여 인터랙티브한 막대 그래프를 생성했습니다.
    * **색상 조건**: `color_discrete_map`을 사용하여 개체수가 **가장 많은 분류군(1등)**은 `#1f77b4` (파란색)로 설정하고, 나머지 분류군은 `#FFD700` (노란색 계열)로 지정하여 요청하신 **색상 강조 효과**를 구현했습니다.

### 📦 Streamlit Cloud 배포 준비
Streamlit Cloud에 앱을 배포하려면 다음 폴더/파일 구조를 갖추어야 합니다.
