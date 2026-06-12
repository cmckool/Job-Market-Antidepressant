import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -------------------------------------------------------
# Page setup
# -------------------------------------------------------

st.set_page_config(
    page_title="Antidepressant Use & Job Market Dashboard",
    page_icon="📊",
    layout="wide"
)

# -------------------------------------------------------
# File paths
# -------------------------------------------------------

DATA_DIR = Path("antidepressant_Job_project/final_project_data")

FINAL_DATA_PATH = DATA_DIR / "final_antidepressant_job_occupation_dataset.csv"
CHANGE_SUMMARY_PATH = DATA_DIR / "change_summary_by_gender.csv"
CORRELATION_SUMMARY_PATH = DATA_DIR / "correlation_summary_by_gender.csv"

# -------------------------------------------------------
# Load data
# -------------------------------------------------------

@st.cache_data
def load_data():
    final_df = pd.read_csv(FINAL_DATA_PATH)
    change_df = pd.read_csv(CHANGE_SUMMARY_PATH)
    corr_df = pd.read_csv(CORRELATION_SUMMARY_PATH)

    return final_df, change_df, corr_df


try:
    final_df, change_df, corr_df = load_data()
except FileNotFoundError as e:
    st.error("One or more required data files are missing.")
    st.write("Make sure these files exist inside the `final_project_data` folder:")
    st.code(
        """
final_project_data/final_antidepressant_job_occupation_dataset.csv
final_project_data/change_summary_by_gender.csv
final_project_data/correlation_summary_by_gender.csv
        """
    )
    st.stop()

# -------------------------------------------------------
# Title / intro
# -------------------------------------------------------

st.title("Antidepressant Use, Job Market Stress, and Gendered Occupation Trends")

st.markdown(
    """
This dashboard explores changes in selected antidepressant use among U.S. adults ages **20–35**
and compares those trends with unemployment rates and participation in nontraditional gender occupations.

The project uses three public data sources:

- **NHANES** prescription medication data
- **BLS** unemployment data
- **IPUMS CPS** occupation data
"""
)

# -------------------------------------------------------
# Sidebar filters
# -------------------------------------------------------

st.sidebar.header("Filters")

gender_options = sorted(final_df["gender"].dropna().unique())

selected_gender = st.sidebar.multiselect(
    "Select gender",
    options=gender_options,
    default=gender_options
)

min_year = int(final_df["match_year"].min())
max_year = int(final_df["match_year"].max())

