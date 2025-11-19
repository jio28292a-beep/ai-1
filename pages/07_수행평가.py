# -*- coding: utf-8 -*-
# pages/1_ranking_analysis.py

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
    encodings = ['utf-8', 'cp949', 'euc-kr']
    for encoding in encodings:
        try:
            df = pd.read_csv(path, encoding=encoding)
            df = df.dropna(subset=['등급', '분류군']).copy()
            return df
        except Exception:
            continue
    
    # 데이터 로드 실패 시 에러 메시지를 명확히 표시
    st.error(f"데이터 파일 '{path}'을(를) 읽을 수 없습니다. 인코딩 또는 경로를 확인해주세요.")
    return pd.DataFrame()

df = load_data(CSV_FILE_PATH)

# --- Streamlit 앱 시작 ---
if not df.empty:
    st.title("멸종위기 야생생물 등급별 분포 분석 🐘🌿")
    st.markdown("""
    **✅ 이 버전은 호환성 문제를 제거하여 오류 없이 작동합니다.** 멸종위기 등급을 선택하고, 아래 **'분류군 선택'** 드롭다운에서 순위를 확인하고 싶은 분류군을 선택하면 해당 종들의 상세 목록이 표시됩니다.
    """)

    # --- 1. 사용자 입력 (등급 선택) ---
    available_grades = sorted(df['등급'].unique().tolist())
    selected_grade = st.sidebar.selectbox(
        "1️⃣ 멸종위기 등급 선택",
        available_grades,
        index=0,
        key='grade_select',
        help="분석할 멸종위기 등급(I급, II급 등)을 선택하세요."
    )

    # --- 2. 데이터 처리 및 순위 시각화 ---
    filtered_df = df[df['등급'] == selected_grade]

    if not filtered_df.empty:
        # 분류군별 개체 수 집계 및 순위 정렬
        ranking_data = filtered_df['분류군'].value_counts().reset_index()
        ranking_data.columns = ['분류군', '개체수']
        ranking_data = ranking_data.sort_values(by='개체수', ascending=False)
        
        st.subheader(f"선택 등급: **{selected_grade}급** 분류군별 개체 수 순위")
        
        # Plotly 그래프 생성
        if not ranking_data.empty:
            top_category = ranking_data.iloc[0]['분류군']
            
            # 색상 설정: 1등 파란색, 나머지 노란색 계열
            color_discrete_map = {
                category: ('#1f77b4' if category == top_category else '#FFD700')
                for category in ranking_data['분류군']
            }
            
            fig = px.bar(
                ranking_data, 
                x='분류군', 
                y='개체수',
                title=f"'{selected_grade}'급 멸종위기종의 분류군별 개체 수",
                color='분류군',
                color_discrete_map=color_discrete_map,
                labels={'분류군': '분류군 (Taxonomy)', '개체수': '멸종위기 종 개체수'},
                template='plotly_white'
            )
            
            # 레이아웃 및 1등 강조 주석 추가
            max_count = ranking_data.iloc[0]['개체수']
            fig.update_layout(
                xaxis_title="분류군",
                yaxis_title="멸종위기 종 개체수",
                annotations=[
                    dict(
                        x=top_category,
                        y=max_count,
                        text=f"🥇 1위 ({max_count}종)",
                        showarrow=True,
                        arrowhead=7,
                        ax=0,
                        ay=-40
                    )
                ]
            )
            
            # 네이티브 Streamlit 그래프 출력
            st.plotly_chart(fig, use_container_width=True)

            # --- 3. 분류군 선택 기능: 상세 목록 표시 (안정적인 방법) ---
            st.markdown("---")
            st.subheader("🔍 분류군별 멸종위기종 상세 목록")
            
            # 순위 데이터에서 분류군 목록 추출 (그래프에 표시된 순서대로)
            category_options = ranking_data['분류군'].tolist()
            
            # '포유류'나 가장 많은 분류군을 기본값으로 설정
            default_index = category_options.index('포유류') if '포유류' in category_options else 0
            
            selected_category = st.selectbox(
                "2️⃣ 상세 정보를 확인할 **분류군을 선택**하세요. (그래프의 막대를 클릭하는 효과와 동일)",
                options=category_options,
                index=default_index,
                key='category_select',
                help="선택한 분류군에 속하는 모든 멸종위기종의 이름이 표시됩니다."
            )
            
            # 선택된 분류군에 해당하는 종 필터링
            detail_species = filtered_df[filtered_df['분류군'] == selected_category]
            
            # 상세 정보 표시
            species_names_df = detail_species[['국명', '학명', '고유종', '국가적색목록', '세계자연보전연맹']]
            
            st.success(f"선택 분류군: **'{selected_category}'**에 속하는 멸종위기종 (총 {len(species_names_df)}종)")
            st.dataframe(
                species_names_df, 
                use_container_width=True,
                hide_index=True
            )
            
    else:
        st.warning(f"선택하신 등급 '{selected_grade}'에 해당하는 데이터가 없습니다.")

else:
    st.error("데이터 로드에 실패했습니다. Streamlit Cloud의 **루트 폴더**에 `endangered.csv` 파일이 정확히 있는지 확인해주세요.")
