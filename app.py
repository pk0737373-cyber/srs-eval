import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import plotly.express as px
import plotly.graph_objects as go

# --- [1] 기본 설정 ---
st.set_page_config(page_title="SRS HR System", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db(sheet_name="Users"):
    try: return conn.read(worksheet=sheet_name, ttl=0)
    except: return None

# --- [2] 데이터 정의 (요약본이 아닌 무삭제본) ---
EVAL_DATA = {
    "KO": {
        "1. 업무실적": {
            "업무의 양": {"속도": "업무를 신속하게 처리하며 지체되는 일은 없었는가?", "지속성": "어떤 일이나 차이 없이 끈기있게 했는가?", "능률": "신속 정확하게 낭비 없이 처리 했는가?"},
            "업무의 질": {"정확성": "일의 결과를 믿을 수 있는가?", "성과": "일의 성과가 내용에 있어서 뛰어났는가?", "꼼꼼함": "철저하고 뒷처리를 잘하는가?"}
        },
        "2. 근무태도": {
            "협조성": {"횡적협조": "스스로 동료와 협력하며 조직체의 능률향상에 공헌하는가?", "존중": "자신의 생각보다는 팀(동료) 전체의 의견을 존중하는가?", "상사와의 협조": "상사에 대해 협력하며 성과가 있는가?"},
            "근무의욕": {"적극성": "일에 능동적으로 대처하려는 의욕은 어떤가?", "책임감": "책임을 회피하지 않으며 성실하게 일하려는 의욕은 어떤가?", "연구심": "넓고 깊게 일을 연구하려는 의욕은 어떤가?"},
            "복무상황": {"규율": "규칙을 준수하며 직장질서유지에 애쓰는가?", "DB화": "정기적인 업무보고와 본인업무에 대한 데이터의 체계적인 관리", "근태상황": "지각, 조퇴, 결근 등 상황은 어떤가?"}
        },
        "3. 직무능력": {
            "지식": {"직무지식": "담당업무의 지식이 넓고 깊은가?", "관련지식": "관련업무에 대한 기초지식은 넓고 깊은가?"},
            "이해판단력": {"신속성": "규정, 지시, 자료 등을 바르게 이해하는 속도는 어떤가?", "타당성": "내린 결론은 정확하며 타당한가?", "문제해결": "문제 발생 시 본질을 파악하여 효과적인 해결을 주도하는가?", "통찰력": "사물의 요점을 파악하며 자주적으로 결론을 내릴 수 있는가?"},
            "창의연구력": {"연구개선": "아이디어를 살리고 일의 순서개선이나 전진을 도모하는가?"},
            "표현절충": {"구두표현": "구두 표현이 능숙하며 알기 쉽고 정확한가?", "문장표현": "문장 표현이 능숙하며 알기 쉽고 정확한가?", "절충": "교섭을 원활하게 처리하는 능력은 어떤가?"}
        }
    },
    "EN": {
        "1. Performance": {
            "Quantity": {"Speed": "Quickly?", "Persistence": "Consistently?", "Efficiency": "Efficiently?"},
            "Quality": {"Accuracy": "Reliable?", "Achievement": "Outstanding?", "Thoroughness": "Follow-ups?"}
        },
        "2. Work Attitude": {
            "Cooperation": {"Horizontal": "Colleagues?", "Respect": "Team Opinions?", "Supervisor": "Supervisors?"},
            "Motivation": {"Proactive": "Active?", "Responsible": "Sincerity?", "Research": "Deep Study?"},
            "Compliance": {"Discipline": "Order?", "Data": "Data Mgmt?", "Attendance": "Tardiness?"}
        },
        "3. Job Competency": {
            "Knowledge": {"Job": "Broad/Deep?", "Related": "Basic?"},
            "Judgment": {"Speed": "Understanding?", "Validity": "Conclusion?", "Solving": "Essence?", "Insight": "Grasp?"},
            "Creativity": {"Improvement": "Ideas?"},
            "Expression": {"Verbal": "Clear?", "Written": "Clear?", "Negotiation": "Smooth?"}
        }
    }
}

LEADER_EVAL_DATA = {
    "KO": {
        "리더십": {"고객지향": "내/외부 고객 요구 대응", "책임감": "업무목표 달성 노력", "팀워크지향": "의사결정 배경 공유"},
        "업무실적": {"개방적 의사소통": "사적 소통 통한 친밀감", "문제해결": "원인 규명 능력", "조직이해": "전략/역사 파악", "프로젝트 관리": "계획 수립 능력"},
        "지식": {"분석적 사고": "필요 정보 파악", "세밀한 업무처리": "과거 관행 조사"}
    }
}

UI = {
    "KO": {"m1": "자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드", "m5": "🚀 리더십 자기평가", "sub": "✅ 최종 제출", "already": "✅ 이미 제출 완료"},
    "EN": {"m1": "Self-Eval", "m2": "👥 2nd Eval", "m3": "⚖️ 3rd Final", "m4": "📊 Dashboard", "m5": "🚀 Leadership Eval", "sub": "✅ Submit", "already": "✅ Submitted"}
}

# --- [3] 저장 함수 ---
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
        name = st.text_input("Name")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            u = user_db[user_db['성명'] == name]
            if not u.empty and str(pw) == str(u.iloc[0]['비밀번호']):
                ldr = str(u.iloc[0]['리더여부']).upper() if '리더여부' in u.columns else 'N'
                lng = u.iloc[0]['언어'] if '언어' in u.columns else 'KO'
                st.session_state.update({'auth':True, 'user':name, 'is_leader':ldr, 'lang':lng})
                st.rerun()
    else:
        L, E, user_name = UI[st.session_state.lang], EVAL_DATA[st.session_state.lang], st.session_state.user
        m_list = [L["m1"]]
        if st.session_state.is_leader == 'Y': m_list.append(L["m5"])
        if not user_db[user_db['2차평가자'] == user_name].empty: m_list.append(L["m2"])
        if not user_db[user_db['3차평가자'] == user_name].empty: m_list.append(L["m3"])
        if user_name == "권정순": m_list.append(L["m4"])
        menu = st.sidebar.radio("Menu", m_list)

        def render_form(data_dict, pre, self_data=None):
            tabs = st.tabs(list(data_dict.keys()))
            res_dict = {}
            for i, major in enumerate(data_dict.keys()):
                with tabs[i]:
                    for sub, items in data_dict[major].items():
                        st.markdown(f"#### 📍 {sub}")
                        for it, crit in items.items():
                            c1, c2, c3, c4 = st.columns([1.8, 2.7, 1, 3.5])
                            lbl = f"**{it}**"
                            if self_data and it in self_data:
                                lbl += f"<br><span style='color:blue; font-size: 0.8em;'>[본인: {self_data[it]['score']}]</span>"
                            c1.markdown(lbl, unsafe_allow_html=True)
                            c2.caption(crit)
                            sc = c3.selectbox("Score", [1,2,3,4,5], key=f"{pre}_{it}_s")
                            bs = c4.text_input("Basis", key=f"{pre}_{it}_r")
                            res_dict[it] = {"score": sc, "basis": bs, "category": sub}
            return res_dict

        if menu == L["m4"]:
            st.title("📊 SRS Dashboard")
            st.dataframe(user_db)
        elif menu == L.get("m5", ""):
            st.header(L["m5"])
            ld_eval = render_form(LEADER_EVAL_DATA["KO"], "ld_self")
            if st.button("Submit Leadership"):
                now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                recs = [{"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "카테고리": v["category"], "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in ld_eval.items()]
                if save_data(recs, "Leadership_Results"): st.balloons(); st.rerun()
        elif menu == L["m1"]:
            st.header(L["m1"])
            eval_res = render_form(E, "self")
            r1, r2, r3 = st.text_area("1. 성과"), st.text_area("2. 역량"), st.text_area("3. 노력")
            if st.button(L["sub"]):
                now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                recs = [{"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                recs.append({"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "리포트", "항목": "종합", "점수": "-", "근거": f"성과:{r1}\n역량:{r2}\n노력:{r3}"})
                if save_data(recs, "Results"): st.balloons(); st.rerun()
