import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re

# --- [1] 글로벌 다국어 사전 (이사님 제공 SRS 정식 지표 반영) ---
LANG_DATA = {
    "KO": {
        "login_title": "🛡️ SRS 인사평가 시스템",
        "welcome": "님, 환영합니다.",
        "menu_1": "내 자기고과 작성",
        "menu_2": "팀원 평가(2/3차)",
        "menu_3": "📈 관리자 현황판",
        "criteria_label": "평가 기준",
        "score_label": "점수",
        "comment_label": "판단 근거 (상세히 기록해 주세요)",
        "submit_btn": "✅ 자기고과 최종 제출",
        "validation_msg": "미입력 항목이 있습니다. 모든 항목을 채워주세요! 😊",
        "success_msg": "제출이 완료되었습니다!",
        "tabs": ["1. 업무실적", "2. 근무태도", "3. 직무능력"],
        "items": {
            "속도": "업무를 신속하게 처리하며 지체되는 일은 없었는가?",
            "지속성": "어떤 일이나 차이 없이 끈기있게 했는가?",
            "능률": "신속 정확하게 낭비 없이 처리 했는가?",
            "정확성": "일의 결과를 믿을 수 있는가?",
            "성과": "일의 성과가 내용에 있어서 뛰어났는가?",
            "꼼꼼함": "철저하고 뒷처리를 잘하는가?",
            "횡적협조": "스스로 동료와 협력하며 조직의 능률향상에 공헌하는가?",
            "존중": "동료 전체의 의견을 존중하는가?",
            "적극성": "일에 능동적으로 대처하려는 의욕은 어떤가?",
            "책임감": "책임을 회피하지 않으며 성실한가?",
            "직무지식": "담당업무의 지식이 넓고 깊은가?",
            "문제해결": "문제의 본질을 파악하여 해결을 주도하는가?"
        }
    },
    "EN": {
        "login_title": "🛡️ SRS Evaluation System",
        "welcome": ", Welcome.",
        "menu_1": "Self-Evaluation",
        "menu_2": "Team Evaluation",
        "menu_3": "📈 Admin Dashboard",
        "criteria_label": "Criteria",
        "score_label": "Score",
        "comment_label": "Basis for Judgment (Please record in detail)",
        "submit_btn": "✅ Final Submit",
        "validation_msg": "Some fields are empty. Please fill in all items! 😊",
        "success_msg": "Submission completed successfully!",
        "tabs": ["1. Performance", "2. Work Attitude", "3. Job Competency"],
        "items": {
            "속도": "Did you process work quickly without any delays?",
            "지속성": "Did you work persistently and consistently on all tasks?",
            "능률": "Did you process work efficiently without waste?",
            "정확성": "Is the result of your work reliable and accurate?",
            "성과": "Was the performance outstanding in terms of content?",
            "꼼꼼함": "Are you thorough and do you handle follow-ups well?",
            "횡적협조": "Do you cooperate with colleagues for organizational efficiency?",
            "존중": "Do you respect the opinions of the entire team?",
            "적극성": "How is your willingness to handle tasks proactively?",
            "책임감": "Do you take responsibility and work sincerely?",
            "직무지식": "Is your knowledge of your assigned duties broad and deep?",
            "문제해결": "Do you identify the essence of problems and lead solutions?"
        }
    }
}

# --- [2] 시스템 로직 ---
st.set_page_config(page_title="SRS HR System", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5)
def get_db():
    return conn.read(worksheet="Users")

user_db = get_db()

if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'lang': 'KO'})

# --- [3] 로그인 화면 ---
if not st.session_state.auth:
    st.title("🛡️ Smart Radar System")
    name = st.text_input("Name (실명)")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        u_info = user_db[user_db['성명'] == name]
        if not u_info.empty and str(pw) == str(u_info.iloc[0]['비밀번호']):
            st.session_state.auth = True
            st.session_state.user = name
            # 엑셀의 '언어' 컬럼을 읽어 영문/국문 자동 설정
            st.session_state.lang = u_info.iloc[0]['언어'] if '언어' in u_info.columns else 'KO'
            st.rerun()
        else: st.error("Login Failed. Check your Name or Password.")

# --- [4] 메인 화면 ---
else:
    L = LANG_DATA[st.session_state.lang]
    user = st.session_state.user
    st.sidebar.title(f"👤 {user}{L['welcome']}")
    
    # 관리자 여부 확인 (권정순 이사님 전용)
    menu_list = [L["menu_1"], L["menu_2"]]
    if user == "권정순": menu_list.append(L["menu_3"])
    menu = st.sidebar.radio("Menu", menu_list)

    if menu == L["menu_1"]:
        st.header(L["menu_1"])
        st.info(L["comment_label"])
        
        t1, t2, t3 = st.tabs(L["tabs"])
        
        # 대표로 '업무실적' 탭만 예시 (이사님이 주신 이미지의 모든 문항이 여기에 들어갑니다)
        with t1:
            for item_key, crit in L["items"].items():
                if item_key in ["속도", "지속성", "능률", "정확성", "성과", "꼼꼼함"]:
                    c1, c2, c3, c4 = st.columns([1, 3, 1, 3])
                    c1.write(f"**{item_key}**")
                    c2.caption(crit)
                    c3.selectbox(L["score_label"], [5,4,3,2,1], key=f"v_{item_key}")
                    c4.text_input(L["comment_label"], key=f"t_{item_key}", label_visibility="collapsed")

        if st.button(L["submit_btn"]):
            st.balloons()
            st.success(L["success_msg"])
