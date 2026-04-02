import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- [1] 설정 및 시트 연결 ---
st.set_page_config(page_title="SRS HR System", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5)
def get_db():
    try: return conn.read(worksheet="Users")
    except: return None

# --- [2] 다국어 사전 (UI 및 모든 문항 포함) ---
LANG_DICT = {
    "KO": {
        "welcome": "님, 반갑습니다.",
        "pw_reset_title": "🔑 보안 비밀번호 설정",
        "pw_reset_msg": "첫 로그인(또는 초기화) 상태입니다. 비밀번호를 변경해 주세요.",
        "pw_new": "새 비밀번호 (8자 이상)",
        "pw_btn": "변경 완료",
        "menu_1": "자기고과 작성",
        "menu_2": "팀원 평가",
        "menu_3": "📈 관리자 현황판",
        "eval_title": "📋 2. 개인능력평가 (자기고과)",
        "score": "점수", "basis": "판단 근거",
        "report_title": "🚀 자기 성장 REPORT",
        "rep1": "1. 2025 하반기 주요 성과",
        "rep2": "2. 습득한 지식 및 역량",
        "rep3": "3. 인재양성을 위한 노력",
        "submit": "✅ 최종 제출",
        "admin_reset": "🔑 직원 비밀번호 초기화",
        "reset_btn": "초기화 실행",
        "items": {
            "속도": "업무를 신속하게 처리하며 지체되는 일은 없었는가?",
            "지속성": "어떤 일이나 차이 없이 끈기있게 했는가?",
            "능률": "신속 정확하게 낭비 없이 처리 했는가?",
            "정확성": "일의 결과를 믿을 수 있는가?",
            "성과": "일의 성과가 내용에 있어서 뛰어났는가?",
            "꼼꼼함": "철저하고 뒷처리를 잘하는가?"
        }
    },
    "EN": {
        "welcome": ", Welcome.",
        "pw_reset_title": "🔑 Security Password Setup",
        "pw_reset_msg": "First login (or reset). Please change your password.",
        "pw_new": "New Password (8+ chars)",
        "pw_btn": "Complete Change",
        "menu_1": "Self-Evaluation",
        "menu_2": "Team Evaluation",
        "menu_3": "📈 Admin Dashboard",
        "eval_title": "📋 2. Personal Competency Evaluation",
        "score": "Score", "basis": "Basis for Judgment",
        "report_title": "🚀 Self-Growth REPORT",
        "rep1": "1. Major achievements in 2nd half of 2025",
        "rep2": "2. Knowledge and skills acquired",
        "rep3": "3. Efforts for talent coaching",
        "submit": "✅ Final Submit",
        "admin_reset": "🔑 Reset Employee Password",
        "reset_btn": "Execute Reset",
        "items": {
            "속도": "Processed work quickly without delays?",
            "지속성": "Worked persistently and consistently?",
            "능률": "Worked efficiently without waste?",
            "정확성": "Is the result of work reliable?",
            "성과": "Was the performance outstanding?",
            "꼼꼼함": "Thorough and handles follow-ups well?"
        }
    }
}

# --- [3] 시스템 로직 ---
user_db = get_db()
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'pw_status': 'N', 'lang': 'KO'})

if user_db is not None:
    # 1. 로그인 화면
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System")
        name = st.text_input("Name (성명)")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            u_info = user_db[user_db['성명'] == name]
            if not u_info.empty and str(pw) == str(u_info.iloc[0]['비밀번호']):
                st.session_state.update({'auth': True, 'user': name, 
                                         'pw_status': str(u_info.iloc[0]['비번변경여부']),
                                         'lang': u_info.iloc[0]['언어'] if '언어' in u_info.columns else 'KO'})
                st.rerun()
            else: st.error("Login Failed.")

    # 2. 비번 재설정 화면
    elif st.session_state.pw_status == 'N':
        L = LANG_DICT[st.session_state.lang]
        st.title(L["pw_reset_title"])
        st.warning(L["pw_reset_msg"])
        new_pw = st.text_input(L["pw_new"], type="password")
        if st.button(L["pw_btn"]):
            if len(new_pw) >= 8:
                updated_df = user_db.copy()
                updated_df.loc[updated_df['성명'] == st.session_state.user, ['비밀번호', '비번변경여부']] = [new_pw, 'Y']
                conn.update(worksheet="Users", data=updated_df)
                st.session_state.pw_status = 'Y'; st.rerun()
            else: st.error("Min 8 chars required.")

    # 3. 메인 화면
    else:
        L = LANG_DICT[st.session_state.lang]
        user = st.session_state.user
        st.sidebar.title(f"👤 {user}{L['welcome']}")
        m_list = [L["menu_1"], L["menu_2"]]
        if user == "권정순": m_list.append(L["menu_3"])
        menu = st.sidebar.radio("Menu", m_list)

        # [메뉴 1] 자기고과
        if menu == L["menu_1"]:
            st.header(L["eval_title"])
            for it_ko, crit in L["items"].items():
                c1, c2, c3, c4 = st.columns([1, 2, 1, 3])
                # 언어에 따라 항목명 자동 변환
                display_name = it_ko if st.session_state.lang == "KO" else it_ko 
                c1.write(f"**{display_name}**"); c2.caption(crit)
                c3.selectbox(L["score"], [5,4,3,2,1], key=f"s_{it_ko}")
                c4.text_input(L["basis"], key=f"r_{it_ko}", label_visibility="collapsed")
            
            st.header(L["report_title"])
            st.text_area(L["rep1"], key="rep1"); st.text_area(L["rep2"], key="rep2"); st.text_area(L["rep3"], key="rep3")
            if st.button(L["submit"]): st.balloons(); st.success("Done!")

        # [메뉴 2] 팀원 평가 (여기도 영어 지원!)
        elif menu == L["menu_2"]:
            st.header(L["menu_2"])
            my_team = user_db[(user_db['2차평가자'] == user) | (user_db['3차평가자'] == user)]['성명'].tolist()
            if my_team:
                target = st.selectbox("Select Team Member", my_team)
                st.subheader(f"🔍 {target}")
                for it_ko, crit in L["items"].items():
                    c1, c2, c3, c4 = st.columns([1, 2, 1, 3])
                    c1.write(f"**{it_ko}**"); c2.caption(crit)
                    c3.selectbox(L["score"], [5,4,3,2,1], key=f"eval_s_{target}_{it_ko}")
                    c4.text_input(L["basis"], key=f"eval_r_{target}_{it_ko}", label_visibility="collapsed")
            else: st.info("No team members found.")

        # [메뉴 3] 관리자 현황판 & 비번 초기화
        elif menu == L["menu_3"]:
            st.header(L["menu_3"])
            st.dataframe(user_db, use_container_width=True)
            st.divider()
            st.subheader(L["admin_reset"])
            r_target = st.selectbox("Target Employee", user_db['성명'].tolist())
            if st.button(L["reset_btn"]):
                updated_df = user_db.copy()
                updated_df.loc[updated_df['성명'] == r_target, ['비밀번호', '비번변경여부']] = ['12345678!', 'N']
                conn.update(worksheet="Users", data=updated_df)
                st.success(f"Reset {r_target}'s password to 12345678!")
