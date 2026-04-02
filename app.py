import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta

# --- [1] 기본 설정 ---
st.set_page_config(page_title="SRS Global HR System", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try: return conn.read(worksheet="Users", ttl=0)
    except: return None

# --- [2] 평가 및 UI 데이터 ---
EVAL_DATA = {
    "KO": {
        "1. 업무실적": {
            "업무의 양": {"속도": "업무를 신속하게 처리하며 지체되는 일은 없었는가?", "지속성": "어떤 일이나 차이 없이 끈기있게 했는가?", "능률": "신속 정확하게 낭비 없이 처리 했는가?"},
            "업무의 질": {"정확성": "일의 결과를 믿을 수 있는가?", "성과": "일의 성과가 내용에 있어서 뛰어났는가?", "꼼꼼함": "철저하고 뒷처리를 잘하는가?"}
        },
        "2. 근무태도": {
            "협조성": {"횡적협조": "동료와 협력하며 조직 효율에 공헌하는가?", "존중": "팀 전체의 의견을 존중하는가?", "상사협조": "상사에 대해 협력하며 성과가 있는가?"},
            "근무의욕": {"적극성": "일에 능동적으로 대처하려는 의욕은 어떤가?", "책임감": "성실하게 일하려는 의욕은 어떤가?", "연구심": "깊게 연구하려는 의욕은 어떤가?"},
            "복무상황": {"규율": "규칙 준수?", "DB화": "업무 데이터 관리?", "근태상황": "지각, 조퇴, 결근 등"}
        },
        "3. 직무능력": {
            "지식": {"직무지식": "지식이 넓고 깊은가?", "관련지식": "기초지식이 넓고 깊은가?"},
            "이해판단력": {"신속성": "이해 속도?", "타당성": "결론은 타당한가?", "문제해결": "해결 주도력?", "통찰력": "요점 파악 능력?"},
            "창의연구력": { "연구개선": "아이디어를 살리고 일의 개선을 도모하는가?" },
            "표현절충": {"구두표현": "말하기 능력?", "문장표현": "글쓰기 능력?", "절충": "교섭 능력?"}
        }
    },
    "EN": {
        "1. Performance": {
            "Quantity of Work": {"Speed": "Quickly?", "Persistence": "Consistently?", "Efficiency": "Efficiently?"},
            "Quality of Work": {"Accuracy": "Reliable?", "Achievement": "Outstanding?", "Thoroughness": "Thoroughly?"}
        },
        "2. Work Attitude": {
            "Cooperation": {"Horizontal": "Cooperate?", "Respect": "Team first?", "Supervisor": "Supervisors?"},
            "Motivation": {"Proactivity": "Proactive?", "Responsibility": "Responsible?", "Research": "Study deep?"},
            "Compliance": {"Discipline": "Rules?", "Data Mgmt": "Systematic?", "Attendance": "Attendance?"}
        },
        "3. Job Competency": {
            "Knowledge": {"Job Knowledge": "Broad/Deep?", "Related Knowledge": "Basic related?"},
            "Judgment": {"Speed": "Understand fast?", "Validity": "Valid?", "Problem Solving": "Solutions?", "Insight": "Independent?"},
            "Creativity": {"Improvement": "Improve sequences?"},
            "Communication": {"Verbal": "Clear verbal?", "Written": "Clear writing?", "Negotiation": "Smooth?"}
        }
    }
}

LEADER_DATA = {
    "KO": {
        "리더십 역량": {
            "기본": {"고객지향": "고객 요구 적시 대응", "책임감": "목표 달성 계획성", "팀워크지향": "의견 공유 및 배경 설명"},
            "실행": {"개방적의사소통": "친밀감 형성", "문제해결": "원인 규명", "조직이해": "전략 파악", "프로젝트관리": "체계적 수립"},
            "전문": {"분석적사고": "필요 정보 파악", "세밀한업무처리": "리스크 조사"}
        }
    },
    "EN": {
        "Leadership": {
            "Core": {"Customer Focus": "Respond to customer needs.", "Responsibility": "Act independently.", "Teamwork": "Share opinions."},
            "Execution": {"Communication": "Share personal aspects.", "Problem Solving": "Identify root causes.", "Org Insight": "Understand strategy.", "Project Mgmt": "Establish plans."},
            "Professional": {"Analytical": "Identify data.", "Detailed": "Investigate regulations."}
        }
    }
}

REPORT_UI = {
    "KO": {"q1": "1. 평가 기간동안 내가 낸 성과는 무엇입니까?", "q2": "2. 평가 기간동안 내가 습득한 지식이 무엇입니까?", "q3": "3. 평가 기간동안 내가 인재 양성을 위하여 무엇을 하였습니까?"},
    "EN": {"q1": "1. Achievements?", "q2": "2. Knowledge acquired?", "q3": "3. Talent development?"}
}

UI = {
    "KO": {"m1": "📝 자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드", "m5": "🚀 리더십 자기평가", "m6": "🎖️ 2차 리더십평가", "sub": "✅ 최종 제출", "save": "💾 임시 저장", "report_title": "🚀 자기 성장 REPORT", "score": "점수", "basis": "근거", "target": "대상 선택", "self_info": "본인 입력", "done_msg": "저장되었습니다!"},
    "EN": {"m1": "📝 Self-Evaluation", "m2": "👥 2nd Evaluation", "m3": "⚖️ 3rd Final Review", "m4": "📊 Admin Dashboard", "m5": "🚀 Leadership Self-Eval", "m6": "🎖️ 2nd Leadership Eval", "sub": "✅ Final Submit", "save": "💾 Save Draft", "already": "✅ Done", "err": "⚠️ All fields required.", "report_title": "🚀 Self-Growth REPORT", "score": "Score", "basis": "Basis", "target": "Select Target", "self_info": "Self-Input", "done_msg": "Saved!"}
}

def save_to_sheet(recs, ws="Results"):
    try:
        df = conn.read(worksheet=ws, ttl=0)
        final = pd.concat([df, pd.DataFrame(recs)], ignore_index=True) if df is not None else pd.DataFrame(recs)
        conn.update(worksheet=ws, data=final)
        st.cache_data.clear()
        return True
    except: return False

# --- [3] 메인 실행 ---
db = get_db()
if 'auth' not in st.session_state: 
    st.session_state.update({'auth':False,'user':'','ldr':'N','lang':'KO'})

if db is not None:
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System HR")
        n, p = st.text_input("Name"), st.text_input("PW", type="password")
        if st.button("Login"):
            u = db[db['성명'].str.strip() == n.strip()]
            if not u.empty and str(p) == str(u.iloc[0]['비밀번호']):
                st.session_state.update({'auth':True,'user':n.strip(),'ldr':str(u.iloc[0]['리더여부']).upper(),'lang':u.iloc[0]['언어'] if '언어' in u.columns else 'KO'})
                st.rerun()
            else: st.error("Login Failed")
    else:
        L, user, lang = UI[st.session_state.lang], st.session_state.user, st.session_state.lang
        res_df, ld_df = conn.read(worksheet="Results", ttl=0), conn.read(worksheet="Leadership_Results", ttl=0)

        # 메뉴 리스트 생성
        m_list = []
        
        # 대표님(김용환)은 '자기고과 작성' 메뉴 제외
        if user != "김용환":
            m_list.append(L["m1"])
            
        if st.session_state.ldr == 'Y': m_list.append(L["m5"])
        t2, t3 = db[db['2차평가자']==user]['성명'].tolist(), db[db['3차평가자']==user]['성명'].tolist()
        if t2: m_list += [L["m2"], L["m6"]]
        if t3: m_list.append(L["m3"])
        if user in ["권정순"]: m_list.append(L["m4"])
        
        menu = st.sidebar.radio("Menu", m_list)

        def render_form_logic(data, pre, self_info=None, eval_type="자기", ws_name="Results"):
            with st.form(key=f"form_{pre}"):
                res_dict = {}
                for major, subs in data.items():
                    st.subheader(f"📂 {major}")
                    for sub, items in subs.items():
                        st.markdown(f"**📍 {sub}**")
                        for it, crit in items.items():
                            c1, c2, c3, c4 = st.columns([2, 2.5, 1, 3.5])
                            lbl = f"**{it}**"
                            if self_info and it in self_info:
                                lbl += f"<br><span style='color:blue; font-size:0.85em;'>[{L['self_info']}] {self_info[it]['score']}</span>"
                                if self_info[it]['basis']: lbl += f"<br><span style='color:gray; font-size:0.75em;'>ㄴ{self_info[it]['basis']}</span>"
                            c1.markdown(lbl, unsafe_allow_html=True); c2.caption(crit)
                            s = c3.selectbox(L["score"], [1,2,3,4,5], key=f"s_{pre}_{it}")
                            r = c4.text_input(L["basis"], key=f"r_{pre}_{it}")
                            res_dict[it] = {"score": s, "basis": r, "cat": sub}
                
                report_data = {}
                if pre == "self":
                    st.divider(); st.subheader(L["report_title"])
                    report_data['q1'] = st.text_area(REPORT_UI[lang]['q1'], height=100)
                    report_data['q2'] = st.text_area(REPORT_UI[lang]['q2'], height=100)
                    report_data['q3'] = st.text_area(REPORT_UI[lang]['q3'], height=100)

                col1, col2 = st.columns([1, 1])
                save_btn = col1.form_submit_button(L["save"])
                final_btn = col2.form_submit_button(L["sub"])

                if save_btn or final_btn:
                    if final_btn and any(not v["basis"].strip() for v in res_dict.values()):
                        st.error(L["err"])
                    else:
                        now = (datetime.datetime.now()+timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                        status = "Final" if final_btn else "Draft"
                        target = st.session_state.get('target_user', user)
                        recs = [{"시간":now,"평가자":user,"피평가자":target,"구분":f"{eval_type}({status})","항목":k,"점수":v["score"],"근거":v["basis"]} for k,v in res_dict.items()]
                        if pre == "self":
                            for k_q, v_q in report_data.items():
                                recs.append({"시간":now,"평가자":user,"피평가자":user,"구분":"리포트","항목":REPORT_UI[lang][k_q][:10],"점수":"-","근거":v_q})
                        if save_to_sheet(recs, ws_name):
                            st.success(L["done_msg"])
                            if final_btn: st.balloons()

        if menu == L["m1"]:
            st.header(L["m1"])
            render_form_logic(EVAL_DATA[lang], "self", eval_type="자기")

        elif menu == L["m5"]:
            st.header(L["m5"])
            l_data = LEADER_DATA[lang] if lang in LEADER_DATA else LEADER_DATA["KO"]
            render_form_logic(l_data, "ld_self", eval_type="자기", ws_name="Leadership_Results")

        elif menu in [L["m2"], L["m3"]]:
            st.header(menu)
            m_label = "2차" if menu == L["m2"] else "3차"
            target = st.selectbox(L["target"], t2 if m_label=="2차" else t3)
            st.session_state['target_user'] = target
            target_self = res_df[(res_df['피평가자']==target)&(res_df['구분'].str.contains("자기"))]
            if target_self.empty: st.warning("Waiting for submission...")
            else:
                s_info = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in target_self.iterrows()}
                rep_df = res_df[(res_df['피평가자']==target)&(res_df['구분']=="리포트")]
                if not rep_df.empty:
                    with st.expander(f"📌 {target}'s Growth Report"):
                        for _, r in rep_df.iterrows():
                            st.markdown(f"**{r['항목']}...**"); st.info(r['근거'])
                render_form_logic(EVAL_DATA[lang], f"ev_{m_label}_{target}", s_info, eval_type=m_label)

        elif menu == L["m6"]:
            st.header(L["m6"])
            ldr_t = db[(db['2차평가자']==user)&(db['리더여부']=='Y')]['성명'].tolist()
            if ldr_t:
                target = st.selectbox(L["target"], ldr_t)
                st.session_state['target_user'] = target
                target_ld = ld_df[(ld_df['피평가자']==target)&(ld_df['구분'].str.contains("자기"))]
                s_ld = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in target_ld.iterrows()} if not target_ld.empty else None
                render_form_logic(LEADER_DATA[lang if lang in LEADER_DATA else "KO"], f"ld2_{target}", s_ld, eval_type="2차", ws_name="Leadership_Results")

        elif menu == L["m4"]:
            st.title("Admin Dashboard"); st.dataframe(db)
