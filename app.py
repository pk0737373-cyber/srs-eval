import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta

# --- [1] 기본 설정 및 시트 연결 ---
st.set_page_config(page_title="SRS Global HR System", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db(sheet_name="Users"):
    try: return conn.read(worksheet=sheet_name, ttl=0)
    except: return None

# --- [2] 일반 평가 데이터 (25개 항목 - 한/영 풀번역) ---
EVAL_DATA = {
    "KO": {
        "1. 업무실적": {
            "업무의 양": {"속도": "업무를 신속하게 처리하며 지체되는 일은 없었는가?", "지속성": "어떤 일이나 차이 없이 끈기있게 했는가?", "능률": "신속 정확하게 낭비 없이 처리 했는가?"},
            "업무의 질": {"정확성": "일의 결과를 믿을 수 있는가?", "성과": "일의 성과가 내용에 있어서 뛰어났는가?", "꼼꼼함": "철저하고 뒷처리를 잘하는가?"}
        },
        "2. 근무태도": {
            "협조성": {"횡적협조": "스스로 동료와 협력하며 조직체의 능률향상에 공헌하는가?", "존중": "자신의 생각보다는 팀 전체의 의견을 존중하는가?", "상사협조": "상사에 대해 협력하며 성과가 있는가?"},
            "근무의욕": {"적극성": "일에 능동적으로 대처하려는 의욕은 어떤가?", "책임감": "책임을 회피하지 않으며 성실하게 일하려는 의욕은 어떤가?", "연구심": "넓고 깊게 일을 연구하려는 의욕은 어떤가?"},
            "복무상황": {"규율": "규칙을 준수하며 직장질서유지에 애쓰는가?", "DB화": "정기적인 업무보고와 본인업무에 대한 데이터의 체계적인 관리", "근태상황": "지각, 조퇴, 결근 등 상황은 어떤가?"}
        },
        "3. 직무능력": {
            "지식": {"직무지식": "담당업무의 지식이 넓고 깊은가?", "관련지식": "관련업무에 대한 기초지식은 넓고 깊은가?"},
            "이해판단력": {"신속성": "지시 이해 속도?", "타당성": "내린 결론은 정확하며 타당한가?", "문제해결": "본질 파악 및 해결 주도?", "통찰력": "요점 파악 및 자적 결론?"},
            "창의연구력": { "연구개선": "아이디어를 살리고 일의 순서개선이나 전진을 도모하는가?" },
            "표현절충": {"구두표현": "말하기 능력?", "문장표현": "글쓰기 능력?", "절충": "교섭 능력?"}
        }
    },
    "EN": {
        "1. Performance": {
            "Quantity of Work": {"Speed": "Did you process work quickly?", "Persistence": "Did you work persistently?", "Efficiency": "Did you work efficiently?"},
            "Quality of Work": {"Accuracy": "Reliable result?", "Achievement": "Outstanding performance?", "Thoroughness": "Thorough follow-up?"}
        },
        "2. Work Attitude": {
            "Cooperation": {"Horizontal": "Cooperate with colleagues?", "Respect": "Respect team opinions?", "Supervisor": "Cooperate with supervisors?"},
            "Motivation": {"Proactivity": "Proactive attitude?", "Responsibility": "Sincere responsibility?", "Research": "Deep research mindset?"},
            "Compliance": {"Discipline": "Follow rules?", "Data": "Systematic data management?", "Attendance": "Tardiness/Absence status?"}
        },
        "3. Job Competency": {
            "Knowledge": {"Job": "Broad job knowledge?", "Related": "Broad related knowledge?"},
            "Judgment": {"Speed": "Quick understanding?", "Validity": "Accurate conclusions?", "Solving": "Effective solution?", "Insight": "Independent judgment?"},
            "Creativity": {"Improve": "Improvement ideas?"},
            "Communication": {"Verbal": "Clear verbal?", "Written": "Clear writing?", "Negotiation": "Smooth negotiation?"}
        }
    }
}

# --- [3] 리더십 데이터 (9개 항목 - 한/영 풀번역) ---
LEADER_DATA = {
    "KO": {
        "리더십 역량": {
            "고객지향": "내부 혹은 외부 고객의 요구를 능동적으로 찾아내고 적시에 대응한다",
            "책임감": "특별한 지시를 하지 않더라도 업무목표를 달성하기 위해 계획적으로 행동한다",
            "팀워크지향": "구성원의 공감을 얻기 위해 자주 의견을 공유하고 배경이나 당위성에 대해 설명한다"
        },
        "업무실적 역량": {
            "개방적 의사소통": "상대방이 친밀감을 느낄 수 있도록 자신의 사적인 부분을 먼저 이야기한다",
            "문제해결": "문제 발생 시 정보와 자료를 분석하여 문제의 근본원인을 규명한다",
            "조직이해": "조직의 전략, 운영방식, 역사 등을 파악한다",
            "프로젝트 관리": "프로젝트 관련 정보를 체계적으로 수집하여 계획을 수립한다"
        },
        "지식 역량": {
            "분석적 사고": "문제를 해결하기 위해 필요한 정보나 자료가 무엇인지 정확히 파악한다",
            "세밀한 업무처리": "문제 발생 소지를 최소화하기 위해 관련 규정이나 과거 관행 등을 조사한다"
        }
    },
    "EN": {
        "Leadership Core": {
            "Customer Focus": "Respond to customer needs proactively.",
            "Responsibility": "Act independently to achieve goals.",
            "Teamwork": "Explain backgrounds for consensus."
        },
        "Performance Excel": {
            "Communication": "Share personal aspects to build rapport.",
            "Problem Solving": "Identify root causes by analysis.",
            "Org Insight": "Understand strategy and history.",
            "Project Mgmt": "Establish systematic plans."
        },
        "Skill & Knowledge": {
            "Analytical": "Identify necessary data accurately.",
            "Detailed": "Investigate regulations and practices."
        }
    }
}

UI = {
    "KO": {"m1": "📝 자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드", "m5": "🚀 리더십 자기평가", "m6": "🎖️ 2차 리더십평가", "sub": "✅ 최종 제출", "already": "✅ 이미 제출을 완료하셨습니다.", "err": "⚠️ 모든 항목의 점수와 근거를 작성해야 제출할 수 있습니다.", "report": "🚀 자기 성장 REPORT", "score": "점수", "basis": "근거", "target": "평가 대상 선택", "pw_reset": "🔑 비밀번호 재설정", "self_info": "본인 입력 정보"},
    "EN": {"m1": "📝 Self-Eval", "m2": "👥 2nd Eval", "m3": "⚖️ 3rd Final", "m4": "📊 Admin", "m5": "🚀 Leadership Self-Eval", "m6": "🎖️ 2nd Leadership Eval", "sub": "✅ Submit", "already": "✅ Already Submitted.", "err": "⚠️ All fields required.", "report": "🚀 Growth REPORT", "score": "Score", "basis": "Basis", "target": "Select Target", "pw_reset": "🔑 Reset Password", "self_info": "Self-Input Info"}
}

def save_data(records, worksheet_name="Results"):
    try:
        existing = conn.read(worksheet=worksheet_name, ttl=0)
        new_df = pd.DataFrame(records)
        final = pd.concat([existing, new_df], ignore_index=True) if existing is not None and not existing.empty else new_df
        conn.update(worksheet=worksheet_name, data=final)
        st.cache_data.clear()
        return True
    except: return False

# --- [4] 메인 로직 ---
user_db = get_db("Users")
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'is_leader': 'N', 'lang': 'KO'})

