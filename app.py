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

# --- [2] 평가 데이터 (상세 기준 100% 풀버전) ---
EVAL_DATA = {
    "KO": {
        "1. 업무실적": {
            "업무의 양": {"속도": "업무를 신속하게 처리하며 지체되는 일은 없었는가?", "지속성": "어떤 일이나 차이 없이 끈기있게 했는가?", "능률": "신속 정확하게 낭비 없이 처리 했는가?"},
            "업무의 질": {"정확성": "일의 결과를 믿을 수 있는가?", "성과": "일의 성과가 내용에 있어서 뛰어났는가?", "꼼꼼함": "철저하고 뒷처리를 잘하는가?"}
        },
        "2. 근무태도": {
            "협조성": {"횡적협조": "동료와 협력하며 조직 전체의 능률향상에 공헌하는가?", "존중": "자신의 생각보다는 팀 전체의 의견을 존중하는가?", "상사협조": "상사에 대해 협력하며 성과가 있는가?"},
            "근무의욕": {"적극성": "일에 능동적으로 대처하려는 의욕은 어떤가?", "책임감": "책임을 회피하지 않으며 성실하게 일하려는 의욕은 어떤가?", "연구심": "넓고 깊게 일을 연구하려는 의욕은 어떤가?"},
            "복무상황": {"규율": "규칙을 준수하며 직장질서유지에 애쓰는가?", "DB화": "업무 데이터의 체계적인 관리(공유드라이브 활용 등)", "근태상황": "지각, 조퇴, 결근 등 상황은 어떤가?"}
        },
        "3. 직무능력": {
            "지식": {"직무지식": "담당업무의 지식이 넓고 깊은가?", "관련지식": "관련 기초지식은 넓고 깊은가?"},
            "이해판단력": {"신속성": "지시나 현상을 이해하는 속도가 빠른가?", "타당성": "판단 결과와 결론은 타당한가?", "문제해결": "문제의 본질을 파악하고 해결을 주도하는가?", "통찰력": "요점 파악 및 자적 결론?"},
            "창의연구력": { "연구개선": "항상 창의적인 아이디어를 살리고 일의 개선을 도모하는가?" },
            "표현절충": {"구두표현": "말하기 능력?", "문장표현": "글쓰기 능력?", "절충": "교섭 및 절충 능력?"}
        }
    },
    "EN": {
        "1. Performance": {
            "Quantity": {"Speed": "Did you process work quickly without delay?", "Persistence": "Did you work consistently?", "Efficiency": "Did you handle work accurately and without waste?"},
            "Quality": {"Accuracy": "Are the results reliable?", "Achievement": "Was the achievement outstanding?", "Thoroughness": "Were you thorough in completion?"}
        },
        "2. Work Attitude": {
            "Cooperation": {"Horizontal": "Cooperate with colleagues for team efficiency?", "Respect": "Respect team opinions over personal views?", "Supervisor": "Cooperate effectively with supervisors?"},
            "Motivation": {"Proactivity": "What was your level of proactive engagement?", "Responsibility": "Work sincerely without avoiding responsibility?", "Research": "Desire for deep research and study?"},
            "Compliance": {"Discipline": "Follow rules?", "Data Mgmt": "Manage work data systematically?", "Attendance": "Attendance status?"}
        },
        "3. Competency": {
            "Knowledge": {"Job Knowledge": "Broad and deep?", "Related Knowledge": "Basic related knowledge sufficient?"},
            "Judgment": {"Understand": "Fast understanding?", "Validity": "Are your conclusions valid?", "Problem Solving": "Identify and lead solving?", "Insight": "Grasp key points in complex situations?"},
            "Creativity": {"Improvement": "Seek improvements through creative ideas?"},
            "Communication": {"Verbal": "Verbal reporting skills?", "Written": "Writing (reports, drafts)?", "Negotiation": "Negotiation and coordination?"}
        }
    }
}

