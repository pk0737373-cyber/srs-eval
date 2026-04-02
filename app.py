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

# --- [2] 평가 데이터 ---
EVAL_DATA = {
    "KO": {
        "1. 업무실적": {
            "업무의 양": {"속도": "업무를 신속하게 처리하며 지체되는 일은 없었는가?", "지속성": "어떤 일이나 차이 없이 끈기있게 했는가?", "능률": "신속 정확하게 낭비 없이 처리 했는가?"},
            "업무의 질": {"정확성": "일의 결과를 믿을 수 있는가?", "성과": "일의 성과가 내용에 있어서 뛰어났는가?", "꼼꼼함": "철저하고 뒷처리를 잘하는가?"}
        },
        "2. 근무태도": {
            "협조성": {"횡적협조": "동료와 협력하며 조직 전체의 능률향상에 공헌하는가?", "존중": "팀 전체의 의견을 존중하는가?", "상사협조": "상사에 대해 협력하며 성과가 있는가?"},
            "근무의욕": {"적극성": "일에 능동적으로 대처하려는 의욕은 어떤가?", "책임감": "성실하게 일하려는 의욕은 어떤가?", "연구심": "깊게 연구하려는 의욕은 어떤가?"},
            "복무상황": {"규율": "규칙 준수?", "DB화": "업무 데이터 관리?", "근태상황": "지각/조퇴/결근 등"}
        },
        "3. 직무능력": {
            "지식": {"직무지식": "지식이 넓고 깊은가?", "관련지식": "기초지식이 넓고 깊은가?"},
            "이해판단력": {"신속성": "이해 속도?", "타당성": "결론 타당성?", "문제해결": "해결 주도력?", "통찰력": "요점 파악 능력?"},
            "창의연구력": { "연구개선": "아이디어를 살리고 일의 개선을 도모하는가?" },
            "표현절충": {"구두표현": "말하기 능력?", "문장표현": "글쓰기 능력?", "절충": "교섭 및 절충 능력?"}
        }
    },
    "EN": {
        "1. Performance": {
            "Quantity of Work": {"Speed": "Did you process work quickly?", "Persistence": "Worked consistently?", "Efficiency": "Efficiently without waste?"},
            "Quality of Work": {"Accuracy": "Are results reliable?", "Achievement": "Was achievement outstanding?", "Thoroughness": "Thorough completion?"}
        },
        "2. Work Attitude": {
            "Cooperation": {"Horizontal": "Cooperated for team efficiency?", "Respect": "Respected team opinions?", "Supervisor": "Cooperated with supervisors?"},
            "Motivation": {"Proactivity": "Proactive engagement?", "Responsibility": "Worked sincerely?", "Research": "Desire for research?"},
            "Compliance": {"Discipline": "Followed rules?", "Data Mgmt": "Systematic data management?", "Attendance": "Attendance status?"}
        },
        "3. Job Competency": {
            "Knowledge": {"Job Knowledge": "Broad and deep?", "Related Knowledge": "Basic related knowledge?"},
            "Judgment": {"Understand": "Understanding speed?", "Validity": "Valid conclusions?", "Problem Solving": "Lead solutions?", "Insight": "Grasp key points?"},
            "Creativity": {"Improvement": "Creative improvements?"},
            "Communication": {"Verbal": "Verbal skill?", "Written": "Writing skill?", "Negotiation": "Negotiation skill?"}
        }
    }
}

LEADER_DATA = {
    "KO": { "리더십 역량": { "기본": {"고객지향": "고객 요구 대응", "책임감": "계획적 행동", "팀워크지향": "의견 공유"}, "실행": {"개방적의사소통": "친밀감 형성", "문제해결": "원인 규명", "조직이해": "전략 파악", "프로젝트관리": "계획 수립"}, "전문": {"분석적사고": "정보 파악", "세밀한업무처리": "규정 조사"} } },
    "EN": { "Leadership": { "Core": {"Customer Focus": "Needs", "Responsibility": "Independent", "Teamwork": "Share"}, "Execution": {"Communication": "Rapport", "Problem Solving": "Root causes", "Org Insight": "Strategy", "Project Mgmt": "Plans"}, "Professional": {"Analytical": "Data", "Detailed": "Regulations"} } }
}

