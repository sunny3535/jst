import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import platform
import matplotlib.font_manager as fm
from matplotlib import rc


# 한글 폰트 설정 (예: 맑은 고딕)
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows 기준
plt.rcParams['axes.unicode_minus'] = False     # 마이너스 기호 깨짐 방지

# 깃허브 리눅스 기준
if platform.system() == 'Linux':
    fontname = './NanumGothic.ttf'
    font_files = fm.findSystemFonts(fontpaths=fontname)
    rc('font', family='NanumGothic')


st.set_page_config(page_title="전라북도 병원 정보 분석", layout="wide")

st.title("🏥 전라북도 병원정보 탐색적 데이터 분석")

# ✅ CSV 파일 직접 로드 (같은 폴더에 있는 파일)
@st.cache_data
def load_data():
    df = pd.read_csv("D:\\jst\\전라북도_병원정보.csv")
    # 제거할 열 목록
    drop_cols = [
        "암호화요양기호", "종별코드", "시도코드", "시군구코드", "우편번호", "주소",
        "병원홈페이지", "전화번호", "개설일자"
    ]

    # 실제 존재하는 컬럼만 제거
    existing_drop_cols = [col for col in drop_cols if col in df.columns]
    df = df.drop(columns=existing_drop_cols)

    return df

df = load_data()

# 데이터 기본 정보
st.subheader("📋 데이터 미리보기")
st.write(f"데이터 크기: {df.shape[0]} rows × {df.shape[1]} columns")
st.dataframe(df.head())

# 병원종별 필터링
st.sidebar.header("🔍 필터")
types = sorted(df["종별코드명"].dropna().unique())
selected_types = st.sidebar.multiselect("병원 종류 선택", types, default=types)

filtered_df = df[df["종별코드명"].isin(selected_types)]

# 시군구별 병원 수
st.subheader("📊 시군구별 병원 수")
area_counts = filtered_df["시군구코드명"].value_counts().sort_values(ascending=False)
st.bar_chart(area_counts)


# 인원수 관련 컬럼 식별
staff_cols = [col for col in df.columns if "인원수" in col]

# Streamlit Tabs
tab1, tab2 = st.tabs(["🏥 병원 종류 비율", "👩‍⚕️ 의료 인력 비율"])

with tab1:
    st.subheader("병원 종류별 비율")
    type_counts = df["종별코드명"].value_counts()
    
    fig1, ax1 = plt.subplots()
    ax1.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%', startangle=140)
    ax1.axis('equal')
    st.pyplot(fig1)

with tab2:
    st.subheader("의료 인력 종류별 비율")
    
    # 분야별 인원수 집계
    def safe_sum(cols):
        return df[cols].sum().sum() if all(col in df.columns for col in cols) else 0

    field_counts = {
        "일반의료": safe_sum(["의과일반의 인원수", "의과인턴 인원수", "의과레지던트 인원수", "의과전문의 인원수"]),
        "치과": safe_sum(["치과일반의 인원수", "치과인턴 인원수", "치과레지던트 인원수", "치과전문의 인원수"]),
        "한방": safe_sum(["한방일반의 인원수", "한방인턴 인원수", "한방레지던트 인원수", "한방전문의 인원수"]),
        "조산사": safe_sum(["조산사 인원수"])
    }

    # 값이 0보다 큰 것만 표시
    field_counts = {k: v for k, v in field_counts.items() if v > 0}

    fig2, ax2 = plt.subplots()
    ax2.pie(field_counts.values(), labels=field_counts.keys(), autopct='%1.1f%%', startangle=140)
    ax2.axis('equal')
    st.pyplot(fig2)


# 의료 인력 현황
st.subheader("👨‍⚕️ 의료 인력 분포")
staff_cols = [col for col in df.columns if "인원수" in col]
staff_sum = filtered_df[staff_cols].sum().sort_values(ascending=False)
fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.barplot(x=staff_sum.values, y=staff_sum.index, ax=ax2)
ax2.set_title("전라북도 의료 인력 수")
ax2.set_xlabel("인원 수", fontsize=12)
ax2.set_ylabel("직군", fontsize=12)
st.pyplot(fig2)



# 지도 시각화 (Streamlit 기본)
st.subheader("🗺️ 병원 위치 지도")
# 좌표 컬럼이 있는지 확인
if "좌표(X)" in df.columns and "좌표(Y)" in df.columns:
    map_df = df.dropna(subset=["좌표(X)", "좌표(Y)"]).copy()
    map_df.rename(columns={"좌표(Y)": "latitude", "좌표(X)": "longitude"}, inplace=True)

    # 최신 scatter_map 사용
    fig = px.scatter_map(
        map_df,
        lat="latitude",
        lon="longitude",
        hover_name="요양기관명",
        hover_data=["종별코드명", "시군구코드명"],
        color="종별코드명",
        zoom=8,
        center={"lat": 35.82, "lon": 127.15},
        height=600
    )

    st.plotly_chart(fig)