LEADER_DATA = {
    "KO": {
        "리더십 역량": {
            "기본역량": {"고객지향": "내부 혹은 외부 고객의 요구를 능동적으로 찾아내고 적시에 대응한다", "책임감": "특별한 지시를 하지 않더라도 업무목표를 달성하기 위해 계획적으로 행동한다", "팀워크지향": "구성원의 공감을 얻기 위해 자주 의견을 공유하고 배경을 설명한다"},
            "실행역량": {"개방적의사소통": "상대방이 친밀감을 느낄 수 있도록 자신의 사적인 부분을 먼저 이야기한다", "문제해결": "문제 발생 시 정보와 자료를 분석하여 문제의 근본원인을 규명한다", "조직이해": "조직의 전략, 운영방식, 역사 등을 파악한다", "프로젝트관리": "프로젝트 관련 정보를 체계적으로 수집하여 계획을 수립한다"},
            "전문역량": {"분석적사고": "문제를 해결하기 위해 필요한 정보나 자료가 무엇인지 정확히 파악한다", "세밀한업무처리": "문제 발생 소지를 최소화하기 위해 관련 규정이나 관행 등을 조사한다"}
        }
    },
    "EN": {
        "Leadership": {
            "Core": {"Customer Focus": "Identify and respond to customer needs.", "Responsibility": "Act independently to achieve goals.", "Teamwork": "Share opinions and explain backgrounds."},
            "Execution": {"Communication": "Share personal aspects to build rapport.", "Problem Solving": "Identify root causes by analysis.", "Org Insight": "Understand strategy and history.", "Project Mgmt": "Collect info and establish plans."},
            "Professional": {"Analytical": "Identify necessary data.", "Detailed": "Investigate regulations to minimize risks."}
        }
    }
}

REPORT_UI = {
    "KO": {"q1": "1. 평가 기간동안 내가 낸 성과는 무엇입니까?", "q2": "2. 평가 기간동안 내가 습득한 지식이 무엇입니까?", "q3": "3. 평가 기간동안 내가 인재 양성을 위하여 무엇을 하였습니까?"},
    "EN": {"q1": "1. Your achievements?", "q2": "2. Knowledge acquired?", "q3": "3. Talent development efforts?"}
}

UI = {
    "KO": {"m1": "📝 자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드", "m5": "🚀 리더십 자기평가", "m6": "🎖️ 2차 리더십평가", "sub": "✅ 최종 제출", "save": "💾 임시 저장", "already": "✅ 이미 최종 제출이 완료되었습니다.", "err": "⚠️ 모든 항목의 점수와 근거를 작성해야 최종 제출이 가능합니다.", "report_title": "🚀 자기 성장 REPORT", "score": "점수", "basis": "근거", "target": "대상 선택", "self_info": "본인 입력", "done_msg": "저장되었습니다!"},
    "EN": {"m1": "📝 Self-Evaluation", "m2": "👥 2nd Evaluation", "m3": "⚖️ 3rd Final Review", "m4": "📊 Admin Dashboard", "m5": "🚀 Leadership Self-Eval", "m6": "🎖️ 2nd Leadership Eval", "sub": "✅ Final Submit", "save": "💾 Save Draft", "already": "✅ Final submission completed.", "err": "⚠️ Please fill all fields.", "report_title": "🚀 Self-Growth REPORT", "score": "Score", "basis": "Basis", "target": "Select Target", "self_info": "Self-Input", "done_msg": "Saved!"}
}

# --- [3] 데이터 저장 및 자동 정리 함수 ---
def save_with_cleanup(recs, user_id, target_id, is_final, ws_name="Results"):
    try:
        df = conn.read(worksheet=ws_name, ttl=0)
        if df is None: df = pd.DataFrame()
        
        # 최종 제출 시 기존 이 유저의 Draft 데이터는 모두 지우기
        if is_final and not df.empty:
            df = df[~((df['평가자'] == user_id) & (df['피평가자'] == target_id) & (df['구분'].str.contains("Draft")))]
            if ws_name == "Results": # 일반 평가 시 리포트도 정리
                df = df[~((df['평가자'] == user_id) & (df['피평가자'] == target_id) & (df['구분'] == "리포트"))]
        
        final_df = pd.concat([df, pd.DataFrame(recs)], ignore_index=True)
        conn.update(worksheet=ws_name, data=final_df)
        st.cache_data.clear()
        return True
    except: return False

