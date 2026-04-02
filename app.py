import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import plotly.express as px
import plotly.graph_objects as go

# --- [1] 기본 설정 및 시트 연결 ---
st.set_page_config(page_title="SRS Global HR System", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db(sheet_name="Users"):
    try: return conn.read(worksheet=sheet_name, ttl=0)
    except: return None

# --- [2] 정식 평가 데이터 (25개 일반 항목 상세 문구) ---
EVAL_DATA = {
    "KO": {
        "1. 업무실적": {
            "업무의 양": {
                "속도": "업무를 신속하게 처리하며 지체되는 일은 없었는가?",
                "지속성": "어떤 일이나 차이 없이 끈기있게 했는가?",
                "능률": "신속 정확하게 낭비 없이 처리 했는가?"
            },
            "업무의 질": {
                "정확성": "일의 결과를 믿을 수 있는가?",
                "성과": "일의 성과가 내용에 있어서 뛰어났는가?",
                "꼼꼼함": "철저하고 뒷처리를 잘하는가?"
            }
        },
        "2. 근무태도": {
            "협조성": {
                "횡적협조": "스스로 동료와 협력하며 조직체의 능률향상에 공헌하는가?",
                "존중": "자신의 생각보다는 팀(동료) 전체의 의견을 존중하는가?",
                "상사와의 협조": "상사에 대해 협력하며 성과가 있는가?"
            },
            "근무의욕": {
                "적극성": "일에 능동적으로 대처하려는 의욕은 어떤가?",
                "책임감": "책임을 회피하지 않으며 성실하게 일하려는 의욕은 어떤가?",
                "연구심": "넓고 깊게 일을 연구하려는 의욕은 어떤가?"
            },
            "복무상황": {
                "규율": "규칙을 준수하며 직장질서유지에 애쓰는가?",
                "DB화": "정기적인 업무보고와 본인업무에 대한 데이터의 체계적인 관리",
                "근태상황": "지각, 조퇴, 결근 등 상황은 어떤가?"
            }
        },
        "3. 직무능력": {
            "지식": {
                "직무지식": "담당업무의 지식이 넓고 깊은가?",
                "관련지식": "관련업무에 대한 기초지식은 넓고 깊은가?"
            },
            "이해판단력": {
                "신속성": "규정, 지시, 자료 등을 바르게 이해하는 속도는 어떤가?",
                "타당성": "내린 결론은 정확하며 타당한가?",
                "문제해결": "문제 발생 시 본질을 파악하여 효과적인 해결을 주도하는가?",
                "통찰력": "사물의 요점을 파악하며 자주적으로 결론을 내릴 수 있는가?"
            },
            "창의연구력": { "연구개선": "아이디어를 살리고 일의 순서개선이나 전진을 도모하는가?" },
            "표현절충": {
                "구두표현": "구두 표현이 능숙하며 알기 쉽고 정확한가?",
                "문장표현": "문장 표현이 능숙하며 알기 쉽고 정확한가?",
                "절충": "교섭을 원활하게 처리하는 능력은 어떤가?"
            }
        }
    },
    "EN": {
        "1. Performance": {
            "Quantity": {"Speed": "Did you process work quickly?", "Persistence": "Consistently?", "Efficiency": "Efficiently?"},
            "Quality": {"Accuracy": "Is it reliable?", "Achievement": "Outstanding?", "Thoroughness": "Thorough handling?"}
        },
        "2. Work Attitude": {
            "Cooperation": {"Horizontal": "Cooperate with colleagues?", "Respect": "Team opinions?", "Supervisor": "Supervisors?"},
            "Motivation": {"Proactive": "Proactive approach?", "Responsible": "Accountability?", "Research": "Deep study?"},
            "Compliance": {"Discipline": "Follow rules?", "Data": "Data mgmt?", "Attendance": "Attendance status?"}
        },
        "3. Job Competency": {
            "Knowledge": {"Job Knowledge": "Broad and deep?", "Related": "Related basics?"},
            "Judgment": {"Understanding": "Understanding speed?", "Validity": "Validity?", "Solving": "Essence?", "Insight": "Independent conclusion?"},
            "Creativity": {"Improvement": "Willingness to improve?"},
            "Communication": {"Verbal": "Skillful speaking?", "Written": "Skillful writing?", "Negotiation": "Negotiation ability?"}
        }
    }
}

LEADER_EVAL_DATA = {
    "KO": {
        "리더십": {
            "고객지향": "내부 혹은 외부 고객의 요구를 능동적으로 찾아내고 적시에 대응한다",
            "책임감": "특별한 지시를 하지 않더라도 업무목표를 달성하기 위해 계획적으로 행동한다",
            "팀워크지향": "구성원의 공감을 얻기 위해 자주 의견을 공유하고 의사결정의 배경이나 당위성에 대해 설명한다"
        },
        "업무실적": {
            "개방적 의사소통": "상대방이 친밀감을 느낄 수 있도록 자신의 사적인 부분을 먼저 이야기한다",
            "문제해결": "문제 발생 시 문제상황과 관련된 정보와 자료를 수집하고 분석하여 문제의 근본원인을 규명한다",
            "조직이해": "조직의 전략, 운영방식, 역사 등을 파악한다",
            "프로젝트 관리": "프로젝트와 관련된 정보를 체계적으로 수집, 분석하여 계획을 수립한다"
        },
        "지식": {
            "분석적 사고": "문제를 해결하기 위해 필요한 정보나 자료가 무엇인지 정확히 파악한다",
            "세밀한 업무처리": "문제 발생 소지를 최소화하기 위해 조직의 관련 규정이나 과거 관행 등을 조사한다"
        }
    }
}

UI = {
    "KO": {
        "m1": "자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드", "m5": "🚀 리더십 자기평가",
        "sub": "✅ 최종 제출", "save_ok": "성공적으로 저장되었습니다!", "err": "⚠️ 모든 근거를 작성해 주세요.", "already": "✅ 제출 완료"
    },
    "EN": {
        "m1": "Self-Evaluation", "m2": "👥 2nd Evaluation", "m3": "⚖️ 3rd Final Review", "m4": "📊 Admin Dashboard", "m5": "🚀 Leadership Self-Eval",
        "sub": "✅ Final Submit", "save_ok": "Saved Successfully!", "err": "⚠️ All fields required.", "already": "✅ Done"
    }
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

# --- [5] 메인 로직 ---
user_db = get_db("Users")
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'is_leader': 'N', 'lang': 'KO'})

