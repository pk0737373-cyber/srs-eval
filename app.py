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

# --- [2] 평가 데이터 (설계안 100% 반영) ---
EVAL_DATA = {
    "KO": {
        "1. 업무실적": {
            "업무의 양": {"속도": "업무를 신속하게 처리하며 지체되는 일은 없었는가?", "지속성": "어떤 일이나 차이 없이 끈기있게 했는가?", "능률": "신속 정확하게 낭비 없이 처리 했는가?"},
            "업무의 질": {"정확성": "일의 결과를 믿을 수 있는가?", "성과": "일의 성과가 내용에 있어서 뛰어났는가?", "꼼꼼함": "철저하고 뒷처리를 잘하는가?"}
        },
        "2. 근무태도": {
            "협조성": {"횡적협조": "스스로 동료와 협력하며 조직체의 능률향상에 공헌하는가?", "존중": "팀 전체의 의견을 존중하는가?", "상사와외 협조": "상사에 대해 협력하며 성과가 있는가?"},
            "근무의욕": {"적극성": "일에 능동적으로 대처하려는 의욕은 어떤가?", "책임감": "책임을 회피하지 않으며 성실하게 일하려는 의욕은 어떤가?", "연구심": "넓고 깊게 일을 연구하려는 의욕은 어떤가?"},
            "복무상황": {"규율": "규칙 준수?", "DB화": "업무 데이터의 체계적인 관리", "근태상황": "지각/조퇴/결근 등"}
        },
        "3. 직무능력": {
            "지식": {"직무지식": "담당업무 지식이 깊은가?", "관련지식": "기초지식이 깊은가?"},
            "이해판단력": {"신속성": "이해 속도가 빠른가?", "타당성": "결론은 타당한가?", "문제해결": "해결을 주도하는가?", "통찰력": "요점을 파악하는가?"},
            "창의연구력": {"연구개선": "아이디어를 살리고 개선을 도모하는가?"},
            "표현절충": {"구두표현": "말하기 능력?", "문장표현": "글쓰기 능력?", "절충": "교섭 및 절충 능력?"}
        }
    }
}

LEADER_DATA = {
    "KO": {
        "리더십 역량": {
            "기본역량": {"고객지향": "고객 요구 적시 대응", "책임감": "계획적 목표 달성", "팀워크지향": "의견 공유 및 배경 설명"},
            "실행역량": {"개방적의사소통": "친밀감 형성", "문제해결": "근본원인 규명", "조직이해": "전략 파악", "프로젝트관리": "체계적 수립"},
            "전문역량": {"분석적사고": "필요 정보 파악", "세밀한업무처리": "규정/관행 조사"}
        }
    }
}

REPORT_UI = {"KO": {"q1": "1. 성과", "q2": "2. 습득 지식", "q3": "3. 인재 양성"}}

