import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- [1] 설정 및 시트 연결 ---
st.set_page_config(page_title="SRS 글로벌 인사평가 시스템", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=2)
def get_db(sheet_name="Users"):
    try:
        return conn.read(worksheet=sheet_name)
    except Exception as e:
        st.error(f"데이터를 불러올 수 없습니다: {e}")
        return None

# --- [2] 정식 평가 데이터 (이사님이 주신 25개 전 항목 상세 기준) ---
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
            "창의연구력": { "연구개선": "아이디어를 살리고 일의 순서개선이나 전진을 도모하고 있는가?" },
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
                "Persistence": "Did you work persistently and consistently?",
                "Efficiency": "Did you work efficiently without waste?"
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
                "Supervisor": "Do you cooperate effectively with supervisors?"
            },
            "Motivation": {
                "Proactive": "Willingness to handle tasks proactively?",
                "Responsible": "Sincerity and taking responsibility?",
                "Research": "Willingness to study tasks deeply?"
            },
            "Compliance": {
                "Discipline": "Efforts to maintain workplace order?",
                "Data": "Systematic management of reports and data",
                "Attendance": "Status of tardiness, leaving early, or absence?"
            }
        },
        "3. Competency": {
            "Knowledge": {
                "Job": "Is your job knowledge broad and deep?",
                "Related": "Basic knowledge of related tasks?"
            },
            "Judgment": {
                "Speed": "Speed of understanding rules and materials?",
                "Validity": "Are the conclusions accurate and valid?",
                "Solving": "Identifying essence and leading solutions?",
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

# --- [3] UI 텍스트 사전 ---
UI_TEXT = {
    "KO": {
        "m1": "자기고과 작성", "m2": "팀원 평가", "m3": "📊 관리자 현황판",
        "guide": "💡 본인의 성과와 역량을 객관적으로 증명할 수 있는 근거를 상세히 기록해 주세요. 작성된 근거는 평가의 중요한 기초 자료가 됩니다.",
        "score": "점수", "basis": "판단 근거", "rep": "🚀 자기 성장 REPORT", "sub": "✅ 최종 제출",
        "admin_reset": "🔑 직원 비밀번호 초기화", "save_ok": "성공적으로 저장되었습니다!"
    },
    "EN": {
        "m1": "Self-Evaluation", "m2": "Team Evaluation", "m3": "📊 Admin Dashboard",
        "guide": "💡 Please record detailed evidence that can objectively prove your performance. This is a crucial basis for evaluation.",
        "score": "Score", "basis": "Basis", "rep": "🚀 Self-Growth REPORT", "sub": "✅ Final Submit",
        "admin_reset": "🔑 Reset Employee Password", "save_ok": "Saved Successfully!"
    }
}

# --- [4] 데이터 처리 함수 ---
def save_result(records):
    try:
        existing = get_db("Results")
        new_df = pd.DataFrame(records)
        final = pd.concat([existing, new_df], ignore_index=True) if existing is not None else new_df
        conn.update(worksheet="Results", data=final)
        return True
    except Exception as e:
        st.error(f"저장 실패: {e}")
        return False

# --- [5] 메인 로직 시작 ---
user_db = get_db("Users")

if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'pw_status': 'N', 'lang': 'KO'})