selected_year_range = st.sidebar.slider(
    "Select year range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

filtered_df = final_df[
    (final_df["gender"].isin(selected_gender)) &
    (final_df["match_year"] >= selected_year_range[0]) &
    (final_df["match_year"] <= selected_year_range[1])
].copy()

# -------------------------------------------------------
# KPI cards
# -------------------------------------------------------

st.subheader("Project Snapshot")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Cycles Included", filtered_df["cycle"].nunique())

with col2:
    st.metric("Years Covered", f"{selected_year_range[0]}–{selected_year_range[1]}")

with col3:
    avg_antidepressant = filtered_df["percent_using_target_antidepressant"].mean()
    st.metric("Avg Antidepressant Use", f"{avg_antidepressant:.2f}%")

with col4:
    avg_unemployment = filtered_df["approx_unemployment_rate_20_34"].mean()
    st.metric("Avg Unemployment Rate", f"{avg_unemployment:.2f}%")



# -------------------------------------------------------
# Main dashboard graphs
# -------------------------------------------------------

st.subheader("1. Antidepressant Use Over Time by Gender")

fig_antidepressant = px.line(
    filtered_df,
    x="match_year",
    y="percent_using_target_antidepressant",
    color="gender",
    markers=True,
    hover_data=["cycle"],
    title="Selected Antidepressant Use Among Adults Ages 20–35 by Gender"
)

fig_antidepressant.update_layout(
    xaxis_title="Year",
    yaxis_title="Percent Using Selected Antidepressants",
    legend_title="Gender"
)

st.plotly_chart(fig_antidepressant, use_container_width=True)


st.subheader("2. Unemployment Rate Over Time by Gender")

fig_unemployment = px.line(
    filtered_df,
    x="match_year",
    y="approx_unemployment_rate_20_34",
    color="gender",
    markers=True,
    hover_data=["cycle"],
    title="Approximate Unemployment Rate Ages 20–34 by Gender"
)

fig_unemployment.update_layout(
    xaxis_title="Year",
    yaxis_title="Unemployment Rate (%)",
    legend_title="Gender"
)

st.plotly_chart(fig_unemployment, use_container_width=True)


st.subheader("3. Nontraditional Gender Occupation Participation Over Time")

fig_jobs = px.line(
    filtered_df,
    x="match_year",
    y="percent_in_nontraditional_jobs",
    color="gender",
    markers=True,
    hover_data=["cycle"],
    title="Workers Ages 20–35 in Nontraditional Gender Occupations"
)

fig_jobs.update_layout(
    xaxis_title="Year",
    yaxis_title="Percent in Nontraditional Gender Occupations",
    legend_title="Gender"
)

st.plotly_chart(fig_jobs, use_container_width=True)


# -------------------------------------------------------
# Three metric trend by gender
# -------------------------------------------------------

st.subheader("4. Three-Metric Trend by Gender")

gender_single = st.selectbox(
    "Select one gender for combined trend view",
    options=gender_options
)

gender_df = filtered_df[filtered_df["gender"] == gender_single].copy()

three_metric_df = gender_df[
    [
        "match_year",
        "cycle",
        "percent_using_target_antidepressant",
        "approx_unemployment_rate_20_34",
        "percent_in_nontraditional_jobs"
    ]
].melt(
    id_vars=["match_year", "cycle"],
    var_name="metric",
    value_name="percent"
)

three_metric_df["metric"] = three_metric_df["metric"].map({
    "percent_using_target_antidepressant": "Antidepressant Use %",
    "approx_unemployment_rate_20_34": "Unemployment Rate %",
    "percent_in_nontraditional_jobs": "Nontraditional Jobs %"
})

fig_three = px.line(
    three_metric_df,
    x="match_year",
    y="percent",
    color="metric",
    markers=True,
    hover_data=["cycle"],
    title=f"{gender_single}: Antidepressant Use, Unemployment, and Nontraditional Jobs"
)

fig_three.update_layout(
    xaxis_title="Year",
    yaxis_title="Percent",
    legend_title="Metric"
)

st.plotly_chart(fig_three, use_container_width=True)


# -------------------------------------------------------
# Relationship charts
# -------------------------------------------------------

st.subheader("5. Relationship Charts")

col1, col2 = st.columns(2)

with col1:
    fig_scatter_unemployment = px.scatter(
        filtered_df,
        x="approx_unemployment_rate_20_34",
        y="percent_using_target_antidepressant",
        color="gender",
        text="cycle",
        hover_data=["match_year"],
        title="Antidepressant Use vs Unemployment Rate"
    )

    fig_scatter_unemployment.update_traces(
        textposition="top center"
    )

    fig_scatter_unemployment.update_layout(
        xaxis_title="Unemployment Rate Ages 20–34 (%)",
        yaxis_title="Antidepressant Use Ages 20–35 (%)",
        legend_title="Gender"
    )

    st.plotly_chart(fig_scatter_unemployment, use_container_width=True)

with col2:
    fig_scatter_jobs = px.scatter(
        filtered_df,
        x="percent_in_nontraditional_jobs",
        y="percent_using_target_antidepressant",
        color="gender",
        text="cycle",
        hover_data=["match_year"],
        title="Antidepressant Use vs Nontraditional Job Participation"
    )

    fig_scatter_jobs.update_traces(
        textposition="top center"
    )

    fig_scatter_jobs.update_layout(
        xaxis_title="Nontraditional Gender Occupations (%)",
        yaxis_title="Antidepressant Use Ages 20–35 (%)",
        legend_title="Gender"
    )

    st.plotly_chart(fig_scatter_jobs, use_container_width=True)


# -------------------------------------------------------
# Optional metric selector for exploration
# -------------------------------------------------------

st.subheader("6. Explore Any Metric")

metric_choice = st.selectbox(
    "Choose a metric to explore",
    [
        "percent_using_target_antidepressant",
        "approx_unemployment_rate_20_34",
        "percent_in_nontraditional_jobs"
    ],
    format_func=lambda x: {
        "percent_using_target_antidepressant": "Antidepressant Use %",
        "approx_unemployment_rate_20_34": "Unemployment Rate %",
        "percent_in_nontraditional_jobs": "Nontraditional Jobs %"
    }[x]
)

metric_titles = {
    "percent_using_target_antidepressant": "Antidepressant Use Among Ages 20–35",
    "approx_unemployment_rate_20_34": "Approximate Unemployment Rate Ages 20–34",
    "percent_in_nontraditional_jobs": "Workers Ages 20–35 in Nontraditional Gender Occupations"
}

fig_metric = px.line(
    filtered_df,
    x="match_year",
    y=metric_choice,
    color="gender",
    markers=True,
    hover_data=["cycle"],
    title=metric_titles[metric_choice]
)

fig_metric.update_layout(
    xaxis_title="Year",
    yaxis_title="Percent",
    legend_title="Gender"
)

st.plotly_chart(fig_metric, use_container_width=True)



# -------------------------------------------------------
# Summary tables
# -------------------------------------------------------

st.subheader("Summary Tables")

tab1, tab2, tab3 = st.tabs(
    [
        "Final Dataset",
        "Change Summary",
        "Correlation Summary"
    ]
)

with tab1:
    st.write("Final merged dataset:")
    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download filtered dataset",
        data=csv,
        file_name="filtered_antidepressant_job_dataset.csv",
        mime="text/csv"
    )

with tab2:
    st.write("Change from first cycle to last cycle by gender:")
    st.dataframe(change_df, use_container_width=True)

with tab3:
    st.write("Correlation summary by gender:")
    st.dataframe(corr_df, use_container_width=True)





# -------------------------------------------------------
# Limitations
# -------------------------------------------------------

st.subheader("Limitations")

st.markdown(
    """
- This analysis shows **relationships and trends**, not causation.
- NHANES data is organized by survey cycles, not every single year.
- The BLS unemployment comparison uses ages **20–34**, while the antidepressant analysis uses ages **20–35**.
- The occupation analysis depends on how occupations are coded and classified over time.
- The antidepressant analysis focuses only on selected SSRI drugs: fluoxetine, sertraline, escitalopram, citalopram, and paroxetine.
"""

