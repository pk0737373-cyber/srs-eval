import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import time
import re

# --- [0] 보안 정책 및 환경 설정 ---
INITIAL_PW = "12345678!"
PW_RULE_MSG = "🔐 보안 정책: 영문 + 숫자 + 특수문자 조합 8자 이상 필수 (본사 보안 지침)"

def check_password_strength(pw):
    """비밀번호 보안성 검증 엔진"""
    if len(pw) < 8: return False
    if not re.search("[a-zA-Z]", pw): return False
    if not re.search("[0-9]", pw): return False
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", pw): return False
    return True

# --- [1] 기본 설정 및 데이터 엔진 연결 ---
st.set_page_config(page_title="SRS Global HR Portal", page_icon="🎯", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def get_user_data():
    try:
        df = conn.read(worksheet="Users", ttl=0)
        return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x).fillna("")
    except: return pd.DataFrame()

@st.cache_data(ttl=5)
def get_results_data(ws_name):
    try:
        df = conn.read(worksheet=ws_name, ttl=0)
        return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x).fillna("")
    except: return pd.DataFrame()

# --- [2] 평가 지표 데이터 (이사님 설계 원문 100% 무삭제 복구) ---
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
                "상사와외 협조": "상사에 대해 협력하며 성과가 있는가?"
            },
            "근무의욕": {
                "적극성": "일에 능동적으로 대처하려는 의욕은 어떤가?",
                "책임감": "책임을 회피하지 않으며 성실하게 일하려는 의욕은 어떤가?",
                "연구심": "넓고 깊게 일을 연구하려는 의욕은 어떤가?"
            },
            "복무상황": {
                "규율": "규칙을 준수하며 직장질서유지에 애쓰는가?",
                "DB화": "정기적인 업무보고와 본인업무에 대한 데이터의 체계적인 관리(공유드라이브 활용 등)",
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
                "연구개선": "항상 창의적인 아이디어를 살리고 일의 순서개선이나 전진을 도모하고 있는가?"
            },
            "표현절충": {
                "구두표현": "구두에 의한 표현이 능숙하며 알기 쉽고 정확한가?",
                "문장표현": "문장에 의한 표현이 능숙하며 알기 쉽고 정확한가?",
                "절충": "대내외 관계자들과의 교섭을 원활하게 처리하는 능력은 어떤가?"
            }
        }
    },
    "EN": {
        "1. Performance": {
            "Quantity of Work": {
                "Speed": "Did you process work quickly without any delay?",
                "Persistence": "Did you work consistently and persistently?",
                "Efficiency": "Did you handle work accurately and efficiently without waste?"
            },
            "Quality of Work": {
                "Accuracy": "Are the results of your work reliable?",
                "Achievement": "Was the achievement of your work outstanding in its content?",
                "Thoroughness": "Were you thorough in follow-up and completion?"
            }
        },
        "2. Work Attitude": {
            "Cooperation": {
                "Horizontal": "Did you cooperate with colleagues for efficiency?",
                "Respect": "Did you respect team opinions over your personal views?",
                "Supervisor": "Did you cooperate effectively with your supervisor?"
            },
            "Motivation": {
                "Proactivity": "What was your level of proactive engagement?",
                "Responsibility": "Did you work sincerely without avoiding responsibility?",
                "Research": "What was your level of desire for deep research?"
            },
            "Compliance": {
                "Discipline": "Did you follow rules and maintain workplace order?",
                "Data Mgmt": "Systematic management of periodic reports and data",
                "Attendance": "What was your attendance status (tardiness, leave)?"
            }
        },
        "3. Job Competency": {
            "Knowledge": {
                "Job Knowledge": "Is your knowledge of your duties broad and deep?",
                "Related": "Is your basic knowledge of related work sufficient?"
            },
            "Judgment": {
                "Speed": "How fast do you correctly understand regulations?",
                "Validity": "Are your judgments and conclusions accurate and valid?",
                "Problem Solving": "Do you lead effective solutions for root causes?",
                "Insight": "Do you reach conclusions independently?"
            },
            "Creativity": {
                "Improvement": "Do you seek improvements through creative ideas?"
            },
            "Communication": {
                "Verbal": "Are your verbal reporting skills clear and accurate?",
                "Written": "Are your written reports clear and accurate?",
                "Negotiation": "How is your ability to handle coordination smoothly?"
            }
        }
    }
}