UI = {
    "KO": {"m1": "📝 자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드", "m5": "🚀 리더십 자기평가", "m6": "🎖️ 2차 리더십평가", "sub": "✅ 최종 제출", "save": "💾 임시 저장", "already": "✅ 최종 제출이 완료되었습니다.", "err": "⚠️ 근거를 상세히 작성해 주세요.", "report_title": "🚀 자기 성장 REPORT", "score": "점수", "basis": "근거 (상세히 작성)", "basis_msg": "※ 점수 산출 근거를 상세히 작성해 주세요", "target": "대상 선택", "self_info": "본인 입력", "done_msg": "저장되었습니다!"}
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
    st.session_state.update({'auth':False,'user':'','ldr':'N','lang':'KO'})

if db_raw is not None:
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System HR")
        n, p = st.text_input("Name"), st.text_input("PW", type="password")
        if st.button("Login"):
            u = db_raw[db_raw['성명'].str.strip() == n.strip()]
            if not u.empty and str(p) == str(u.iloc[0]['비밀번호']):
                st.session_state.update({'auth':True,'user':n.strip(),'ldr':str(u.iloc[0]['리더여부']).upper(),'lang':'KO'})
                st.rerun()
            else: st.error("Login Failed")
    else:
        L, user = UI["KO"], st.session_state.user
        res_df = conn.read(worksheet="Results", ttl=0).fillna("")
        ld_df = conn.read(worksheet="Leadership_Results", ttl=0).fillna("")

        m_list = []
        if user != "김용환":
            m_list.append(L["m1"])
            if st.session_state.ldr == 'Y': m_list.append(L["m5"])
        t2, t3 = db_raw[db_raw['2차평가자']==user]['성명'].tolist(), db_raw[db_raw['3차평가자']==user]['성명'].tolist()
        if t2: m_list += [L["m2"], L["m6"]]
        if t3: m_list.append(L["m3"])
        if user == "권정순": m_list.append(L["m4"])
        menu = st.sidebar.radio("Menu", m_list)

        def render_form(data_dict, pre, self_info=None, eval_type="자기", ws_name="Results", force_target=None):
            # [핵심 수정] 자기평가 메뉴(m1, m5)에서는 강제로 본인을 타겟으로 설정
            target = force_target if force_target else st.session_state.get('cur_target', user)
            check_df = res_df if ws_name == "Results" else ld_df
            
            existing = check_df[(check_df['평가자']==user) & (check_df['피평가자']==target)]
            is_final_done = not existing[existing['구분'].str.contains("Final|최종|자기", na=False)].empty
            draft_vals = existing[existing['구분'].str.contains("Draft", na=False)]

            if is_final_done:
                st.success(L["already"])
            else:
                if not draft_vals.empty: st.warning("⚠️ 임시 저장된 데이터를 불러왔습니다.")
                with st.form(key=f"f_{pre}_{target}"):
                    tabs = st.tabs(list(data_dict.keys()))
                    res_dict = {}
                    for i, (major, subs) in enumerate(data_dict.items()):
                        with tabs[i]:
                            for sub, items in subs.items():
                                st.markdown(f"#### 📍 {sub}")
                                for it, crit in items.items():
                                    saved = draft_vals[draft_vals['항목']==it]
                                    score_raw = saved.iloc[0]['점수'] if not saved.empty else 3
                                    basis_raw = saved.iloc[0]['근거'] if not saved.empty else ""
                                    init_score = int(score_raw) if str(score_raw).isdigit() else 3
                                    init_basis = str(basis_raw) if str(basis_raw).lower() != "nan" else ""

                                    c1, c2, c3, c4 = st.columns([2, 3, 1, 3])
                                    lbl = f"**{it}**"
                                    if self_info and it in self_info:
                                        s_v, b_v = self_info[it]['score'], self_info[it]['basis']
                                        lbl += f"<br><span style='color:blue; font-size:0.85em;'>[{L['self_info']}] {s_v}점</span>"
                                        if b_v and str(b_v).lower() != "nan":
                                            lbl += f"<br><span style='color:#0056b3; font-size:0.75em;'>ㄴ근거: {b_v}</span>"
                                    
                                    c1.markdown(lbl, unsafe_allow_html=True); c2.info(crit)
                                    s = c3.selectbox(L["score"], [1,2,3,4,5], index=init_score-1, key=f"s_{pre}_{target}_{it}")
                                    r = c4.text_input(L["basis"], value=init_basis, key=f"r_{pre}_{target}_{it}")
                                    res_dict[it] = {"score": s, "basis": r}
                    
                    rep_data = {}
                    if pre == "self":
                        st.divider(); st.subheader(L["report_title"])
                        for k, v in REPORT_UI["KO"].items():
                            saved_rep = existing[(existing['구분']=="리포트") & (existing['항목']==v)]
                            rep_raw = saved_rep.iloc[0]['근거'] if not saved_rep.empty else ""
                            rep_data[k] = st.text_area(v, value=str(rep_raw) if str(rep_raw).lower() != "nan" else "", key=f"rep_{k}")

                    c1, c2 = st.columns(2)
                    if c1.form_submit_button(L["save"]) or c2.form_submit_button(L["sub"]):
                        is_f = c2.form_submit_button(L["sub"])
                        if is_f and any(len(str(v["basis"]).strip()) < 2 for v in res_dict.values()): st.error(L["err"])
                        else:
                            now = (datetime.datetime.now()+timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                            stt = "Final" if is_f else "Draft"
                            recs = [{"시간":now,"평가자":user,"피평가자":target,"구분":f"자기({stt})","항목":k,"점수":v["score"],"근거":v["basis"]} for k,v in res_dict.items()]
                            if pre == "self":
                                for kq, vq in rep_data.items(): recs.append({"시간":now,"평가자":user,"피평가자":user,"구분":"리포트","항목":REPORT_UI["KO"][kq],"점수":"-","근거":vq})
                            if save_with_cleanup(recs, user, target, is_f, ws_name):
                                st.success(L["done_msg"]); st.cache_data.clear(); st.rerun()

        if menu == L["m1"]: render_form(EVAL_DATA["KO"], "self", force_target=user)
        elif menu == L["m5"]: render_form(LEADER_DATA["KO"], "ld", ws_name="Leadership_Results", force_target=user)
        elif menu in [L["m2"], L["m3"]]:
            ml = "2차" if menu == L["m2"] else "3차"
            target = st.selectbox(L["target"], t2 if ml=="2차" else t3)
            st.session_state['cur_target'] = target
            ts = res_df[(res_df['피평가자']==target)&(res_df['구분'].str.contains("자기", na=False))]
            if not ts.empty:
                si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ts.iterrows()}
                rd = res_df[(res_df['피평가자']==target)&(res_df['구분']=="리포트")]
                if not rd.empty:
                    with st.expander(f"📌 {target}님의 리포트 확인"):
                        for _, r in rd.iterrows(): st.markdown(f"**{r['항목']}**"); st.info(r['근거'])
                render_form(EVAL_DATA["KO"], f"ev_{target}", si, eval_type=ml)
        elif menu == L["m6"]:
            target = st.selectbox(L["target"], db_raw[(db_raw['2차평가자']==user)&(db_raw['리더여부']=='Y')]['성명'].tolist())
            st.session_state['cur_target'] = target
            ls = ld_df[(ld_df['피평가자']==target)&(ld_df['구분'].str.contains("자기", na=False))]
            si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ls.iterrows()} if not ls.empty else None
            render_form(LEADER_DATA["KO"], "ld2", si, eval_type="2차", ws_name="Leadership_Results")
        elif menu == L["m4"]:
            st.title("📊 Admin Dashboard")
            sel_u = st.selectbox("직원 선택", db_raw['성명'].tolist())
            new_pw = st.text_input("새 비밀번호", type="password")
            if st.button("비밀번호 변경"):
                db_raw.loc[db_raw['성명'] == sel_u, '비밀번호'] = new_pw
                conn.update(worksheet="Users", data=db_raw); st.success(f"{sel_u}님 변경 완료!")
            st.divider(); st.subheader("👥 직원 명단"); st.dataframe(db_raw)