REPORT_UI = {
    "KO": {"q1": "1. 성과", "q2": "2. 습득 지식", "q3": "3. 인재 양성"},
    "EN": {"q1": "1. Achievements", "q2": "2. Knowledge Acquired", "q3": "3. Talent Development"}
}

UI = {
    "KO": {"m1": "📝 자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드", "m5": "🚀 리더십 자기평가", "m6": "🎖️ 2차 리더십평가", "sub": "✅ 최종 제출", "save": "💾 임시 저장", "already": "✅ 최종 제출이 완료되었습니다.", "err": "⚠️ 근거를 상세히 작성해 주세요.", "report_title": "🚀 자기 성장 REPORT", "score": "점수", "basis": "근거 (상세히 작성)", "basis_msg": "※ 근거를 상세히 작성해 주세요", "target": "대상 선택", "self_info": "본인 입력", "done_msg": "저장되었습니다!"},
    "EN": {"m1": "📝 Self-Eval", "m2": "👥 2nd Eval", "m3": "⚖️ 3rd Final", "m4": "📊 Admin", "m5": "🚀 Leadership Eval", "m6": "🎖️ 2nd Leadership", "sub": "✅ Final Submit", "save": "💾 Save Draft", "already": "✅ Submission completed.", "err": "⚠️ Provide details.", "report_title": "🚀 Self-Growth REPORT", "score": "Score", "basis": "Basis", "target": "Target", "self_info": "Self-Input", "done_msg": "Saved!"}
}

# --- [3] 데이터 처리 함수 ---
def save_with_cleanup(recs, user_id, target_id, is_final, ws_name="Results"):
    try:
        df = conn.read(worksheet=ws_name, ttl=0)
        if df is None: df = pd.DataFrame()
        # [수정] 저장/제출 시 기존의 Draft 데이터는 무조건 삭제하여 중복 방지
        if not df.empty:
            df = df[~((df['평가자'] == user_id) & (df['피평가자'] == target_id) & (df['구분'].str.contains("Draft", na=False)))]
            if is_final: # 최종 제출일 경우 이전 리포트나 다른 임시본도 정리
                df = df[~((df['평가자'] == user_id) & (df['피평가자'] == target_id) & (df['구분'] == "리포트"))]
        f_df = pd.concat([df, pd.DataFrame(recs)], ignore_index=True)
        conn.update(worksheet=ws_name, data=f_df)
        st.cache_data.clear()
        return True
    except: return False

# --- [4] 메인 실행 ---
db_raw = get_db()
if 'auth' not in st.session_state: 
    st.session_state.update({'auth':False,'user':'','ldr':'N','lang':'KO'})

