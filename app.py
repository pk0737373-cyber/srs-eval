import streamlit as st
import pandas as pd
import re

# --- [1] 시트 데이터 직통 연결 (이사님의 시트 ID 적용) ---
# 구글 시트의 CSV 내보내기용 직통 주소입니다.
SHEET_ID = "1maaFMA7RXkUWjO9kZuvuLyGGYddb0_3vEHczNZe1GSQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=5) # 5초마다 최신 데이터를 확인합니다.
def get_user_db():
    try:
        # 구글 시트를 즉시 읽어옵니다.
        df = pd.read_csv(SHEET_URL)
        return df
    except Exception as e:
        st.error("❌ 구글 시트에 연결할 수 없습니다. 공유 설정을 확인해 주세요.")
        return None

# --- [2] 다국어 사전 (국문/영문) ---
LANG_DATA = {
    "KO": {
        "title": "🛡️ SRS 인사평가 시스템",
        "login": "로그인",
        "welcome": "님, 환영합니다.",
        "menu_1": "내 자기고과 작성",
        "menu_2": "팀원 평가(2/3차)",
        "menu_3": "📈 관리자 현황판",
        "item_guide": "판단 근거를 상세히 기록해 주세요.",
        "submit": "최종 제출",
        "success": "성공적으로 제출되었습니다!",
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
        "title": "🛡️ SRS Evaluation System",
        "login": "Login",
        "welcome": ", Welcome.",
        "menu_1": "Self-Evaluation",
        "menu_2": "Team Member Evaluation",
        "menu_3": "📈 Admin Dashboard",
        "item_guide": "Please record the basis for judgment in detail.",
        "submit": "Final Submit",
        "success": "Submitted successfully!",
        "items": {
            "속도": "Did you process work quickly without delays?",
            "지속성": "Did you work persistently and consistently?",
            "능률": "Did you work efficiently without waste?",
            "정확성": "Is the result of your work reliable?",
            "성과": "Was the performance outstanding?",
            "꼼꼼함": "Are you thorough and handle follow-ups well?"
        }
    }
}

# --- [3] 메인 시스템 로직 ---
st.set_page_config(page_title="SRS HR System", layout="wide")

user_db = get_user_db()

if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'lang': 'KO'})

if user_db is not None:
    # 로그인 화면
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System")
        name = st.text_input("Name (성명)")
        pw = st.text_input("Password (비밀번호)", type="password")
        
        if st.button("Login"):
            # 이름으로 사용자 찾기
            u_info = user_db[user_db['성명'] == name]
            if not u_info.empty and str(pw) == str(u_info.iloc[0]['비밀번호']):
                st.session_state.auth = True
                st.session_state.user = name
                # 언어 설정 (없으면 기본 KO)
                st.session_state.lang = u_info.iloc[0]['언어'] if '언어' in u_info.columns else 'KO'
                st.rerun()
            else:
                st.error("이름 또는 비밀번호를 확인하세요. (Check Name or PW)")

    # 로그인 후 메인 화면
    else:
        L = LANG_DATA[st.session_state.lang]
        st.sidebar.title(f"👤 {st.session_state.user}{L['welcome']}")
        
        menu_list = [L["menu_1"], L["menu_2"]]
        if st.session_state.user == "권정순":
            menu_list.append(L["menu_3"])
            
        menu = st.sidebar.radio("Menu", menu_list)

        if menu == L["menu_1"]:
            st.header(L["menu_1"])
            st.info(L["item_guide"])
            
            # 문항 출력
            for item_ko, criteria in L["items"].items():
                c1, c2, c3, c4 = st.columns([1, 3, 1, 3])
                c1.write(f"**{item_ko if st.session_state.lang == 'KO' else item_ko}**")
                c2.caption(criteria)
                c3.selectbox("Score", [5,4,3,2,1], key=f"s_{item_ko}")
                c4.text_input("Basis", key=f"r_{item_ko}", label_visibility="collapsed", placeholder="Details")
            
            if st.button(L["submit"]):
                st.balloons()
                st.success(L["success"])
