import streamlit as st
import pandas as pd
import re

# --- [1] 기본 설정 및 보안 ---
st.set_page_config(page_title="SRS 인사평가 시스템", layout="wide")

ADMIN_USERS = ["권정순"]

if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'pw_changed': False, 'emp_df': None})

def is_valid_password(p):
    if len(p) < 8: return False
    if not re.search("[a-zA-Z]", p) or not re.search("[0-9]", p) or not re.search("[!@#$%^&*()]", p): return False
    return True

# --- [2] 로그인 / 비번 변경 (규정 준수) ---
if not st.session_state.auth:
    st.title("🛡️ Smart Radar System 인사평가")
    name = st.text_input("성명 (실명 입력)")
    pw = st.text_input("비밀번호 (초기: 12345678!)", type="password")
    if st.button("로그인"):
        if pw == "12345678!":
            st.session_state.auth, st.session_state.user = True, name
            st.rerun()
        else: st.error("정보가 올바르지 않습니다.")

elif not st.session_state.pw_changed:
    st.title("🔑 보안 비밀번호 설정")
    new_p = st.text_input("새 비밀번호 (영문, 숫자, 특수문자 포함 8자 이상)", type="password")
    if st.button("변경 완료"):
        if is_valid_password(new_p):
            st.session_state.pw_changed = True
            st.rerun()
        else: st.error("⚠️ 규정 미달: 영문/숫자/특수문자 포함 8자 이상 입력하세요.")

# --- [3] 메인 시스템 (정식 평가 데이터 반영) ---
else:
    user = st.session_state.user
    st.sidebar.title(f"👤 {user}님")
    menu = st.sidebar.radio("메뉴", ["내 자기고과 작성", "팀원 평가(2/3차)", "📈 관리자 현황판"] if user in ADMIN_USERS else ["내 자기고과 작성", "팀원 평가(2/3차)"])

    # 정식 평가 데이터 구조화
    EVAL_DATA = {
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
            "지식": {"직무지식": "담당업무의 지식이 넓고 깊은가?", "관련지식": "관련업무에 대한 기초지식은 넓고 깊은가?"},
            "이해판단력": {
                "신속성": "규정, 지시, 자료 등을 바르게 이해하는 속도는 어떤가?",
                "타당성": "내린 결론은 정확하며 타당한가?",
                "문제해결": "문제 발생 시 문제의 본질을 정확히 파악하여 효과적인 해결을 주도하는가?",
                "통찰력": "사물의 요점을 파악하며 자주적으로 결론을 내릴 수 있는가?"
            },
            "창의연구력": {"연구개선": "아이디어를 살리고 일의 순서개선이나 전진을 도모하고 있는가?"},
            "표현절충": {
                "구두표현": "구두에 의한 표현이 능숙하며 알기 쉽고 정확한가?",
                "문장표현": "문장에 의한 표현이 능숙하며 알기 쉽고 정확한가?",
                "절충": "교섭을 원활하게 처리하는 능력은 어떤가?"
            }
        }
    }

    if menu == "내 자기고과 작성":
        st.header("📋 2. 개인능력평가 (자기고과)")
        tabs = st.tabs(list(EVAL_DATA.keys()))
        
        for i, (major, subs) in enumerate(EVAL_DATA.items()):
            with tabs[i]:
                for sub_name, items in subs.items():
                    st.subheader(f"📍 {sub_name}")
                    for item, criteria in items.items():
                        c1, c2, c3, c4 = st.columns([1, 3, 1, 3])
                        c1.write(f"**{item}**")
                        c2.caption(criteria)
                        c3.selectbox("점수", [5,4,3,2,1], key=f"s_{item}", index=1, label_visibility="collapsed")
                        c4.text_input("근거 의견", key=f"o_{item}", placeholder="사례 입력", label_visibility="collapsed")
                    st.divider()
        
        if st.button("✅ 자기고과 최종 제출"):
            st.balloons(); st.success("SRS 정식 평가표 기준에 따라 제출되었습니다.")

    elif menu == "팀원 평가(2/3차)":
        st.header("👥 팀원 능력 평가")
        if st.session_state.emp_df is not None:
            df = st.session_state.emp_df
            my_team = df[(df['2차평가자'] == user) | (df['3차평가자'] == user)]['성명'].tolist()
            target = st.selectbox("평가 대상 선택", my_team)
            if target:
                st.info(f"{target}님의 역량을 정식 기준에 따라 평가해 주세요.")
                # (내용은 자기고과와 동일한 루프 적용 가능)
        else: st.warning("조직도를 먼저 업로드하세요.")

    elif menu == "📈 관리자 현황판":
        st.header("📊 전사 통합 관리")
        f = st.file_uploader("조직도 엑셀 업로드", type=["xlsx"])
        if f: st.session_state.emp_df = pd.read_excel(f); st.success("로드 완료")
