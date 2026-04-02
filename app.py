import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- [1] 기본 설정 및 시트 연결 ---
st.set_page_config(page_title="SRS HR System", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db(sheet_name="Users"):
    try: return conn.read(worksheet=sheet_name)
    except: return None

# --- [2] 정식 평가 데이터 (25개 전 항목 상세) ---
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
                "상사협조": "상사에 대해 협력하며 성과가 있는가?"
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
                "문제해결": "문제 본질을 파악하여 효과적인 해결을 주도하는가?",
                "통찰력": "사물의 요점을 파악하며 자주적으로 결론을 내릴 수 있는가?"
            },
            "창의연구력": { "연구개선": "아이디어를 살리고 일의 순서개선이나 전진을 도모하고 있는가?" },
            "표현절충": {
                "구두표현": "구두에 의한 표현이 능숙하며 알기 쉽고 정확한가?",
                "문장표현": "문장에 의한 표현이 능숙하며 알기 쉽고 정확한가?",
                "절충": "교섭을 원활하게 처리하는 능력은 어떤가?"
            }
        }
    },
    "EN": {
        "1. Performance": {
            "Quantity": {
                "Speed": "Did you process work quickly without delays?",
                "Persistence": "Did you work persistently and consistently?",
                "Efficiency": "Did you work efficiently without waste?"
            },
            "Quality": {
                "Accuracy": "Is the result of your work reliable?",
                "Achievement": "Was the performance outstanding in content?",
                "Thoroughness": "Are you thorough and handle follow-ups well?"
            }
        },
        "2. Work Attitude": {
            "Cooperation": { "Horizontal": "Cooperate with colleagues?", "Respect": "Respect team opinions?", "Supervisor": "Cooperate with supervisors?" },
            "Motivation": { "Proactive": "Proactive attitude?", "Responsible": "Sincerity?", "Research": "Study tasks deeply?" },
            "Compliance": { "Discipline": "Workplace order?", "Data": "Systematic data mgmt?", "Attendance": "Tardiness/Absence?" }
        },
        "3. Competency": {
            "Knowledge": { "Job": "Deep job knowledge?", "Related": "Related basic knowledge?" },
            "Judgment": { "Speed": "Understanding speed?", "Validity": "Conclusion validity?", "Solving": "Problem solving?", "Insight": "Independent conclusion?" },
            "Creativity": { "Improve": "Willingness to improve?" },
            "Communication": { "Verbal": "Clear verbal?", "Written": "Clear written?", "Negotiation": "Smooth negotiation?" }
        }
    }
}

# --- [3] UI 텍스트 ---
UI = {
    "KO": {
        "m1": "자기고과 작성", "m2": "팀원 평가", "m3": "📊 관리자 현황판", 
        "guide": "💡 성과와 역량을 객관적으로 증명할 수 있는 근거를 상세히 기록해 주세요. 작성된 근거는 평가의 중요한 기초 자료가 됩니다.",
        "score": "점수", "basis": "판단 근거", "rep": "🚀 자기 성장 REPORT", "sub": "✅ 최종 제출", "admin_reset": "🔑 직원 비밀번호 초기화", "save_ok": "성공적으로 저장되었습니다!"
    },
    "EN": {
        "m1": "Self-Evaluation", "m2": "Team Evaluation", "m3": "📊 Admin Dashboard", 
        "guide": "💡 Please record detailed evidence that can objectively prove your performance. This is a crucial basis for evaluation.",
        "score": "Score", "basis": "Basis", "rep": "🚀 Self-Growth REPORT", "sub": "✅ Final Submit", "admin_reset": "🔑 Reset Employee Password", "save_ok": "Saved Successfully!"
    }
}

# --- [4] 데이터 저장 함수 ---
def save_result(records):
    try:
        existing = get_db("Results")
        new_df = pd.DataFrame(records)
        final = pd.concat([existing, new_df], ignore_index=True) if existing is not None else new_df
        conn.update(worksheet="Results", data=final)
        return True
    except Exception as e:
        st.error(f"저장 실패: {e}")
        return False

# --- [5] 메인 로직 ---
user_db = get_db("Users")
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'pw_status': 'N', 'lang': 'KO'})

