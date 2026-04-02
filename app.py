import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta

# --- [1] 기본 설정 ---
st.set_page_config(page_title="SRS Global HR System", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        df = conn.read(worksheet="Users", ttl=0)
        if df is not None:
            return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x).fillna("")
        return None
    except: return None

# --- [2] 평가 데이터 (설계안 상세 문구 100% 반영) ---
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
                "Horizontal": "Did you cooperate with colleagues for team efficiency?",
                "Respect": "Did you respect team opinions over your personal views?",
                "Supervisor": "Did you cooperate effectively with results?"
            },
            "Motivation": {
                "Proactivity": "What was your level of proactive engagement?",
                "Responsibility": "Work sincerely without avoiding responsibility?",
                "Research": "What was your level of desire for deep research?"
            },
            "Compliance": {
                "Discipline": "Did you follow rules and maintain order?",
                "Data Mgmt": "Systematic management of periodic reports and data",
                "Attendance": "How was your attendance status?"
            }
        },
        "3. Job Competency": {
            "Knowledge": {
                "Job Knowledge": "Broad and deep knowledge of assigned duties?",
                "Related Knowledge": "Basic knowledge of related work sufficient?"
            },
            "Judgment": {
                "Speed": "How fast do you correctly understand regulations?",
                "Validity": "Are your judgments accurate and valid?",
                "Problem Solving": "Do you identify root causes and lead solutions?",
                "Insight": "Do you grasp key points independently?"
            },
            "Creativity": {
                "Improvement": "Do you always seek improvements through creative ideas?"
            },
            "Communication": {
                "Verbal": "Clear and accurate verbal reporting?",
                "Written": "Clear and accurate written reports?",
                "Negotiation": "Coordination and negotiation ability?"
            }
        }
    }
}

LEADER_DATA = {
    "KO": {
        "1. 리더십(기본역량)": {"리더십": {"고객지향": "내부 혹은 외부 고객의 요구를 능동적으로 찾아내고 적시에 대응한다", "책임감": "특별한 지시를 하지 않더라도 업무목표를 달성하기 위해 계획적으로 행동한다.", "팀워크지향": "구성원의 공감을 얻기 위해 자주 의견을 공유하고 의사결정의 배경이나 당위성에 대해 설명한다."}},
        "2. 업무실적(실행역량)": {"업무실적": {"개방적 의사소통": "상대방이 친밀감을 느낄 수 있도록 자신의 사적인 부분을 먼저 이야기한다.", "문제해결": "문제 발생 시 정보와 자료를 분석하여 문제의 근본원인을 규명한다.", "조직이해": "조직의 전략, 운영방식, 역사 등을 파악한다.", "프로젝트 관리": "프로젝트와 관련된 정보를 체계적으로 수집, 분석하여 계획을 수립한다."}},
        "3. 지식(전문역량)": {"지식": {"분석적사고": "문제를 해결하기 위해 필요한 정보나 자료가 무엇인지 정확히 파악한다.", "세밀한업무처리": "문제 발생 소지를 최소화하기 위해 관련 규정이나 과거 관행 등을 조사한다."}}
    },
    "EN": {
        "1. Leadership(Core)": {"Leadership": {"Customer Focus": "Proactively identify and respond to needs.", "Responsibility": "Act planfully to achieve goals.", "Teamwork": "Share opinions and explain backgrounds."}},
        "2. Performance(Execution)": {"Performance": {"Open Comm": "Share personal aspects first to build rapport.", "Problem Solving": "Identify root causes when problems occur.", "Org Insight": "Understand strategy and operational methods.", "Project Mgmt": "Systematically collect info and establish plans."}},
        "3. Knowledge(Professional)": {"Knowledge": {"Analytical": "Identify needed info or data for problems.", "Detailed": "Investigate rules or practices to minimize issues."}}
    }
}

