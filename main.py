import streamlit as st
st.title('나의 첫 웹 서비스 만들기!')
name=st.text_input('이름을 입력해주세요!')
menu=st.selectbox('좋아하는 음식을 선택해주세요',['엽떡','마라탕','라면'])
if st.button('인사말 생성가능'):
  st.info(name+'님! 반가워요!')
  st.warning(menu+'을(를) 좋아하세요??,저도요!!')
  st.error('반갑습니다')