LEADER_DATA = {
    "KO": {
        "1. 리더십(기본역량)": {
            "리더십": {
                "고객지향": "내부 혹은 외부 고객의 요구를 능동적으로 찾아내고 적시에 대응한다.",
                "책임감": "특별한 지시를 하지 않더라도 업무목표를 달성하기 위해 계획적으로 행동한다.",
                "팀워크지향": "구성원의 공감을 얻기 위해 자주 의견을 공유하고 의사결정의 배경이나 당위성에 대해 설명한다."
            }
        },
        "2. 업무실적(실행역량)": {
            "업무실적": {
                "개방적 의사소통": "상대방이 친밀감을 느낄 수 있도록 자신의 사적인 부분을 먼저 이야기한다.",
                "문제해결": "문제 발생 시 문제상황과 관련된 정보와 자료를 수집하고 분석하여 문제의 근본원인을 규명한다.",
                "조직이해": "조직의 전략, 운영방식, 역사 등을 파악한다.",
                "프로젝트 관리": "프로젝트와 관련된 정보를 체계적으로 수집, 분석하여 계획을 수립한다."
            }
        }
    },
    "EN": {
        "1. Leadership(Core)": {
            "Leadership": {
                "Customer Focus": "Proactively identify and respond to needs of customers.",
                "Responsibility": "Act planfully to achieve goals without instructions.",
                "Teamwork": "Share opinions to gain consensus from members."
            }
        },
        "2. Performance(Execution)": {
            "Communication": "Share personal aspects to build rapport.",
            "Problem Solving": "Analyze data to identify root causes.",
            "Project Mgmt": "Systematically collect info and establish plans."
        }
    }
}

NORMAL_MAPPING = {"속도":"업무의 양","지속성":"업무의 양","능률":"업무의 양","정확성":"업무의 질","성과":"업무의 질","꼼꼼함":"업무의 질","횡적협조":"협조성","존중":"협조성","상사와외 협조":"협조성","적극성":"근무의욕","책임감":"근무의욕","연구심":"근무의욕","규율":"복무상황","DB화":"복무상황","근태상황":"복무상황","직무지식":"지식","관련지식":"지식","신속성":"이해판단력","타당성":"이해판단력","문제해결":"이해판단력","통찰력":"이해판단력","연구개선":"창의연구력","구두표현":"표현절충","문장표현":"표현절충","절충":"표현절충"}

REPORT_QS = {
    "KO": {"q1": "1. 주요 성과", "q2": "2. 습득 지식", "q3": "3. 인재 양성 노력"},
    "EN": {"q1": "1. Key Achievements", "q2": "2. Knowledge Acquired", "q3": "3. Talent Development Efforts"}
}

UI = {
    "KO": {
        "m1": "📝 자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드",
        "m5": "🚀 리더십 자기평가", "m6": "🎖️ 2차 리더십평가", "m8": "📈 팀원 평가현황(누계)",
        "save": "💾 임시 저장 (Draft)", "sub": "✅ 최종 제출 (Final)", "logout": "🔓 로그아웃",
        "err_null": "⚠️ [제출 불가] 점수 선택 및 근거(5자 이상)를 상세히 작성해 주세요.",
        "already": "✅ 최종 제출이 완료되어 조회 모드로 전환합니다.", "ref_1": "👤 팀원(1차)", "ref_2": "👥 리더(2차)", "score": "점수", "basis": "근거"
    },
    "EN": {
        "m1": "📝 Self-Evaluation", "m2": "👥 2nd Peer Eval", "m3": "⚖️ 3rd Final Eval", "m4": "📊 Admin Dashboard",
        "m5": "🚀 Leader Self-Eval", "m6": "🎖️ 2nd Lead Eval", "m8": "📈 Team Summary",
        "save": "💾 Save Draft", "sub": "✅ Final Submit", "logout": "🔓 Logout",
        "err_null": "⚠️ [Submission Failed] Please provide all scores and details (min 5 chars).",
        "already": "✅ Submission Completed.", "ref_1": "👤 Self(1st)", "ref_2": "👥 Leader(2nd)", "score": "Score", "basis": "Comments"
    }
}

# --- [3] 데이터 저장 및 누계 대시보드 엔진 ---
def save_data_engine(recs, user_id, target_id, is_final, ws_name="Results"):
    try:
        df_old = conn.read(worksheet=ws_name, ttl=0).fillna("")
        if any("리포트" in r['구분'] for r in recs):
            df_new = df_old[~((df_old['평가자'] == user_id) & (df_old['구분'].str.contains("리포트", na=False)))]
        else:
            df_new = df_old[~((df_old['평가자'] == user_id) & (df_old['피평가자'] == target_id) & (~df_old['구분'].str.contains("리포트", na=False)))]
        final_df = pd.concat([df_new, pd.DataFrame(recs)], ignore_index=True)
        conn.update(worksheet=ws_name, data=final_df)
        st.cache_data.clear()
        return True
    except: return False