REPORT_UI = {
    "KO": {
        "q1": "1. 평가 기간동안 내가 낸 성과는 무엇입니까?",
        "q2": "2. 평가 기간동안 내가 습득한 지식이 무엇입니까?",
        "q3": "3. 평가 기간동안 내가 인재 양성을 위하여 무엇을 하였습니까?"
    },
    "EN": {
        "q1": "1. What are your achievements during the evaluation period?",
        "q2": "2. What knowledge did you acquire during the evaluation period?",
        "q3": "3. What did you do for talent development during the evaluation period?"
    }
}

UI = {
    "KO": {
        "m1": "📝 자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드",
        "m5": "🚀 리더십 자기평가", "m6": "🎖️ 2차 리더십평가", "m7": "🎖️ 3차 리더십평가",
        "sub": "✅ 최종 제출", "save": "💾 임시 저장", "already": "✅ 제출 완료되었습니다.",
        "err": "⚠️ 모든 항목의 근거를 상세히 작성해 주세요.", "report_title": "🚀 자기 성장 REPORT",
        "score": "점수", "basis": "근거 (상세히 작성)", "target": "대상 선택", "self_info": "본인 입력", "done_msg": "저장되었습니다!"
    },
    "EN": {
        "m1": "📝 Self-Eval", "m2": "👥 2nd Eval", "m3": "⚖️ 3rd Final", "m4": "📊 Admin",
        "m5": "🚀 Lead Self-Eval", "m6": "🎖️ 2nd Lead Eval", "m7": "🎖️ 3rd Lead Eval",
        "sub": "✅ Final Submit", "save": "💾 Save Draft", "already": "✅ Completed.",
        "err": "⚠️ Please provide detailed reasons.", "report_title": "🚀 Growth REPORT",
        "score": "Score", "basis": "Basis", "target": "Select Target", "self_info": "Self-Input", "done_msg": "Saved!"
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
    except: return False

# --- [4] 메인 로직 ---
db_raw = get_db()
if 'auth' not in st.session_state: 
    st.session_state.update({'auth':False, 'user':'', 'ldr':'N', 'lang':'KO'})

if db_raw is not None:
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System HR")
        n, p = st.text_input("Name"), st.text_input("PW", type="password")
        if st.button("Login"):
            u = db_raw[db_raw['성명'] == n.strip()]
            if not u.empty and str(p) == str(u.iloc[0]['비밀번호']):
                u_lang = str(u.iloc[0].get('언어', 'KO')).upper()
                st.session_state.update({'auth':True, 'user':n.strip(), 'ldr':str(u.iloc[0]['리더여부']).upper(), 'lang':u_lang if u_lang in ["KO", "EN"] else "KO"})
                st.rerun()
            else: st.error("Login Failed")
    else:
        lang = st.session_state.lang if st.session_state.lang in UI else "KO"
        L, user = UI[lang], st.session_state.user
        res_df = conn.read(worksheet="Results", ttl=0).fillna("")
        ld_df = conn.read(worksheet="Leadership_Results", ttl=0).fillna("")

        m_list = []
        if user != "김용환":
            m_list.append(L["m1"])
            if st.session_state.ldr == 'Y': m_list.append(L["m5"])
        t2, t3 = db_raw[db_raw['2차평가자'] == user]['성명'].tolist(), db_raw[db_raw['3차평가자'] == user]['성명'].tolist()
        if t2: m_list.append(L["m2"])
        my_ldr_targets = db_raw[(db_raw['2차평가자'] == user) & (db_raw['리더여부'] == 'Y')]['성명'].tolist()
        if my_ldr_targets: m_list.append(L["m6"])
        if t3: m_list.append(L["m3"])
        my_ldr_3rd_targets = db_raw[(db_raw['3차평가자'] == user) & (db_raw['리더여부'] == 'Y')]['성명'].tolist()
        if my_ldr_3rd_targets: m_list.append(L["m7"])
        if user == "권정순": m_list.append(L["m4"])
        menu = st.sidebar.radio("Menu", m_list)

        def render_form(data_dict, pre, self_info=None, eval_type="자기", ws_name="Results", is_3rd=False, target_name=None):
            if not target_name: return
            try:
                check_df = res_df if ws_name == "Results" else ld_df
                existing = check_df[(check_df['평가자']==user) & (check_df['피평가자']==target_name)]
                is_final_done = not existing[existing['구분'].str.contains("Final|최종|자기", na=False)].empty
                draft_vals = existing[existing['구분'].str.contains("Draft", na=False)]

                if is_final_done:
                    st.success(L["already"])
                else:
                    if not draft_vals.empty: st.warning("⚠️ Loaded draft content.")
                    with st.form(key=f"form_v3_{pre}_{target_name}"):
                        tabs = st.tabs(list(data_dict.keys()))
                        res_dict = {}
                        for i, (major, subs) in enumerate(data_dict.items()):
                            with tabs[i]:
                                if is_3rd:
                                    st.subheader(f"🔍 {major} Review")
                                    for sub_n, sub_items in subs.items():
                                        for it_n, crit in sub_items.items():
                                            info = self_info.get(it_n, {"score": "-", "basis": ""})
                                            st.markdown(f"**{it_n}**: {info['score']} | {info['basis']}")
                                    st.divider()
                                    c1, c2 = st.columns([1, 3])
                                    s = c1.selectbox(L["score"], [1,2,3,4,5], index=2, key=f"s3_{target_name}_{major}")
                                    r = c2.text_area(L["basis"], key=f"r3_{target_name}_{major}")
                                    res_dict[major] = {"score": s, "basis": r}
                                else:
                                    for sub, items in subs.items():
                                        st.markdown(f"#### 📍 {sub}")
                                        for it, crit in items.items():
                                            saved = draft_vals[draft_vals['항목']==it]
                                            score_raw = saved.iloc[0]['점수'] if not saved.empty else 3
                                            basis_raw = saved.iloc[0]['근거'] if not saved.empty else ""
                                            try: init_score = int(float(score_raw)) if str(score_raw).replace('.','',1).isdigit() else 3
                                            except: init_score = 3
                                            init_basis = str(basis_raw) if str(basis_raw).lower() != "nan" else ""

                                            c1, c2, c3, c4 = st.columns([2, 3, 1, 3])
                                            lbl = f"**{it}**"
                                            if self_info and it in self_info:
                                                lbl += f"<br><span style='color:blue; font-size:0.85em;'>[{L['self_info']}] {self_info[it]['score']}</span>"
                                                if self_info[it]['basis']: lbl += f"<br><small>ㄴ{self_info[it]['basis']}</small>"
                                            
                                            c1.markdown(lbl, unsafe_allow_html=True); c2.info(crit)
                                            s = c3.selectbox(L["score"], [1,2,3,4,5], index=max(0, min(4, init_score-1)), key=f"s_{pre}_{target_name}_{it}")
                                            r = c4.text_input(L["basis"], value=init_basis, key=f"r_{pre}_{target_name}_{it}")
                                            res_dict[it] = {"score": s, "basis": r}
                        
                        rep_data = {}
                        if pre == "self":
                            st.divider(); st.subheader(L["report_title"])
                            for k, v in REPORT_UI[lang].items():
                                saved_rep = existing[(existing['구분']=="리포트") & (existing['항목']==v)]
                                rep_data[k] = st.text_area(v, value=str(saved_rep.iloc[0]['근거']) if not saved_rep.empty else "", key=f"rep_{k}_{target_name}")

                        # [임시저장 & 최종제출 버튼 복구]
                        bc1, bc2 = st.columns(2)
                        btn_save = bc1.form_submit_button(L["save"])
                        btn_sub = bc2.form_submit_button(L["sub"])

                        if btn_save or btn_sub:
                            is_f = btn_sub
                            if is_f and any(len(str(v["basis"]).strip()) < 2 for v in res_dict.values()):
                                st.error(L["err"])
                            else:
                                now = (datetime.datetime.now()+timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                                stt = "Final" if is_f else "Draft"
                                recs = [{"시간":now,"평가자":user,"피평가자":target_name,"구분":f"{eval_type}({stt})","항목":k if not is_3rd else f"[{k}] 종합","점수":v["score"],"근거":v["basis"]} for k,v in res_dict.items()]
                                if pre == "self":
                                    for kq, vq in rep_data.items(): recs.append({"시간":now,"평가자":user,"피평가자":user,"구분":"리포트","항목":REPORT_UI[lang][kq],"점수":"-","근거":vq})
                                if save_with_cleanup(recs, user, target_name, is_f, ws_name):
                                    st.success(L["done_msg"]); st.cache_data.clear(); st.rerun()
            except Exception as e: st.error("⚠️ Loading Error")

        # --- [실행] ---
        if menu == L["m1"]: render_form(EVAL_DATA[lang], "self", target_name=user)
        elif menu == L["m5"]: render_form(LEADER_DATA[lang], "ld", ws_name="Leadership_Results", target_name=user)
        elif menu == L["m2"]:
            target = st.selectbox(L["target"], t2, key="sel_m2_f")
            if target:
                ts = res_df[(res_df['피평가자']==target)&(res_df['구분'].str.contains("자기", na=False))]
                if ts.empty: st.warning(f"⚠️ {target} has not submitted yet.")
                else:
                    si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ts.iterrows()}
                    rd = res_df[(res_df['피평가자']==target)&(res_df['구분']=="리포트")]
                    if not rd.empty:
                        with st.expander("📌 View Report"):
                            for _, r in rd.iterrows(): st.markdown(f"**{r['항목']}**"); st.info(r['근거'])
                    render_form(EVAL_DATA[lang], "ev2", si, eval_type="2차", target_name=target)
        elif menu == L["m6"]:
            target = st.selectbox(L["target"], my_ldr_targets, key="sel_m6_f")
            if target:
                ls = ld_df[(ld_df['피평가자']==target)&(ld_df['구분'].str.contains("자기", na=False))]
                if ls.empty: st.warning(f"⚠️ {target} has not submitted yet.")
                else:
                    si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ls.iterrows()}
                    render_form(LEADER_DATA[lang], "ld2", si, eval_type="2차", ws_name="Leadership_Results", target_name=target)
        elif menu == L["m3"]:
            target = st.selectbox(L["target"], t3, key="sel_m3_f")
            if target:
                ts = res_df[(res_df['피평가자']==target)&(res_df['구분'].str.contains("자기", na=False))]
                if ts.empty: st.warning("⚠️ Waiting for self-evaluation...")
                else:
                    si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ts.iterrows()}
                    render_form(EVAL_DATA[lang], "ev3", si, eval_type="3차", is_3rd=True, target_name=target)
        elif menu == L["m7"]:
            target = st.selectbox(L["target"], my_ldr_3rd_targets, key="sel_m7_f")
            if target:
                ls3 = ld_df[(ld_df['피평가자']==target)&(ld_df['구분'].str.contains("자기", na=False))]
                if ls3.empty: st.warning("⚠️ Waiting for leadership self-eval...")
                else:
                    si3 = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ls3.iterrows()}
                    render_form(LEADER_DATA[lang], "ld3", si3, eval_type="3차", ws_name="Leadership_Results", is_3rd=True, target_name=target)
        elif menu == L["m4"]:
            st.title(L["m4"])
            status_df = []
            for _, r in db_raw.iterrows():
                nm = r['성명']
                s_stat = "✅" if nm in res_df[res_df['구분'].str.contains("자기", na=False)]['피평가자'].values else "⏳"
                l_stat = "✅" if nm in ld_df[ld_df['구분'].str.contains("자기", na=False)]['피평가자'].values else ("-" if r['리더여부']=='N' else "⏳")
                status_df.append({"Name": nm, "Self-Eval": s_stat, "Leadership": l_stat})
            st.table(pd.DataFrame(status_df))
            st.divider()
            sel_u = st.selectbox("Employee", db_raw['성명'].tolist(), key="admin_sel")
            new_pw = st.text_input("New PW", type="password", key="admin_pw")
            if st.button("Change Password"):
                db_raw.loc[db_raw['성명'] == sel_u, '비밀번호'] = new_pw
                conn.update(worksheet="Users", data=db_raw); st.success("Updated!")