if db_raw is not None:
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System HR")
        n, p = st.text_input("Name"), st.text_input("PW", type="password")
        if st.button("Login"):
            u = db_raw[db_raw['성명'].str.strip() == n.strip()]
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
        t2, t3 = db_raw[db_raw['2차평가자']==user]['성명'].tolist(), db_raw[db_raw['3차평가자']==user]['성명'].tolist()
        if t2: m_list += [L["m2"], L["m6"]]
        if t3: m_list.append(L["m3"])
        if user == "권정순": m_list.append(L["m4"])
        
        menu = st.sidebar.radio("Menu", m_list)

        def render_form(data_dict, pre, self_info=None, eval_type="자기", ws_name="Results"):
            target = st.session_state.get('cur_target', user)
            check_df = res_df if ws_name == "Results" else ld_df
            
            # [수정] 제출 여부 판정: 오직 Final/최종/2차/3차 글자가 있을 때만 닫힘 (Draft는 제외)
            is_done = False
            if not check_df.empty:
                is_done = not check_df[(check_df['평가자']==user) & (check_df['피평가자']==target) & (check_df['구분'].str.contains("Final|최종|2차\(Final\)|3차\(Final\)", na=False))].empty
            
            if is_done: st.success(L["already"])
            else:
                with st.form(key=f"f_{pre}"):
                    tabs = st.tabs(list(data_dict.keys()))
                    res_dict = {}
                    for i, (major, subs) in enumerate(data_dict.items()):
                        with tabs[i]:
                            for sub, items in subs.items():
                                st.markdown(f"#### 📍 {sub}")
                                for it, crit in items.items():
                                    c1, c2, c3, c4 = st.columns([2, 3, 1, 3])
                                    lbl = f"**{it}**"
                                    if self_info and it in self_info:
                                        lbl += f"<br><span style='color:blue; font-size:0.85em;'>[{L['self_info']}] {self_info[it]['score']}점</span>"
                                        if self_info[it]['basis']: lbl += f"<br><span style='color:#0056b3; font-size:0.75em;'>ㄴ근거: {self_info[it]['basis']}</span>"
                                    c1.markdown(lbl, unsafe_allow_html=True); c2.info(crit)
                                    s = c3.selectbox(L["score"], [1,2,3,4,5], key=f"s_{pre}_{it}")
                                    r = c4.text_input(L["basis"], placeholder=L["basis_msg"], key=f"r_{pre}_{it}")
                                    res_dict[it] = {"score": s, "basis": r}
                    
                    rep_data = {}
                    if pre == "self":
                        st.divider(); st.subheader(L["report_title"])
                        for k, v in REPORT_UI[lang].items(): rep_data[k] = st.text_area(v, key=f"rep_{k}")

                    c1, c2 = st.columns(2)
                    save_btn, final_btn = c1.form_submit_button(L["save"]), c2.form_submit_button(L["sub"])

                    if save_btn or final_btn:
                        is_f = True if final_btn else False
                        if is_f and any(len(v["basis"].strip()) < 2 for v in res_dict.values()): st.error(L["err"])
                        else:
                            now = (datetime.datetime.now()+timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                            stt = "Final" if is_f else "Draft"
                            recs = [{"시간":now,"평가자":user,"피평가자":target,"구분":f"{eval_type}({stt})","항목":k,"점수":v["score"],"근거":v["basis"]} for k,v in res_dict.items()]
                            if pre == "self":
                                for kq, vq in rep_data.items(): recs.append({"시간":now,"평가자":user,"피평가자":user,"구분":"리포트","항목":REPORT_UI[lang][kq],"점수":"-","근거":vq})
                            if save_with_cleanup(recs, user, target, is_f, ws_name):
                                st.success(L["done_msg"]); st.cache_data.clear(); st.rerun()

        if menu == L["m1"]: render_form(EVAL_DATA[lang], "self")
        elif menu == L["m5"]: render_form(LEADER_DATA[lang if lang in LEADER_DATA else "KO"], "ld", ws_name="Leadership_Results")
        elif menu in [L["m2"], L["m3"]]:
            ml = "2차" if menu == L["m2"] else "3차"
            target = st.selectbox(L["target"], t2 if ml=="2차" else t3)
            st.session_state['cur_target'] = target
            ts = res_df[(res_df['피평가자']==target)&(res_df['구분'].str.contains("자기", na=False))]
            if ts.empty: st.warning("Waiting...")
            else:
                si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ts.iterrows()}
                rd = res_df[(res_df['피평가자']==target)&(res_df['구분']=="리포트")]
                if not rd.empty:
                    with st.expander(f"📌 {target}'s Report"):
                        for _, r in rd.iterrows(): st.markdown(f"**{r['항목']}**"); st.info(r['근거'])
                render_form(EVAL_DATA[lang], f"ev_{target}", si, eval_type=ml)
        elif menu == L["m6"]:
            target = st.selectbox(L["target"], db_raw[(db_raw['2차평가자']==user)&(db_raw['리더여부']=='Y')]['성명'].tolist())
            st.session_state['cur_target'] = target
            ls = ld_df[(ld_df['피평가자']==target)&(ld_df['구분'].str.contains("자기", na=False))]
            si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ls.iterrows()} if not ls.empty else None
            render_form(LEADER_DATA[lang if lang in LEADER_DATA else "KO"], f"ld2", si, eval_type="2차", ws_name="Leadership_Results")
        elif menu == L["m4"]:
            st.title("📊 Admin Dashboard")
            st.subheader("🔑 비밀번호 관리")
            u_list = db_raw['성명'].tolist(); sel_u = st.selectbox("직원 선택", u_list); new_pw = st.text_input("새 비밀번호", type="password")
            if st.button("비밀번호 변경"):
                db_raw.loc[db_raw['성명'] == sel_u, '비밀번호'] = new_pw
                conn.update(worksheet="Users", data=db_raw); st.success(f"{sel_u}님의 비밀번호가 변경되었습니다.")
            st.divider(); st.subheader("👥 직원 명단"); st.dataframe(db_raw)
