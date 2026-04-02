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

# --- [2] 정식 평가 데이터 (25개 일반 항목 + 9개 리더십 항목) ---
EVAL_DATA = {
    "KO": {
        "1. 업무실적": {
            "업무의 양": {"속도": "업무를 신속하게 처리하며 지체되는 일은 없었는가?", "지속성": "어떤 일이나 차이 없이 끈기있게 했는가?", "능률": "신속 정확하게 낭비 없이 처리 했는가?"},
            "업무의 질": {"정확성": "일의 결과를 믿을 수 있는가?", "성과": "일의 성과가 내용에 있어서 뛰어났는가?", "꼼꼼함": "철저하고 뒷처리를 잘하는가?"}
        },
        "2. 근무태도": {
            "협조성": {"횡적협조": "동료와 협력하며 조직 효율에 공헌하는가?", "존중": "팀 전체의 의견을 존중하는가?", "상사협조": "상사에 대해 협력하며 성과가 있는가?"},
            "근무의욕": {"적극성": "능동적 대처 의욕?", "책임감": "성실하게 일하려는 의욕?", "연구심": "깊게 연구하려는 의욕?"},
            "복무상황": {"규율": "규칙 준수 및 질서 유지?", "DB화": "업무 데이터의 체계적인 관리", "근태상황": "지각, 조퇴, 결근 상황 등"}
        },
        "3. 직무능력": {
            "지식": {"직무지식": "담당업무 지식이 깊은가?", "관련지식": "관련 기초지식이 넓은가?"},
            "이해판단력": {"신속성": "지시 이해 속도?", "타당성": "결론의 타당성?", "문제해결": "본질 파악 및 해결 주도?", "통찰력": "요점 파악 및 자적 결론?"},
            "창의연구력": { "연구개선": "아이디어 제안 및 개선 도모?" },
            "표현절충": {"구두표현": "말하기 능력?", "문장표현": "글쓰기 능력?", "절충": "교섭 능력?"}
        }
    },
    "EN": {
        "1. Performance": {
            "Quantity": {"Speed": "Quickly?", "Persistence": "Consistently?", "Efficiency": "Efficiently?"},
            "Quality": {"Accuracy": "Reliable?", "Achievement": "Outstanding?", "Thoroughness": "Follow-ups?"}
        },
        "2. Attitude": {
            "Cooperation": {"Horizontal": "Colleagues?", "Respect": "Team Opinions?", "Supervisor": "Supervisors?"},
            "Motivation": {"Proactive": "Active?", "Responsible": "Sincerity?", "Research": "Deep Study?"},
            "Compliance": {"Discipline": "Order?", "Data": "Data Mgmt?", "Attendance": "Tardiness?"}
        },
        "3. Competency": {
            "Knowledge": {"Job": "Deep?", "Related": "Basic?"},
            "Judgment": {"Speed": "Understanding?", "Validity": "Conclusion?", "Solving": "Essence?", "Insight": "Grasp?"},
            "Creativity": {"Improve": "Ideas?"},
            "Communication": {"Verbal": "Speaking?", "Written": "Writing?", "Negotiation": "Smooth?"}
        }
    }
}

LEADER_DATA = {
    "KO": {
        "리더십_항목": {
            "LD_고객지향": "내/외부 고객의 요구를 능동적으로 찾아내고 적시에 대응한다",
            "LD_책임감": "업무목표 달성을 위해 계획적으로 행동한다",
            "LD_팀워크지향": "의사결정 배경이나 당위성에 대해 설명한다"
        },
        "업무실적_항목": {
            "LD_개방적의사소통": "자신의 사적인 부분을 먼저 이야기하여 친밀감 형성",
            "LD_문제해결": "정보 분석을 통해 문제의 근본원인을 규명한다",
            "LD_조직이해": "조직 전략, 방식, 역사 등을 파악한다",
            "LD_프로젝트관리": "정보를 체계적으로 수집하여 계획을 수립한다"
        },
        "지식_항목": {
            "LD_분석적사고": "필요 정보가 무엇인지 정확히 파악한다",
            "LD_세밀한업무처리": "규정이나 과거 관행 등을 조사한다"
        }
    },
    "EN": {
        "Leadership": {
            "LD_Customer": "Respond to needs proactively.",
            "LD_Responsibility": "Act independently to achieve goals.",
            "LD_Teamwork": "Explain backgrounds for consensus."
        }
    }
}

UI = {
    "KO": {"m1": "📝 자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드", "m5": "🚀 리더십 자기평가", "sub": "✅ 최종 제출", "already": "✅ 제출 완료", "err": "⚠️ 모든 근거를 작성해 주세요.", "report": "🚀 자기 성장 REPORT", "score": "점수", "basis": "근거", "target": "평가 대상 선택", "pw_reset": "🔑 비밀번호 재설정"},
    "EN": {"m1": "📝 Self-Eval", "m2": "👥 2nd Eval", "m3": "⚖️ 3rd Final", "m4": "📊 Admin", "m5": "🚀 Leadership Eval", "sub": "✅ Submit", "already": "✅ Done", "err": "⚠️ Required.", "report": "🚀 Growth REPORT", "score": "Score", "basis": "Basis", "target": "Target", "pw_reset": "🔑 Reset PW"}
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

# --- [3] 메인 로직 ---
user_db = get_db("Users")
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'is_leader': 'N', 'lang': 'KO'})

