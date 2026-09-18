# ============================================================
# EURO 2024 - SHOT ANALYSIS DASHBOARD
# ============================================================

# ============================================================
# 1. IMPORT LIBRARIES
# ============================================================

import streamlit as st
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import VerticalPitch


# ============================================================
# 2. APP TITLE & DESCRIPTION
# ============================================================

st.title("Euro 2024 Shot Analysis Dashboard")

st.subheader(
    "Explore shot locations, shot quality, outcomes, and distance "
    "for teams and players"
)
st.caption("Own goals are not included in the analysis.")


# ============================================================
# 3. LOAD THE DATA
# ============================================================

df = pd.read_csv("euros_2024_shot_map.csv")


# ============================================================
# 4. DATA PREPARATION / CLEANING
# ============================================================

# Keep only events that are shots
# Exclude period 5 because it represents penalty shootouts
df = df[
    (df["type"] == "Shot") &
    (df["period"] != 5)
].reset_index(drop=True)


# Convert location from a string into a Python list
# Example:
# "[102, 35]" → [102, 35]

df["location"] = df["location"].apply(json.loads)


# Extract X coordinate
df["x"] = df["location"].apply(
    lambda loc: loc[0]
)


# Extract Y coordinate
df["y"] = df["location"].apply(
    lambda loc: loc[1]
)


# ============================================================
# 5. CALCULATE SHOT DISTANCE
# ============================================================

# Calculate the distance between the shot location
# and the center of the opponent's goal.
#
# StatsBomb pitch coordinates represent a pitch of
# approximately 120m x 80m.
#
# The center of the opponent's goal is approximately:
# X = 120
# Y = 40

df["shot_distance"] = np.sqrt(
    (120 - df["x"]) ** 2 +
    (40 - df["y"]) ** 2
)


# ============================================================
# 6. CLASSIFY SHOTS INTO DISTANCE ZONES
# ============================================================

def classify_distance(distance):

    if distance < 12:
        return "Close"

    elif distance < 20:
        return "Medium"

    else:
        return "Long"


df["shot_zone"] = df["shot_distance"].apply(
    classify_distance
)


# ============================================================
# 7. CLASSIFY SHOTS INTO xG ZONES
# ============================================================

def classify_xg(xg):

    if xg < 0.05:
        return "Very Low"

    elif xg < 0.15:
        return "Low"

    elif xg < 0.30:
        return "Medium"

    else:
        return "High"


df["xg_zone"] = df["shot_statsbomb_xg"].apply(
    classify_xg
)


# ============================================================
# 8. USER FILTERS
# ============================================================

# -------------------------
# Team selection
# -------------------------

team = st.selectbox(
    "Select a team",
    df["team"].sort_values().unique(),
    index=None
)


# -------------------------
# Player selection
# -------------------------

# Only display players from the selected team

if team:

    available_players = (
        df[df["team"] == team]["player"]
        .dropna()
        .sort_values()
        .unique()
    )

else:

    available_players = []


player = st.selectbox(
    "Select a player",
    available_players,
    index=None
)


# ============================================================
# 9. FILTER FUNCTION
# ============================================================

def filter_data(
    df: pd.DataFrame,
    team: str,
    player: str
):

    # Filter by team
    if team:
        df = df[df["team"] == team]

    # Filter by player
    if player:
        df = df[df["player"] == player]

    return df


# Apply filters
filtered_df = filter_data(
    df,
    team,
    player
)


# ============================================================
# 10. SHOT OUTCOME FILTER
# ============================================================

# Get all available shot outcomes

outcomes = sorted(
    filtered_df["shot_outcome"]
    .dropna()
    .unique()
)


# Allow the user to select multiple outcomes

selected_outcomes = st.multiselect(
    "Select shot outcomes",
    outcomes,
    default=outcomes
)


# Keep only selected outcomes

filtered_df = filtered_df[
    filtered_df["shot_outcome"].isin(
        selected_outcomes
    )
]


# ============================================================
# 11. KEY PERFORMANCE INDICATORS
# ============================================================

# Total number of shots

shots = len(filtered_df)


