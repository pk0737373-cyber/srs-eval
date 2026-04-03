import streamlit as st
from streamlit_gsheets_connection import GSheetsConnection # [수정] 최신 라이브러리 경로
import pandas as pd
import datetime
from datetime import timedelta
import time
import re

# --- [0] 보안 및 정책 설정 ---
INITIAL_PW = "12345678!"
PW_RULE_MSG = "🔐 보안 정책: 영문 + 숫자 + 특수문자 조합 8자 이상 필수"

def check_password_strength(pw):
    if len(pw) < 8: return False
    if not re.search("[a-zA-Z]", pw): return False
    if not re.search("[0-9]", pw): return False
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", pw): return False
    return True

# --- [1] 기본 설정 및 데이터 엔진 ---
st.set_page_config(page_title="SRS Global HR Portal", page_icon="🎯", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def get_user_data():
    try:
        df = conn.read(worksheet="Users", ttl=0)
        return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x).fillna("")
    except: return pd.DataFrame()

@st.cache_data(ttl=5)
def get_results_data(ws_name):
    try:
        df = conn.read(worksheet=ws_name, ttl=0)
        return df.apply(lambda x: x.str.strip() if x.dtype == "object" else x).fillna("")
    except: return pd.DataFrame()

# --- [2] 평가 지표 데이터 (이사님 원문 100% 복구) ---
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
                "상사와외 협조": "상사에 대해 협력하며 성과가 있는가?"
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
            "지식": {"직무지식": "담당업무 지식이 넓고 깊은가?", "관련지식": "기초지식이 충분한가?"},
            "이해판단력": {"신속성": "이해 속도?", "타당성": "결론의 타당성?", "문제해결": "본질 파악 및 해결 주도?", "통찰력": "요점 파악 및 자발적 결론?"},
            "창의연구력": {"연구개선": "창의적 아이디어로 개선 도모?"},
            "표현절충": {"구두표현": "알기 쉬운 표현?", "문장표현": "정확한 문장력?", "절충": "원활한 교섭 능력?"}
        }
    },
    "EN": {
        "1. Performance": {
            "Quantity": {"Speed": "Quickly processed?", "Persistence": "Consistently?", "Efficiency": "Efficiently?"},
            "Quality": {"Accuracy": "Reliable?", "Achievement": "Outstanding?", "Thoroughness": "Thorough?"}
        }
    }
}

LEADER_DATA = {
    "KO": {
        "1. 리더십": {
            "기본역량": {"고객지향": "고객 요구 적시 대응", "책임감": "계획적 행동", "팀워크": "의견 공유 및 설명"},
            "실행역량": {"의사소통": "친밀감 형성", "문제해결": "근본원인 규명", "조직이해": "전략/역사 파악", "프로젝트관리": "체계적 수립"}
        }
    }
}

REPORT_QS = {"KO": {"q1": "1. 주요 성과", "q2": "2. 습득 지식", "q3": "3. 인재 양성 노력"}}

UI = {
    "KO": {
        "m1": "📝 자기고과 작성", "m2": "👥 2차 팀원평가", "m3": "⚖️ 3차 최종평가", "m4": "📊 관리자 대시보드",
        "m5": "🚀 리더십 자기평가", "save": "💾 임시 저장", "sub": "✅ 최종 제출",
        "err_null": "⚠️ [제출 불가] 점수 선택 및 근거(5자 이상)를 모두 입력해 주세요.",
        "already": "✅ 최종 제출이 완료되어 조회 모드로 전환합니다.", "logout": "🔓 로그아웃", "score": "점수", "basis": "근거"
    },
    "EN": { "m1": "📝 Self-Eval", "m5": "🚀 Leader Eval", "m4": "📊 Admin", "save": "💾 Save Draft", "sub": "✅ Final Submit" }
}

# --- [3] 데이터 저장 엔진 (타인 데이터 보존) ---
def save_data_engine(recs, user_id, target_id, is_final, ws_name="Results"):
    try:
        df_old = conn.read(worksheet=ws_name, ttl=0).fillna("")
        if any("리포트" in r['구분'] for r in recs):
            df_new = df_old[~((df_old['평가자'] == user_id) & (df_old['구분'].str.contains("리포트", na=False)))]
        else:
            df_new = df_old[~((df_old['평가자'] == user_id) & (df_old['피평가자'] == target_id) & (~df_old['구분'].str.contains("리포트", na=False)))]
            
        final_df = pd.concat([df_new, pd.DataFrame(recs)], ignore_index=True)
        conn.update(worksheet=ws_name, data=final_df)
        st.cache_data.clear()
        return True
    except: return False

