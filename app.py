import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import time
import re

# --- [0] 보안 및 관리자 설정 ---
INITIAL_PW = "12345678!"
ADMIN_INFO = "경영관리부 권정순 이사 (010-2912-1408)"

def check_password_strength(pw):
    """비밀번호 정책: 8자 이상, 영문, 숫자, 특수문자 포함 여부 체크"""
    if len(pw) < 8: return False
    if not re.search("[a-zA-Z]", pw): return False
    if not re.search("[0-9]", pw): return False
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", pw): return False
    return True

# --- [1] 기본 설정 및 데이터 로딩 ---
st.set_page_config(page_title="SRS Global HR System", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data_fresh(worksheet_name):
    """데이터 로드 실패 시 백화현상을 방지하기 위한 안전장치 포함"""
    try:
        df = conn.read(worksheet=worksheet_name, ttl=0)
        if df is not None:
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x).fillna("")
            return df
        return pd.DataFrame()
    except Exception as e:
        # 에러 발생 시 로그만 찍고 빈 데이터프레임 반환하여 시스템 다운 방지
        print(f"Error loading {worksheet_name}: {e}")
        return pd.DataFrame()

# --- [2] 평가 데이터 (이사님 설계안 상세 문구 100% 무삭제 복구) ---
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
                "Persistence": "Did you work consistently and persistently without gaps?",
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
                "Horizontal": "Did you cooperate with colleagues to contribute to team efficiency?",
                "Respect": "Did you respect team opinions over your personal views?",
                "Supervisor": "Did you cooperate effectively with your supervisor for results?"
            },
            "Motivation": {
                "Proactivity": "What was your level of proactive engagement in your work?",
                "Responsibility": "Did you work sincerely without avoiding responsibility?",
                "Research": "What was your level of desire for deep research and study?"
            },
            "Compliance": {
                "Discipline": "Did you follow rules and strive to maintain workplace order?",
                "Data Mgmt": "Systematic management of periodic reports and personal work data",
                "Attendance": "How was your attendance status (tardiness, early leave, absence)?"
            }
        },
        "3. Job Competency": {
            "Knowledge": {
                "Job Knowledge": "Is your knowledge of your assigned duties broad and deep?",
                "Related Knowledge": "Is your basic knowledge of related work sufficient?"
            },
            "Judgment": {
                "Speed": "How fast do you correctly understand regulations, instructions, and data?",
                "Validity": "Are your judgments and conclusions accurate and valid?",
                "Problem Solving": "Do you identify root causes and lead effective solutions?",
                "Insight": "Do you grasp key points and reach conclusions independently?"
            },
            "Creativity": {
                "Improvement": "Do you always seek improvements through creative ideas and sequences?"
            },
            "Communication": {
                "Verbal": "Are your verbal reporting and explanation skills clear and accurate?",
                "Written": "Are your written reports and drafts clear and accurate?",
                "Negotiation": "How is your ability to handle coordination and negotiation smoothly?"
            }
        }
    }
}

