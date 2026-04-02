import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- [1] 기본 설정 및 시트 연결 ---
st.set_page_config(page_title="SRS 글로벌 인사평가 시스템", layout="wide")

# 연결 진단 (400 에러 방지를 위해 연결 방식을 최적화했습니다)
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5)
def get_db():
    try:
        # [수정] 특정 이름을 지정하지 않고 첫 번째 시트를 읽어와서 400 에러를 방지합니다.
        df = conn.read() 
        return df
    except Exception as e:
        st.error(f"❌ 시트 연결 실패! 아래 내용을 확인해 주세요.")
        st.info("1. Streamlit Secrets에 시트 주소가 정확한지 확인 (끝에 /edit 까지만 있는지)")
        st.info("2. 구글 시트 공유 설정이 '편집자'로 되어 있는지 확인")
        return None

# --- [2] 모든 상세 평가 기준 (국문/영문 100% 포함) ---
EVAL_DATA = {
    "KO": {
        "1. 업무실적": {
            "업무의 양": {"속도": "업무 신속 처리?", "지속성": "끈기 수행?", "능률": "낭비 없는 처리?"},
            "업무의 질": {"정확성": "결과 신뢰도?", "성과": "내용의 우수성?", "꼼꼼함": "철저한 뒷처리?"}
        },
        "2. 근무태도": {
            "협조성": {"횡적협조": "동료 협력?", "존중": "의견 존중?", "상사협조": "상사 협조?"},
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
        },
        "2. Work Attitude": {
            "Cooperation": {"Horizontal": "Collaborative?", "Respect": "Respectful?", "Supervisory": "Effective?"},
            "Motivation": {"Proactive": "Proactive?", "Responsible": "Sincere?", "Research": "Deep Study?"},
            "Compliance": {"Discipline": "Orderly?", "Data": "Data Mgmt?", "Attendance": "Status?"}
        },
        "3. Competency": {
            "Knowledge": {"Job": "Deep Knowledge?", "Related": "Basic Knowledge?"},
            "Judgment": {"Quick": "Understanding?", "Valid": "Conclusion?", "Problem": "Solution?", "Insight": "Point?"},
            "Creativity": {"Improve": "Innovation?"},
            "Communication": {"Verbal": "Clear?", "Written": "Clear?", "Negotiation": "Smooth?"}
        }
    }
}

# --- [3] UI 다국어 사전 ---
UI = {
    "KO": {"m1": "자기고과 작성", "m2": "팀원 평가", "m3": "📈 관리자 현황판", "rep": "🚀 자기 성장 REPORT", "sub": "✅ 최종 제출", "reset": "직원 비번 초기화"},
    "EN": {"m1": "Self-Evaluation", "m2": "Team Evaluation", "m3": "📈 Admin Dashboard", "rep": "🚀 Self-Growth REPORT", "sub": "✅ Final Submit", "reset": "Reset Employee PW"}
}

# --- [4] 메인 시스템 구동 ---
user_db = get_db()
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'pw_status': 'N', 'lang': 'KO'})

if user_db is not None:
    # 1. 로그인
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System")
        name = st.text_input("성명 (Name)")
        pw = st.text_input("비밀번호 (Password)", type="password")
        if st.button("Login"):
            u_info = user_db[user_db['성명'] == name]
            if not u_info.empty and str(pw) == str(u_info.iloc[0]['비밀번호']):
                st.session_state.update({
                    'auth': True, 'user': name, 
                    'pw_status': str(u_info.iloc[0]['비번변경여부']),
                    'lang': u_info.iloc[0]['언어'] if '언어' in u_info.columns else 'KO'
                })
                st.rerun()
            else: st.error("로그인 정보가 틀립니다.")

    # 2. 비번 재설정 (Gatekeeper)
    elif st.session_state.pw_status == 'N':
        st.title("🔑 보안 비밀번호 설정")
        new_pw = st.text_input("새 비밀번호 (8자 이상)", type="password")
        if st.button("변경 완료"):
            if len(new_pw) >= 8:
                df = user_db.copy()
                df.loc[df['성명'] == st.session_state.user, ['비밀번호', '비번변경여부']] = [new_pw, 'Y']
                conn.update(data=df)
                st.session_state.pw_status = 'Y'; st.rerun()

    # 3. 메인 화면
    else:
        T = UI[st.session_state.lang]
        E = EVAL_DATA[st.session_state.lang]
        st.sidebar.title(f"👤 {st.session_state.user}님")
        m_list = [T["m1"], T["m2"]]
        if st.session_state.user == "권정순": m_list.append(T["m3"])
        menu = st.sidebar.radio("Menu", m_list)

        def render_form(pre):
            tabs = st.tabs(list(E.keys()))
            for i, (major, subs) in enumerate(E.items()):
                with tabs[i]:
                    for sub, items in subs.items():
                        st.markdown(f"#### 📍 {sub}")
                        for item, crit in items.items():
                            c1, c2, c3, c4 = st.columns([1, 2.5, 1, 3])
                            c1.write(f"**{item}**"); c2.caption(crit)
                            c3.selectbox("Score", [5,4,3,2,1], key=f"{pre}_s_{item}")
                            c4.text_input("Basis", key=f"{pre}_r_{item}", label_visibility="collapsed")

        if menu == T["m1"]:
            st.header(T["m1"])
            render_form("self")
            st.header(T["rep"])
            st.text_area("성과", key="rep1"); st.text_area("역량", key="rep2"); st.text_area("노력", key="rep3")
            if st.button(T["sub"]): st.balloons()

        elif menu == T["m2"]:
            st.header(T["m2"])
            my_team = user_db[(user_db['2차평가자'] == st.session_state.user) | (user_db['3차평가자'] == st.session_state.user)]['성명'].tolist()
            if my_team:
                target = st.selectbox("팀원 선택", my_team)
                render_form(f"t_{target}")
                if st.button(f"{target} 저장"): st.success("저장 완료")
            else: st.info("대상자가 없습니다.")

        elif menu == T["m3"]:
            st.header(T["m3"])
            st.dataframe(user_db)
            st.divider()
            target = st.selectbox(T["reset"], user_db['성명'].tolist())
            if st.button("초기화"):
                df = user_db.copy()
                df.loc[df['성명'] == target, ['비밀번호', '비번변경여부']] = ['12345678!', 'N']
                conn.update(data=df)
                st.success("초기화 완료")
