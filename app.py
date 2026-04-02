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

# --- [2] 일반 평가 데이터 (25항목) ---
EVAL_DATA = {
    "KO": {
        "1. 업무실적": {
            "Quantity_업무의 양": {"Speed": "업무를 신속하게 처리하며 지체되는 일은 없었는가?", "Persistence": "어떤 일이나 차이 없이 끈기있게 했는가?", "Efficiency": "신속 정확하게 낭비 없이 처리 했는가?"},
            "Quality_업무의 질": {"Accuracy": "일의 결과를 믿을 수 있는가?", "Achievement": "일의 성과가 내용에 있어서 뛰어났는가?", "Thoroughness": "철저하고 뒷처리를 잘하는가?"}
        },
        "2. 근무태도": {
            "Cooperation_협조성": {"Horizontal": "동료와 협력하며 조직 효율에 공헌하는가?", "Respect": "팀 전체의 의견을 존중하는가?", "Supervisor": "상사에 대해 협력하며 성과가 있는가?"},
            "Motivation_근무의욕": {"Proactive": "일에 능동적으로 대처하려는 의욕은 어떤가?", "Responsible": "성실하게 일하려는 의욕은 어떤가?", "Research": "넓고 깊게 일을 연구하려는 의욕은 어떤가?"},
            "Compliance_복무상황": {"Discipline": "규칙 준수 및 질서 유지?", "Data": "업무 데이터의 체계적인 관리", "Attendance": "지각, 조퇴, 결근 상황 등"}
        },
        "3. 직무능력": {
            "Knowledge_지식": {"Job": "담당업무 지식이 깊은가?", "Related": "관련 기초지식이 넓은가?"},
            "Judgment_이해판단력": {"Speed": "지시 이해 속도?", "Validity": "결론의 타당성?", "Problem Solving": "본질 파악 및 해결 주도?", "Insight": "요점 파악 및 자적 결론?"},
            "Creativity_창의연구력": { "Improve": "아이디어를 살리고 일의 전진을 도모하는가?" },
            "Communication_표현절충": {"Verbal": "말하기 능력?", "Written": "글쓰기 능력?", "Negotiation": "교섭 능력?"}
        }
    },
    "EN": {
        "1. Performance": {
            "Quantity": {"Speed": "Processed quickly?", "Persistence": "Worked consistently?", "Efficiency": "Processed efficiently?"},
            "Quality": {"Accuracy": "Reliable results?", "Achievement": "Outstanding performance?", "Thoroughness": "Thorough follow-ups?"}
        },
        "2. Attitude": {
            "Cooperation": {"Horizontal": "Cooperated with colleagues?", "Respect": "Respected team opinions?", "Supervisor": "Cooperated with supervisors?"},
            "Motivation": {"Proactive": "Active attitude?", "Responsible": "Sincere responsibility?", "Research": "Deep study?"},
            "Compliance": {"Discipline": "Followed rules?", "Data": "Systematic data management?", "Attendance": "Tardiness status?"}
        },
        "3. Competency": {
            "Knowledge": {"Job": "Broad knowledge?", "Related": "Basic knowledge?"},
            "Judgment": {"Speed": "Understanding speed?", "Validity": "Accurate conclusions?", "Solving": "Identifying root causes?", "Insight": "Independent judgment?"},
            "Creativity": {"Improve": "Improving sequences?"},
            "Communication": {"Verbal": "Clear verbal?", "Written": "Clear writing?", "Negotiation": "Smooth negotiation?"}
        }
    }
}

# --- [3] 리더십 평가 데이터 (9항목 - 구조 통일) ---
LEADER_DATA = {
    "KO": {
        "Leadership_리더십": {
            "Core_기본": {
                "LD_고객지향": "내부 혹은 외부 고객의 요구를 능동적으로 찾아내고 적시에 대응한다",
                "LD_책임감": "업무목표를 달성하기 위해 계획적으로 행동한다",
                "LD_팀워크지향": "구성원의 공감을 얻기 위해 자주 의견을 공유하고 배경을 설명한다"
            }
        },
        "Performance_업무실적": {
            "Work_실행": {
                "LD_개방적의사소통": "상대방이 친밀감을 느낄 수 있도록 자신의 사적인 부분을 먼저 이야기한다",
                "LD_문제해결": "문제 발생 시 정보와 자료를 분석하여 문제의 근본원인을 규명한다",
                "LD_조직이해": "조직의 전략, 운영방식, 역사 등을 파악한다",
                "LD_프로젝트관리": "프로젝트와 관련된 정보를 체계적으로 수집하여 계획을 수립한다"
            }
        },
        "Knowledge_지식": {
            "Mind_역량": {
                "LD_분석적사고": "문제를 해결하기 위해 필요한 정보나 자료가 무엇인지 정확히 파악한다",
                "LD_세밀한업무처리": "문제 발생 소지를 최소화하기 위해 관련 규정이나 과거 관행 등을 조사한다"
            }
        }
    },
    "EN": {
        "Leadership_Core": {
            "Basic_Items": {
                "LD_Customer": "Actively identify and timely respond to customer needs.",
                "LD_Responsibility": "Act systematically to achieve work goals.",
                "LD_Teamwork": "Share opinions frequently and explain decision backgrounds."
            }
        }
    }
}

