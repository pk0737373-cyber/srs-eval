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

# --- [2] 일반 평가 데이터 (한/영 풀번역) ---
EVAL_DATA = {
    "KO": {
        "1. 업무실적": {
            "업무의 양": {"속도": "업무를 신속하게 처리하며 지체되는 일은 없었는가?", "지속성": "어떤 일이나 차이 없이 끈기있게 했는가?", "능률": "신속 정확하게 낭비 없이 처리 했는가?"},
            "업무의 질": {"정확성": "일의 결과를 믿을 수 있는가?", "성과": "일의 성과가 내용에 있어서 뛰어났는가?", "꼼꼼함": "철저하고 뒷처리를 잘하는가?"}
        },
        "2. 근무태도": {
            "협조성": {"횡적협조": "동료와 협력하며 조직체의 능률향상에 공헌하는가?", "존중": "팀 전체의 의견을 존중하는가?", "상사협조": "상사에 대해 협력하며 성과가 있는가?"},
            "근무의욕": {"적극성": "일에 능동적으로 대처하려는 의욕은 어떤가?", "책임감": "책임을 회피하지 않으며 성실하게 일하려는 의욕은 어떤가?", "연구심": "깊게 연구하려는 의욕은 어떤가?"},
            "복무상황": {"규율": "규칙 준수 및 질서 유지?", "DB화": "업무 데이터의 체계적인 관리", "근태상황": "지각, 조퇴, 결근 상황 등"}
        },
        "3. 직무능력": {
            "지식": {"직무지식": "담당업무 지식이 깊은가?", "관련지식": "관련 기초지식이 넓은가?"},
            "이해판단력": {"신속성": "지시 이해 속도?", "타당성": "결론의 타당성?", "문제해결": "해결 주도력?", "통찰력": "요점 파악 능력?"},
            "창의연구력": { "연구개선": "아이디어를 살리고 일의 개선을 도모하는가?" },
            "표현절충": {"구두표현": "말하기 능력?", "문장표현": "글쓰기 능력?", "절충": "교섭 능력?"}
        }
    },
    "EN": {
        "1. Performance": {
            "Quantity of Work": {"Speed": "Did you process work quickly?", "Persistence": "Worked consistently?", "Efficiency": "Processed without waste?"},
            "Quality of Work": {"Accuracy": "Reliable results?", "Achievement": "Outstanding performance?", "Thoroughness": "Thorough follow-ups?"}
        },
        "2. Work Attitude": {
            "Cooperation": {"Horizontal": "Cooperated with colleagues?", "Respect": "Respected team opinions?", "Supervisor": "Cooperated with supervisors?"},
            "Motivation": {"Proactivity": "Proactive attitude?", "Responsibility": "Sincere responsibility?", "Research": "Deep study mindset?"},
            "Compliance": {"Discipline": "Followed rules?", "Data Mgmt": "Systematic data management?", "Attendance": "Tardiness status?"}
        },
        "3. Job Competency": {
            "Knowledge": {"Job Knowledge": "Broad/Deep?", "Related Knowledge": "Basic knowledge?"},
            "Judgment": {"Understand Speed": "Understanding speed?", "Validity": "Accurate conclusions?", "Solving": "Lead solutions?", "Insight": "Grasp key points?"},
            "Creativity": {"Improvement": "Improve work sequences?"},
            "Communication": {"Verbal": "Proficient verbal?", "Written": "Proficient writing?", "Negotiation": "Smooth negotiation?"}
        }
    }
}

