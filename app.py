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

# --- [2] 평가 데이터 (무삭제 상세 지표) ---
EVAL_DATA = {
    "KO": {
        "1. 업무실적": {
            "업무의 양": {"속도": "업무를 신속하게 처리하며 지체되는 일은 없었는가?", "지속성": "어떤 일이나 차이 없이 끈기있게 했는가?", "능률": "신속 정확하게 낭비 없이 처리 했는가?"},
            "업무의 질": {"정확성": "일의 결과를 믿을 수 있는가?", "성과": "일의 성과가 내용에 있어서 뛰어났는가?", "꼼꼼함": "철저하고 뒷처리를 잘하는가?"}
        },
        "2. 근무태도": {
            "협조성": {"횡적협조": "스스로 동료와 협력하며 조직체의 능률향상에 공헌하는가?", "존중": "자신의 생각보다는 팀(동료) 전체의 의견을 존중하는가?", "상사와외 협조": "상사에 대해 협력하며 성과가 있는가?"},
            "근무의욕": {"적극성": "일에 능동적으로 대처하려는 의욕은 어떤가?", "책임감": "책임을 회피하지 않으며 성실하게 일하려는 의욕은 어떤가?", "연구심": "넓고 깊게 일을 연구하려는 의욕은 어떤가?"},
            "복무상황": {"규율": "규칙을 준수하며 직장질서유지에 애쓰는가?", "DB화": "정기적인 업무보고와 본인업무에 대한 데이터의 체계적인 관리", "근태상황": "지각, 조퇴, 결근 등 상황은 어떤가?"}
        },
        "3. 직무능력": {
            "지식": {"직무지식": "담당업무의 지식이 넓고 깊은가?", "관련지식": "관련업무에 대한 기초지식은 넓고 깊은가?"},
            "이해판단력": {"신속성": "규정, 자료 등을 바르게 이해하는 속도는 어떤가?", "타당성": "내린 결론은 정확하며 타당한가?", "문제해결": "문제 발생 시 본질을 파악하여 해결을 주도하는가?", "통찰력": "사물의 요점을 파악하며 자주적으로 결론을 내리는가?"},
            "창의연구력": {"연구개선": "항상 창의적인 아이디어를 살리고 일의 개선을 도모하는가?"},
            "표현절충": {"구두표현": "구두 표현이 능숙하며 정확한가?", "문장표현": "문장 표현이 능숙하며 정확한가?", "절충": "대내외 관계자들과의 원활한 교섭 능력은?"}
        }
    }
}

LEADER_DATA = {
    "KO": {
        "1. 리더십(기본역량)": {"고객지향": "내외부 고객의 요구를 능동적으로 찾아내고 적시에 대응한다", "책임감": "업무목표를 달성하기 위해 계획적으로 행동한다.", "팀워크지향": "구성원의 공감을 얻기 위해 자주 의견을 공유하고 설명한다."},
        "2. 업무실적(실행역량)": {"개방적 의사소통": "상대방이 친밀감을 느낄 수 있도록 사적인 부분을 이야기한다.", "문제해결": "문제상황과 관련된 정보와 자료를 수집/분석하여 근본원인을 규명한다.", "조직이해": "조직의 전략, 운영방식, 역사 등을 파악한다.", "프로젝트 관리": "프로젝트 관련 정보를 체계적으로 수집/분석하여 계획을 수립한다."},
        "3. 지식(전문역량)": {"분석적사고": "문제를 해결하기 위해 필요한 정보나 자료를 정확히 파악한다.", "세밀한업무처리": "관련 규정이나 과거 관행 등을 조사하여 문제 소지를 최소화한다."}
    }
}