UI = {
    "KO": {"m1": "📝 자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드", "m5": "🚀 리더십 자기평가", "m6": "🎖️ 2차 리더십평가", "sub": "✅ 최종 제출", "already": "✅ 제출 완료", "err": "⚠️ 모든 근거를 작성해 주세요.", "report": "🚀 자기 성장 REPORT", "score": "점수", "basis": "근거", "target": "평가 대상 선택", "pw_reset": "🔑 비밀번호 재설정"},
    "EN": {"m1": "📝 Self-Eval", "m2": "👥 2nd Eval", "m3": "⚖️ 3rd Final", "m4": "📊 Admin", "m5": "🚀 Leadership Self-Eval", "m6": "🎖️ 2nd Leadership Eval", "sub": "✅ Submit", "already": "✅ Done", "err": "⚠️ All fields required.", "report": "🚀 Growth REPORT", "score": "Score", "basis": "Basis", "target": "Target", "pw_reset": "🔑 Reset PW"}
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
        st.title("🛡️ SRS HR System")
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

        # 메뉴 구성
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

        def render_form(data_dict, pre, self_data=None):
            tabs = st.tabs([t.split('_')[-1] for t in data_dict.keys()])
            res_dict = {}
            for i, major in enumerate(data_dict.keys()):
                with tabs[i]:
                    for sub, items in data_dict[major].items():
                        st.markdown(f"#### 📍 {sub.split('_')[-1]}")
                        for it, crit in items.items():
                            c1, c2, c3, c4 = st.columns([1.8, 2.7, 1, 3.5])
                            it_label = it.split('_')[-1]
                            label = f"**{it_label}**"
                            if self_data and it in self_data:
                                label += f"<br><span style='color:blue; font-size: 0.8em;'>[{L['score']}: {self_data[it]}]</span>"
                            c1.markdown(label, unsafe_allow_html=True)
                            c2.caption(crit)
                            score = c3.selectbox(L["score"], [1,2,3,4,5], key=f"{pre}_{it}_s")
                            basis = c4.text_input(L["basis"], key=f"{pre}_{it}_r")
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
                r1, r2, r3 = st.text_area("1. Achievement Summary"), st.text_area("2. Competency Plan"), st.text_area("3. Suggestions")
                if st.button(L["sub"]):
                    now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                    recs = [{"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                    recs.append({"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "리포트", "항목": "종합", "점수": "-", "근거": f"성과:{r1}\n역량:{r2}\n노력:{r3}"})
                    if save_data(recs): st.success(L["already"]); st.rerun()

        # 5. 리더십 자기평가
        elif menu == L["m5"]:
            st.header(L["m5"])
            if ld_df is not None and not ld_df[(ld_df['피평가자'] == user_name) & (ld_df['구분'] == "자기")].empty:
                st.success(L["already"])
            else:
                eval_res = render_form(LEADER_DATA[lang], "ld_self")
                if st.button(L["sub"]):
                    now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                    recs = [{"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                    if save_data(recs, "Leadership_Results"): st.success(L["already"]); st.rerun()

        # 6. 2차 리더십 평가
        elif menu == L["m6"]:
            st.header(L["m6"])
            ldr_targets = user_db[(user_db['2차평가자'] == user_name) & (user_db['리더여부'] == 'Y')]['성명'].tolist()
            if not ldr_targets: st.warning("평가할 리더 대상이 없습니다.")
            else:
                target = st.selectbox(L["target"], ldr_targets)
                target_self = ld_df[(ld_df['피평가자'] == target) & (ld_df['구분'] == "자기")]
                self_ld_scores = dict(zip(target_self['항목'], target_self['점수']))
                eval_res = render_form(LEADER_DATA[lang], f"ld_2nd_{target}", self_ld_scores)
                if st.button(f"Submit Evaluation for {target}"):
                    now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                    recs = [{"시간": now, "평가자": user_name, "피평가자": target, "구분": "2차", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                    if save_data(recs, "Leadership_Results"): st.success("평가 완료!"); st.balloons()

        # 2차/3차 팀원평가
        elif menu in [L["m2"], L["m3"]]:
            st.header(menu)
            mode = "2차" if menu == L["m2"] else "3차"
            targets = targets_2nd if mode == "2차" else targets_3rd
            selected = st.selectbox(L["target"], targets)
            target_self = res_df[(res_df['피평가자'] == selected) & (res_df['구분'] == "자기")]
            if target_self.empty: st.warning("대상이 아직 제출 전입니다.")
            else:
                self_scores = dict(zip(target_self['항목'], target_self['점수']))
                eval_res = render_form(EVAL_DATA[lang], f"eval_{mode}_{selected}", self_scores)
                if st.button(f"Submit {mode} Evaluation"):
                    now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                    recs = [{"시간": now, "평가자": user_name, "피평가자": selected, "구분": mode, "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                    if save_data(recs): st.success("완료!"); st.balloons()

        # 대시보드
        elif menu == L["m4"]:
            st.title("Dashboard")
            st.dataframe(user_db)