# --- [3] 리더십 데이터 (한/영 풀번역) ---
LEADER_DATA = {
    "KO": {
        "리더십 역량": {
            "기본역량": {
                "고객지향": "내부 혹은 외부 고객의 요구를 능동적으로 찾아내고 적시에 대응한다",
                "책임감": "업무목표를 달성하기 위해 계획적으로 행동한다",
                "팀워크지향": "구성원의 공감을 얻기 위해 자주 의견을 공유하고 배경을 설명한다"
            },
            "실행역량": {
                "개방적 의사소통": "친밀감을 위해 자신의 사적인 부분을 먼저 이야기한다",
                "문제해결": "분석을 통해 문제의 근본원인을 규명한다",
                "조직이해": "조직의 전략, 운영방식, 역사 등을 파악한다",
                "프로젝트 관리": "정보를 체계적으로 수집하여 계획을 수립한다"
            },
            "전문역량": {
                "분석적 사고": "필요한 정보나 자료가 무엇인지 정확히 파악한다",
                "세밀한 업무처리": "문제 소지를 줄이기 위해 규정이나 관행 등을 조사한다"
            }
        }
    },
    "EN": {
        "Leadership": {
            "Core Competency": {
                "Customer Focus": "Respond to customer needs proactively.",
                "Responsibility": "Act independently to achieve goals.",
                "Teamwork": "Share opinions for consensus."
            },
            "Execution": {
                "Communication": "Share personal aspects for rapport.",
                "Problem Solving": "Identify root causes by analysis.",
                "Org Insight": "Understand strategy and history.",
                "Project Mgmt": "Establish systematic plans."
            },
            "Knowledge": {
                "Analytical": "Identify necessary data accurately.",
                "Detailed": "Investigate regulations and practices."
            }
        }
    }
}