REPORT_UI = {
    "KO": {"q1": "1. 평가 기간동안 내가 낸 성과는 무엇입니까?", "q2": "2. 평가 기간동안 내가 습득한 지식이 무엇입니까?", "q3": "3. 평가 기간동안 내가 인재 양성을 위하여 무엇을 하였습니까?"}
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
        "dash_title": "🔍 내가 평가한 직원 점수 요약", "dash_desc": "평가하신 내역을 한눈에 확인하여 상대평가의 적절성을 검토하시기 바랍니다.",
        "contact_admin": f"💡 수정이 필요한 경우 관리자({ADMIN_INFO})에게 연락해 주세요."
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
                    st.session_state.update({'auth':True, 'user':n.strip(), 'ldr':str(u.iloc[0]['리더여부']).upper(), 'lang': 'KO'})
                    if stored_pw == INITIAL_PW: st.session_state.need_pw_change = True
                    st.rerun()
                else: st.error("Password Incorrect")
            else: st.error("User Not Found")
            
    elif st.session_state.need_pw_change:
        L = UI["KO"]
        st.title(L["pw_change"])
        with st.form("pw_change_form"):
            new_p = st.text_input("New Password", type="password")
            confirm_p = st.text_input("Confirm New Password", type="password")
            if st.form_submit_button("Change and Start"):
                if len(new_p) < 6: st.error("보안을 위해 6자리 이상으로 설정해 주세요.")
                elif new_p == INITIAL_PW: st.error("초기 비밀번호와 다르게 설정해야 합니다.")
                elif new_p != confirm_p: st.error("비밀번호가 일치하지 않습니다.")
                else:
                    db_full = conn.read(worksheet="Users", ttl=0)
                    db_full.loc[db_full['성명'] == st.session_state.user, '비밀번호'] = str(new_p)
                    conn.update(worksheet="Users", data=db_full)
                    st.session_state.need_pw_change = False
                    st.cache_data.clear(); st.success("비밀번호 변경 완료!"); time.sleep(1); st.rerun()

    else:
        L, user = UI["KO"], st.session_state.user
        res_df = get_data_cached("Results")
        ld_df = get_data_cached("Leadership_Results")

        # 메뉴 리스트 생성
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
                    form_id = f"f_final_full_dash_{pre}_{eval_type}_{target_name}_{ws_name}"
                    with st.form(key=form_id):
                        tabs = st.tabs(list(data_dict.keys()))
                        res_dict = {}
                        for i, (major, subs) in enumerate(data_dict.items()):
                            with tabs[i]:
                                if is_3rd:
                                    st.subheader(f"🔍 {major} Review")
                                    for sub_n, sub_items in subs.items():
                                        # 리더십 데이터는 서브가 없으므로 체크
                                        item_iterator = sub_items.items() if isinstance(sub_items, dict) else {sub_n: sub_items}.items()
                                        for it_n, crit in item_iterator:
                                            info = self_info.get(it_n, {"score": "-", "basis": ""}) if self_info else {"score": "-", "basis": ""}
                                            st.markdown(f"**{it_n}**: {info['score']} | {info['basis']}")
                                    st.divider()
                                    c1, c2 = st.columns([1, 3])
                                    s = c1.selectbox(L["score"], [1,2,3,4,5], index=2, key=f"s3_{target_name}_{major}_{form_id}")
                                    r = c2.text_area(L["basis"], key=f"r3_{target_name}_{major}_{form_id}")
                                    res_dict[major] = {"score": s, "basis": r}
                                else:
                                    sub_iterator = subs.items() if isinstance(subs, dict) else {major: subs}.items()
                                    for sub, items in sub_iterator:
                                        if isinstance(items, dict):
                                            st.markdown(f"#### 📍 {sub}")
                                            for it, crit in items.items():
                                                saved = draft_vals[draft_vals['항목']==it] if not draft_vals.empty else pd.DataFrame()
                                                score_raw = saved.iloc[0]['점수'] if not saved.empty else 3
                                                try: init_score = int(float(score_raw))
                                                except: init_score = 3
                                                init_basis = str(saved.iloc[0]['근거']) if not saved.empty else ""
                                                c1, c2, c3, c4 = st.columns([2, 3, 1, 3])
                                                lbl = f"**{it}**"
                                                if self_info and it in self_info: lbl += f"<br><span style='color:blue; font-size:0.85em;'>[{L['self_info']}] {self_info[it]['score']}</span>"
                                                c1.markdown(lbl, unsafe_allow_html=True); c2.info(crit)
                                                s = c3.selectbox(L["score"], [1,2,3,4,5], index=max(0, min(4, init_score-1)), key=f"s_{target_name}_{it}_{form_id}")
                                                r = c4.text_input(L["basis"], value=init_basis, placeholder=L["basis_msg"], key=f"r_{target_name}_{it}_{form_id}")
                                                res_dict[it] = {"score": s, "basis": r}
                                        else: # 리더십 단일 항목 케이스
                                            saved = draft_vals[draft_vals['항목']==sub] if not draft_vals.empty else pd.DataFrame()
                                            score_raw = saved.iloc[0]['점수'] if not saved.empty else 3
                                            try: init_score = int(float(score_raw))
                                            except: init_score = 3
                                            init_basis = str(saved.iloc[0]['근거']) if not saved.empty else ""
                                            c1, c2, c3, c4 = st.columns([2, 3, 1, 3])
                                            lbl = f"**{sub}**"
                                            if self_info and sub in self_info: lbl += f"<br><span style='color:blue; font-size:0.85em;'>[{L['self_info']}] {self_info[sub]['score']}</span>"
                                            c1.markdown(lbl, unsafe_allow_html=True); c2.info(items)
                                            s = c3.selectbox(L["score"], [1,2,3,4,5], index=max(0, min(4, init_score-1)), key=f"s_{target_name}_{sub}_{form_id}")
                                            r = c4.text_input(L["basis"], value=init_basis, placeholder=L["basis_msg"], key=f"r_{target_name}_{sub}_{form_id}")
                                            res_dict[sub] = {"score": s, "basis": r}

                        if pre == "self":
                            st.divider(); st.subheader(L["report_title"])
                            rep_data = {}
                            for k, v in REPORT_UI["KO"].items():
                                saved_rep = existing[(existing['구분']=="리포트") & (existing['항목']==v)] if not existing.empty else pd.DataFrame()
                                rep_data[k] = st.text_area(v, value=str(saved_rep.iloc[0]['근거']) if not saved_rep.empty else "", key=f"rep_{k}_{target_name}_{form_id}")

                        bc1, bc2 = st.columns(2)
                        if bc1.form_submit_button(L["save"]):
                            now = (datetime.datetime.now()+timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                            recs = [{"시간":now,"평가자":user,"피평가자":target_name,"구분":f"{eval_type}(Draft)","항목":k if not is_3rd else f"[{k}] 종합","점수":v["score"],"근거":v["basis"]} for k,v in res_dict.items()]
                            if pre == "self":
                                for kq, vq in rep_data.items(): recs.append({"시간":now,"평가자":user,"피평가자":user,"구분":"리포트","항목":REPORT_UI["KO"][kq],"점수":"-","근거":vq})
                            if save_with_cleanup(recs, user, target_name, False, ws_name): st.success(L["done_msg"]); st.cache_data.clear(); st.rerun()
                        
                        if bc2.form_submit_button(L["sub"]):
                            if any(len(str(v["basis"]).strip()) < 2 for v in res_dict.values()): st.error(L["err"])
                            else:
                                now = (datetime.datetime.now()+timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                                recs = [{"시간":now,"평가자":user,"피평가자":target_name,"구분":f"{eval_type}(Final)","항목":k if not is_3rd else f"[{k}] 종합","점수":v["score"],"근거":v["basis"]} for k,v in res_dict.items()]
                                if pre == "self":
                                    for kq, vq in rep_data.items(): recs.append({"시간":now,"평가자":user,"피평가자":user,"구분":"리포트","항목":REPORT_UI["KO"][kq],"점수":"-","근거":vq})
                                if save_with_cleanup(recs, user, target_name, True, ws_name): st.success(L["done_msg"]); st.cache_data.clear(); st.rerun()
            except Exception as e: st.error(f"⚠️ 처리 오류: {str(e)}")

        # --- [신규: 2차 팀원평가 세부 대시보드] ---
        if menu == L["m8"]:
            st.title(L["m8"])
            st.markdown(L["dash_desc"])
            my_evals = res_df[(res_df['평가자']==user) & (res_df['구분'].str.contains("2차"))]
            if my_evals.empty: st.warning("아직 제출된 평가 내역이 없습니다.")
            else:
                # 피벗 테이블 생성
                pivot = my_evals.pivot_table(index='피평가자', columns='항목', values='점수', aggfunc='first').fillna(0)
                for col in pivot.columns: pivot[col] = pd.to_numeric(pivot[col], errors='coerce').fillna(0)
                
                # [이사님 요청] 업무의 양/질 15점 만점 계산
                if all(c in pivot.columns for c in ["속도", "지속성", "능률"]):
                    pivot["업무의 양 (합계/15)"] = pivot["속도"] + pivot["지속성"] + pivot["능률"]
                if all(c in pivot.columns for c in ["정확성", "성과", "꼼꼼함"]):
                    pivot["업무의 질 (합계/15)"] = pivot["정확성"] + pivot["성과"] + pivot["꼼꼼함"]
                
                # 컬럼 순서 정리 (중요 항목 우선 배치)
                main_cols = ["업무의 양 (합계/15)", "업무의 질 (합계/15)"]
                other_cols = [c for c in pivot.columns if c not in main_cols]
                st.dataframe(pivot[main_cols + other_cols], use_container_width=True)
                st.divider(); st.warning(L["contact_admin"])

        # --- [신규: 2차 리더십평가 세부 대시보드] ---
        elif menu == L["m9"]:
            st.title(L["m9"])
            st.markdown(L["dash_desc"])
            my_evals_ld = ld_df[(ld_df['평가자']==user) & (ld_df['구분'].str.contains("2차"))]
            if my_evals_ld.empty: st.warning("아직 제출된 리더십 평가 내역이 없습니다.")
            else:
                pivot_ld = my_evals_ld.pivot_table(index='피평가자', columns='항목', values='점수', aggfunc='first').fillna(0)
                st.dataframe(pivot_ld, use_container_width=True)
                st.divider(); st.warning(L["contact_admin"])

        elif menu == L["m1"]: render_form(EVAL_DATA["KO"], "self", target_name=user)
        elif menu == L["m5"]: render_form(LEADER_DATA["KO"], "ld_self", ws_name="Leadership_Results", target_name=user)
        elif menu == L["m2"]:
            target = st.selectbox(L["target"], t2_list, key="sel_m2_f")
            if target and not res_df.empty:
                ts = res_df[(res_df['피평가자']==target)&(res_df['구분'].str.contains("자기", na=False))]
                if ts.empty: st.warning(f"⚠️ {target}님이 아직 자기고과를 제출하지 않았습니다.")
                else:
                    si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ts.iterrows()}
                    render_form(EVAL_DATA["KO"], "ev2", si, eval_type="2차", target_name=target)
        elif menu == L["m6"]:
            target_ldr = st.selectbox(L["target"], ldr_t2_list, key="sel_m6_f")
            if target_ldr and not ld_df.empty:
                ls = ld_df[(ld_df['피평가자']==target_ldr)&(ld_df['구분'].str.contains("자기", na=False))]
                if ls.empty: st.warning(f"⚠️ {target_ldr}님이 아직 리더십 자기평가를 제출하지 않았습니다.")
                else:
                    si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ls.iterrows()}
                    render_form(LEADER_DATA["KO"], "ld2", si, eval_type="2차", ws_name="Leadership_Results", target_name=target_ldr)
        elif menu == L["m3"]:
            target = st.selectbox(L["target"], t3_list, key="sel_m3_f")
            if target and not res_df.empty:
                ts = res_df[(res_df['피평가자']==target)&(res_df['구분'].str.contains("자기", na=False))]
                if ts.empty: st.warning("⚠️ Waiting for self-evaluation...")
                else:
                    si = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ts.iterrows()}
                    render_form(EVAL_DATA["KO"], "ev3", si, eval_type="3차", is_3rd=True, target_name=target)
        elif menu == L["m7"]:
            target_ldr3 = st.selectbox(L["target"], ldr_t3_list, key="sel_m7_f")
            if target_ldr3 and not ld_df.empty:
                ls3 = ld_df[(ld_df['피평가자']==target_ldr3)&(ld_df['구분'].str.contains("자기", na=False))]
                if ls3.empty: st.warning("⚠️ Waiting for leadership self-eval...")
                else:
                    si3 = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in ls3.iterrows()}
                    render_form(LEADER_DATA["KO"], "ld3", si3, eval_type="3차", ws_name="Leadership_Results", is_3rd=True, target_name=target_ldr3)
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
            sel_u = st.selectbox("Employee", db_raw['성명'].tolist(), key="admin_sel")
            new_pw = st.text_input("New PW", type="password", key="admin_pw")
            if st.button("Update PW"):
                db_full = conn.read(worksheet="Users", ttl=0)
                db_full.loc[db_full['성명'] == sel_u, '비밀번호'] = str(new_pw)
                conn.update(worksheet="Users", data=db_full); st.success("Updated!"); st.cache_data.clear()