else:
    st.error("❌ 좌표 정보(좌표(X), 좌표(Y))가 누락되었습니다.")


@st.cache_data
def load_population_data():
    df = pd.read_csv("D:\\jst\\202505_202505_연령별인구현황_월간.csv", encoding='euc-kr')

    # 전라북도 전체(코드 5200000000) 제외
    df = df[~df["행정구역"].str.contains("5200000000")].copy()
    df = df[~df["행정구역"].str.contains("5211000000")].copy()

    # 총 인구수 숫자형으로 변환
    df["총 인구수"] = df["총 인구수"].str.replace(",", "").astype(int)

    # 지역명 정리
    df["지역"] = df["행정구역"].str.extract(r'전북특별자치도\s*(.*)\s*\(')[0].fillna("기타")
    return df[["지역", "총 인구수"]]

# 데이터 로드
pop_df = load_population_data()
pop_df = pop_df.rename(columns={"지역": "시군구"})
pop_df["시군구"] = pop_df["시군구"].str.replace("전주시 덕진구", "전주덕진구")
pop_df["시군구"] = pop_df["시군구"].str.replace("전주시 완산구", "전주완산구")
pop_df["시군구"] = pop_df["시군구"].str.strip()


# 병원 데이터에서 시군구 병원 수 집계
hosp_by_region = df["시군구코드명"].value_counts().reset_index()
hosp_by_region.columns = ["시군구", "병원수"]
hosp_by_region["시군구"] = hosp_by_region["시군구"].str.strip()

# 의료 인력 집계 (시군구별)
staff_cols = [col for col in df.columns if "인원수" in col]
staff_by_region = df.groupby("시군구코드명")[staff_cols].sum()
staff_by_region["의료인력수"] = staff_by_region.sum(axis=1)
staff_by_region = staff_by_region[["의료인력수"]].reset_index()
staff_by_region.columns = ["시군구", "의료인력수"]

# 병원 + 인력 데이터 병합
merged = pd.merge(hosp_by_region, staff_by_region, on="시군구", how="outer")
merged = pd.merge(merged, pop_df, on="시군구", how="left", validate="one_to_one")

# 비율 계산
merged["인구 10만명당 병원 수"] = merged["병원수"] / merged["총 인구수"] * 100000
merged["인구 10만명당 의료인력 수"] = merged["의료인력수"] / merged["총 인구수"] * 100000

# Streamlit Tabs
tab1, tab2, tab3 = st.tabs(["🏥 시군별 병원 수", "🏥 인구 대비 병원 수", "👩‍⚕️ 인구 대비 의료 인력 수"])


with tab1:
    st.subheader("시군구별 병원 수")
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.bar(merged["시군구"], merged["병원수"], color="skyblue")
    ax1.set_ylabel("병원 수")
    ax1.set_xticklabels(merged["시군구"], rotation=45, ha="right")
    st.pyplot(fig1)

with tab2:
    st.subheader("시군구별 인구 10만명당 병원 수")
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    ax2.bar(merged["시군구"], merged["인구 10만명당 병원 수"], color="orange")
    ax2.set_ylabel("병원 수 (per 100,000명)")
    ax2.set_xticklabels(merged["시군구"], rotation=45, ha="right")
    st.pyplot(fig2)

with tab3:
    st.subheader("시군구별 인구 10만명당 의료 인력 수")
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    ax3.bar(merged["시군구"], merged["인구 10만명당 의료인력 수"], color="seagreen")
    ax3.set_ylabel("의료 인력 수 (per 100,000명)")
    ax3.set_xticklabels(merged["시군구"], rotation=45, ha="right")
    st.pyplot(fig3)

# 시사점 요약
st.markdown("---")
st.header("📝 시사점 요약")

st.markdown("""
- 📍 **전주시, 익산시** 등 주요 도시를 중심으로 병원 수와 의료 인력이 집중되어 있습니다.
- 📉 **무주군, 완주군, 장수군** 등 농촌·산간 지역은 상대적으로 병원 수와 의료 인력 수가 매우 적습니다.
- 👩‍⚕️ 임실군은 인구 대비 병원수는 많지만 의료 인력수가 적은 것으로 보아 개인 병원이 많은 것으로 보입니다. 
- 🏥 인구 10만명당 병원 수 또는 의료 인력 수를 기준으로 보면 일부 지역은 **의료 접근성이 크게 제한될 가능성**이 있습니다.
- ⚠️ 이러한 지역 간 불균형은 **고령화** 및 **응급 의료 대응** 측면에서 정책적 보완이 필요함을 시사합니다.
- 🔎 추가적으로 병원 종류나 특정 진료과목 분포 분석을 통해 **전문 진료 서비스의 지역별 편차**도 파악할 수 있습니다.
""")