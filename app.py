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

# --- [2] 평가 데이터 (일반 및 리더십 풀번역본 유지) ---
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
            "Quantity of Work": {"Speed": "Did you process work quickly?", "Persistence": "Consistently?", "Efficiency": "Without waste?"},
            "Quality of Work": {"Accuracy": "Reliable?", "Achievement": "Outstanding?", "Thoroughness": "Follow-ups?"}
        },
        "2. Work Attitude": {
            "Cooperation": {"Horizontal": "Cooperate with colleagues?", "Respect": "Team opinions?", "Supervisor": "Supervisors?"},
            "Motivation": {"Proactivity": "Proactive?", "Responsibility": "Sincerity?", "Research": "Deep study?"},
            "Compliance": {"Discipline": "Order?", "Data Mgmt": "Systematic data?", "Attendance": "Tardiness?"}
        },
        "3. Job Competency": {
            "Knowledge": {"Job Knowledge": "Deep?", "Related Knowledge": "Broad?"},
            "Judgment": {"Speed": "Understand fast?", "Validity": "Accurate conclusion?", "Problem Solving": "Lead solutions?", "Insight": "Grasp key points?"},
            "Creativity": {"Improvement": "Improve sequences?"},
            "Communication": {"Verbal": "Proficient verbal?", "Written": "Proficient writing?", "Negotiation": "Smoothly?"}
        }
    }
}

LEADER_DATA = {
    "KO": {
        "Leadership_리더십": {
            "LD_고객지향": "내부 혹은 외부 고객의 요구를 능동적으로 찾아내고 적시에 대응한다",
            "LD_책임감": "업무목표를 달성하기 위해 계획적으로 행동한다",
            "LD_팀워크지향": "공감을 얻기 위해 의견을 공유하고 배경을 설명한다"
        },
        "Performance_업무실적": {
            "LD_개방적의사소통": "친밀감을 위해 사적인 부분을 먼저 이야기한다",
            "LD_문제해결": "분석을 통해 문제의 근본원인을 규명한다",
            "LD_조직이해": "조직의 전략, 운영방식, 역사 등을 파악한다",
            "LD_프로젝트관리": "정보를 수집/분석하여 계획을 수립한다"
        },
        "Knowledge_지식": {
            "LD_분석적사고": "필요 정보/자료가 무엇인지 정확히 파악한다",
            "LD_세밀한업무처리": "규정이나 과거 관행 등을 조사한다"
        }
    },
    "EN": {
        "Leadership_Core": {
            "LD_Customer": "Actively identify and timely respond to customer needs.",
            "LD_Responsibility": "Act systematically to achieve goals.",
            "LD_Teamwork": "Share opinions and explain decision backgrounds."
        },
        "Leadership_Performance": {
            "LD_Communication": "Share personal aspects for rapport.",
            "LD_Problem Solving": "Identify root causes via analysis.",
            "LD_Org Insight": "Identify strategy and history.",
            "LD_Project Mgmt": "Establish plans via systematic analysis."
        },
        "Leadership_Knowledge": {
            "LD_Analytical": "Identify necessary info accurately.",
            "LD_Detailed": "Investigate regulations/practices."
        }
    }
}