# Number of goals

goals = (
    filtered_df["shot_outcome"] == "Goal"
).sum()


# Number of penalty goals

penalty_goals = (
    (filtered_df["shot_outcome"] == "Goal") &
    (
        filtered_df["shot_type"]
        .str.contains(
            "Penalty",
            case=False,
            na=False
        )
    )
).sum()


# Total expected goals

total_xg = (
    filtered_df["shot_statsbomb_xg"].sum()
)


# Conversion rate = Goals / Shots

conversion = (
    goals / shots
) if shots else 0


# Average xG per shot

xg_per_shot = (
    total_xg / shots
) if shots else 0


# Goals compared to expected goals

goals_vs_xg = (
    goals - total_xg
)


# Average shot distance

avg_distance = (
    filtered_df["shot_distance"].mean()
) if shots else 0


# ============================================================
# 12. DISPLAY KPI SUMMARY
# ============================================================

st.subheader("Selected Shots Summary")


metric_cols_top = st.columns(4)
metric_cols_bottom = st.columns(3)


metric_cols_top[0].metric(
    "Shots",
    f"{shots}"
)


metric_cols_top[1].metric(
    "Goals",
    f"{goals}"
)


metric_cols_top[2].metric(
    "xG",
    f"{total_xg:.2f}"
)


metric_cols_top[3].metric(
    "Conversion",
    f"{conversion:.1%}"
)


metric_cols_bottom[0].metric(
    "Goals - xG",
    f"{goals_vs_xg:.2f}"
)


metric_cols_bottom[1].metric(
    "Avg Shot Distance",
    f"{avg_distance:.1f} m"
)


metric_cols_bottom[2].metric(
    "Penalty Goals",
    f"{penalty_goals}"
)


# ============================================================
# 13. INTERACTIVE SHOT MAP VISUALIZATION (PLOTLY)
# ============================================================
import plotly.graph_objects as go

st.subheader("🗺️ Interactive Shot Map")
st.caption("Hover over any shot to see the player, outcome, and xG value.")