if user_db is not None:
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System HR")
        name = st.text_input("Name (성명)")
        pw = st.text_input("Password (비밀번호)", type="password")
        if st.button("Login"):
            u = user_db[user_db['성명'] == name]
            if not u.empty and str(pw) == str(u.iloc[0]['비밀번호']):
                is_ldr = str(u.iloc[0]['리더여부']).upper() if '리더여부' in u.columns else 'N'
                lang = u.iloc[0]['언어'] if '언어' in u.columns else 'KO'
                st.session_state.update({'auth':True,'user':name,'is_leader':is_ldr,'lang':lang})
                st.rerun()
            else: st.error("Login Failed")
    else:
        L, user_name, lang = UI[st.session_state.lang], st.session_state.user, st.session_state.lang
        res_df = conn.read(worksheet="Results", ttl=0)
        ld_df = conn.read(worksheet="Leadership_Results", ttl=0)

        m_list = [L["m1"]]
        if st.session_state.is_leader == 'Y': m_list.append(L["m5"])
        targets_2nd = user_db[user_db['2차평가자'] == user_name]['성명'].tolist()
        targets_3rd = user_db[user_db['3차평가자'] == user_name]['성명'].tolist()
        if targets_2nd: 
            m_list.append(L["m2"])
            m_list.append(L["m6"])
        if targets_3rd: m_list.append(L["m3"])
        if user_name == "권정순": m_list.append(L["m4"])
        menu = st.sidebar.radio("Menu", m_list)

        def render_form(data_dict, pre, self_data_dict=None):
            res_dict = {}
            for major, sub_items in data_dict.items():
                with st.expander(f"📂 {major}", expanded=True):
                    for sub, items in sub_items.items():
                        st.markdown(f"**📍 {sub}**")
                        for it, crit in items.items():
                            c1, c2, c3, c4 = st.columns([2, 2.5, 1, 3.5])
                            
                            # 항목 및 본인 입력 데이터 노출
                            label_html = f"**{it}**"
                            if self_data_dict and it in self_data_dict:
                                s_score = self_data_dict[it]['score']
                                s_basis = self_data_dict[it]['basis']
                                label_html += f"<br><span style='color:blue; font-size: 0.85em;'>[{L['self_info']}]</span>"
                                label_html += f"<br><span style='color:blue; font-size: 0.85em;'>점수: {s_score}</span>"
                                if s_basis:
                                    label_html += f"<br><span style='color:gray; font-size: 0.75em;'>ㄴ근거: {s_basis}</span>"
                            c1.markdown(label_html, unsafe_allow_html=True)
                            
                            c2.caption(crit)
                            score = c3.selectbox(L["score"], [1,2,3,4,5], key=f"{pre}_{it}_s")
                            basis = c4.text_input(L["basis"], key=f"{pre}_{it}_r", placeholder="평가 의견 입력")
                            res_dict[it] = {"score": score, "basis": basis, "category": sub}
            return res_dict

        # 1. 자기고과
        if menu == L["m1"]:
            st.header(L["m1"])
            if res_df is not None and not res_df[(res_df['피평가자'] == user_name) & (res_df['구분'] == "자기")].empty:
                st.success(L["already"])
            else:
                eval_res = render_form(EVAL_DATA[lang], "self")
                st.subheader(L["report"])
                r1 = st.text_area("Achievement Summary (성과 요약)")
                if st.button(L["sub"]):
                    if any(not v["basis"].strip() for v in eval_res.values()) or not r1.strip(): st.error(L["err"])
                    else:
                        now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                        recs = [{"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                        recs.append({"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "리포트", "항목": "종합", "점수": "-", "근거": r1})
                        if save_data(recs): st.success("Success!"); st.rerun()

        # 5. 리더십 자기평가
        elif menu == L["m5"]:
            st.header(L["m5"])
            if ld_df is not None and not ld_df[(ld_df['피평가자'] == user_name) & (ld_df['구분'] == "자기")].empty:
                st.success(L["already"])
            else:
                eval_res = render_form(LEADER_DATA[lang], "ld_self")
                if st.button(L["sub"]):
                    if any(not v["basis"].strip() for v in eval_res.values()): st.error(L["err"])
                    else:
                        now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                        recs = [{"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                        if save_data(recs, "Leadership_Results"): st.success("Success!"); st.rerun()

        # 6. 2차 리더십 평가 (이사님 전용 - 본인 근거 노출 추가)
        elif menu == L["m6"]:
            st.header(L["m6"])
            ldr_targets = user_db[(user_db['2차평가자'] == user_name) & (user_db['리더여부'] == 'Y')]['성명'].tolist()
            if not ldr_targets: st.warning("No targets available.")
            else:
                target = st.selectbox(L["target"], ldr_targets)
                target_ld_self = ld_df[(ld_df['피평가자'] == target) & (ld_df['구분'] == "자기")]
                
                # 리더십 자기 점수 및 근거 매핑 로직 강화
                self_ld_info = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in target_ld_self.iterrows()} if not target_ld_self.empty else None
                
                eval_res = render_form(LEADER_DATA[lang], f"ld_2nd_{target}", self_ld_info)
                if st.button(f"Submit Evaluation for {target}"):
                    if any(not v["basis"].strip() for v in eval_res.values()): st.error(L["err"])
                    else:
                        now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                        recs = [{"시간": now, "평가자": user_name, "피평가자": target, "구분": "2차", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                        if save_data(recs, "Leadership_Results"): st.success("Done!"); st.balloons()

        # 팀원평가 (2차/3차)
        elif menu in [L["m2"], L["m3"]]:
            st.header(menu)
            mode = "2차" if menu == L["m2"] else "3차"
            targets = targets_2nd if mode == "2차" else targets_3rd
            selected = st.selectbox(L["target"], targets)
            target_self_rows = res_df[(res_df['피평가자'] == selected) & (res_df['구분'] == "자기")]
            if target_self_rows.empty: st.warning("Target employee has not submitted yet.")
            else:
                self_info_dict = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in target_self_rows.iterrows()}
                rep = res_df[(res_df['피평가자'] == selected) & (res_df['구분'] == "리포트")]
                if not rep.empty:
                    with st.expander(f"📌 {selected}'s Self-Report", expanded=True): st.info(rep.iloc[0]['근거'])
                eval_res = render_form(EVAL_DATA[lang], f"eval_{mode}_{selected}", self_info_dict)
                if st.button(f"Submit {mode} Eval"):
                    if any(not v["basis"].strip() for v in eval_res.values()): st.error(L["err"])
                    else:
                        now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                        recs = [{"시간": now, "평가자": user_name, "피평가자": selected, "구분": mode, "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                        if save_data(recs): st.success("Done!"); st.balloons()

        # 대시보드
        elif menu == L["m4"]:
            st.title("Admin")
            st.dataframe(user_db)
            st.divider(); st.subheader(L["pw_reset"])
            target_user = st.selectbox("Employee", user_db['성명'].tolist())
            new_pw = st.text_input("New PW", type="password")
            if st.button("Save PW"):
                idx = user_db[user_db['성명'] == target_user].index[0]
                user_db.at[idx, '비밀번호'] = new_pw
                if conn.update(worksheet="Users", data=user_db): st.success("Saved!"); st.rerun()
