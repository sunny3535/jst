import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Load data
df = pd.read_csv("농림식품기술기획평가원_농림식품RnD 계속과제 정보_20241231.csv", encoding='cp949')
df.columns = df.columns.str.strip()  # Remove whitespace from column names

st.set_page_config(layout="wide")
st.title("농림식품 R&D 계속과제 분석 대시보드")

# Sidebar Filters
st.sidebar.header("🔍 필터 선택")
사업_options = st.sidebar.multiselect("세부사업명", sorted(df['세부사업명'].unique()))
기관_options = st.sidebar.multiselect("연구기관명", sorted(df['연구기관명'].unique()))

min_budget, max_budget = int(df['총 연구개발비'].min()), int(df['총 연구개발비'].max())
selected_budget = st.sidebar.slider("총 연구개발비 범위", min_budget, max_budget, (min_budget, max_budget))

keyword = st.sidebar.text_input("과제명 키워드 검색")

# Data Filtering
filtered_df = df.copy()
if 사업_options:
    filtered_df = filtered_df[filtered_df['세부사업명'].isin(사업_options)]
if 기관_options:
    filtered_df = filtered_df[filtered_df['연구기관명'].isin(기관_options)]
filtered_df = filtered_df[
    (filtered_df['총 연구개발비'] >= selected_budget[0]) & 
    (filtered_df['총 연구개발비'] <= selected_budget[1])
]
if keyword:
    filtered_df = filtered_df[filtered_df['연구개발과제명'].str.contains(keyword, case=False, na=False)]

# Show filtered data
st.subheader(f"📊 필터링된 과제 수: {len(filtered_df)}개")
st.dataframe(filtered_df, use_container_width=True)

# Charts
st.subheader("📈 예산 분포 시각화")
budget_fig = px.histogram(filtered_df, x='총 연구개발비', nbins=30, title="총 연구개발비 분포")
st.plotly_chart(budget_fig, use_container_width=True)

box_fig = px.box(filtered_df, y='총 연구개발비', points="all", title="총 연구개발비 박스플롯")
st.plotly_chart(box_fig, use_container_width=True)

# Bar Chart of top research institutions
st.subheader("🏢 연구기관별 과제 수 (Top 10)")
top_institutes = filtered_df['연구기관명'].value_counts().nlargest(10)
st.bar_chart(top_institutes)

# Pie chart for 사업명 분포
st.subheader("📌 세부사업명 구성 비율")
사업_counts = filtered_df['세부사업명'].value_counts().reset_index()
사업_counts.columns = ['세부사업명', '건수']
pie_fig = px.pie(사업_counts, values='건수', names='세부사업명')
st.plotly_chart(pie_fig, use_container_width=True)

# File download
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 필터링된 데이터 다운로드",
    data=filtered_df.to_csv(index=False).encode('cp949'),
    file_name='filtered_rnd_data.csv',
    mime='text/csv'
)

st.markdown("---")
st.caption("데이터 출처: 농림식품기술기획평가원")

# Insights Section
st.markdown("## 📌 주요 인사이트")
st.markdown("""
- **예산 분포**: 대부분의 과제는 비교적 적은 예산 범위에 집중되어 있으며, 일부 대형 프로젝트가 높은 예산을 차지하고 있음
- **기관 집중도**: 특정 연구기관에 과제가 집중되어 있는 경향이 있으며, 상위 10개 기관이 전체 과제의 큰 비중을 차지함
- **사업 다양성**: 세부사업명이 다양하게 분포되어 있으며, 일부 사업은 다른 사업에 비해 훨씬 더 많은 과제를 보유하고 있음
- **검색 기능 유용성**: 특정 키워드를 통해 유사한 주제의 과제들을 빠르게 찾을 수 있음
""")
