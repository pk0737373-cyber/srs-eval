import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- [1] 기본 설정 및 시트 연결 ---
st.set_page_config(page_title="SRS 글로벌 인사평가 시스템", layout="wide")

# 연결 에러 진단용 로직
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"❌ 시트 연결 설정 에러: {e}")
    st.stop()

@st.cache_data(ttl=5)
def get_db():
    try:
        return conn.read(worksheet="Users")
    except Exception as e:
        st.error(f"❌ 'Users' 탭을 읽을 수 없습니다: {e}")
        return None

# --- [2] 정식 평가 항목 상세 데이터 (이미지 100% 반영) ---
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
            "협조성": {
                "횡적협조": "스스로 동료와 협력하며 조직체의 능률향상에 공헌하는가?",
                "존중": "자신의 생각보다는 팀(동료) 전체의 의견을 존중하는가?",
                "상사협조": "상사에 대해 협력하며 성과가 있는가?"
            },
            "근무의욕": {
                "적극성": "일에 능동적으로 대처하려는 의욕은 어떤가?",
                "책임감": "책임을 회피하지 않으며 성실하게 일하려는 의욕은 어떤가?",
                "연구심": "넓고 깊게 일을 연구하려는 의욕은 어떤가?"
            },
            "복무상황": {
                "규율": "규칙을 준수하며 직장질서유지에 애쓰는가?",
                "DB화": "정기적인 업무보고와 본인업무에 대한 데이터의 체계적인 관리",
                "근태상황": "지각, 조퇴, 결근 등 상황은 어떤가?"
            }
        },
        "3. 직무능력": {
            "지식": {
                "직무지식": "담당업무의 지식이 넓고 깊은가?",
                "관련지식": "관련업무에 대한 기초지식은 넓고 깊은가?"
            },
            "이해판단력": {
                "신속성": "규정, 지시, 자료 등을 바르게 이해하는 속도는 어떤가?",
                "타당성": "내린 결론은 정확하며 타당한가?",
                "문제해결": "문제 본질을 파악하여 효과적인 해결을 주도하는가?",
                "통찰력": "사물의 요점을 파악하며 자주적으로 결론을 내릴 수 있는가?"
            },
            "창의연구력": { "연구개선": "아이디어를 살리고 일의 순서개선이나 전진을 도모하는가?" },
            "표현절충": {
                "구두표현": "구두에 의한 표현이 능숙하며 알기 쉽고 정확한가?",
                "문장표현": "문장에 의한 표현이 능숙하며 알기 쉽고 정확한가?",
                "절충": "교섭을 원활하게 처리하는 능력은 어떤가?"
            }
        }
    },
    "EN": {
        "1. Performance": {
            "Quantity": {
                "Speed": "Did you process work quickly without delays?",
                "Persistence": "Did you work persistently without variation?",
                "Efficiency": "Did you process work accurately without waste?"
            },
            "Quality": {
                "Accuracy": "Is the result of your work reliable?",
                "Achievement": "Was the performance outstanding in content?",
                "Thoroughness": "Are you thorough and handle follow-ups well?"
            }
        },
        "2. Work Attitude": {
            "Cooperation": {
                "Horizontal": "Do you cooperate with colleagues for efficiency?",
                "Respect": "Do you respect the opinions of the entire team?",
                "Supervisory": "Do you cooperate effectively with supervisors?"
            },
            "Motivation": {
                "Proactiveness": "Willingness to handle tasks proactively?",
                "Responsibility": "Sincerity and taking responsibility?",
                "Research Mind": "Willingness to study tasks deeply?"
            },
            "Compliance": {
                "Discipline": "Efforts to maintain workplace order?",
                "Data Mgmt": "Systematic management of reports and data",
                "Attendance": "Status of tardiness, leaving early, or absence?"
            }
        },
        "3. Competency": {
            "Knowledge": {
                "Job Knowledge": "Is your job knowledge broad and deep?",
                "Related Knowledge": "Basic knowledge of related tasks?"
            },
            "Judgment": {
                "Quickness": "Speed of understanding rules and materials?",
                "Validity": "Are the conclusions accurate and valid?",
                "Problem Solving": "Identifying essence and leading solutions?",
                "Insight": "Grasping points and making independent conclusions?"
            },
            "Creativity": { "Improvement": "Willingness to improve task sequences?" },
            "Communication": {
                "Verbal": "Is verbal expression clear and accurate?",
                "Written": "Is written expression clear and accurate?",
                "Negotiation": "Ability to handle negotiations smoothly?"
            }
        }
    }
}

