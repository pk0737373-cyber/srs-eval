import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import time

# --- [0] 보안 및 관리자 설정 ---
INITIAL_PW = "12345678!"
ADMIN_INFO = "경영관리부 권정순 이사 (010-2912-1408)"

# --- [1] 기본 설정 ---
st.set_page_config(page_title="SRS Global HR System", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 구글 API 차단 방지를 위한 캐싱 (60초 유지)
@st.cache_data(ttl=60)
def get_data_cached(worksheet_name):
    try:
        df = conn.read(worksheet=worksheet_name, ttl=0)
        if df is not None:
            return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x).fillna("")
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# --- [2] 평가 데이터 (상세 문구 100% 무삭제 반영) ---
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
                "Speed": "Did you process work quickly without delay?",
                "Persistence": "Did you work consistently and persistently?",
                "Efficiency": "Did you handle work accurately without waste?"
            },
            "Quality of Work": {
                "Accuracy": "Are the results of your work reliable?",
                "Achievement": "Was the achievement outstanding in content?",
                "Thoroughness": "Were you thorough in follow-up and completion?"
            }
        },
        "2. Work Attitude": {
            "Cooperation": {
                "Horizontal": "Did you cooperate with colleagues for efficiency?",
                "Respect": "Did you respect team opinions over yours?",
                "Supervisor": "Did you cooperate effectively with your supervisor?"
            },
            "Motivation": {
                "Proactivity": "What was your level of proactive engagement?",
                "Responsibility": "Did you work sincerely without avoiding it?",
                "Research": "What was your level of desire for research?"
            },
            "Compliance": {
                "Discipline": "Did you follow rules and maintain order?",
                "Data Mgmt": "Systematic management of periodic reports and data",
                "Attendance": "How was your attendance status?"
            }
        },
        "3. Job Competency": {
            "Knowledge": {
                "Job Knowledge": "Is your knowledge of duties broad and deep?",
                "Related Knowledge": "Is your basic related knowledge sufficient?"
            },
            "Judgment": {
                "Speed": "How fast do you understand instructions and data?",
                "Validity": "Are your judgments and conclusions accurate?",
                "Problem Solving": "Do you lead effective solutions for problems?",
                "Insight": "Do you grasp key points independently?"
            },
            "Creativity": {
                "Improvement": "Do you seek improvements through creative ideas?"
            },
            "Communication": {
                "Verbal": "Are your verbal reporting skills clear?",
                "Written": "Are your written reports clear and accurate?",
                "Negotiation": "Ability to handle coordination smoothly?"
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
                "Customer Focus": "Respond to internal/external customer needs timely.",
                "Responsibility": "Act planfully to achieve goals independently.",
                "Teamwork": "Share opinions and explain backgrounds for consensus."
            }
        },
        "2. Performance(Execution)": {
            "Performance": {
                "Open Comm": "Share personal aspects first to build rapport.",
                "Problem Solving": "Analyze data to identify root causes of problems.",
                "Org Insight": "Understand strategy, operational methods, and history.",
                "Project Mgmt": "Collect project info and establish detailed plans."
            }
        },
        "3. Knowledge(Professional)": {
            "Knowledge": {
                "Analytical": "Identify exactly what information is needed for problems.",
                "Detailed": "Investigate regulations or practices to minimize issues."
            }
        }
    }
}

# [대시보드 합산 매핑] 이사님 설계안 기준
NORMAL_MAPPING = {
    "속도": "업무의 양", "지속성": "업무의 양", "능률": "업무의 양",
    "정확성": "업무의 질", "성과": "업무의 질", "꼼꼼함": "업무의 질",
    "횡적협조": "협조성", "존중": "협조성", "상사와외 협조": "협조성",
    "적극성": "근무의욕", "책임감": "근무의욕", "연구심": "근무의욕",
    "규율": "복무상황", "DB화": "복무상황", "근태상황": "복무상황",
    "직무지식": "지식", "관련지식": "지식",
    "신속성": "이해판단력", "타당성": "이해판단력", "문제해결": "이해판단력", "통찰력": "이해판단력",
    "연구개선": "창의연구력",
    "구두표현": "표현절충", "문장표현": "표현절충", "절충": "표현절충"
}

REPORT_UI = {
    "KO": {"q1": "1. 평가 기간동안 내가 낸 성과는 무엇입니까?", "q2": "2. 평가 기간동안 내가 습득한 지식이 무엇입니까?", "q3": "3. 평가 기간동안 내가 인재 양성을 위하여 무엇을 하였습니까?"},
    "EN": {"q1": "1. What are your achievements?", "q2": "2. What knowledge acquired?", "q3": "3. Efforts for talent development?"}
}