# --- [4] 메인 렌더링 엔진 (백화 현상 해결 버전) ---
def render_engine(data_dict, pre, eval_type="자기", ws_name="Results", target_name=None):
    if not target_name: return
    L = UI[st.session_state.lang]
    
    check_df = get_results_data(ws_name)
    existing = check_df[(check_df['평가자']==st.session_state.user) & (check_df['피평가자']==target_name)] if not check_df.empty else pd.DataFrame()
    # [수정] contains 조건 정교화
    is_final_done = not existing[existing['구분'].str.contains("Final", na=False) & ~existing['구분'].str.contains("리포트", na=False)].empty

    if is_final_done:
        st.success(L["already"])
        st.dataframe(existing, use_container_width=True, hide_index=True)
    else:
        draft_vals = existing[existing['구분'].str.contains("Draft", na=False)]
        
        # [해결] 탭을 폼 외부로 분리하여 레이아웃 충돌 방지
        tab_list = list(data_dict.keys())
        tabs = st.tabs(tab_list)
        
        # 폼 시작
        with st.form(key=f"form_main_{pre}_{target_name}"):
            res_dict = {}
            for i, major in enumerate(tab_list):
                with tabs[i]:
                    subs = data_dict[major]
                    for sub_key, items in subs.items():
                        st.markdown(f"#### 📍 {sub_key}")
                        for it, crit in items.items():
                            val = draft_vals[draft_vals['항목']==it]
                            init_s = int(val.iloc[0]['점수']) if not val.empty else 0
                            init_b = str(val.iloc[0]['근거']) if not val.empty else ""
                            
                            c1, c2, c3 = st.columns([3, 1, 3])
                            c1.markdown(f"**{it}**\n\n{crit}")
                            s = c2.selectbox(L["score"], [0, 1, 2, 3, 4, 5], index=init_s, key=f"s_{pre}_{it}_{target_name}")
                            r = c3.text_input(L["basis"], value=init_b, key=f"r_{pre}_{it}_{target_name}")
                            res_dict[it] = {"score": s, "basis": r}

            rep_data = {}
            if pre in ["self", "ld_self"]:
                st.divider(); st.subheader("🚀 자기 성장 REPORT")
                for k, v in REPORT_QS["KO"].items():
                    val_rep = existing[(existing['구분'].str.contains("리포트")) & (existing['항목']==v)]
                    rep_data[k] = st.text_area(v, value=str(val_rep.iloc[0]['근거']) if not val_rep.empty else "", key=f"rep_{pre}_{k}_{target_name}")

            col1, col2 = st.columns(2)
            btn_save = col1.form_submit_button(L["save"])
            btn_sub = col2.form_submit_button(L["sub"])

            if btn_save or btn_sub:
                is_f = btn_sub
                has_null = any(v["score"] == 0 or len(str(v["basis"]).strip()) < 5 for v in res_dict.values())
                if is_f and has_null:
                    st.error(L["err_null"])
                else:
                    status = "Final" if is_f else "Draft"
                    now = (datetime.datetime.now()+timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                    recs = [{"시간":now,"평가자":st.session_state.user,"피평가자":target_name,"구분":f"{eval_type}({status})","항목":k,"점수":v["score"],"근거":v["basis"]} for k,v in res_dict.items()]
                    if rep_data:
                        for kq, vq in rep_data.items(): recs.append({"시간":now,"평가자":st.session_state.user,"피평가자":target_name,"구분":f"리포트({status})","항목":REPORT_QS["KO"][kq],"점수":0,"근거":vq})
                    
                    if save_data_engine(recs, st.session_state.user, target_name, is_f, ws_name):
                        st.success(L["done_msg"]); time.sleep(1); st.rerun()

# --- [5] 권한 제어 및 실행부 ---
if 'auth' not in st.session_state: st.session_state.update({'auth':False, 'user':'', 'ldr':'N', 'lang':'KO', 'need_pw_change':False})
db_users = get_user_data()

if not db_users.empty:
    if not st.session_state.auth:
        st.title("🛡️ SRS Global HR Portal")
        n, p = st.text_input("Name"), st.text_input("PW", type="password")
        if st.button("Login"):
            u = db_users[db_users['성명'] == n.strip()]
            if not u.empty and str(p).strip() == str(u.iloc[0]['비밀번호']).strip():
                st.session_state.update({'auth':True, 'user':n.strip(), 'ldr':str(u.iloc[0]['리더여부']).upper(), 'lang':str(u.iloc[0]['언어'])})
                if str(p).strip() == INITIAL_PW: st.session_state.need_pw_change = True
                st.rerun()
            else: st.error("로그인 실패")
    else:
        L, user = UI[st.session_state.lang], st.session_state.user
        if st.sidebar.button(L["logout"]): st.session_state.clear(); st.rerun()
        
        m_list = []
        if user != "김용환": m_list.append(L["m1"])
        if st.session_state.ldr == 'Y': m_list.append(L["m5"])
        t2_list = db_users[db_users['2차평가자'] == user]['성명'].tolist()
        if t2_list: m_list.append(L["m2"])
        if user == "권정순": m_list.append(L["m4"])
        
        menu = st.sidebar.radio("Menu", m_list)
        # [수정] 제목(Title)을 먼저 출력하여 화면이 로딩됨을 표시
        if menu == L["m1"]: st.title(L["m1"]); render_engine(EVAL_DATA[st.session_state.lang], "self", target_name=user)
        elif menu == L["m5"]: st.title(L["m5"]); render_engine(LEADER_DATA["KO"], "ld_self", eval_type="리더십", ws_name="Leadership_Results", target_name=user)
        elif menu == L["m2"]: st.title(L["m2"]); target = st.selectbox("대상 선택", t2_list); render_engine(EVAL_DATA[st.session_state.lang], "peer2", eval_type="2차팀원", target_name=target)
        elif menu == L["m4"]:
            st.title("📊 Admin Dashboard"); st.write("### [Results]"); st.dataframe(get_results_data("Results"), use_container_width=True)
            st.write("### [Leadership]"); st.dataframe(get_results_data("Leadership_Results"), use_container_width=True)
else:
    st.error("데이터 로딩 실패")