if user_db is not None:
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System")
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
        
        # 메뉴 구성 자동 필터링
        m_list = [L["m1"]]
        if st.session_state.is_leader == 'Y': m_list.append(L["m5"])
        
        targets_2nd = user_db[user_db['2차평가자'] == user_name]['성명'].tolist()
        targets_3rd = user_db[user_db['3차평가자'] == user_name]['성명'].tolist()
        
        if targets_2nd: m_list.append(L["m2"])
        if targets_3rd: m_list.append(L["m3"])
        if user_name == "권정순": m_list.append(L["m4"])
        
        menu = st.sidebar.radio("Menu", m_list)

        def render_form(data_dict, pre, self_data=None):
            tabs = st.tabs([t.split('_')[0] for t in data_dict.keys()])
            res_dict = {}
            for i, major in enumerate(data_dict.keys()):
                with tabs[i]:
                    for sub, items in data_dict[major].items():
                        st.markdown(f"#### 📍 {sub.split('_')[-1]}")
                        if isinstance(items, dict):
                            for it, crit in items.items():
                                c1, c2, c3, c4 = st.columns([1.8, 2.7, 1, 3.5])
                                label = f"**{it}**"
                                if self_data and it in self_data:
                                    label += f"<br><span style='color:blue; font-size: 0.8em;'>[{L['score']}: {self_data[it]}]</span>"
                                c1.markdown(label, unsafe_allow_html=True)
                                c2.caption(crit)
                                score = c3.selectbox(L["score"], [1,2,3,4,5], key=f"{pre}_{it}_s")
                                basis = c4.text_input(L["basis"], key=f"{pre}_{it}_r")
                                res_dict[it] = {"score": score, "basis": basis, "category": sub}
                        else:
                            # 단일 항목 처리 (리더십 등)
                            c1, c2, c3, c4 = st.columns([1.8, 2.7, 1, 3.5])
                            it_name = sub.split('_')[-1]
                            label = f"**{it_name}**"
                            if self_data and it_name in self_data:
                                label += f"<br><span style='color:blue; font-size: 0.8em;'>[{L['score']}: {self_data[it_name]}]</span>"
                            c1.markdown(label, unsafe_allow_html=True)
                            c2.caption(items)
                            score = c3.selectbox(L["score"], [1,2,3,4,5], key=f"{pre}_{sub}_s")
                            basis = c4.text_input(L["basis"], key=f"{pre}_{sub}_r")
                            res_dict[it_name] = {"score": score, "basis": basis, "category": major}
            return res_dict

        # --- 2차 & 3차 평가 화면 ---
        if menu in [L["m2"], L["m3"]]:
            st.header(menu)
            mode = "2차" if menu == L["m2"] else "3차"
            targets = targets_2nd if mode == "2차" else targets_3rd
            selected_target = st.selectbox(L["target"], targets)
            
            res_df = conn.read(worksheet="Results", ttl=0)
            ld_df = conn.read(worksheet="Leadership_Results", ttl=0)
            
            # 피평가자 본인 점수 로드
            target_self = res_df[(res_df['피평가자'] == selected_target) & (res_df['구분'] == "자기")]
            if target_self.empty:
                st.warning(f"⚠️ {selected_target}님이 아직 평가를 제출하지 않았습니다.")
            else:
                self_scores = dict(zip(target_self['항목'], target_self['점수']))
                
                # 리포트(성과/역량/노력) 보여주기
                rep = res_df[(res_df['피평가자'] == selected_target) & (res_df['구분'] == "리포트")]
                if not rep.empty:
                    with st.expander(f"📌 {selected_target}'s Self-Report", expanded=True):
                        st.info(rep.iloc[0]['근거'])
                
                # 일반 평가 폼
                eval_res = render_form(EVAL_DATA[lang], f"eval_{mode}_{selected_target}", self_scores)
                
                if st.button(f"Submit {mode} Evaluation"):
                    now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                    recs = [{"시간": now, "평가자": user_name, "피평가자": selected_target, "구분": mode, "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                    if save_data(recs): st.success(f"{selected_target}님 평가 완료!"); st.balloons()

        # --- 자기고과 작성 ---
        elif menu == L["m1"]:
            st.header(L["m1"])
            eval_res = render_form(EVAL_DATA[lang], "self")
            st.subheader(L["report"])
            r1, r2, r3 = st.text_area("1. 성과 요약"), st.text_area("2. 역량 계획"), st.text_area("3. 제언")
            if st.button(L["sub"]):
                now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                recs = [{"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                recs.append({"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "리포트", "항목": "종합", "점수": "-", "근거": f"성과:{r1}\n역량:{r2}\n노력:{r3}"})
                if save_data(recs): st.success(L["already"]); st.balloons()

        # --- 리더십 자기평가 ---
        elif menu == L["m5"]:
            st.header(L["m5"])
            ld_res = render_form(LEADER_DATA[lang], "ldr_self")
            if st.button(L["sub"]):
                now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                recs = [{"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in ld_res.items()]
                if save_data(recs, "Leadership_Results"): st.success(L["already"]); st.balloons()

        # --- 관리자 대시보드 ---
        elif menu == L["m4"]:
            st.title(L["m4"])
            st.dataframe(user_db)
            st.divider(); st.subheader(L["pw_reset"])
            target = st.selectbox(L["target"], user_db['성명'].tolist())
            new_pw = st.text_input(L["pw_reset"], type="password")
            if st.button("Change Password"):
                idx = user_db[user_db['성명'] == target].index[0]
                user_db.at[idx, '비밀번호'] = new_pw
                if conn.update(worksheet="Users", data=user_db): st.success("Updated!"); st.rerun()
