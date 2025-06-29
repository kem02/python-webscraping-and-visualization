import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3


def load_data():
    conn = sqlite3.connect("mlb_stats.db")
    batting = pd.read_sql_query("SELECT * FROM batting_avg", conn)
    homerun = pd.read_sql_query("SELECT * FROM home_runs", conn)
    strikeout = pd.read_sql_query("SELECT * FROM career_strikeouts", conn)
    conn.close()
    return batting, homerun, strikeout


df_batting, df_home, df_strike = load_data()

# ——— Sidebar Filters ———
st.sidebar.header("Filters")
top_n_hr = st.sidebar.slider("Top N Home-Run Hitters", 1, 20, 10)
available_leagues = df_batting["League"].unique().tolist()
selected_leagues = st.sidebar.multiselect(
    "Leagues to Include", options=available_leagues, default=available_leagues
)
min_avg = st.sidebar.slider(
    "Minimum Batting Average",
    float(df_batting["Batting_Average"].min()),
    float(df_batting["Batting_Average"].max()),
    float(df_batting["Batting_Average"].quantile(0.5)),
)
top_n_players = st.sidebar.slider(
    "Top N Players by Avg", 1, len(df_batting["Name"].unique()), 20
)

# ——— Main Page ———
st.title("MLB Stats")

# Bar chart of top career home-run hitters
st.subheader("All-Time Home-Run Leaders")
hr_top = df_home.sort_values("Career_Home_Runs", ascending=False).head(top_n_hr)
fig_hr = px.bar(
    hr_top,
    x="Name",
    y="Career_Home_Runs",
    labels={"Name": "Player", "Career_Home_Runs": "Home Runs"},
)
st.plotly_chart(fig_hr, use_container_width=True)

# Line chart of cumulative batting-average records over time
st.subheader("Record-Break Count Over Time")
df_sorted = df_batting.sort_values("Year")
df_sorted["Cumulative Records"] = range(1, len(df_sorted) + 1)
records_df = df_sorted.set_index("Year")[["Cumulative Records"]]
records_df.index = records_df.index.astype(str)
st.line_chart(records_df, x_label="Season Year", y_label="Total Records Broken")

# Pie chart showing share of batting records by league
st.subheader("Records by League")
league_counts = df_batting["League"].value_counts().reset_index()
league_counts.columns = ["League", "Count"]
fig_pie = px.pie(league_counts, names="League", values="Count")
st.plotly_chart(fig_pie, use_container_width=True)

# Sunburst chart of best batting averages by league, team, and player
st.subheader("Top Batting Averages by League → Team → Player")
best_per_player = df_batting.sort_values(
    "Batting_Average", ascending=False
).drop_duplicates(subset="Name")
filtered = best_per_player[
    best_per_player["League"].isin(selected_leagues)
    & (best_per_player["Batting_Average"] >= min_avg)
].nlargest(top_n_players, "Batting_Average")
fig_sunburst = px.sunburst(
    filtered,
    path=["League", "Team", "Name"],
    values="Batting_Average",
    hover_data=["Year"],
)
st.plotly_chart(fig_sunburst, use_container_width=True)