UI = {
    "KO": {"m1": "📝 자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드", "m5": "🚀 리더십 자기평가", "m6": "🎖️ 2차 리더십평가", "sub": "✅ 최종 제출", "already": "✅ 이미 제출을 완료하셨습니다.", "err": "⚠️ 모든 항목의 점수와 근거를 작성해야 제출할 수 있습니다.", "report": "🚀 자기 성장 REPORT", "score": "점수", "basis": "근거", "target": "평가 대상 선택", "self_info": "본인 입력 정보"},
    "EN": {"m1": "📝 Self-Eval", "m2": "👥 2nd Eval", "m3": "⚖️ 3rd Final", "m4": "📊 Admin", "m5": "🚀 Leadership Self-Eval", "m6": "🎖️ 2nd Leadership Eval", "sub": "✅ Submit", "already": "✅ Already Submitted.", "err": "⚠️ All fields required.", "report": "🚀 Growth REPORT", "score": "Score", "basis": "Basis", "target": "Select Target", "self_info": "Self-Input"}
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
        t2 = user_db[user_db['2차평가자'] == user_name]['성명'].tolist()
        t3 = user_db[user_db['3차평가자'] == user_name]['성명'].tolist()
        if t2: 
            m_list.append(L["m2"])
            m_list.append(L["m6"])
        if t3: m_list.append(L["m3"])
        if user_name == "권정순": m_list.append(L["m4"])
        menu = st.sidebar.radio("Menu", m_list)

        def render_form(data_dict, pre, self_info=None):
            res_dict = {}
            for major, subs in data_dict.items():
                with st.expander(f"📂 {major}", expanded=True):
                    for sub, items in subs.items():
                        st.markdown(f"**📍 {sub}**")
                        for it, crit in items.items():
                            c1, c2, c3, c4 = st.columns([2, 2.5, 1, 3.5])
                            label = f"**{it}**"
                            if self_info and it in self_info:
                                label += f"<br><span style='color:blue; font-size: 0.85em;'>[{L['self_info']}] {self_info[it]['score']}</span>"
                                if self_info[it]['basis']: label += f"<br><span style='color:gray; font-size: 0.75em;'>ㄴ{self_info[it]['basis']}</span>"
                            c1.markdown(label, unsafe_allow_html=True)
                            c2.caption(crit)
                            # 중복 방지를 위해 키 값에 프리픽스, 대분류, 소분류, 항목명을 모두 조합
                            s_key = f"{pre}_{major}_{sub}_{it}_score".replace(" ","_")
                            r_key = f"{pre}_{major}_{sub}_{it}_basis".replace(" ","_")
                            s = c3.selectbox(L["score"], [1,2,3,4,5], key=s_key)
                            r = c4.text_input(L["basis"], key=r_key)
                            res_dict[it] = {"score": s, "basis": r, "category": sub}
            return res_dict

        # 자기고과
        if menu == L["m1"]:
            st.header(L["m1"])
            if res_df is not None and not res_df[(res_df['피평가자'] == user_name) & (res_df['구분'] == "자기")].empty:
                st.success(L["already"])
            else:
                eval_res = render_form(EVAL_DATA[lang], "self")
                st.subheader(L["report"])
                r1 = st.text_area("Achievement Summary")
                if st.button(L["sub"]):
                    if any(not v["basis"].strip() for v in eval_res.values()) or not r1.strip(): st.error(L["err"])
                    else:
                        now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                        recs = [{"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                        recs.append({"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "리포트", "항목": "종합", "점수": "-", "근거": r1})
                        if save_data(recs): st.success("Done!"); st.rerun()

        # 리더십 자기평가
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
                        if save_data(recs, "Leadership_Results"): st.success("Done!"); st.rerun()

        # 2차/3차 평가 (모두 본인 점수/근거 노출)
        elif menu in [L["m2"], L["m3"]]:
            st.header(menu)
            mode = "2차" if menu == L["m2"] else "3차"
            targets = t2 if mode == "2차" else t3
            selected = st.selectbox(L["target"], targets)
            target_self = res_df[(res_df['피평가자'] == selected) & (res_df['구분'] == "자기")]
            if target_self.empty: st.warning("Not submitted yet.")
            else:
                s_info = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in target_self.iterrows()}
                rep = res_df[(res_df['피평가자'] == selected) & (res_df['구분'] == "리포트")]
                if not rep.empty:
                    with st.expander(f"📌 {selected}'s Self-Report", expanded=True): st.info(rep.iloc[0]['근거'])
                eval_res = render_form(EVAL_DATA[lang], f"ev_{mode}_{selected}", s_info)
                if st.button(f"Submit {mode} Eval"):
                    if any(not v["basis"].strip() for v in eval_res.values()): st.error(L["err"])
                    else:
                        now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                        recs = [{"시간": now, "평가자": user_name, "피평가자": selected, "구분": mode, "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                        if save_data(recs): st.success("Done!"); st.balloons()

        # 2차 리더십 평가
        elif menu == L["m6"]:
            st.header(L["m6"])
            ldr_t = user_db[(user_db['2차평가자'] == user_name) & (user_db['리더여부'] == 'Y')]['성명'].tolist()
            if ldr_t:
                target = st.selectbox(L["target"], ldr_t)
                target_ld_self = ld_df[(ld_df['피평가자'] == target) & (ld_df['구분'] == "자기")]
                s_ld_info = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in target_ld_self.iterrows()} if not target_ld_self.empty else None
                eval_res = render_form(LEADER_DATA[lang], f"ld2_{target}", s_ld_info)
                if st.button(f"Submit for {target}"):
                    if any(not v["basis"].strip() for v in eval_res.values()): st.error(L["err"])
                    else:
                        now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                        recs = [{"시간": now, "평가자": user_name, "피평가자": target, "구분": "2차", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                        if save_data(recs, "Leadership_Results"): st.success("Done!"); st.balloons()

        # 관리자 대시보드
        elif menu == L["m4"]:
            st.title("Admin")
            st.dataframe(user_db)
            st.divider()
            target_user = st.selectbox("Employee", user_db['성명'].tolist())
            new_pw = st.text_input("New PW", type="password")
            if st.button("Save PW"):
                idx = user_db[user_db['성명'] == target_user].index[0]
                user_db.at[idx, '비밀번호'] = new_pw
                if conn.update(worksheet="Users", data=user_db): st.success("Saved!"); st.rerun()
