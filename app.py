import streamlit as st
import pandas as pd

# --- [1] 시트 데이터 연결 ---
SHEET_ID = "1maaFMA7RXkUWjO9kZuvuLyGGYddb0_3vEHczNZe1GSQ"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=5)
def get_user_db():
    try: return pd.read_csv(SHEET_URL)
    except: return None

# --- [2] 정식 평가 항목 데이터 (이미지 100% 반영) ---
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
        "협조성": {
            "횡적협조": "스스로 동료와 협력하며 조직체의 능률향상에 공헌하는가?",
            "존중": "자신의 생각보다는 팀(동료) 전체의 의견을 존중하는가?",
            "상사와의 협조": "상사에 대해 협력하며 성과가 있는가?"
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
            "문제해결": "문제 발생 시 문제의 본질을 정확히 파악하여 효과적인 해결을 주도하는가?",
            "통찰력": "사물의 요점을 파악하며 자주적으로 결론을 내릴 수 있는가?"
        },
        "창의연구력": {
            "연구개선": "아이디어를 살리고 일의 순서개선이나 전진을 도모하고 있는가?"
        },
        "표현절충": {
            "구두표현": "구두에 의한 표현이 능숙하며 알기 쉽고 정확한가?",
            "문장표현": "문장에 의한 표현이 능숙하며 알기 쉽고 정확한가?",
            "절충": "교섭을 원활하게 처리하는 능력은 어떤가?"
        }
    }
}

# --- [3] 시스템 구동 ---
st.set_page_config(page_title="SRS 인사평가", layout="wide")
user_db = get_user_db()

if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'lang': 'KO'})

if user_db is not None:
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System")
        name = st.text_input("성명 (Name)")
        pw = st.text_input("비밀번호 (Password)", type="password")
        if st.button("로그인"):
            u_info = user_db[user_db['성명'] == name]
            if not u_info.empty and str(pw) == str(u_info.iloc[0]['비밀번호']):
                st.session_state.auth, st.session_state.user = True, name
                st.session_state.lang = u_info.iloc[0]['언어'] if '언어' in u_info.columns else 'KO'
                st.rerun()
            else: st.error("정보를 확인하세요.")

    else:
        user = st.session_state.user
        st.sidebar.title(f"👤 {user}님")
        menu = st.sidebar.radio("메뉴", ["자기고과 작성", "팀원 평가", "관리자 현황판"] if user == "권정순" else ["자기고과 작성", "팀원 평가"])

        if menu == "자기고과 작성":
            st.header("📋 2. 개인능력평가 (자기고과)")
            st.info("💡 각 항목의 평가 기준을 읽고 점수와 근거를 정성껏 작성해 주세요.")
            
            # 탭 구성
            tabs = st.tabs(list(EVAL_STRUCTURE.keys()))
            all_keys = [] # 검증용 키 리스트

            for i, (major, subs) in enumerate(EVAL_STRUCTURE.items()):
                with tabs[i]:
                    for sub_name, items in subs.items():
                        st.markdown(f"#### 📍 {sub_name}")
                        for item, crit in items.items():
                            c1, c2, c3, c4 = st.columns([1, 3, 1.2, 4])
                            c1.write(f"**{item}**")
                            c2.caption(crit)
                            c3.selectbox("점수", [5,4,3,2,1], key=f"s_{item}", index=1)
                            c4.text_input("판단 근거", key=f"r_{item}", placeholder="상세 사유 기록")
                            all_keys.append(f"r_{item}")
                        st.divider()

            # --- 이사님이 강조하신 자기 성장 REPORT ---
            st.header("🚀 자기 성장 REPORT")
            st.write("2025년 하반기 본인의 노력을 자유롭게 기록해 주세요.")
            rep1 = st.text_area("1. 2025 하반기 주요 성과", placeholder="구체적인 실적을 적어주세요.", key="rep1")
            rep2 = st.text_area("2. 하반기 동안 습득한 지식 및 역량", placeholder="새로 배운 기술이나 지식", key="rep2")
            rep3 = st.text_area("3. 하반기 동안 인재양성을 위한 노력(교육, 전파 등)", placeholder="팀원 성장에 기여한 내용", key="rep3")

            if st.button("✅ 최종 제출하기"):
                # 필수 항목 체크 (근거 의견 및 리포트가 비었는지 확인)
                empty_fields = [k for k in all_keys if not st.session_state[k].strip()]
                if not rep1.strip() or not rep2.strip() or not rep3.strip() or empty_fields:
                    st.warning("⚠️ 작성되지 않은 항목이 있습니다. 본인의 성장을 위해 모든 항목을 채워주세요!")
                else:
                    st.balloons()
                    st.success("성공적으로 제출되었습니다! 수고하셨습니다.")