UI = {
    "KO": {
        "m1": "📝 자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드",
        "m5": "🚀 리더십 자기평가", "m6": "🎖️ 2차 리더십평가", "m7": "🎖️ 3차 리더십평가", 
        "m8": "📈 2차 팀원평가 대시보드", "m9": "🏆 2차 리더십평가 대시보드",
        "sub": "✅ 최종 제출", "save": "💾 임시 저장", "already": "✅ 제출 완료되었습니다.",
        "err": "⚠️ 모든 항목의 근거를 상세히 작성해 주세요.", "report_title": "🚀 자기 성장 REPORT",
        "score": "점수", "basis": "근거 (상세히 작성)", "basis_msg": "※ 점수 산출 근거를 상세히 작성해 주세요",
        "target": "대상 선택", "self_info": "본인 입력", "done_msg": "저장되었습니다!", "pw_change": "🔒 비밀번호 변경 안내",
        "dash_title": "🔍 세부항목별 합산 점수 요약", "dash_desc": "평가하신 결과가 세부항목 단위로 합산되어 표시됩니다. 상대평가의 적절성을 검토해 주세요.",
        "contact_admin": f"💡 수정이 필요한 경우 관리자({ADMIN_INFO})에게 연락해 주세요."
    },
    "EN": {
        "m1": "📝 Self-Eval", "m2": "👥 2nd Eval", "m3": "⚖️ 3rd Final", "m4": "📊 Admin",
        "m5": "🚀 Lead Self-Eval", "m6": "🎖️ 2nd Lead Eval", "m7": "🎖️ 3rd Lead Eval",
        "m8": "📈 2nd Team Dashboard", "m9": "🏆 2nd Leadership Dashboard",
        "sub": "✅ Submit", "save": "💾 Save Draft", "already": "✅ Completed.",
        "err": "⚠️ Provide detailed reasons.", "report_title": "🚀 Growth Report",
        "score": "Score", "basis": "Basis", "basis_msg": "※ Please provide detailed basis",
        "target": "Select Target", "self_info": "Self-Input", "done_msg": "Saved!", "pw_change": "🔒 Password Change",
        "dash_title": "🔍 Summary by Sub-categories", "dash_desc": "Scores are aggregated by sub-category. Please review for relative fairness.",
        "contact_admin": f"💡 For corrections, contact Admin ({ADMIN_INFO})."
    }
}

# --- [3] 데이터 처리 함수 ---
def save_with_cleanup(recs, user_id, target_id, is_final, ws_name="Results"):
    try:
        df = conn.read(worksheet=ws_name, ttl=0).fillna("")
        if not df.empty:
            df = df[~((df['평가자'] == user_id) & (df['피평가자'] == target_id) & (df['구분'].str.contains("Draft", na=False)))]
            if is_final:
                df = df[~((df['평가자'] == user_id) & (df['피평가자'] == target_id))]
        f_df = pd.concat([df, pd.DataFrame(recs)], ignore_index=True)
        conn.update(worksheet=ws_name, data=f_df)
        st.cache_data.clear()
        return True
    except Exception: return False

# --- [4] 메인 로직 ---
db_raw = get_data_cached("Users")
if 'auth' not in st.session_state: 
    st.session_state.update({'auth':False, 'user':'', 'ldr':'N', 'lang':'KO', 'need_pw_change':False})