def draw_interactive_pitch(df):
    fig = go.Figure()

    # --------------------------------------------------------
    # 1. DRAW THE PITCH GEOMETRY (layer="below" keeps markers on top)
    # --------------------------------------------------------
    fig.add_shape(type="rect", x0=80, y0=60, x1=0, y1=120, fillcolor="#2b8a44", line=dict(color="white", width=1.5), layer="below")
    fig.add_shape(type="rect", x0=62, y0=102, x1=18, y1=120, line=dict(color="white", width=1.5), layer="below")
    fig.add_shape(type="rect", x0=50, y0=114, x1=30, y1=120, line=dict(color="white", width=1.5), layer="below")
    fig.add_shape(type="rect", x0=44, y0=120, x1=36, y1=122, line=dict(color="white", width=2), layer="below")
    fig.add_shape(type="circle", x0=40.5, y0=107.5, x1=39.5, y1=108.5, fillcolor="white", line=dict(color="white"), layer="below")
    fig.add_shape(type="circle", x0=50, y0=50, x1=30, y1=70, line=dict(color="white", width=1.5), layer="below")
    fig.add_shape(type="path", path="M 48 102 A 10 10 0 0 0 32 102", line=dict(color="white", width=1.5), layer="below")

    # --------------------------------------------------------
    # 2. PREPARE THE DATA FOR PLOTTING
    # --------------------------------------------------------
    plot_df = df.copy()
    plot_df["is_goal"] = (plot_df["shot_outcome"] == "Goal")
    plot_df = plot_df.sort_values(by="is_goal")

    def get_plotly_color(row):
        if row["shot_outcome"] == "Goal": return "blue"
        elif row["xg_zone"] == "High": return "red"
        elif row["xg_zone"] == "Medium": return "orange"
        elif row["xg_zone"] == "Low": return "white"
        return "lightgray"

    plot_df["color"] = plot_df.apply(get_plotly_color, axis=1)
    plot_df["size"] = np.maximum(8, plot_df["shot_statsbomb_xg"] * 35)

    # --------------------------------------------------------
    # 3. ADD THE INTERACTIVE SHOTS (WITH TOOLTIPS)
    # --------------------------------------------------------
    if not plot_df.empty:
        fig.add_trace(go.Scatter(
            x=plot_df["y"],
            y=plot_df["x"],
            mode="markers",
            marker=dict(
                size=plot_df["size"],
                color=plot_df["color"],
                line=dict(width=1, color="black"),
                opacity=0.95
            ),
            text="<b>" + plot_df["player"].astype(str) + "</b><br>" +
                 "Outcome: " + plot_df["shot_outcome"].astype(str) + "<br>" +
                 "xG: " + plot_df["shot_statsbomb_xg"].round(2).astype(str),
            hoverinfo="text",
            showlegend=False  # Hide the default trace legend
        ))

    # --------------------------------------------------------
    # 4. ADD THE LEGEND (DUMMY TRACES)
    # --------------------------------------------------------
    legend_items = [
        {"name": "Goal", "color": "blue"},
        {"name": "High xG (≥ 0.30)", "color": "red"},
        {"name": "Medium xG (0.15–0.29)", "color": "orange"},
        {"name": "Low xG (0.05–0.14)", "color": "white"},
        {"name": "Very Low xG (< 0.05)", "color": "lightgray"}
    ]

    # Add invisible points just to generate the legend labels
    for item in legend_items:
        fig.add_trace(go.Scatter(
            x=[None], y=[None], 
            mode="markers",
            marker=dict(size=10, color=item["color"], line=dict(width=1, color="black")),
            name=item["name"],
            showlegend=True
        ))

    # --------------------------------------------------------
    # 5. CONFIGURE MAP LAYOUT & LOCK ZOOM
    # --------------------------------------------------------
    fig.update_layout(
        xaxis=dict(range=[80, 0], showgrid=False, zeroline=False, visible=False, fixedrange=True),
        yaxis=dict(range=[60, 122], showgrid=False, zeroline=False, visible=False, fixedrange=True),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=550,
        
        # Position and style the legend
        legend=dict(
            yanchor="top",
            y=0.98,
            xanchor="right",
            x=0.98,
            bgcolor="rgba(255, 255, 255, 0.85)",
            bordercolor="black",
            borderwidth=1,
            font=dict(size=10, color="black")
        )
    )
    
    return fig

# Render the interactive map on screen and hide the Plotly toolbar
st.plotly_chart(
    draw_interactive_pitch(filtered_df), 
    use_container_width=True,
    config={'displayModeBar': False}
)
# ============================================================
# 14. SHOT OUTCOME ANALYSIS
# ============================================================

outcome_stats = (
    filtered_df
    .groupby("shot_outcome")
    .agg(
        Shots=(
            "shot_outcome",
            "size"
        ),

        xG=(
            "shot_statsbomb_xg",
            "sum"
        )
    )
    .reset_index()
)


# Round xG
outcome_stats["xG"] = (
    outcome_stats["xG"]
    .round(2)
)

st.subheader("Shot Outcome Statistics")

st.dataframe(
    outcome_stats,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 15. GLOBAL TEAM OVERVIEW
# ============================================================

st.divider()
st.subheader("📊 Global Team Overview")
st.caption("A summary of all teams across the tournament (Unfiltered).")

team_overview = (
    df
    .groupby("team")
    .agg(
        Total_Goals=("shot_outcome", lambda x: (x == "Goal").sum()),
        Total_xG=("shot_statsbomb_xg", "sum"),
        Matches=("match_id", "nunique"),
    )
    .reset_index()
    .sort_values(["Total_Goals", "Total_xG"], ascending=False)
)

team_overview_display = team_overview.rename(
    columns={
        "team": "Team",
        "Total_Goals": "Total Goals",
        "Total_xG": "Total xG",
        "Matches": "Matches",
    }
)

team_overview_display["Total xG"] = team_overview_display["Total xG"].map(
    lambda value: f"{value:.2f}"
)

st.dataframe(
    team_overview_display,
    use_container_width=True,
    hide_index=True,
)