# --- [3] UI 다국어 사전 ---
UI_TEXT = {
    "KO": {
        "welcome": "님, 반갑습니다.", "pw_reset": "🔑 비밀번호 변경", "menu_1": "자기고과 작성",
        "menu_2": "팀원 평가", "menu_3": "📊 관리자 현황판", "score": "점수", "basis": "근거",
        "report": "🚀 자기 성장 REPORT", "submit": "✅ 최종 제출", "admin_reset": "직원 비번 초기화"
    },
    "EN": {
        "welcome": ", Welcome.", "pw_reset": "🔑 Reset Password", "menu_1": "Self-Evaluation",
        "menu_2": "Team Evaluation", "menu_3": "📊 Admin Dashboard", "score": "Score", "basis": "Basis",
        "report": "🚀 Self-Growth REPORT", "submit": "✅ Final Submit", "admin_reset": "Reset Employee PW"
    }
}

# --- [4] 메인 로직 ---
user_db = get_db()
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'pw_status': 'N', 'lang': 'KO'})

if user_db is not None:
    # 1. 로그인
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System")
        name = st.text_input("성명 (Name)")
        pw = st.text_input("비밀번호", type="password")
        if st.button("Login"):
            u_info = user_db[user_db['성명'] == name]
            if not u_info.empty and str(pw) == str(u_info.iloc[0]['비밀번호']):
                st.session_state.update({
                    'auth': True, 'user': name, 
                    'pw_status': str(u_info.iloc[0]['비번변경여부']),
                    'lang': u_info.iloc[0]['언어'] if '언어' in u_info.columns else 'KO'
                })
                st.rerun()
            else: st.error("로그인 정보 오류")

    # 2. 비번 재설정 (Gatekeeper)
    elif st.session_state.pw_status == 'N':
        L = UI_TEXT[st.session_state.lang]
        st.title(L["pw_reset"])
        st.warning("첫 로그인입니다. 비밀번호를 변경해 주세요.")
        new_pw = st.text_input("새 비밀번호 (8자 이상)", type="password")
        if st.button("변경 완료"):
            if len(new_pw) >= 8:
                updated_df = user_db.copy()
                updated_df.loc[updated_df['성명'] == st.session_state.user, ['비밀번호', '비번변경여부']] = [new_pw, 'Y']
                conn.update(worksheet="Users", data=updated_df)
                st.session_state.pw_status = 'Y'; st.rerun()

    # 3. 메인 시스템
    else:
        L = UI_TEXT[st.session_state.lang]
        E = EVAL_DATA[st.session_state.lang]
        st.sidebar.title(f"👤 {st.session_state.user}{L['welcome']}")
        m_list = [L["menu_1"], L["menu_2"]]
        if st.session_state.user == "권정순": m_list.append(L["menu_3"])
        menu = st.sidebar.radio("Menu", m_list)

        # 평가 화면 출력 함수
        def render_eval_form(prefix):
            tabs = st.tabs(list(E.keys()))
            for i, (major, subs) in enumerate(E.items()):
                with tabs[i]:
                    for sub, items in subs.items():
                        st.markdown(f"#### 📍 {sub}")
                        for item, crit in items.items():
                            c1, c2, c3, c4 = st.columns([1, 2.5, 1, 3])
                            c1.write(f"**{item}**"); c2.caption(crit)
                            c3.selectbox(L["score"], [5,4,3,2,1], key=f"{prefix}_s_{item}")
                            c4.text_input(L["basis"], key=f"{prefix}_r_{item}", label_visibility="collapsed")
                        st.divider()

        if menu == L["menu_1"]:
            st.header(L["menu_1"])
            render_eval_form("self")
            st.header(L["report"])
            st.text_area("1. 주요 성과", key="rep1")
            st.text_area("2. 습득 역량", key="rep2")
            st.text_area("3. 인재양성 노력", key="rep3")
            if st.button(L["submit"]): st.balloons()

        elif menu == L["menu_2"]:
            st.header(L["menu_2"])
            my_team = user_db[(user_db['2차평가자'] == st.session_state.user) | (user_db['3차평가자'] == st.session_state.user)]['성명'].tolist()
            if my_team:
                target = st.selectbox("팀원 선택", my_team)
                st.subheader(f"🔍 {target}님 평가")
                render_eval_form(f"team_{target}")
                if st.button(f"{target}님 평가 저장"): st.success("저장 완료")
            else: st.info("대상자가 없습니다.")

        elif menu == L["menu_3"]:
            st.header(L["menu_3"])
            st.dataframe(user_db, use_container_width=True)
            st.divider()
            target = st.selectbox(L["admin_reset"], user_db['성명'].tolist())
            if st.button("초기화 실행"):
                df = user_db.copy()
                df.loc[df['성명'] == target, ['비밀번호', '비번변경여부']] = ['12345678!', 'N']
                conn.update(worksheet="Users", data=df)
                st.success("초기화 완료")