LEADER_DATA = {
    "KO": {
        "1. 리더십(기본역량)": {
            "리더십": {
                "고객지향": "내부 혹은 외부 고객의 요구를 능동적으로 찾아내고 적시에 대응한다",
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
        },
        "3. 지식(전문역량)": {
            "지식": {
                "분석적사고": "문제를 해결하기 위해 필요한 정보나 자료가 무엇인지 정확히 파악한다.",
                "세밀한업무처리": "문제 발생 소지를 최소화하기 위해 조직의 관련 규정이나 과거 관행 등을 조사한다."
            }
        }
    },
    "EN": {
        "1. Leadership(Core)": {
            "Leadership": {
                "Customer Focus": "Proactively identify and respond to needs of internal/external customers in a timely manner.",
                "Responsibility": "Act planfully to achieve goals even without specific instructions.",
                "Teamwork": "Share opinions and explain decision backgrounds to gain consensus from members."
            }
        },
        "2. Performance(Execution)": {
            "Performance": {
                "Open Comm": "Share personal aspects first to build rapport and intimacy with others.",
                "Problem Solving": "Collect and analyze info/data to identify root causes when problems occur.",
                "Org Insight": "Understand the organization's strategy, operational methods, and history.",
                "Project Mgmt": "Systematically collect/analyze project info and establish detailed plans."
            }
        },
        "3. Knowledge(Professional)": {
            "Knowledge": {
                "Analytical": "Identify exactly what information or data is needed to solve problems.",
                "Detailed": "Investigate related regulations or past practices to minimize potential issues."
            }
        }
    }
}

# --- [3] 매핑 및 UI 사전 ---
NORMAL_MAPPING = {
    "속도": "업무의 양", "지속성": "업무의 양", "능률": "업무의 양", "정확성": "업무의 질", "성과": "업무의 질", "꼼꼼함": "업무의 질",
    "횡적협조": "협조성", "존중": "협조성", "상사와외 협조": "협조성", "적극성": "근무의욕", "책임감": "근무의욕", "연구심": "근무의욕",
    "규율": "복무상황", "DB화": "복무상황", "근태상황": "복무상황", "직무지식": "지식", "관련지식": "지식",
    "신속성": "이해판단력", "타당성": "이해판단력", "문제해결": "이해판단력", "통찰력": "이해판단력",
    "연구개선": "창의연구력", "구두표현": "표현절충", "문장표현": "표현절충", "절충": "표현절충"
}
LEADER_MAPPING = {"고객지향": "리더십", "책임감": "리더십", "팀워크지향": "리더십", "개방적 의사소통": "업무실적", "문제해결": "업무실적", "조직이해": "업무실적", "프로젝트 관리": "업무실적", "분석적사고": "지식", "세밀한업무처리": "지식"}

REPORT_QS = {
    "KO": {"q1": "1. 평가 기간동안 내가 낸 성과는 무엇입니까?", "q2": "2. 평가 기간동안 내가 습득한 지식이 무엇입니까?", "q3": "3. 평가 기간동안 내가 인재 양성을 위하여 무엇을 하였습니까?"},
    "EN": {"q1": "1. What are your achievements during this period?", "q2": "2. What knowledge did you acquire during this period?", "q3": "3. What did you do for talent development?"}
}

UI = {
    "KO": {
        "m1": "📝 자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드",
        "m5": "🚀 리더십 자기평가", "m6": "🎖️ 2차 리더십평가", "m7": "🎖️ 3차 리더십평가", 
        "m8": "📈 2차 팀원평가 대시보드", "m9": "🏆 2차 리더십평가 대시보드",
        "sub": "✅ 최종 제출", "save": "💾 임시 저장", "already": "✅ 제출 완료되었습니다.",
        "err": "⚠️ 모든 항목의 근거를 상세히(최소 5자) 작성해 주세요.", "report_title": "🚀 자기 성장 REPORT",
        "score": "점수", "basis": "근거 (상세히 작성)", "basis_msg": "※ 점수 산출 근거를 상세히 작성해 주세요",
        "target": "대상 선택", "self_info": "본인 입력", "l2_info": "2차 평가자", "done_msg": "저장되었습니다!", "pw_change": "🔒 비밀번호 변경 안내",
        "dash_title": "🔍 세부항목별 합산 점수 요약", "dash_desc": "평가 대상자 전체 명단입니다. 2차 평가(Final) 완료 시 점수가 자동으로 표시됩니다.",
        "contact_admin": f"📢 평가 내역 수정을 원하시면 {ADMIN_INFO}에게 연락해 주시기 바랍니다."
    },
    "EN": {
        "m1": "📝 Self-Evaluation", "m2": "👥 2nd Peer Eval", "m3": "⚖️ 3rd Final Eval", "m4": "📊 Admin Dashboard",
        "m5": "🚀 Leader Self-Eval", "m6": "🎖️ 2nd Lead Eval", "m7": "🎖️ 3rd Lead Eval",
        "m8": "📈 2nd Team Dashboard", "m9": "🏆 2nd Lead Dashboard",
        "sub": "✅ Final Submit", "save": "💾 Save Draft", "already": "✅ Submission Completed.",
        "err": "⚠️ Please provide detailed basis (min. 5 chars) for all items.", "report_title": "🚀 Self-Growth REPORT",
        "score": "Score", "basis": "Basis (Required)", "basis_msg": "※ Please provide detailed basis",
        "target": "Select Target", "self_info": "Self-Input", "l2_info": "2nd Eval", "done_msg": "Saved!", "pw_change": "🔒 Password Change Required",
        "dash_title": "🔍 Score Summary", "dash_desc": "Full target list. 2nd evaluation scores are shown once finalized.",
        "contact_admin": f"📢 For corrections, please contact {ADMIN_INFO}."
    }
}

# --- [4] 데이터 처리 함수 ---
def save_with_cleanup(recs, user_id, target_id, is_final, ws_name="Results"):
    try:
        df = conn.read(worksheet=ws_name, ttl=0).fillna("")
        if not df.empty:
            df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
            # 기존 Draft 데이터 제거 (덮어쓰기 로직)
            df = df[~((df['평가자'] == user_id) & (df['피평가자'] == target_id) & (df['구분'].str.contains("Draft", na=False)))]
            if is_final:
                # 최종 제출 시 기존 해당 조합의 모든 데이터 제거 후 새로 추가
                df = df[~((df['평가자'] == user_id) & (df['피평가자'] == target_id))]
        
        new_data = pd.DataFrame(recs)
        new_data['점수'] = pd.to_numeric(new_data['점수'], errors='coerce').fillna(0)
        f_df = pd.concat([df, new_data], ignore_index=True)
        conn.update(worksheet=ws_name, data=f_df)
        st.cache_data.clear()
        return True
    except: return False

# --- [5] 메인 엔진 가동 ---
if 'auth' not in st.session_state: st.session_state.update({'auth':False, 'user':'', 'ldr':'N', 'lang':'KO', 'need_pw_change':False})

# [백화현상 방지] Users 시트를 먼저 로드하고 실패 시 안내
db_raw = get_data_fresh("Users")

if db_raw.empty:
    st.error("⚠️ 시스템 데이터베이스 연결에 실패했습니다. 페이지를 새로고침(F5) 해주세요.")
else:
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System HR")
        n, p = st.text_input("Name"), st.text_input("PW", type="password")
        if st.button("Login"):
            u = db_raw[db_raw['성명'] == n.strip()]
            if not u.empty and str(p).strip() == str(u.iloc[0]['비밀번호']).strip():
                st.session_state.update({
                    'auth':True, 'user':n.strip(), 
                    'ldr':str(u.iloc[0]['리더여부']).upper(), 
                    'lang': str(u.iloc[0].get('언어', 'KO')).upper()
                })
                if str(p).strip() == INITIAL_PW: st.session_state.need_pw_change = True
                st.rerun()
            else: st.error("Login Error / Check Password")
            
    elif st.session_state.need_pw_change:
        L = UI[st.session_state.lang]
        st.title(L["pw_change"])
        st.warning("영문, 숫자, 특수문자를 모두 포함하여 8자 이상으로 변경해야 합니다.")
        with st.form("pw_form"):
            new_p = st.text_input("New PW", type="password"); confirm_p = st.text_input("Confirm", type="password")
            if st.form_submit_button("Change and Start"):
                if not check_password_strength(new_p): st.error("⚠️ 보안 취약 (영문+숫자+특수문자 조합 8자 이상 필수)")
                elif new_p != confirm_p: st.error("⚠️ 비밀번호 불일치")
                else:
                    db_f = conn.read(worksheet="Users", ttl=0)
                    db_f.loc[db_f['성명'] == st.session_state.user, '비밀번호'] = str(new_p)
                    conn.update(worksheet="Users", data=db_f); st.session_state.need_pw_change = False
                    st.cache_data.clear(); st.success("OK"); time.sleep(1); st.rerun()

    else:
        lang = st.session_state.lang if st.session_state.lang in UI else "KO"
        L, user = UI[lang], st.session_state.user
        res_df, ld_df = get_data_fresh("Results"), get_data_fresh("Leadership_Results")

        m_list = []
        if user != "김용환":
            m_list.append(L["m1"])
            if st.session_state.ldr == 'Y': m_list.append(L["m5"])
        t2_list = db_raw[db_raw['2차평가자'] == user]['성명'].tolist()
        t3_list = db_raw[db_raw['3차평가자'] == user]['성명'].tolist()
        if t2_list: m_list.extend([L["m2"], L["m8"]])
        ldr_t2 = db_raw[(db_raw['2차평가자'] == user) & (db_raw['리더여부'] == 'Y')]['성명'].tolist()
        if ldr_t2: m_list.extend([L["m6"], L["m9"]])
        if t3_list: 
            m_list.append(L["m3"])
            if L["m8"] not in m_list: m_list.append(L["m8"])
        ldr_t3 = db_raw[(db_raw['3차평가자'] == user) & (db_raw['리더여부'] == 'Y')]['성명'].tolist()
        if ldr_t3:
            m_list.append(L["m7"])
            if L["m9"] not in m_list: m_list.append(L["m9"])
        if user == "권정순": m_list.append(L["m4"])
        
        menu = st.sidebar.radio("Menu", m_list)

        def render_form(data_dict, pre, self_info=None, l2_info=None, eval_type="자기", ws_name="Results", is_3rd=False, target_name=None):
            if not target_name: return
            try:
                check_df = res_df if ws_name == "Results" else ld_df
                existing = check_df[(check_df['평가자']==user) & (check_df['피평가자']==target_name)] if not check_df.empty else pd.DataFrame()
                
                # [수정] Draft가 있어도 Final(최종)이 없으면 입력 창이 뜨도록 판별식 정교화
                is_final_done = not existing[existing['구분'].str.contains("Final|최종", na=False) & ~existing['구분'].str.contains("Draft", na=False)].empty
                draft_vals = existing[existing['구분'].str.contains("Draft", na=False)] if not existing.empty else pd.DataFrame()

                if is_final_done: st.success(L["already"])
                else:
                    if not draft_vals.empty: st.warning("⚠️ Loaded temporary saved data.")
                    with st.form(key=f"f_final_{pre}_{target_name}"):
                        tabs = st.tabs(list(data_dict.keys()))
                        res_dict = {}
                        for i, (major, subs) in enumerate(data_dict.items()):
                            with tabs[i]:
                                if is_3rd:
                                    st.subheader(f"🔍 {major} Review")
                                    s_sum, l2_sum, count = 0, 0, 0
                                    for sub_n, sub_items in subs.items():
                                        it_it = sub_items.items() if isinstance(sub_items, dict) else {sub_n: sub_items}.items()
                                        for it_n, crit in it_it:
                                            s_data = self_info.get(it_n, {"score": 0, "basis": "-"}) if self_info else {"score": 0, "basis": "-"}
                                            l2_data = l2_info.get(it_n, {"score": 0, "basis": "-", "evaluator": ""}) if l2_info else {"score": 0, "basis": "-", "evaluator": ""}
                                            s_sum += pd.to_numeric(s_data['score'], errors='coerce'); l2_sum += pd.to_numeric(l2_data['score'], errors='coerce'); count += 1
                                            st.markdown(f"**{it_n}**")
                                            c1, c2 = st.columns(2); c1.caption(f"[{L['self_info']}] {s_data['score']} | {s_data['basis']}"); c2.caption(f"[{l2_data.get('evaluator', L['l2_info'])}] {l2_data['score']} | {l2_data['basis']}")
                                    max_v = count * 5
                                    st.info(f"📊 {major} Summary - Self: **{int(s_sum)}** | 2nd: **{int(l2_sum)}** | **(Max: {max_v})**")
                                    st.divider()
                                    s = st.number_input(f"Final {major} {L['score']} (0~{max_v})", 0, max_v, value=int(l2_sum), key=f"s3_{target_name}_{major}")
                                    r = st.text_area(L["basis"], key=f"r3_{target_name}_{major}")
                                    res_dict[major] = {"score": s, "basis": r}
                                else:
                                    # 계층 구조 유연하게 처리하여 백화현상 방지
                                    for sub_key, items_or_desc in subs.items():
                                        if isinstance(items_or_desc, dict):
                                            st.markdown(f"#### 📍 {sub_key}")
                                            for it, crit in items_or_desc.items():
                                                saved = draft_vals[draft_vals['항목']==it] if not draft_vals.empty else pd.DataFrame()
                                                init_s = int(pd.to_numeric(saved['점수'], errors='coerce').iloc[0]) if not saved.empty else 3
                                                init_b = str(saved.iloc[0]['근거']) if not saved.empty else ""
                                                c1, c2, c3, c4 = st.columns([2, 4, 1, 3])
                                                lbl = f"**{it}**"
                                                if self_info and it in self_info: lbl += f"<br><span style='color:blue;'>[{L['self_info']}] {self_info[it]['score']}</span>"
                                                c1.markdown(lbl, unsafe_allow_html=True); c2.info(crit)
                                                s = c3.selectbox(L["score"], [1,2,3,4,5], index=max(0, min(4, init_s-1)), key=f"s_{target_name}_{it}_{ws_name}")
                                                r = c4.text_input(L["basis"], value=init_b, placeholder=L["basis_msg"], key=f"r_{target_name}_{it}_{ws_name}")
                                                res_dict[it] = {"score": s, "basis": r}
                                        else:
                                            saved = draft_vals[draft_vals['항목']==sub_key] if not draft_vals.empty else pd.DataFrame()
                                            init_s = int(pd.to_numeric(saved['점수'], errors='coerce').iloc[0]) if not saved.empty else 3
                                            init_b = str(saved.iloc[0]['근거']) if not saved.empty else ""
                                            c1, c2, c3, c4 = st.columns([2, 4, 1, 3]); c1.markdown(f"**{sub_key}**"); c2.info(items_or_desc)
                                            s = c3.selectbox(L["score"], [1,2,3,4,5], index=max(0, min(4, init_s-1)), key=f"s_{target_name}_{sub_key}_{ws_name}")
                                            r = c4.text_input(L["basis"], value=init_b, placeholder=L["basis_msg"], key=f"r_{target_name}_{sub_key}_{ws_name}")
                                            res_dict[sub_key] = {"score": s, "basis": r}

                        if pre == "self": # 영문에서도 REPORT 표시되도록 일원화
                            st.divider(); st.subheader(L["report_title"])
                            rep_data = {}
                            for k, v in REPORT_QS[lang].items():
                                saved_rep = existing[(existing['구분']=="리포트") & (existing['항목']==v)] if not existing.empty else pd.DataFrame()
                                rep_data[k] = st.text_area(v, value=str(saved_rep.iloc[0]['근거']) if not saved_rep.empty else "", key=f"rep_{k}_{target_name}")

                        bc1, bc2 = st.columns(2)
                        btn_s, btn_f = bc1.form_submit_button(L["save"]), bc2.form_submit_button(L["sub"])
                        if btn_s or btn_f:
                            is_f = btn_f
                            if is_f and any(len(str(v["basis"]).strip()) < 5 for v in res_dict.values()): st.error(L["err"])
                            else:
                                now = (datetime.datetime.now()+timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                                recs = [{"시간":now,"평가자":user,"피평가자":target_name,"구분":f"{eval_type}({'Final' if is_f else 'Draft'})","항목":k,"점수":v["score"],"근거":v["basis"]} for k,v in res_dict.items()]
                                if pre == "self":
                                    for kq, vq in rep_data.items(): recs.append({"시간":now,"평가자":user,"피평가자":user,"구분":"리포트","항목":REPORT_QS[lang][kq],"점수":0,"근거":vq})
                                if save_with_cleanup(recs, user, target_name, is_f, ws_name): st.success(L["done_msg"]); st.cache_data.clear(); st.rerun()
            except Exception as e: st.error(f"Render Error: {str(e)}")

        # --- [각 메뉴 핸들링] ---
        if menu == L["m1"]: render_form(EVAL_DATA[lang], "self", target_name=user)
        elif menu == L["m5"]: render_form(LEADER_DATA[lang], "ld_self", ws_name="Leadership_Results", target_name=user)
        elif menu == L["m2"]:
            target = st.selectbox(L["target"], t2_list, key="sel_m2")
            if target:
                ts = res_df[(res_df['피평가자']==target)&(res_df['구분'].str.contains("자기", na=False))]; si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ts.iterrows()}
                render_form(EVAL_DATA[lang], "ev2", si, eval_type="2차", target_name=target)
        elif menu == L["m6"]:
            target_l = st.selectbox(L["target"], ldr_t2, key="sel_m6")
            if target_l:
                ls = ld_df[(ld_df['피평가자']==target_l)&(ld_df['구분'].str.contains("자기", na=False))]; si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ls.iterrows()}
                render_form(LEADER_DATA[lang], "ld2", si, eval_type="2차", ws_name="Leadership_Results", target_name=target_l)
        elif menu == L["m3"]:
            target = st.selectbox(L["target"], t3_list, key="sel_m3")
            if target:
                ts = res_df[(res_df['피평가자']==target)&(res_df['구분'].str.contains("자기", na=False))]; te2 = res_df[(res_df['피평가자']==target)&(res_df['구분'].str.contains("2차", na=False))]
                si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ts.iterrows()}; l2i = {row['항목']: {'score': row['점수'], 'basis': row['근거'], 'evaluator': row['평가자']} for _, row in te2.iterrows()}
                render_form(EVAL_DATA[lang], "ev3", si, l2i, eval_type="3차", is_3rd=True, target_name=target)
        elif menu == L["m7"]:
            target_l3 = st.selectbox(L["target"], ldr_t3, key="sel_m7")
            if target_l3:
                ls3 = ld_df[(ld_df['피평가자']==target_l3)&(ld_df['구분'].str.contains("자기", na=False))]; le2 = ld_df[(ld_df['피평가자']==target_l3)&(ld_df['구분'].str.contains("2차", na=False))]
                si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ls3.iterrows()}; l2i = {row['항목']: {'score': row['점수'], 'basis': row['근거'], 'evaluator': row['평가자']} for _, row in le2.iterrows()}
                render_form(LEADER_DATA[lang], "ld3", si, l2i, eval_type="3차", ws_name="Leadership_Results", is_3rd=True, target_name=target_l3)
        elif menu == L["m8"]:
            st.title(L["m8"]); st.info(L["dash_desc"])
            my_targets = db_raw[(db_raw['2차평가자'] == user) | (db_raw['3차평가자'] == user)]['성명'].unique().tolist()
            if my_targets:
                my_evs = res_df[(res_df['피평가자'].isin(my_targets)) & (res_df['구분'].str.contains("2차", na=False)) & (res_df['구분'].str.contains("Final", na=False))].copy()
                my_evs['점수'] = pd.to_numeric(my_evs['점수'], errors='coerce').fillna(0); my_evs['세부항목'] = my_evs['항목'].map(NORMAL_MAPPING); pivot = my_evs.pivot_table(index='피평가자', columns='세부항목', values='점수', aggfunc='sum').fillna(0)
                dash_df = pd.DataFrame(index=my_targets); dash_df.index.name = '피평가자'
                fixed_cols = ["업무의 양", "업무의 질", "협조성", "근무의욕", "복무상황", "지식", "이해판단력", "창의연구력", "표현절충"]
                for c in fixed_cols:
                    if c not in pivot.columns: pivot[c] = 0
                st.dataframe(dash_df.join(pivot[fixed_cols]).fillna(0).assign(총점=lambda x: x.sum(axis=1)), use_container_width=True)
                st.divider(); st.warning(L["contact_admin"])
        elif menu == L["m9"]:
            st.title(L["m9"]); st.info(L["dash_desc"])
            my_ldr_t = db_raw[((db_raw['2차평가자'] == user) | (db_raw['3차평가자'] == user)) & (db_raw['리더여부'] == 'Y')]['성명'].unique().tolist()
            if my_ldr_t:
                my_evs_ld = ld_df[(ld_df['피평가자'].isin(my_ldr_t)) & (ld_df['구분'].str.contains("2차", na=False)) & (ld_df['구분'].str.contains("Final", na=False))].copy()
                my_evs_ld['점수'] = pd.to_numeric(my_evs_ld['점수'], errors='coerce').fillna(0); my_evs_ld['세부항목'] = my_evs_ld['항목'].map(LEADER_MAPPING); pivot_ld = my_evs_ld.pivot_table(index='피평가자', columns='세부항목', values='점수', aggfunc='sum').fillna(0)
                dash_ld_df = pd.DataFrame(index=my_ldr_t); dash_ld_df.index.name = '피평가자'
                fixed_ld = ["리더십", "업무실적", "지식"]
                for c in fixed_ld:
                    if c not in pivot_ld.columns: pivot_ld[c] = 0
                st.dataframe(dash_ld_df.join(pivot_ld[fixed_ld]).fillna(0).assign(총점=lambda x: x.sum(axis=1)), use_container_width=True)
                st.divider(); st.warning(L["contact_admin"])
        elif menu == L["m4"]:
            st.title(L["m4"]); status_df = []
            for _, r in db_raw.iterrows():
                nm = r['성명']; s_stat = "✅" if nm in res_df[res_df['구분'].str.contains("자기(Final)", na=False)]['피평가자'].values else "⏳"
                l_stat = ("✅" if nm in ld_df[ld_df['구분'].str.contains("자기(Final)", na=False)]['피평가자'].values else "⏳") if r['리더여부']=='Y' else "-"
                status_df.append({"Name": nm, "Self-Eval": s_stat, "Leadership": l_stat})
            st.table(pd.DataFrame(status_df))