# --- [4] 메인 실행 ---
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

        m_list = []
        if user != "김용환":
            m_list.append(L["m1"])
            if st.session_state.ldr == 'Y': m_list.append(L["m5"])
        t2, t3 = db[db['2차평가자']==user]['성명'].tolist(), db[db['3차평가자']==user]['성명'].tolist()
        if t2: m_list += [L["m2"], L["m6"]]
        if t3: m_list.append(L["m3"])
        if user in ["권정순"]: m_list.append(L["m4"])
        menu = st.sidebar.radio("Menu", m_list)

        def render_full_form(data, pre, self_info=None, eval_type="자기", ws_name="Results"):
            target = st.session_state.get('cur_target', user)
            check_df = res_df if ws_name == "Results" else ld_df
            is_done = not check_df[(check_df['평가자']==user) & (check_df['피평가자']==target) & (check_df['구분'].str.contains("Final"))].empty
            
            if is_done: st.success(L["already"])
            else:
                with st.form(key=f"f_{pre}"):
                    res_dict = {}
                    for major, subs in data.items():
                        st.subheader(f"📂 {major}")
                        for sub, items in subs.items():
                            st.markdown(f"**📍 {sub}**")
                            for it, crit in items.items():
                                c1, c2, c3, c4 = st.columns([2, 3, 1, 3])
                                lbl = f"**{it}**"
                                if self_info and it in self_info:
                                    lbl += f"<br><span style='color:blue; font-size:0.85em;'>[{L['self_info']}] {self_info[it]['score']}</span>"
                                    if self_info[it]['basis']: lbl += f"<br><span style='color:gray; font-size:0.75em;'>ㄴ{self_info[it]['basis']}</span>"
                                c1.markdown(lbl, unsafe_allow_html=True); c2.info(crit) # 상세 기준 복구
                                s = c3.selectbox(L["score"], [1,2,3,4,5], key=f"s_{pre}_{it}")
                                r = c4.text_input(L["basis"], key=f"r_{pre}_{it}")
                                res_dict[it] = {"score": s, "basis": r}
                    
                    report_data = {}
                    if pre == "self":
                        st.divider(); st.subheader(L["report_title"])
                        report_data['q1'] = st.text_area(REPORT_UI[lang]['q1'], key="q1_v")
                        report_data['q2'] = st.text_area(REPORT_UI[lang]['q2'], key="q2_v")
                        report_data['q3'] = st.text_area(REPORT_UI[lang]['q3'], key="q3_v")

                    c1, c2 = st.columns(2)
                    save_btn, final_btn = c1.form_submit_button(L["save"]), c2.form_submit_button(L["sub"])

                    if save_btn or final_btn:
                        if final_btn and any(not v["basis"].strip() for v in res_dict.values()): st.error(L["err"])
                        else:
                            now = (datetime.datetime.now()+timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                            stt = "Final" if final_btn else "Draft"
                            recs = [{"시간":now,"평가자":user,"피평가자":target,"구분":f"{eval_type}({stt})","항목":k,"점수":v["score"],"근거":v["basis"]} for k,v in res_dict.items()]
                            if pre == "self":
                                for kq, vq in report_data.items():
                                    recs.append({"시간":now,"평가자":user,"피평가자":user,"구분":"리포트","항목":REPORT_UI[lang][kq][:10],"점수":"-","근거":vq})
                            if save_with_cleanup(recs, user, target, final_btn, ws_name):
                                st.success(L["done_msg"])
                                if final_btn: st.balloons(); st.rerun()

        if menu == L["m1"]: render_full_form(EVAL_DATA[lang], "self")
        elif menu == L["m5"]: render_full_form(LEADER_DATA[lang if lang in LEADER_DATA else "KO"], "ld_self", ws_name="Leadership_Results")
        elif menu in [L["m2"], L["m3"]]:
            ml = "2차" if menu == L["m2"] else "3차"
            target = st.selectbox(L["target"], t2 if ml=="2차" else t3)
            st.session_state['cur_target'] = target
            ts = res_df[(res_df['피평가자']==target)&(res_df['구분'].str.contains("자기"))]
            if ts.empty: st.warning("Waiting...")
            else:
                si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ts.iterrows()}
                rd = res_df[(res_df['피평가자']==target)&(res_df['구분']=="리포트")]
                if not rd.empty:
                    with st.expander(f"📌 {target}'s Report"):
                        for _, r in rd.iterrows(): st.markdown(f"**{r['항목']}...**"); st.info(r['근거'])
                render_full_form(EVAL_DATA[lang], f"ev_{target}", si, eval_type=ml)
        elif menu == L["m6"]:
            target = st.selectbox(L["target"], db[(db['2차평가자']==user)&(db['리더여부']=='Y')]['성명'].tolist())
            st.session_state['cur_target'] = target
            ls = ld_df[(ld_df['피평가자']==target)&(ld_df['구분'].str.contains("자기"))]
            si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ls.iterrows()} if not ls.empty else None
            render_full_form(LEADER_DATA[lang if lang in LEADER_DATA else "KO"], f"ld2_{target}", si, eval_type="2차", ws_name="Leadership_Results")
        elif menu == L["m4"]: st.title("Admin"); st.dataframe(db)
