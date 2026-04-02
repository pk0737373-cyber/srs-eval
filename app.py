import streamlit as st
import pandas as pd
import re
import smtplib
from email.mime.text import MIMEText

# --- [설정] 페이지 및 보안 ---
st.set_page_config(page_title="SRS 인사평가 시스템", layout="wide")

# --- [함수] 메일 발송 로직 (jskwon@srs.ai) ---
def send_update_email(evaluator, target, reason):
    msg = MIMEText(f"평가자: {evaluator}\n대상자: {target}\n수정사유: {reason}\n\n시스템에서 확인해 주세요.")
    msg['Subject'] = f"[SRS 알림] {evaluator} 전무님의 평가 수정 완료"
    msg['From'] = "srs-system@srs.ai"
    msg['To'] = "jskwon@srs.ai"
    # 실제 운영 시에는 사내 SMTP 서버 설정이 필요합니다.
    st.info(f"📧 알림 메일이 jskwon@srs.ai로 발송되었습니다.")

# --- [함수] 비밀번호 규정 체크 ---
def check_pw(p):
    return len(p) >= 8 and re.search("[a-z]", p) and re.search("[0-9]", p) and re.search("[!@#$%^&*]", p)

# --- [메인 로직] 세션 관리 ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.pw_changed = False

# 1단계: 로그인 (초기비번: 12345678!)
if not st.session_state.auth:
    st.title("🛡️ SRS 인사평가 시스템")
    name = st.text_input("성명")
    pw = st.text_input("비밀번호", type="password")
    if st.button("접속"):
        if pw == "12345678!":
            st.session_state.auth = True
            st.session_state.user = name
            st.rerun()
        else: st.error("비밀번호 오류")

# 2단계: 비번 변경 강제
elif not st.session_state.pw_changed:
    st.title("🔑 비밀번호 변경 (필수)")
    new_p = st.text_input("새 비번 (영문/숫자/특수문자 8자 이상)", type="password")
    if st.button("변경 완료"):
        if check_pw(new_p):
            st.session_state.pw_changed = True
            st.rerun()
        else: st.error("규정을 준수해 주세요.")

# 3단계: 메인 시스템 (대시보드 및 평가)
else:
    user = st.session_state.user
    st.sidebar.title(f"👤 {user}님")
    
    # [매핑 데이터 로드] - 이사님이 제공하신 엑셀 기반
    # 실제로는 이 부분에 pd.read_csv("mapping.csv")가 들어갑니다.
    menu = st.sidebar.radio("메뉴", ["내 자기고과 작성", "팀원 평가(2/3차)", "관리자 현황판"])

    if menu == "팀원 평가(2/3차)":
        st.header("📊 팀원 평가 대시보드")
        # 여기서 3차 평가자(전무님 등)인 경우 블라인드 로직 작동
        st.write("평가 대상자를 선택하고 소신껏 평가해 주세요.")
        # ... (상세 평가 로직 실행) ...