UI = {
    "KO": {"m1": "📝 자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드", "m5": "🚀 리더십 자기평가", "m6": "🎖️ 2차 리더십평가", "sub": "✅ 최종 제출", "already": "✅ 이미 제출을 완료하셨습니다.", "report": "🚀 자기 성장 REPORT", "score": "점수", "basis": "근거", "target": "평가 대상 선택"},
    "EN": {"m1": "📝 Self-Eval", "m2": "👥 2nd Eval", "m3": "⚖️ 3rd Final", "m4": "📊 Admin", "m5": "🚀 Leadership Self-Eval", "m6": "🎖️ 2nd Leadership Eval", "sub": "✅ Submit", "already": "✅ You have already submitted.", "report": "🚀 Growth REPORT", "score": "Score", "basis": "Basis", "target": "Target"}
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
        st.title("🛡️ SRS HR System")
        name = st.text_input("성명")
        pw = st.text_input("비밀번호", type="password")
        if st.button("Login"):
            u = user_db[user_db['성명'] == name]
            if not u.empty and str(pw) == str(u.iloc[0]['비밀번호']):
                st.session_state.update({'auth':True,'user':name,'is_leader':str(u.iloc[0]['리더여부']).upper(),'lang':u.iloc[0]['언어'] if '언어' in u.columns else 'KO'})
                st.rerun()
    else:
        L, user_name, lang = UI[st.session_state.lang], st.session_state.user, st.session_state.lang
        res_df = conn.read(worksheet="Results", ttl=0)
        ld_df = conn.read(worksheet="Leadership_Results", ttl=0)

        # 메뉴 필터링
        m_list = [L["m1"]]
        if st.session_state.is_leader == 'Y': m_list.append(L["m5"])
        targets_2nd = user_db[user_db['2차평가자'] == user_name]['성명'].tolist()
        targets_3rd = user_db[user_db['3차평가자'] == user_name]['성명'].tolist()
        if targets_2nd: 
            m_list.append(L["m2"])
            m_list.append(L["m6"]) # 2차 리더십 평가 메뉴 추가
        if targets_3rd: m_list.append(L["m3"])
        if user_name == "권정순": m_list.append(L["m4"])
        menu = st.sidebar.radio("Menu", m_list)

        def render_form(data_dict, pre, self_data=None):
            res_dict = {}
            for major in data_dict.keys():
                with st.expander(f"📂 {major}", expanded=True):
                    for sub, items in data_dict[major].items():
                        st.markdown(f"**📍 {sub}**")
                        for it, crit in items.items():
                            c1, c2, c3, c4 = st.columns([1.5, 2.5, 1, 3.5])
                            label = f"**{it}**"
                            if self_data and it in self_data: label += f"<br><span style='color:blue;'>[{self_data[it]}]</span>"
                            c1.markdown(label, unsafe_allow_html=True)
                            c2.caption(crit)
                            score = c3.selectbox(L["score"], [1,2,3,4,5], key=f"{pre}_{it}_s")
                            basis = c4.text_input(L["basis"], key=f"{pre}_{it}_r")
                            res_dict[it] = {"score": score, "basis": basis, "category": sub}
            return res_dict

        # --- [자기고과 작성] 중복 방지 로직 적용 ---
        if menu == L["m1"]:
            st.header(L["m1"])
            if res_df is not None and not res_df[(res_df['피평가자'] == user_name) & (res_df['구분'] == "자기")].empty:
                st.info(L["already"])
            else:
                eval_res = render_form(EVAL_DATA[lang], "self")
                st.subheader(L["report"])
                r1, r2, r3 = st.text_area("성과"), st.text_area("역량"), st.text_area("제언")
                if st.button(L["sub"]):
                    now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                    recs = [{"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                    recs.append({"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "리포트", "항목": "종합", "점수": "-", "근거": f"성과:{r1}\n역량:{r2}\n노력:{r3}"})
                    if save_data(recs): st.success("제출 완료!"); st.rerun()

        # --- [2차 리더십 평가] ---
        elif menu == L["m6"]:
            st.header(L["m6"])
            # 2차 평가 대상 중 '리더'인 사람만 필터링 (이사님이 평가할 리더 목록)
            leader_targets = user_db[(user_db['2차평가자'] == user_name) & (user_db['리더여부'] == 'Y')]['성명'].tolist()
            if not leader_targets:
                st.warning("평가할 리더 대상이 없습니다.")
            else:
                target = st.selectbox("리더 선택", leader_targets)
                # 대상 리더의 자기 리더십 평가 점수 로드
                target_ld_self = ld_df[(ld_df['피평가자'] == target) & (ld_df['구분'] == "자기")]
                self_ld_scores = dict(zip(target_ld_self['항목'], target_ld_self['점수'])) if not target_ld_self.empty else None
                
                ld_eval_res = render_form(LEADER_DATA[lang], f"ld_2nd_{target}", self_ld_scores)
                if st.button(f"{target}님 리더십 평가 제출"):
                    now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                    recs = [{"시간": now, "평가자": user_name, "피평가자": target, "구분": "2차", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in ld_eval_res.items()]
                    if save_data(recs, "Leadership_Results"): st.success("리더십 평가 완료!"); st.balloons()

        # --- [리더십 자기평가] 중복 방지 ---
        elif menu == L["m5"]:
            st.header(L["m5"])
            if ld_df is not None and not ld_df[(ld_df['피평가자'] == user_name) & (ld_df['구분'] == "자기")].empty:
                st.info(L["already"])
            else:
                ld_res = render_form(LEADER_DATA[lang], "ld_self")
                if st.button(L["sub"]):
                    now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                    recs = [{"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in ld_res.items()]
                    if save_data(recs, "Leadership_Results"): st.success("제출 완료!"); st.rerun()

        # --- [2차/3차 팀원평가] ---
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
                if st.button(f"{mode} 평가 제출"):
                    now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                    recs = [{"시간": now, "평가자": user_name, "피평가자": selected, "구분": mode, "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                    if save_data(recs): st.success("완료!"); st.balloons()

        # --- [관리자] ---
        elif menu == L["m4"]:
            st.title("Admin")
            st.dataframe(user_db)