if user_db is not None:
    # 1. 로그인 화면
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System")
        name = st.text_input("성명 (Name)")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            u = user_db[user_db['성명'] == name]
            if not u.empty and str(pw) == str(u.iloc[0]['비밀번호']):
                st.session_state.update({
                    'auth': True, 'user': name, 
                    'pw_status': str(u.iloc[0]['비번변경여부']), 
                    'lang': u.iloc[0]['언어'] if '언어' in u.columns else 'KO'
                })
                st.rerun()
            else: st.error("정보가 일치하지 않습니다.")

    # 2. 첫 로그인 시 비밀번호 변경 화면
    elif st.session_state.pw_status == 'N':
        st.title("🔑 보안 비밀번호 설정")
        st.warning("첫 로그인입니다. 안전한 사용을 위해 비밀번호를 변경해 주세요.")
        new_pw = st.text_input("새 비밀번호 (8자 이상)", type="password")
        if st.button("변경 완료"):
            if len(new_pw) >= 8:
                df = user_db.copy()
                df.loc[df['성명'] == st.session_state.user, ['비밀번호', '비번변경여부']] = [new_pw, 'Y']
                conn.update(worksheet="Users", data=df)
                st.session_state.pw_status = 'Y'
                st.success("비밀번호가 변경되었습니다!")
                st.rerun()
            else: st.error("8자 이상 입력하세요.")

    # 3. 메인 시스템 화면
    else:
        L = UI_TEXT[st.session_state.lang]
        E = EVAL_DATA[st.session_state.lang]
        user_name = st.session_state.user

        # 메뉴 구성 (이사님 전용 관리자 메뉴 포함)
        m_list = [L["m1"], L["m2"]]
        if user_name == "권정순": m_list.append(L["m3"])
        menu = st.sidebar.radio("메뉴", m_list)

        # 평가 폼 공통 함수
        def render_eval_form(pre, self_scores=None):
            st.info(L["guide"])
            tabs = st.tabs(list(E.keys()))
            current_results = {}
            for i, major in enumerate(E.keys()):
                with tabs[i]:
                    for sub, items in E[major].items():
                        st.markdown(f"#### 📍 {sub}")
                        for it, crit in items.items():
                            c1, c2, c3, c4 = st.columns([1.5, 3, 1, 3.5])
                            
                            # 팀장(2차 평가자)에게만 본인 점수 노출
                            label = f"**{it}**"
                            if self_scores and it in self_scores:
                                label += f" <span style='color:blue'>(본인:{self_scores[it]}점)</span>"
                            
                            c1.markdown(label, unsafe_allow_html=True)
                            c2.caption(crit)
                            # 기본 점수를 1점으로 설정 (이사님 요청)
                            score = c3.selectbox("점수", [1,2,3,4,5], key=f"{pre}_s_{it}")
                            basis = c4.text_input("근거", key=f"{pre}_r_{it}", placeholder="상세 근거 작성", label_visibility="collapsed")
                            current_results[it] = {"score": score, "basis": basis}
                        st.divider()
            return current_results

        # [메뉴 1] 자기고과 작성
        if menu == L["m1"]:
            st.header(L["m1"])
            eval_dict = render_eval_form("self")
            
            st.header(L["rep"])
            r1 = st.text_area("1. 2025 하반기 주요 성과", key="rep1")
            r2 = st.text_area("2. 하반기 동안 습득한 지식 및 역량", key="rep2")
            r3 = st.text_area("3. 하반기 동안 인재양성을 위한 노력", key="rep3")
            
            if st.button(L["sub"]):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                final_records = []
                for it, val in eval_dict.items():
                    final_records.append({"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "항목": it, "점수": val["score"], "근거": val["basis"]})
                # 리포트 통합 저장
                final_records.append({"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "리포트", "항목": "성과/역량/노력", "점수": "-", "근거": f"1:{r1}\n2:{r2}\n3:{r3}"})
                if save_result(final_records):
                    st.balloons()
                    st.success(L["save_ok"])

        # [메뉴 2] 팀원 평가 (2차/3차)
        elif menu == L["m2"]:
            st.header(L["m2"])
            # 내가 평가자인 팀원만 추출
            team_df = user_db[(user_db['2차평가자'] == user_name) | (user_db['3차평가자'] == user_name)]
            team_list = team_df['성명'].tolist()
            
            if team_list:
                target = st.selectbox("피평가자 선택", team_list)
                target_info = team_df[team_df['성명'] == target].iloc[0]
                
                # 2차 평가자(팀장)만 본인 점수 로드
                self_score_dict = None
                if target_info['2차평가자'] == user_name:
                    res_df = get_db("Results")
                    if res_df is not None:
                        target_eval = res_df[(res_df['피평가자'] == target) & (res_df['구분'] == "자기")]
                        if not target_eval.empty:
                            self_score_dict = dict(zip(target_eval['항목'], target_eval['점수']))
                
                eval_dict = render_eval_form(f"team_{target}", self_scores=self_score_dict)
                
                if st.button(f"{target}님 평가 결과 최종 제출"):
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    eval_type = "2차" if target_info['2차평가자'] == user_name else "3차"
                    records = [{"시간": now, "평가자": user_name, "피평가자": target, "구분": eval_type, "항목": it, "점수": v["score"], "근거": v["basis"]} for it, v in eval_dict.items()]
                    if save_result(records):
                        st.success(f"{target}님 {eval_type} 평가 {L['save_ok']}")
            else:
                st.info("평가할 팀원이 없습니다.")

        # [메뉴 3] 관리자 현황판
        elif menu == L["m3"]:
            st.header(L["m3"])
            st.subheader("👥 전사 직원 명단 및 비번 상태")
            st.dataframe(user_db[["성명", "부서", "직급", "비번변경여부", "언어", "2차평가자", "3차평가자"]], use_container_width=True)
            
            st.divider()
            st.subheader(L["admin_reset"])
            r_target = st.selectbox("초기화 대상 선택", user_db['성명'].tolist())
            if st.button("비밀번호 '12345678!'로 즉시 초기화"):
                new_df = user_db.copy()
                new_df.loc[new_df['성명'] == r_target, ['비밀번호', '비번변경여부']] = ['12345678!', 'N']
                conn.update(worksheet="Users", data=new_df)
                st.success(f"{r_target}님의 비밀번호가 초기화되었습니다. (전달: 12345678!)")
                st.rerun()
