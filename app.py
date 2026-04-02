import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- [1] 기본 설정 및 시트 연결 ---
st.set_page_config(page_title="SRS 글로벌 인사평가 시스템", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 유실 방지를 위해 캐시 없이 즉시 읽어오는 설정
def get_db(sheet_name="Users"):
    try:
        return conn.read(worksheet=sheet_name, ttl=0)
    except:
        return None

# --- [2] 정식 평가 데이터 (25개 상세 항목) ---
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
    }
}

# --- [3] UI 텍스트 ---
UI = {
    "KO": {
        "m1": "자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 현황판",
        "guide": "💡 성과와 역량을 객관적으로 증명할 수 있는 근거를 상세히 기록해 주세요.",
        "score": "점수", "basis": "판단 근거", "sub": "✅ 최종 제출", "save_ok": "저장되었습니다!"
    }
}

# --- [4] 데이터 저장 함수 (유실 방지 업그레이드 버전) ---
def save_result(records):
    try:
        existing = conn.read(worksheet="Results", ttl=0)
        new_df = pd.DataFrame(records)
        if existing is not None and not existing.empty:
            final_df = pd.concat([existing, new_df], ignore_index=True)
        else:
            final_df = new_df
        conn.update(worksheet="Results", data=final_df)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"저장 중 오류 발생: {e}")
        return False

# --- [5] 시스템 로직 시작 ---
user_db = get_db("Users")
if 'auth' not in st.session_state:
    st.session_state.update({'auth': False, 'user': '', 'pw_status': 'N'})

if user_db is not None:
    # 로그인
    if not st.session_state.auth:
        st.title("🛡️ Smart Radar System")
        name = st.text_input("성명")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            u = user_db[user_db['성명'] == name]
            if not u.empty and str(pw) == str(u.iloc[0]['비밀번호']):
                st.session_state.update({'auth': True, 'user': name, 'pw_status': str(u.iloc[0]['비번변경여부'])})
                st.rerun()
            else: st.error("정보가 일치하지 않습니다.")

    # 비번 변경
    elif st.session_state.pw_status == 'N':
        st.title("🔑 비밀번호 변경")
        new_pw = st.text_input("새 비밀번호 (8자 이상)", type="password")
        if st.button("변경 완료"):
            df = user_db.copy()
            df.loc[df['성명']==st.session_state.user, ['비밀번호','비번변경여부']] = [new_pw,'Y']
            conn.update(worksheet="Users", data=df)
            st.session_state.pw_status = 'Y'; st.rerun()

    # 메인
    else:
        L, E = UI["KO"], EVAL_DATA["KO"]
        user_name = st.session_state.user
        m_list = [L["m1"]]
        if not user_db[user_db['2차평가자'] == user_name].empty: m_list.append(L["m2"])
        if not user_db[user_db['3차평가자'] == user_name].empty: m_list.append(L["m3"])
        if user_name == "권정순": m_list.append(L["m4"])
        menu = st.sidebar.radio("Menu", m_list)

        def render_form(pre, self_scores=None):
            st.info(L["guide"])
            tabs = st.tabs(list(E.keys()))
            res_dict = {}
            for i, major in enumerate(E.keys()):
                with tabs[i]:
                    for sub, items in E[major].items():
                        st.markdown(f"#### 📍 {sub}")
                        for it, crit in items.items():
                            c1, c2, c3, c4 = st.columns([1.5, 3, 1, 3.5])
                            label = f"**{it}**"
                            if self_scores and it in self_scores:
                                label += f" <br><span style='color:blue; font-size: 0.8em;'>(본인제출: {self_scores[it]}점)</span>"
                            c1.markdown(label, unsafe_allow_html=True)
                            c2.caption(crit)
                            score = c3.selectbox("점수", [1,2,3,4,5], key=f"{pre}_{it}_s")
                            basis = c4.text_input("근거", key=f"{pre}_{it}_r", placeholder="내용 입력")
                            res_dict[it] = {"score": score, "basis": basis}
                        st.divider()
            return res_dict

        if menu == L["m1"]:
            st.header(L["m1"])
            eval_res = render_form("self")
            st.header("🚀 성장 리포트")
            r1 = st.text_area("1. 주요 성과", key="rep1")
            r2 = st.text_area("2. 습득 역량", key="rep2")
            r3 = st.text_area("3. 인재양성 노력", key="rep3")
            if st.button(L["sub"]):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                recs = [{"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "자기", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                recs.append({"시간": now, "평가자": user_name, "피평가자": user_name, "구분": "리포트", "항목": "종합", "점수": "-", "근거": f"성과:{r1}\n역량:{r2}\n노력:{r3}"})
                if save_result(recs): st.balloons(); st.success(L["save_ok"])

        elif menu == L["m2"]:
            st.header(L["m2"])
            team = user_db[user_db['2차평가자'] == user_name]['성명'].tolist()
            target = st.selectbox("2차 평가 대상", team)
            self_scores = None
            res_df = conn.read(worksheet="Results", ttl=0)
            if res_df is not None:
                target_eval = res_df[(res_df['피평가자'] == target) & (res_df['구분'] == "자기")]
                if not target_eval.empty: self_scores = dict(zip(target_eval['항목'], target_eval['점수']))
            eval_res = render_form(f"2nd_{target}", self_scores=self_scores)
            if st.button(f"{target}님 평가 완료"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                recs = [{"시간": now, "평가자": user_name, "피평가자": target, "구분": "2차", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                if save_result(recs): st.success(f"{target}님 {L['save_ok']}")

        elif menu == L["m3"]:
            st.header(L["m3"])
            team = user_db[user_db['3차평가자'] == user_name]['성명'].tolist()
            target = st.selectbox("3차 평가 대상", team)
            eval_res = render_form(f"3rd_{target}")
            if st.button(f"{target}님 최종 확정"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                recs = [{"시간": now, "평가자": user_name, "피평가자": target, "구분": "3차", "항목": k, "점수": v["score"], "근거": v["basis"]} for k,v in eval_res.items()]
                if save_result(recs): st.success(f"{target}님 최종 확정 {L['save_ok']}")

        elif menu == L["m4"]:
            st.header(L["m4"])
            st.dataframe(user_db)
            st.divider()
            r_target = st.selectbox("초기화 대상", user_db['성명'].tolist())
            if st.button("비번 초기화"):
                df = user_db.copy()
                df.loc[df['성명']==r_target, ['비밀번호','비번변경여부']] = ['12345678!','N']
                conn.update(worksheet="Users", data=df); st.success("완료")