if user_db is not None:
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System")
        name = st.text_input("Name")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            u = user_db[user_db['성명'] == name]
            if not u.empty and str(pw) == str(u.iloc[0]['비밀번호']):
                ldr = str(u.iloc[0]['리더여부']).upper() if '리더여부' in u.columns else 'N'
                lng = u.iloc[0]['언어'] if '언어' in u.columns else 'KO'
                st.session_state.update({'auth':True,'user':name,'is_leader':ldr,'lang':lng})
                st.rerun()
            else: st.error("Login Failed")
    else:
        L, E = UI[st.session_state.lang], EVAL_DATA[st.session_state.lang]
        user_name = st.session_state.user
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
                            label = f"**{it}**"
                            if self_data and it in self_data:
                                label += f"<br><span style='color:blue; font-size: 0.85em;'>[본인: {self_data[it]['score']}점]</span>"
                                if self_data[it]['basis']: label += f"<br><span style='color:gray; font-size: 0.8em;'>ㄴ 사유: {self_data[it]['basis']}</span>"
                            c1.markdown(label, unsafe_allow_html=True)
                            c2.caption(crit)
                            score = c3.selectbox("Score", [1,2,3,4,5], key=f"{pre}_{it}_s")
                            basis = c4.text_input("Basis", key=f"{pre}_{it}_r")
                            res_dict[it] = {"score": score, "basis": basis, "category": sub}
            return res_dict

        if menu == L["m4"]:
            st.title("📊 Dashboard")
            res_df = conn.read(worksheet="Results", ttl=0)
            if res_df is not None and not res_df.empty:
                res_df['점수'] = pd.to_numeric(res_df['점수'], errors='coerce')
                st.plotly_chart(px.bar(res_df[res_df['구분']=='자기'].groupby('피평가자')['점수'].mean().reset_index(), x='피평가자', y='점수', title="직원별 자기평가 평균"))
            st.dataframe(user_db)

        elif menu == L["m1"]:
            st.header(L["m1"])
            eval_res = render_form(E, "self")
            r1, r2, r3 = st.text_area("1. 성과"), st.text_area("2. 역량"), st.text_area("3. 노력")
            if st.button(L["sub"]):
                if any(not v["basis"].strip() for v in eval_res.values()) or not r1.strip(): st.error(L["err"])
                else:
                    now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                    recs = [{"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                    recs.append({"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "리포트", "항목": "종합", "점수": "-", "근거": f"성과:{r1}\n역량:{r2}\n노력:{r3}"})
                    if save_data(recs, "Results"): st.balloons(); st.rerun()

        elif menu == L["m5"]:
            st.header(L["m5"])
            ld_eval = render_form(LEADER_EVAL_DATA["KO"], "ldr_self")
            if st.button(L["sub"]):
                if any(not v["basis"].strip() for v in ld_eval.values()): st.error(L["err"])
                else:
                    now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                    recs = [{"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "카테고리": v["category"], "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in ld_eval.items()]
                    if save_data(recs, "Leadership_Results"): st.balloons(); st.rerun()

        elif menu == L["m2"]:
            st.header(L["m2"])
            team = user_db[user_db['2차평가자'] == user_name]['성명'].tolist()
            target = st.selectbox("Target", team)
            is_target_ldr = str(user_db[user_db['성명']==target].iloc[0]['리더여부']).upper() == 'Y'
            res_df = conn.read(worksheet="Results", ttl=0)
            st.subheader(f"1️⃣ {target} 평가")
            self_data = None
            if res_df is not None:
                t_eval = res_df[(res_df['피평가자'] == target) & (res_df['구분'] == "자기")]
                self_data = {row['항목']: {'score': row['점수'], 'basis': row['근거']} for _, row in t_eval.iterrows()}
            gen_res = render_form(E, f"2nd_gen_{target}", self_data)
            if st.button(f"Submit for {target}"):
                now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                g_recs = [{"시간": now, "평가자": user_name, "피평가자": target, "구분": "2차", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in gen_res.items()]
                if save_data(g_recs, "Results"): st.success(L["save_ok"])
