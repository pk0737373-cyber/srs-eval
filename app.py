import streamlit as st
import pandas as pd

# --- [1] 기본 설정 및 보안 ---
st.set_page_config(page_title="SRS 인사평가 시스템", layout="wide")

# 관리자 설정 (이사님 성함)
ADMIN_USERS = ["권정순"]

# 세션 상태 초기화
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'pw_changed': False, 'emp_df': None})

# --- [2] 로그인 화면 ---
if not st.session_state.auth:
    st.title("🛡️ Smart Radar System 인사평가")
    name = st.text_input("성명 (실명 입력)")
    pw = st.text_input("비밀번호 (초기: 12345678!)", type="password")
    
    if st.button("로그인"):
        if pw == "12345678!":
            st.session_state.auth, st.session_state.user = True, name
            st.rerun()
        else: st.error("정보가 올바르지 않습니다.")

# --- [3] 비밀번호 변경 로직 ---
elif not st.session_state.pw_changed:
    st.title("🔑 보안 비밀번호 설정")
    new_p = st.text_input("새 비밀번호 (8자 이상)", type="password")
    if st.button("변경 완료"):
        if len(new_p) >= 8:
            st.session_state.pw_changed = True
            st.rerun()
        else: st.error("8자 이상 입력해 주세요.")

# --- [4] 메인 시스템 ---
else:
    user = st.session_state.user
    st.sidebar.title(f"👤 {user}님")
    
    menu_options = ["내 자기고과 작성", "팀원 평가(2/3차)"]
    if user in ADMIN_USERS:
        menu_options.append("📈 관리자 현황판")
    
    menu = st.sidebar.radio("메뉴", menu_options)

    # --- 메뉴 1: 내 자기고과 작성 ---
    if menu == "내 자기고과 작성":
        st.header("📝 본인 업무 실적 작성")
        items = ["속도", "지속성", "능률", "정확성", "성과", "꼼꼼함"]
        for item in items:
            col1, col2, col3 = st.columns([2, 1, 4])
            col1.write(f"**{item}**")
            col2.selectbox("점수", [5,4,3,2,1], key=f"s_{item}", index=1)
            col3.text_input("성과 근거 의견", key=f"o_{item}")
        st.button("최종 제출")

    # --- 메뉴 2: 팀원 평가 (오류가 났던 부분 수정 완료) ---
    elif menu == "팀원 평가(2/3차)":
        st.header("👥 내 팀원 평가하기")
        if st.session_state.emp_df is not None:
            df = st.session_state.emp_df
            my_team = df[(df['2차평가자'] == user) | (df['3차평가자'] == user)]['성명'].tolist()
            if my_team:
                target = st.selectbox("평가 대상 팀원 선택", my_team)
                with st.expander("✅ 실적 세부 평가", expanded=True):
                    for p_item in ["업무의 양", "업무의 질"]:
                        c1, c2, c3 = st.columns([2, 1, 3])
                        c1.write(f"**{p_item}**")
                        c2.selectbox("점수", [5,4,3,2,1], key=f"eval_{target}_{p_item}")
                        c3.text_input("비고/참고", value="표준 기준 준수", key=f"note_{target}_{p_item}")
                if st.button(f"{target}님 평가 완료"):
                    st.success("저장되었습니다.")
            else: st.info("평가 대상 팀원이 없습니다.")
        else: st.warning("관리자가 조직도를 먼저 업로드해야 합니다.")

    # --- 메뉴 3: 관리자 현황판 ---
    elif menu == "📈 관리자 현황판":
        st.header("📊 전사 인사평가 통합 관리")
        uploaded_file = st.file_uploader("엑셀 파일(.xlsx) 선택", type=["xlsx"])
        if uploaded_file:
            st.session_state.emp_df = pd.read_excel(uploaded_file)
            st.success("✅ 조직도 로드 완료!")