if user_db is not None:
    # 1. 로그인
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System")
        name = st.text_input("Name (성명)")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            u = user_db[user_db['성명'] == name]
            if not u.empty and str(pw) == str(u.iloc[0]['비밀번호']):
                st.session_state.update({'auth':True,'user':name,'pw_status':str(u.iloc[0]['비번변경여부']),'lang':u.iloc[0]['언어']})
                st.rerun()
            else: st.error("Check Name/PW")

    # 2. 비번 변경
    elif st.session_state.pw_status == 'N':
        st.title("🔑 비밀번호 변경")
        new_pw = st.text_input("새 비밀번호 (8자 이상)", type="password")
        if st.button("변경 완료"):
            df = user_db.copy()
            df.loc[df['성명']==st.session_state.user, ['비밀번호','비번변경여부']] = [new_pw,'Y']
            conn.update(worksheet="Users", data=df)
            st.session_state.pw_status = 'Y'; st.rerun()

    # 3. 메인 시스템
    else:
        T, E = UI[st.session_state.lang], EVAL_DATA[st.session_state.lang]
        user_name = st.session_state.user
        
        # 권정순 이사님만 관리자 메뉴 보이게 설정
        m_list = [T["m1"], T["m2"]]
        if user_name == "권정순": m_list.append(T["m3"])
        menu = st.sidebar.radio("Menu", m_list)

        # 공통 평가 폼 렌더링 함수
        def render_form(pre):
            st.info(T["guide"])
            tabs = st.tabs(list(E.keys()))
            eval_results = {}
            for i, major in enumerate(E.keys()):
                with tabs[i]:
                    for sub, items in E[major].items():
                        st.subheader(f"📍 {sub}")
                        for it, crit in items.items():
                            c1, c2, c3, c4 = st.columns([1.2, 3, 1, 3.5])
                            c1.write(f"**{it}**"); c2.caption(crit)
                            score = c3.selectbox(T["score"], [5,4,3,2,1], key=f"{pre}_s_{it}")
                            basis = c4.text_input(T["basis"], key=f"{pre}_r_{it}", placeholder="상세 근거 작성")
                            eval_results[it] = {"score": score, "basis": basis}
            return eval_results

        # [메뉴 1] 자기고과
        if menu == T["m1"]:
            st.header(T["m1"])
            current_eval = render_form("self")
            st.divider()
            st.header(T["rep"])
            r1 = st.text_area("1. 주요 성과", key="rep1")
            r2 = st.text_area("2. 습득 역량", key="rep2")
            r3 = st.text_area("3. 인재양성 노력", key="rep3")
            
            if st.button(T["sub"]):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                records = []
                for it, val in current_eval.items():
                    records.append({"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "항목": it, "점수": val["score"], "근거": val["basis"]})
                records.append({"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "리포트", "항목": "성과/역량/노력", "점수": "-", "근거": f"1:{r1}\n2:{r2}\n3:{r3}"})
                if save_result(records): st.balloons(); st.success(T["save_ok"])

        # [메뉴 2] 팀원 평가 (2/3차)
        elif menu == T["m2"]:
            st.header(T["m2"])
            # 내가 2차 또는 3차 평가자로 지정된 팀원만 필터링
            team = user_db[(user_db['2차평가자'] == user_name) | (user_db['3차평가자'] == user_name)]['성명'].tolist()
            if team:
                target = st.selectbox("평가 대상 선택", team)
                current_eval = render_form(f"team_{target}")
                if st.button(f"{target}님 평가 결과 제출"):
                    now = datetime.now().strftime("%Y-%m-%d %H:%M")
                    records = [{"시간": now, "평가자": user_name, "피평가자": target, "구분": "팀원", "항목": it, "점수": v["score"], "근거": v["basis"]} for it, v in current_eval.items()]
                    if save_result(records): st.success(f"{target} {T['save_ok']}")
            else: st.info("평가할 팀원이 없습니다.")

        # [메뉴 3] 관리자 모드
        elif menu == T["m3"]:
            st.header(T["m3"])
            st.subheader("전체 직원 현황")
            st.dataframe(user_db, use_container_width=True)
            st.divider()
            st.subheader(T["admin_reset"])
            r_target = st.selectbox("초기화할 직원 선택", user_db['성명'].tolist())
            if st.button("비밀번호 12345678!로 초기화"):
                df = user_db.copy()
                df.loc[df['성명']==r_target, ['비밀번호','비번변경여부']] = ['12345678!','N']
                conn.update(worksheet="Users", data=df)
                st.success(f"{r_target}님의 비밀번호가 초기화되었습니다.")