def render_leader_summary(ws_name):
    st.subheader(f"📊 나의 팀원 평가 점수 누계 ({ws_name})")
    df = get_results_data(ws_name)
    if df.empty: return
    my_evals = df[df['평가자'] == st.session_state.user].copy()
    if my_evals.empty:
        st.info("아직 완료한 평가 데이터가 없습니다.")
        return
    my_evals['Category'] = my_evals['항목'].map(NORMAL_MAPPING).fillna("기타/종합")
    my_evals['점수'] = pd.to_numeric(my_evals['점수'], errors='coerce').fillna(0)
    summary = my_evals.pivot_table(index='피평가자', columns='Category', values='점수', aggfunc='sum').fillna(0)
    st.dataframe(summary.style.background_gradient(cmap='Blues'), use_container_width=True)

# --- [4] 메인 렌더링 엔진 (이사님 요청: 3차 간소화 로직 적용) ---
def render_engine(data_dict, pre, eval_type="자기", ws_name="Results", target_name=None):
    if not target_name:
        st.info("평가 대상을 선택하시면 항목이 나타납니다.")
        return
    
    L = UI[st.session_state.lang]
    check_df = get_results_data(ws_name)
    existing = check_df[(check_df['평가자']==st.session_state.user) & (check_df['피평가자']==target_name)] if not check_df.empty else pd.DataFrame()
    is_final_done = not existing[existing['구분'].str.contains("Final", na=False)].empty

    if is_final_done:
        st.success(L["already"])
        st.dataframe(existing, use_container_width=True, hide_index=True)
    else:
        # [데이터 참조] 팀원(자기) 및 2차 평가 데이터 로드
        ref_self = check_df[(check_df['피평가자']==target_name) & (check_df['구분'].str.contains("자기", na=False))]
        ref_peer = check_df[(check_df['피평가자']==target_name) & (check_df['구분'].str.contains("2차", na=False))]
        draft_vals = existing[existing['구분'].str.contains("Draft", na=False)]

        tab_list = list(data_dict.keys())
        tabs = st.tabs(tab_list)
        
        with st.form(key=f"form_{pre}_{target_name}_{ws_name}"):
            res_dict = {}
            for i, major in enumerate(tab_list):
                with tabs[i]:
                    # --- [이사님 요청] 3차 최종평가 전용 간소화 로직 ---
                    if eval_type == "3차최종":
                        st.markdown(f"### 🎯 {major} 종합 평가")
                        for sub_cat, items in data_dict[major].items():
                            st.write(f"**[{sub_cat}]**")
                            for it_name in items.keys():
                                s_row = ref_self[ref_self['항목']==it_name]
                                p_row = ref_peer[ref_peer['항목']==it_name]
                                s_val = f"{s_row.iloc[0]['점수']}점" if not s_row.empty else "-"
                                p_val = f"{p_row.iloc[0]['점수']}점" if not p_row.empty else "-"
                                st.caption(f"• {it_name} ➔ {L['ref_1']}: {s_val} | {L['ref_2']}: {p_val}")
                        
                        d_row = draft_vals[draft_vals['항목']==major]
                        init_s = int(d_row.iloc[0]['점수']) if not d_row.empty else 0
                        init_b = str(d_row.iloc[0]['근거']) if not d_row.empty else ""
                        c1, c2 = st.columns([1, 4])
                        s = c1.selectbox(f"{L['score']}", [0,1,2,3,4,5], index=init_s, key=f"s_{pre}_{major}_{target_name}")
                        r = c2.text_input(f"{L['basis']}", value=init_b, key=f"r_{pre}_{major}_{target_name}")
                        res_dict[major] = {"score": s, "basis": r}
                    
                    # --- [일반] 자기/2차 평가 로직 (세부 항목 전체 노출) ---
                    else:
                        for sub_key, items in data_dict[major].items():
                            st.markdown(f"#### 📍 {sub_key}")
                            for it, crit in items.items():
                                val = draft_vals[draft_vals['항목']==it]
                                init_s = int(val.iloc[0]['점수']) if not val.empty else 0
                                init_b = str(val.iloc[0]['근거']) if not val.empty else ""
                                
                                # [참조] 팀원 의견 노출 (2차 평가 시)
                                r_row = ref_self[ref_self['항목']==it]
                                r_s = r_row.iloc[0]['점수'] if not r_row.empty else "-"
                                r_b = r_row.iloc[0]['근거'] if not r_row.empty else "의견 없음"
                                
                                c1, c2, c3 = st.columns([3, 1, 3])
                                c1.markdown(f"**{it}**\n\n{crit}")
                                if pre != "self": c1.caption(f"👤 {L['ref_1']}: ({r_s}점) {r_b}")
                                s = c2.selectbox(L["score"], [0, 1, 2, 3, 4, 5], index=init_s, key=f"s_{pre}_{it}_{target_name}")
                                r = c3.text_input(L["basis"], value=init_b, key=f"r_{pre}_{it}_{target_name}")
                                res_dict[it] = {"score": s, "basis": r}

            if pre in ["self", "ld_self"]:
                st.divider(); st.subheader("🚀 자기 성장 REPORT")
                for k, v in REPORT_QS[st.session_state.lang].items():
                    r_val = existing[(existing['구분'].str.contains("리포트")) & (existing['항목']==v)]
                    st.text_area(v, value=str(r_val.iloc[0]['근거']) if not r_val.empty else "", key=f"rep_{pre}_{k}_{target_name}")

            col1, col2 = st.columns(2)
            if col1.form_submit_button(L["save"]) or col2.form_submit_button(L["sub"]):
                is_f = col2.form_submit_button(L["sub"])
                if is_f and any(v["score"] == 0 or len(str(v["basis"]).strip()) < 5 for v in res_dict.values()):
                    st.error(L["err_null"])
                else:
                    status = "Final" if is_f else "Draft"
                    now = (datetime.datetime.now()+timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                    recs = [{"시간":now,"평가자":st.session_state.user,"피평가자":target_name,"구분":f"{eval_type}({status})","항목":k,"점수":v["score"],"근거":v["basis"]} for k,v in res_dict.items()]
                    if save_data_engine(recs, st.session_state.user, target_name, is_f, ws_name):
                        st.success("데이터가 반영되었습니다."); time.sleep(1); st.rerun()

# --- [5] 권한 제어 및 실행부 ---
if 'auth' not in st.session_state: st.session_state.update({'auth':False, 'user':'', 'ldr':'N', 'lang':'KO'})
db_users = get_user_data()

if not db_users.empty:
    if not st.session_state.auth:
        st.title("🛡️ SRS Global HR Portal")
        n, p = st.text_input("Name"), st.text_input("PW", type="password")
        if st.button("Login"):
            u = db_users[db_users['성명'] == n.strip()]
            if not u.empty and str(p).strip() == str(u.iloc[0]['비밀번호']).strip():
                st.session_state.update({'auth':True, 'user':n.strip(), 'ldr':str(u.iloc[0]['리더여부']).upper(), 'lang':str(u.iloc[0]['언어'])})
                st.rerun()
            else: st.error("Login Failed")
    else:
        L, user = UI[st.session_state.lang], st.session_state.user
        if st.sidebar.button(L["logout"]): st.session_state.clear(); st.rerun()
        
        m_list = []
        if user != "김용환": m_list.append(L["m1"])
        if st.session_state.ldr == 'Y': m_list.extend([L["m5"], L["m8"]])
        t2_list = db_users[db_users['2차평가자'] == user]['성명'].tolist()
        if t2_list: m_list.append(L["m2"])
        t3_list = db_users[db_users['3차평가자'] == user]['성명'].tolist()
        if t3_list: m_list.append(L["m3"])
        
        menu = st.sidebar.radio("Menu", m_list)
        if menu == L["m1"]: st.title(L["m1"]); render_engine(EVAL_DATA[st.session_state.lang], "self", target_name=user)
        elif menu == L["m5"]: st.title(L["m5"]); render_engine(LEADER_DATA[st.session_state.lang], "ld_self", eval_type="리더십", ws_name="Leadership_Results", target_name=user)
        elif menu == L["m2"]:
            st.title(L["m2"]); target = st.selectbox("대상 선택", [""] + t2_list)
            render_engine(EVAL_DATA[st.session_state.lang], "peer2", eval_type="2차팀원", target_name=target)
        elif menu == L["m3"]:
            st.title(L["m3"]); target = st.selectbox("최종 평가 대상 선택", [""] + t3_list)
            render_engine(EVAL_DATA[st.session_state.lang], "peer3", eval_type="3차최종", target_name=target)
        elif menu == L["m8"]: render_leader_summary("Results")
        elif menu == L["m4"]:
            st.title("📊 Admin Dashboard"); st.dataframe(get_results_data("Results"), use_container_width=True)
else: st.error("Data Load Error.")
