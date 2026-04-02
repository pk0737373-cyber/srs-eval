import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- [1] 설정 및 구글 시트 연결 ---
st.set_page_config(page_title="SRS 인사평가 시스템", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=5)
def get_db():
    try:
        return conn.read(worksheet="Users")
    except:
        st.error("❌ 구글 시트 연결 에러! Secrets 주소와 공유 설정을 확인해 주세요.")
        return None

# --- [2] 정식 평가 항목 데이터 ---
EVAL_STRUCTURE = {
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
        "협조성": {"횡적협조": "동료와 협력하며 공헌하는가?", "존중": "의견을 존중하는가?", "상사와의 협조": "상사에 협력하는가?"},
        "근무의욕": {"적극성": "능동적인가?", "책임감": "성실한가?", "연구심": "연구하려는 의욕은?"},
        "복무상황": {"규율": "질서를 준수하는가?", "DB화": "데이터 체계적 관리", "근태상황": "지각/조퇴 등 상황"}
    },
    "3. 직무능력": {
        "지식": {"직무지식": "전문 지식이 깊은가?", "관련지식": "기초 지식이 넓은가?"},
        "이해판단력": {"신속성": "이해 속도", "타당성": "결론의 타당성", "문제해결": "본질 파악 및 해결", "통찰력": "요점 파악"},
        "창의연구력": {"연구개선": "개선을 도모하는가?"},
        "표현절충": {"구두표현": "말하기 능력", "문장표현": "글쓰기 능력", "절충": "교섭 능력"}
    }
}

# --- [3] 시스템 로직 시작 ---
user_db = get_db()
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'pw_status': 'N', 'lang': 'KO'})

if user_db is not None:
    # [STEP 1] 로그인 화면
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System")
        name = st.text_input("성명 (Name)")
        pw = st.text_input("비밀번호 (Password)", type="password")
        if st.button("로그인"):
            u_info = user_db[user_db['성명'] == name]
            if not u_info.empty and str(pw) == str(u_info.iloc[0]['비밀번호']):
                st.session_state.auth = True
                st.session_state.user = name
                st.session_state.pw_status = str(u_info.iloc[0]['비번변경여부'])
                st.session_state.lang = u_info.iloc[0]['언어'] if '언어' in u_info.columns else 'KO'
                st.rerun()
            else: st.error("정보가 일치하지 않습니다.")

    # [STEP 2] 비밀번호 재설정 (Gatekeeper)
    elif st.session_state.pw_status == 'N':
        st.title("🔑 보안 비밀번호 설정")
        st.warning("첫 로그인입니다. 안전한 사용을 위해 비밀번호를 변경해 주세요.")
        new_pw = st.text_input("새 비밀번호 (8자 이상, 특수문자 포함)", type="password")
        if st.button("비밀번호 변경 완료"):
            if len(new_pw) >= 8:
                # 구글 시트에 업데이트
                updated_df = user_db.copy()
                updated_df.loc[updated_df['성명'] == st.session_state.user, '비밀번호'] = new_pw
                updated_df.loc[updated_df['성명'] == st.session_state.user, '비번변경여부'] = 'Y'
                conn.update(worksheet="Users", data=updated_df)
                st.session_state.pw_status = 'Y'
                st.success("✅ 비밀번호가 변경되었습니다! 이제 평가를 시작합니다.")
                st.rerun()
            else: st.error("비밀번호 규칙을 지켜주세요.")

    # [STEP 3] 메인 평가 시스템
    else:
        user = st.session_state.user
        st.sidebar.title(f"👤 {user}님")
        menu = st.sidebar.radio("메뉴", ["자기고과 작성", "팀원 평가", "관리자 현황판"])

        if menu == "자기고과 작성":
            st.header("📋 2. 개인능력평가 (자기고과)")
            tabs = st.tabs(list(EVAL_STRUCTURE.keys()))
            for i, (major, subs) in enumerate(EVAL_STRUCTURE.items()):
                with tabs[i]:
                    for sub_name, items in subs.items():
                        st.markdown(f"#### 📍 {sub_name}")
                        for item, crit in items.items():
                            c1, c2, c3, c4 = st.columns([1, 3, 1.2, 4])
                            c1.write(f"**{item}**")
                            c2.caption(crit)
                            c3.selectbox("점수", [5,4,3,2,1], key=f"s_{item}")
                            c4.text_input("근거", key=f"r_{item}", placeholder="상세 사유")
            
            st.header("🚀 자기 성장 REPORT")
            st.text_area("1. 2025 하반기 주요 성과", key="rep1")
            st.text_area("2. 습득한 지식 및 역량", key="rep2")
            st.text_area("3. 인재양성을 위한 노력", key="rep3")
            if st.button("✅ 최종 제출"): st.balloons(); st.success("제출 완료!")

        elif menu == "팀원 평가":
            st.header("👥 팀원 능력 평가")
            my_team = user_db[(user_db['2차평가자'] == user) | (user_db['3차평가자'] == user)]['성명'].tolist()
            if my_team:
                target = st.selectbox("평가 대상 선택", my_team)
                st.info(f"{target}님에 대한 객관적인 평가를 부탁드립니다.")
            else: st.info("평가할 팀원이 없습니다.")

        elif menu == "관리자 현황판":
            st.header("📊 전사 관리 데이터")
            st.dataframe(user_db)
