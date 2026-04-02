import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from datetime import timedelta
import plotly.express as px

# --- [1] 기본 설정 및 시트 연결 ---
st.set_page_config(page_title="SRS Global HR System", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db(sheet_name="Users"):
    try: return conn.read(worksheet=sheet_name, ttl=0)
    except: return None

# --- [2] 평가 데이터 (일반 25개 항목) ---
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
            "창의연구력": { "연구개선": "아이디어를 살리고 일의 순서개선이나 전진을 도모하는가?" },
            "표현절충": {"구두표현": "구두 표현이 능숙하며 알기 쉽고 정확한가?", "문장표현": "문장 표현이 능숙하며 알기 쉽고 정확한가?", "절충": "교섭을 원활하게 처리하는 능력은 어떤가?"}
        }
    }
}

# --- [3] 리더십 데이터 (9개 항목) ---
LEADER_DATA = {
    "KO": {
        "리더십": {"고객지향": "내/외부 고객 요구 능동 대응", "책임감": "목표 달성 계획적 행동", "팀워크지향": "의사결정 배경 공유"},
        "업무실적": {"개방적 의사소통": "사적 소통/친밀감", "문제해결": "근본원인 규명", "조직이해": "전략/역사 파악", "프로젝트 관리": "계획 수립 능력"},
        "지식": {"분석적 사고": "필요 정보 파악", "세밀한 업무처리": "규정/관행 조사"}
    }
}

UI = {
    "KO": {"m1": "📝 자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드", "m5": "🚀 리더십 자기평가", "sub": "✅ 최종 제출", "already": "✅ 제출 완료", "err": "⚠️ 모든 근거를 작성해 주세요."}
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
        name = st.text_input("성명")
        pw = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            u = user_db[user_db['성명'] == name]
            if not u.empty and str(pw) == str(u.iloc[0]['비밀번호']):
                ldr = str(u.iloc[0]['리더여부']).upper() if '리더여부' in u.columns else 'N'
                st.session_state.update({'auth':True,'user':name,'is_leader':ldr})
                st.rerun()
            else: st.error("로그인 실패")
    else:
        L, user_name = UI["KO"], st.session_state.user
        m_list = [L["m1"]]
        if st.session_state.is_leader == 'Y': m_list.append(L["m5"])
        if not user_db[user_db['2차평가자'] == user_name].empty: m_list.append(L["m2"])
        if not user_db[user_db['3차평가자'] == user_name].empty: m_list.append(L["m3"])
        if user_name == "권정순": m_list.append(L["m4"])
        menu = st.sidebar.radio("메뉴", m_list)

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
                                label += f"<br><span style='color:blue; font-size: 0.85em;'>[본인: {self_data[it]['score']}]</span>"
                            c1.markdown(label, unsafe_allow_html=True)
                            c2.caption(crit)
                            score = c3.selectbox("점수", [1,2,3,4,5], key=f"{pre}_{it}_s")
                            basis = c4.text_input("근거", key=f"{pre}_{it}_r")
                            res_dict[it] = {"score": score, "basis": basis, "category": sub}
            return res_dict

        # --- 메뉴 1: 일반 자기고과 ---
        if menu == L["m1"]:
            st.header(L["m1"])
            res_df = conn.read(worksheet="Results", ttl=0)
            if res_df is not None and not res_df.empty and not res_df[(res_df['피평가자'] == user_name) & (res_df['구분'] == "자기")].empty:
                st.success(L["already"])
            else:
                eval_res = render_form(EVAL_DATA["KO"], "self")
                st.divider()
                st.subheader("🚀 자기 성장 REPORT")
                r1 = st.text_area("1. 금기 성과 요약", key="r1")
                r2 = st.text_area("2. 향후 역량 개발 계획", key="r2")
                r3 = st.text_area("3. 회사에 바라는 점", key="r3")
                if st.button(L["sub"]):
                    if any(not v["basis"].strip() for v in eval_res.values()) or not r1.strip(): st.error(L["err"])
                    else:
                        now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                        recs = [{"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                        recs.append({"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "리포트", "항목": "종합", "점수": "-", "근거": f"성과:{r1}\n역량:{r2}\n노력:{r3}"})
                        if save_data(recs, "Results"): st.balloons(); st.rerun()

        # --- 메뉴 5: 리더십 자기평가 ---
        elif menu == L["m5"]:
            st.header(L["m5"])
            ld_df = conn.read(worksheet="Leadership_Results", ttl=0)
            if ld_df is not None and not ld_df.empty and not ld_df[(ld_df['피평가자'] == user_name) & (ld_df['구분'] == "자기")].empty:
                st.success(L["already"])
            else:
                ld_res = render_form(LEADER_DATA["KO"], "ldr_self")
                if st.button("리더십 제출"):
                    if any(not v["basis"].strip() for v in ld_res.values()): st.error(L["err"])
                    else:
                        now = (datetime.datetime.now() + timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                        recs = [{"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "카테고리": v["category"], "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in ld_res.items()]
                        if save_data(recs, "Leadership_Results"): st.balloons(); st.rerun()

        # --- 메뉴 4: 관리자 대시보드 (비밀번호 재설정 포함) ---
        elif menu == L["m4"]:
            st.title("📊 관리자 대시보드")
            st.dataframe(user_db)
            st.divider()
            st.subheader("🔑 직원 비밀번호 재설정")
            target = st.selectbox("직원 선택", user_db['성명'].tolist())
            new_pw = st.text_input("새 비밀번호", type="password")
            if st.button("변경 저장"):
                idx = user_db[user_db['성명'] == target].index[0]
                user_db.at[idx, '비밀번호'] = new_pw
                if conn.update(worksheet="Users", data=user_db):
                    st.success(f"{target}님 비밀번호 변경 완료!"); st.cache_data.clear()
