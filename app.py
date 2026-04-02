import streamlit as st
import pandas as pd

# --- [1] 기본 설정 및 보안 ---
st.set_page_config(page_title="SRS 인사평가 시스템", layout="wide")

# 관리자 설정 (이사님 성함)
ADMIN_USERS = ["권정순"] 

# 세션 상태 초기화 (비번 초기화 상태를 추적하기 위한 가상 데이터 포함)
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'pw_changed': False})
if 'user_db' not in st.session_state:
    # 실무용 가상 유저 데이터베이스
    st.session_state.user_db = {
        "한명희 부장": {"pw": "12345678!", "changed": False},
        "이종민 차장": {"pw": "12345678!", "changed": False},
        "장미희 과장": {"pw": "12345678!", "changed": False}
    }

# --- [2] 로그인 로직 ---
if not st.session_state.auth:
    st.title("🛡️ Smart Radar System 인사평가")
    name = st.text_input("성명 (실명 입력)")
    pw = st.text_input("비밀번호", type="password")
    
    if st.button("로그인"):
        if pw == "12345678!":
            st.session_state.auth, st.session_state.user = True, name
            st.rerun()
        else: st.error("성명 또는 비밀번호가 올바르지 않습니다.")

# --- [3] 비밀번호 변경 로직 ---
elif not st.session_state.pw_changed:
    st.title("🔑 보안을 위한 비밀번호 변경")
    st.info("비밀번호가 초기화되었거나 최초 접속입니다. 새 비밀번호를 설정하세요.")
    new_p = st.text_input("새 비밀번호 (8자 이상)", type="password")
    if st.button("변경 완료"):
        if len(new_p) >= 8:
            st.session_state.pw_changed = True
            st.success("변경되었습니다. 시스템으로 진입합니다.")
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

    # --- 메뉴 1: 자기고과 / 메뉴 2: 팀원평가 (생략 - 이전과 동일) ---
    if menu == "내 자기고과 작성":
        st.header("📝 본인 업무 실적 작성")
        st.write("항목별 성과를 입력해 주세요.")

    # --- 메뉴 3: 관리자 현황판 (이사님 전용 - 초기화 기능 추가) ---
    elif menu == "📈 관리자 현황판":
        st.header("📊 전사 인사평가 통합 관리")
        
        # 현황 표
        df = pd.DataFrame({
            "성명": ["한명희 부장", "이종민 차장", "장미희 과장"],
            "상태": ["✅ 완료", "⏳ 작성중", "❌ 미접속"]
        })
        st.table(df)
        
        st.divider()
        
        # [추가된 기능] 비밀번호 초기화 섹션
        st.subheader("🔑 직원 비밀번호 관리")
        st.write("비밀번호를 분실한 직원을 선택하면 초기값(`12345678!`)으로 리셋됩니다.")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            target_user = st.selectbox("비밀번호 초기화 대상 선택", list(st.session_state.user_db.keys()))
        with col2:
            if st.button("🔄 즉시 초기화"):
                # 실제 서버 운영 시에는 DB의 해당 유저 'pw_changed' 값을 False로 바꾸는 로직
                st.success(f"✅ {target_user}님의 비밀번호가 초기화되었습니다!")
                st.warning("해당 직원에게 '12345678!'로 접속 후 비번을 재설정하라고 안내해 주세요.")
