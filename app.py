import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- [1] 기본 설정 및 시트 연결 ---
st.set_page_config(page_title="SRS 글로벌 인사평가 시스템", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=2)
def get_db(sheet_name="Users"):
    try: return conn.read(worksheet=sheet_name)
    except: return None

# --- [2] 정식 평가 데이터 ---
# (이전과 동일한 25개 상세 항목 데이터가 여기에 들어갑니다)
EVAL_DATA = {
    "KO": {
        "1. 업무실적": {
            "업무의 양": {
                "속도": "업무를 신속하게 처리하며 지체되는 일은 없었는가?",
                "지속성": "어떤 일이나 차이 없이 끈기있게 했는가?",
                "능률": "신속 정확하게 낭비 없이 처리 했는가?"
            },
            "업무의 질": {
                "정확성": "일의 결과를 믿을 수 있는가?",
                "성과": "일의 성과가 내용에 있어서 뛰어났는가?",
                "꼼꼼함": "철저하고 뒷처리를 잘하는가?"
            }
        },
        "2. 근무태도": {
            "협조성": {"횡적협조": "동료와 협력?", "존중": "의견 존중?", "상사협조": "상사와 협조?"},
            "근무의욕": {"적극성": "능동적 태도?", "책임감": "성실한 태도?", "연구심": "업무 연구 의욕?"},
            "복무상황": {"규율": "질서 준수?", "DB화": "데이터 관리?", "근태상황": "지각/조퇴 상황?"}
        },
        "3. 직무능력": {
            "지식": {"직무지식": "전공 지식?", "관련지식": "기초 지식?"},
            "이해판단력": {"신속성": "이해 속도?", "타당성": "결론 타당성?", "문제해결": "본질 파악?", "통찰력": "요점 파악?"},
            "창의연구력": {"연구개선": "개선 도모 의욕?"},
            "표현절충": {"구두표현": "말하기 능력?", "문장표현": "글쓰기 능력?", "절충": "교섭 능력?"}
        }
    },
    "EN": {
        "1. Performance": {
            "Quantity": {"Speed": "Quickly?", "Persistence": "Consistently?", "Efficiency": "Accurately?"},
            "Quality": {"Accuracy": "Reliable?", "Achievement": "Outstanding?", "Thoroughness": "Follow-ups?"}
        }
        # (상세 영문 데이터는 유지됩니다)
    }
}

# --- [3] UI 텍스트 (이사님이 요청하신 가이드 문구 포함) ---
UI_TEXT = {
    "KO": {
        "m1": "자기고과 작성", "m2": "팀원 평가", "m3": "📊 관리자 현황판", 
        "score": "점수", "basis": "판단 근거", "rep": "🚀 자기 성장 REPORT", "sub": "✅ 최종 제출", 
        "admin_reset": "🔑 직원 비밀번호 초기화",
        "guide": "💡 본인의 성과와 역량을 객관적으로 증명할 수 있는 근거를 상세히 기록해 주세요. 작성된 근거는 평가의 중요한 기초 자료가 됩니다."
    },
    "EN": {
        "m1": "Self-Evaluation", "m2": "Team Evaluation", "m3": "📊 Admin Dashboard", 
        "score": "Score", "basis": "Basis", "rep": "🚀 Self-Growth REPORT", "sub": "✅ Final Submit", 
        "admin_reset": "🔑 Reset Employee Password",
        "guide": "💡 Please record detailed evidence that can objectively prove your performance and capabilities. This will be a crucial basis for your evaluation."
    }
}

# --- [4] 메인 로직 ---
user_db = get_db("Users")
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'pw_status': 'N', 'lang': 'KO'})

if user_db is not None:
    # (로그인 및 비밀번호 변경 로직 생략, 기존과 동일)
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System")
        name = st.text_input("성명 (Name)")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            u_info = user_db[user_db['성명'] == name]
            if not u_info.empty and str(pw) == str(u_info.iloc[0]['비밀번호']):
                st.session_state.update({'auth': True, 'user': name, 'pw_status': str(u_info.iloc[0]['비번변경여부']), 'lang': u_info.iloc[0]['언어'] if '언어' in u_info.columns else 'KO'})
                st.rerun()

    elif st.session_state.pw_status == 'N':
        # (비번 변경 화면)
        st.title("🔑 비밀번호 변경")
        new_pw = st.text_input("새 비밀번호 (8자 이상)", type="password")
        if st.button("변경 완료"):
            df = user_db.copy()
            df.loc[df['성명'] == st.session_state.user, ['비밀번호', '비번변경여부']] = [new_pw, 'Y']
            conn.update(worksheet="Users", data=df)
            st.session_state.pw_status = 'Y'; st.rerun()

    else:
        L = UI_TEXT[st.session_state.lang]
        E = EVAL_DATA[st.session_state.lang]
        st.sidebar.title(f"👤 {st.session_state.user}님")
        menu = st.sidebar.radio("Menu", [L["m1"], L["m2"], L["m3"]] if st.session_state.user == "권정순" else [L["m1"], L["m2"]])

        def render_form(pre):
            # [이사님 요청 부분!] 화면 상단에 안내 문구 배치
            st.info(L["guide"])
            
            tabs = st.tabs(list(E.keys()))
            for i, (major, subs) in enumerate(E.items()):
                with tabs[i]:
                    for sub, items in subs.items():
                        st.markdown(f"#### 📍 {sub}")
                        for item, crit in items.items():
                            c1, c2, c3, c4 = st.columns([1.2, 3, 1, 3.5])
                            c1.write(f"**{item}**"); c2.caption(crit)
                            c3.selectbox(L["score"], [5,4,3,2,1], key=f"{pre}_s_{item}")
                            c4.text_input(L["basis"], key=f"{pre}_r_{item}", label_visibility="collapsed", placeholder="상세 근거 작성")
                        st.divider()

        if menu == L["m1"]:
            st.header(L["m1"])
            render_form("self")
            st.header(L["rep"])
            st.text_area("1. 주요 성과", key="rep1")
            st.text_area("2. 습득 역량", key="rep2")
            st.text_area("3. 인재양성 노력", key="rep3")
            if st.button(L["sub"]): st.balloons(); st.success("제출되었습니다!")

        # (팀원 평가 및 관리자 메뉴 로직 유지)