if not db_raw.empty:
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System HR")
        n, p = st.text_input("Name"), st.text_input("PW", type="password")
        if st.button("Login"):
            u = db_raw[db_raw['성명'] == n.strip()]
            if not u.empty:
                stored_pw = str(u.iloc[0]['비밀번호']).strip()
                if str(p).strip() == stored_pw:
                    u_lang = str(u.iloc[0].get('언어', 'KO')).upper()
                    st.session_state.update({'auth':True, 'user':n.strip(), 'ldr':str(u.iloc[0]['리더여부']).upper(), 'lang': u_lang if u_lang in ["KO", "EN"] else "KO"})
                    if stored_pw == INITIAL_PW: st.session_state.need_pw_change = True
                    st.rerun()
                else: st.error("Password Incorrect")
            else: st.error("User Not Found")
            
    elif st.session_state.need_pw_change:
        L = UI[st.session_state.lang]
        st.title(L["pw_change"])
        with st.form("pw_change_form"):
            new_p = st.text_input("New Password", type="password")
            confirm_p = st.text_input("Confirm New Password", type="password")
            if st.form_submit_button("Change and Start"):
                if len(new_p) < 6: st.error("6자리 이상 설정")
                elif new_p == INITIAL_PW: st.error("초기 비번과 다르게 설정")
                elif new_p != confirm_p: st.error("비밀번호 불일치")
                else:
                    db_f = conn.read(worksheet="Users", ttl=0)
                    db_f.loc[db_f['성명'] == st.session_state.user, '비밀번호'] = str(new_p)
                    conn.update(worksheet="Users", data=db_f)
                    st.session_state.need_pw_change = False
                    st.cache_data.clear(); st.success("변경 완료!"); time.sleep(1); st.rerun()

    else:
        lang = st.session_state.lang if st.session_state.lang in UI else "KO"
        L, user = UI[lang], st.session_state.user
        res_df = get_data_cached("Results")
        ld_df = get_data_cached("Leadership_Results")

        # [핵심] 김용환 대표님 전용 메뉴 필터링 로직
        m_list = []
        if user != "김용환":
            m_list.append(L["m1"])
            if st.session_state.ldr == 'Y': m_list.append(L["m5"])
        
        t2_list = db_raw[db_raw['2차평가자'] == user]['성명'].tolist()
        t3_list = db_raw[db_raw['3차평가자'] == user]['성명'].tolist()
        
        if t2_list: 
            m_list.append(L["m2"])
            m_list.append(L["m8"]) 
        ldr_t2_list = db_raw[(db_raw['2차평가자'] == user) & (db_raw['리더여부'] == 'Y')]['성명'].tolist()
        if ldr_t2_list:
            m_list.append(L["m6"])
            m_list.append(L["m9"]) 
        if t3_list: m_list.append(L["m3"])
        ldr_t3_list = db_raw[(db_raw['3차평가자'] == user) & (db_raw['리더여부'] == 'Y')]['성명'].tolist()
        if ldr_t3_list: m_list.append(L["m7"])
        if user == "권정순": m_list.append(L["m4"])
        
        menu = st.sidebar.radio("Menu", m_list)

        def render_form(data_dict, pre, self_info=None, eval_type="자기", ws_name="Results", is_3rd=False, target_name=None):
            if not target_name: return
            try:
                check_df = res_df if ws_name == "Results" else ld_df
                existing = check_df[(check_df['평가자']==user) & (check_df['피평가자']==target_name)] if not check_df.empty else pd.DataFrame()
                is_final_done = not existing[existing['구분'].str.contains("Final|최종|자기", na=False)].empty if not existing.empty else False
                draft_vals = existing[existing['구분'].str.contains("Draft", na=False)] if not existing.empty else pd.DataFrame()

                if is_final_done:
                    st.success(L["already"])
                else:
                    if not draft_vals.empty: st.warning("⚠️ Loaded draft content.")
                    form_id = f"f_vfinal_full_{pre}_{eval_type}_{target_name}_{ws_name}"
                    with st.form(key=form_id):
                        tabs = st.tabs(list(data_dict.keys()))
                        res_dict = {}
                        for i, (major, subs) in enumerate(data_dict.items()):
                            with tabs[i]:
                                if is_3rd:
                                    st.subheader(f"🔍 {major} Review")
                                    item_it = subs.items() if isinstance(subs, dict) else {major: subs}.items()
                                    for sub_n, sub_items in item_it:
                                        sub_it = sub_items.items() if isinstance(sub_items, dict) else {sub_n: sub_items}.items()
                                        for it_n, crit in sub_it:
                                            info = self_info.get(it_n, {"score": "-", "basis": ""}) if self_info else {"score": "-", "basis": ""}
                                            st.markdown(f"**{it_n}**: {info['score']} | {info['basis']}")
                                    st.divider()
                                    c1, c2 = st.columns([1, 3])
                                    s = c1.selectbox(L["score"], [1,2,3,4,5], index=2, key=f"s3_{target_name}_{major}_{form_id}")
                                    r = c2.text_area(L["basis"], key=f"r3_{target_name}_{major}_{form_id}")
                                    res_dict[major] = {"score": s, "basis": r}
                                else:
                                    sub_it = subs.items() if isinstance(subs, dict) else {major: subs}.items()
                                    for sub, items in sub_it:
                                        if isinstance(items, dict):
                                            st.markdown(f"#### 📍 {sub}")
                                            for it, crit in items.items():
                                                saved = draft_vals[draft_vals['항목']==it] if not draft_vals.empty else pd.DataFrame()
                                                init_s = int(float(saved.iloc[0]['점수'])) if not saved.empty else 3
                                                init_b = str(saved.iloc[0]['근거']) if not saved.empty else ""
                                                c1, c2, c3, c4 = st.columns([2, 3, 1, 3])
                                                lbl = f"**{it}**"
                                                if self_info and it in self_info: lbl += f"<br><span style='color:blue; font-size:0.85em;'>[{L['self_info']}] {self_info[it]['score']}</span>"
                                                c1.markdown(lbl, unsafe_allow_html=True); c2.info(crit)
                                                s = c3.selectbox(L["score"], [1,2,3,4,5], index=max(0, min(4, init_s-1)), key=f"s_{target_name}_{it}_{form_id}")
                                                r = c4.text_input(L["basis"], value=init_b, placeholder=L["basis_msg"], key=f"r_{target_name}_{it}_{form_id}")
                                                res_dict[it] = {"score": s, "basis": r}
                                        else:
                                            saved = draft_vals[draft_vals['항목']==sub] if not draft_vals.empty else pd.DataFrame()
                                            init_s = int(float(saved.iloc[0]['점수'])) if not saved.empty else 3
                                            init_b = str(saved.iloc[0]['근거']) if not saved.empty else ""
                                            c1, c2, c3, c4 = st.columns([2, 3, 1, 3])
                                            lbl = f"**{sub}**"
                                            if self_info and sub in self_info: lbl += f"<br><span style='color:blue; font-size:0.85em;'>[{L['self_info']}] {self_info[sub]['score']}</span>"
                                            c1.markdown(lbl, unsafe_allow_html=True); c2.info(items)
                                            s = c3.selectbox(L["score"], [1,2,3,4,5], index=max(0, min(4, init_s-1)), key=f"s_{target_name}_{sub}_{form_id}")
                                            r = c4.text_input(L["basis"], value=init_b, placeholder=L["basis_msg"], key=f"r_{target_name}_{sub}_{form_id}")
                                            res_dict[sub] = {"score": s, "basis": r}

                        if pre == "self":
                            st.divider(); st.subheader(L["report_title"])
                            rep_data = {}
                            for k, v in REPORT_UI[lang].items():
                                saved_rep = existing[(existing['구분']=="리포트") & (existing['항목']==v)] if not existing.empty else pd.DataFrame()
                                rep_data[k] = st.text_area(v, value=str(saved_rep.iloc[0]['근거']) if not saved_rep.empty else "", key=f"rep_{k}_{target_name}_{form_id}")

                        bc1, bc2 = st.columns(2)
                        if bc1.form_submit_button(L["save"]):
                            now = (datetime.datetime.now()+timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                            recs = [{"시간":now,"평가자":user,"피평가자":target_name,"구분":f"{eval_type}(Draft)","항목":k,"점수":v["score"],"근거":v["basis"]} for k,v in res_dict.items()]
                            if pre == "self":
                                for kq, vq in rep_data.items(): recs.append({"시간":now,"평가자":user,"피평가자":user,"구분":"리포트","항목":REPORT_UI[lang][kq],"점수":"-","근거":vq})
                            if save_with_cleanup(recs, user, target_name, False, ws_name): st.success(L["done_msg"]); st.cache_data.clear(); st.rerun()
                        
                        if bc2.form_submit_button(L["sub"]):
                            if any(len(str(v["basis"]).strip()) < 2 for v in res_dict.values()): st.error(L["err"])
                            else:
                                now = (datetime.datetime.now()+timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                                recs = [{"시간":now,"평가자":user,"피평가자":target_name,"구분":f"{eval_type}(Final)","항목":k,"점수":v["score"],"근거":v["basis"]} for k,v in res_dict.items()]
                                if pre == "self":
                                    for kq, vq in rep_data.items(): recs.append({"시간":now,"평가자":user,"피평가자":user,"구분":"리포트","항목":REPORT_UI[lang][kq],"점수":"-","근거":vq})
                                if save_with_cleanup(recs, user, target_name, True, ws_name): st.success(L["done_msg"]); st.cache_data.clear(); st.rerun()
            except Exception as e: st.error(f"⚠️ Error: {str(e)}")

        # --- [대시보드: 합산 로직 완벽 반영] ---
        if menu == L["m8"]:
            st.title(L["m8"])
            st.info(L["dash_desc"])
            my_evals = res_df[(res_df['평가자']==user) & (res_df['구분'].str.contains("2차"))]
            if my_evals.empty: st.warning("아직 최종 완료된 평가 내역이 없습니다.")
            else:
                my_evals['세부항목'] = my_evals['항목'].map(NORMAL_MAPPING)
                my_evals['점수'] = pd.to_numeric(my_evals['점수'], errors='coerce').fillna(0)
                pivot = my_evals.pivot_table(index='피평가자', columns='세부항목', values='점수', aggfunc='sum').fillna(0)
                pivot['총점 (125점)'] = pivot.sum(axis=1)
                cols = ["업무의 양", "업무의 질", "협조성", "근무의욕", "복무상황", "지식", "이해판단력", "창의연구력", "표현절충", "총점 (125점)"]
                st.dataframe(pivot[[c for c in cols if c in pivot.columns]], use_container_width=True)
                st.divider(); st.warning(L["contact_admin"])

        elif menu == L["m9"]:
            st.title(L["m9"])
            st.info(L["dash_desc"])
            my_evals_ld = ld_df[(ld_df['평가자']==user) & (ld_df['구분'].str.contains("2차"))]
            if my_evals_ld.empty: st.warning("아직 최종 완료된 리더십 평가 내역이 없습니다.")
            else:
                my_evals_ld['점수'] = pd.to_numeric(my_evals_ld['점수'], errors='coerce').fillna(0)
                pivot_ld = my_evals_ld.pivot_table(index='피평가자', columns='항목', values='점수', aggfunc='first').fillna(0)
                pivot_ld['리더십 총점'] = pivot_ld.sum(axis=1)
                st.dataframe(pivot_ld, use_container_width=True)
                st.divider(); st.warning(L["contact_admin"])

        elif menu == L["m1"]: render_form(EVAL_DATA[lang], "self", target_name=user)
        elif menu == L["m5"]: render_form(LEADER_DATA[lang], "ld_self", ws_name="Leadership_Results", target_name=user)
        elif menu == L["m2"]:
            target = st.selectbox(L["target"], t2_list, key="sel_m2")
            if target:
                ts = res_df[(res_df['피평가자']==target)&(res_df['구분'].str.contains("자기", na=False))]
                if ts.empty: st.warning(f"⚠️ {target} 미제출")
                else:
                    si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ts.iterrows()}
                    render_form(EVAL_DATA[lang], "ev2", si, eval_type="2차", target_name=target)
        elif menu == L["m6"]:
            target_l = st.selectbox(L["target"], ldr_t2_list, key="sel_m6")
            if target_l:
                ls = ld_df[(ld_df['피평가자']==target_l)&(ld_df['구분'].str.contains("자기", na=False))]
                if ls.empty: st.warning(f"⚠️ {target_l} 미제출")
                else:
                    si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ls.iterrows()}
                    render_form(LEADER_DATA[lang], "ld2", si, eval_type="2차", ws_name="Leadership_Results", target_name=target_l)
        elif menu == L["m3"]:
            target = st.selectbox(L["target"], t3_list, key="sel_m3")
            if target:
                ts = res_df[(res_df['피평가자']==target)&(res_df['구분'].str.contains("자기", na=False))]
                if ts.empty: st.warning("⚠️ 미제출")
                else:
                    si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ts.iterrows()}
                    render_form(EVAL_DATA[lang], "ev3", si, eval_type="3차", is_3rd=True, target_name=target)
        elif menu == L["m7"]:
            target_l3 = st.selectbox(L["target"], ldr_t3_list, key="sel_m7")
            if target_l3:
                ls3 = ld_df[(ld_df['피평가자']==target_l3)&(ld_df['구분'].str.contains("자기", na=False))]
                if ls3.empty: st.warning("⚠️ 미제출")
                else:
                    si3 = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ls3.iterrows()}
                    render_form(LEADER_DATA[lang], "ld3", si3, eval_type="3차", ws_name="Leadership_Results", is_3rd=True, target_name=target_l3)
        elif menu == L["m4"]:
            st.title(L["m4"])
            status_df = []
            for _, r in db_raw.iterrows():
                nm = r['성명']
                s_stat = "✅" if not res_df.empty and nm in res_df[res_df['구분'].str.contains("자기", na=False)]['피평가자'].values else "⏳"
                l_stat = "✅" if not ld_df.empty and nm in ld_df[ld_df['구분'].str.contains("자기", na=False)]['피평가자'].values else ("-" if r['리더여부']=='N' else "⏳")
                status_df.append({"Name": nm, "Self-Eval": s_stat, "Leadership": l_stat})
            st.table(pd.DataFrame(status_df))
            st.divider()
            sel_u = st.selectbox("Employee", db_raw['성명'].tolist(), key="ad_sel")
            new_p = st.text_input("New PW", type="password", key="ad_pw")
            if st.button("Update"):
                db_f = conn.read(worksheet="Users", ttl=0)
                db_f.loc[db_f['성명'] == sel_u, '비밀번호'] = str(new_p)
                conn.update(worksheet="Users", data=db_f); st.success("Updated!"); st.cache_data.clear()
