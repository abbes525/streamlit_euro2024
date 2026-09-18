import json
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import VerticalPitch

st.set_page_config(
    page_title="Euro 2024 - Player Hub",
    layout="wide",
)

@st.cache_data
def load_shots() -> pd.DataFrame:
    df = pd.read_csv("euros_2024_shot_map.csv")
    df = df[(df["type"] == "Shot") & (df["period"] != 5)].reset_index(drop=True)

    df["location"] = df["location"].apply(
        lambda value: json.loads(value) if isinstance(value, str) else value
    )
    df["shot_end_location"] = df["shot_end_location"].apply(
        lambda value: json.loads(value) if isinstance(value, str) else value
    )
    
    # Extract coordinates for the pitch maps
    df["x"] = df["location"].apply(lambda loc: loc[0] if isinstance(loc, list) and len(loc) >= 2 else np.nan)
    df["y"] = df["location"].apply(lambda loc: loc[1] if isinstance(loc, list) and len(loc) >= 2 else np.nan)
    
    df["is_goal"] = df["shot_outcome"].eq("Goal")
    df["is_penalty"] = df["shot_type"].fillna("").astype(str).str.contains(
        "Penalty",
        case=False,
        na=False,
    )
    df["is_penalty_goal"] = df["is_penalty"] & df["is_goal"]
    
    return df

def sorted_values(series: pd.Series) -> list[str]:
    return sorted(series.dropna().astype(str).unique())


st.title("🏆 Euro 2024 - Player Hub")
st.subheader("Filter by team and rank players by shots, goals, xG, and penalty goals.")

shots_df = load_shots()

# ============================================================
# 1. PLAYER RANKING
# ============================================================

team_options = ["All Teams"] + sorted_values(shots_df["team"])
selected_team = st.selectbox("Choose a team for ranking", team_options)

filtered_df = shots_df if selected_team == "All Teams" else shots_df[shots_df["team"] == selected_team]

shots = len(filtered_df)
goals = int(filtered_df["is_goal"].sum())
total_xg = float(filtered_df["shot_statsbomb_xg"].sum())
penalty_goals = int(filtered_df["is_penalty_goal"].sum())

st.subheader("Team summary")
summary_cols = st.columns(4)
summary_cols[0].metric("Shots", f"{shots}")
summary_cols[1].metric("Goals", f"{goals}")
summary_cols[2].metric("xG", f"{total_xg:.2f}")
summary_cols[3].metric("Penalty Goals", f"{penalty_goals}")

if filtered_df.empty:
    st.warning("No shots match the selected team.")
else:
    ranking = (
        filtered_df.groupby(["player", "team"], as_index=False)
        .agg(
            Shots=("player", "size"),
            Goals=("is_goal", "sum"),
            xG=("shot_statsbomb_xg", "sum"),
            Penalty_Shots=("is_penalty", "sum"),
            Penalty_Goals=("is_penalty_goal", "sum"),
        )
        .sort_values(["Goals", "xG", "Shots"], ascending=False)
    )

    ranking["Conversion"] = ranking["Goals"].div(ranking["Shots"]).fillna(0)
    ranking["Penalty Conversion"] = ranking["Penalty_Goals"].div(ranking["Penalty_Shots"]).fillna(0)

    ranking_display = ranking.rename(
        columns={
            "Penalty_Shots": "Penalty Shots",
            "Penalty_Goals": "Penalty Goals",
        }
    ).copy()

    ranking_display["xG"] = ranking_display["xG"].map(lambda value: f"{value:.2f}")
    ranking_display["Conversion"] = ranking_display["Conversion"].map(lambda value: f"{value:.1%}")
    ranking_display["Penalty Conversion"] = ranking_display["Penalty Conversion"].map(lambda value: f"{value:.1%}")

    st.subheader("Player ranking")
    st.caption("Players are sorted by goals, then xG, then shots.")

    st.dataframe(
        ranking_display,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# 3. PLAYER COMPARISON
# ============================================================

st.divider()

st.header("👥 Player Comparison")
st.write("Compare two players independently. Each player can belong to a different team. " \
"chose the team first, then the player to display the comparison")

teams = sorted_values(shots_df["team"])

# Player 1 Selection
st.subheader("Player 1")
p1_col1, p1_col2 = st.columns(2)

with p1_col1:
    team_1 = st.selectbox(
        "Select Team",
        teams,
        index=None,
        placeholder="Choose a team...",
        key="comparison_team_1"
    )

with p1_col2:
    players_team_1 = sorted_values(shots_df[shots_df["team"] == team_1]["player"]) if team_1 else []
    player_1 = st.selectbox(
        "Select Player",
        players_team_1,
        index=None,
        placeholder="Choose a player..." if team_1 else "Select a team first",
        disabled=not bool(team_1),
        key="comparison_player_1"
    )

# Player 2 Selection
st.subheader("Player 2")
p2_col1, p2_col2 = st.columns(2)

with p2_col1:
    team_2 = st.selectbox(
        "Select Team",
        teams,
        index=None,
        placeholder="Choose a team...",
        key="comparison_team_2"
    )

with p2_col2:
    players_team_2 = sorted_values(shots_df[shots_df["team"] == team_2]["player"]) if team_2 else []
    player_2 = st.selectbox(
        "Select Player",
        players_team_2,
        index=None,
        placeholder="Choose a player..." if team_2 else "Select a team first",
        disabled=not bool(team_2),
        key="comparison_player_2"
    )

# Stop here until both players are selected
if not player_1 or not player_2:
    st.info("👆 Please select both Player 1 and Player 2 above to view the head-to-head comparison.")
    st.stop()

# ============================================================
# GET PLAYER DATA & RENDER COMPARISON
# ============================================================

player_1_df = shots_df[(shots_df["team"] == team_1) & (shots_df["player"] == player_1)].copy()
player_2_df = shots_df[(shots_df["team"] == team_2) & (shots_df["player"] == player_2)].copy()

def calculate_player_stats(player_df):
    shots_count = len(player_df)
    goals_count = (player_df["shot_outcome"] == "Goal").sum()
    total_xg_val = player_df["shot_statsbomb_xg"].sum()
    
    conversion_val = (goals_count / shots_count * 100) if shots_count > 0 else 0
    xg_per_shot = (total_xg_val / shots_count) if shots_count > 0 else 0
    outcomes = player_df["shot_outcome"].value_counts().to_dict()
    
    return {
        "Shots": shots_count,
        "Goals": goals_count,
        "Total xG": total_xg_val,
        "Conversion %": conversion_val,
        "xG per Shot": xg_per_shot,
        "outcomes": outcomes
    }

p1_stats = calculate_player_stats(player_1_df)
p2_stats = calculate_player_stats(player_2_df)

# Player Statistics Table
st.subheader("📊 Player Statistics")

all_outcomes = sorted(set(p1_stats["outcomes"].keys()).union(p2_stats["outcomes"].keys()))

comparison_rows = [
    {"Metric": "Shots", player_1: p1_stats["Shots"], player_2: p2_stats["Shots"]},
    {"Metric": "Goals", player_1: p1_stats["Goals"], player_2: p2_stats["Goals"]},
    {"Metric": "Total xG", player_1: round(p1_stats["Total xG"], 2), player_2: round(p2_stats["Total xG"], 2)},
    {"Metric": "Conversion %", player_1: round(p1_stats["Conversion %"], 1), player_2: round(p2_stats["Conversion %"], 1)}
]

for outcome in all_outcomes:
    comparison_rows.append({
        "Metric": outcome,
        player_1: p1_stats["outcomes"].get(outcome, 0),
        player_2: p2_stats["outcomes"].get(outcome, 0)
    })

comparison_table = pd.DataFrame(comparison_rows)
st.dataframe(comparison_table, use_container_width=True, hide_index=True)

# Side-by-Side Shot Maps
st.subheader("🎯 Shot Location Comparison")
map_col1, map_col2 = st.columns(2)

def get_shot_color(shot):
    xg = float(shot["shot_statsbomb_xg"])
    if shot["shot_outcome"] == "Goal":
        return "blue"
    elif xg >= 0.30:
        return "red"
    elif xg >= 0.15:
        return "orange"
    elif xg >= 0.05:
        return "white"
    return "lightgray"

legend_handles = [
    Line2D([0], [0], marker="o", linestyle="", markerfacecolor="blue", markeredgecolor="black", markersize=9, label="Goal"),
    Line2D([0], [0], marker="o", linestyle="", markerfacecolor="red", markeredgecolor="black", markersize=11, label="High xG (≥ 0.30)"),
    Line2D([0], [0], marker="o", linestyle="", markerfacecolor="orange", markeredgecolor="black", markersize=10, label="Medium xG (0.15–0.29)"),
    Line2D([0], [0], marker="o", linestyle="", markerfacecolor="white", markeredgecolor="black", markersize=8, label="Low xG (0.05–0.14)"),
    Line2D([0], [0], marker="o", linestyle="", markerfacecolor="lightgray", markeredgecolor="black", markersize=7, label="Very Low xG (< 0.05)")
]

with map_col1:
    st.markdown(f"### 🔵 {player_1}")
    st.caption(f"Team: {team_1}")
    pitch_p1 = VerticalPitch(pitch_type="statsbomb", half=True, pitch_color="grass", line_color="white")
    fig_p1, ax_p1 = pitch_p1.draw(figsize=(6, 7))
    
    for _, shot in player_1_df.iterrows():
        pitch_p1.scatter(
            float(shot["x"]), float(shot["y"]), ax=ax_p1, 
            s=max(40, 900 * float(shot["shot_statsbomb_xg"])), 
            color=get_shot_color(shot), edgecolors="black", 
            linewidth=0.8, alpha=0.95, zorder=3
        )
        
    ax_p1.legend(handles=legend_handles, title="Shot Legend", loc="upper center", bbox_to_anchor=(0.5, 0.04), ncol=2, fontsize=7, frameon=True)
    st.pyplot(fig_p1, use_container_width=True)

with map_col2:
    st.markdown(f"### 🔴 {player_2}")
    st.caption(f"Team: {team_2}")
    pitch_p2 = VerticalPitch(pitch_type="statsbomb", half=True, pitch_color="grass", line_color="white")
    fig_p2, ax_p2 = pitch_p2.draw(figsize=(6, 7))
    
    for _, shot in player_2_df.iterrows():
        pitch_p2.scatter(
            float(shot["x"]), float(shot["y"]), ax=ax_p2, 
            s=max(40, 900 * float(shot["shot_statsbomb_xg"])), 
            color=get_shot_color(shot), edgecolors="black", 
            linewidth=0.8, alpha=0.95, zorder=3
        )
        
    ax_p2.legend(handles=legend_handles, title="Shot Legend", loc="upper center", bbox_to_anchor=(0.5, 0.04), ncol=2, fontsize=7, frameon=True)
    st.pyplot(fig_p2, use_container_width=True)

# Comparison Summary
st.subheader("🔎 Comparison Summary")

p1_xg, p2_xg = p1_stats["Total xG"], p2_stats["Total xG"]
if p1_xg > p2_xg:
    st.write(f"🎯 **{player_1}** generated more total xG: **{p1_xg:.2f}** vs **{p2_xg:.2f}**.")
elif p2_xg > p1_xg:
    st.write(f"🎯 **{player_2}** generated more total xG: **{p2_xg:.2f}** vs **{p1_xg:.2f}**.")
else:
    st.write("🎯 Both players generated the same total xG.")

p1_xg_per_shot, p2_xg_per_shot = p1_stats["xG per Shot"], p2_stats["xG per Shot"]
st.write(f"💡 **xG per shot** measures the average quality of the chances a player takes. **{player_1}: {p1_xg_per_shot:.3f}** | **{player_2}: {p2_xg_per_shot:.3f}**.")
if p1_xg_per_shot > p2_xg_per_shot:
    st.write(f"➡️ {player_1} takes shots that have a higher average expected-goal value.")
elif p2_xg_per_shot > p1_xg_per_shot:
    st.write(f"➡️ {player_2} takes shots that have a higher average expected-goal value.")
else:
    st.write("➡️ Both players have the same average shot quality.")

p1_shots, p2_shots = p1_stats["Shots"], p2_stats["Shots"]
if p1_shots > p2_shots:
    st.write(f"📊 **{player_1}** took more shots: **{p1_shots}** vs **{p2_shots}**.")
elif p2_shots > p1_shots:
    st.write(f"📊 **{player_2}** took more shots: **{p2_shots}** vs **{p1_shots}**.")
else:
    st.write("📊 Both players took the same number of shots.")

p1_goals, p2_goals = p1_stats["Goals"], p2_stats["Goals"]
if p1_goals > p2_goals:
    st.write(f"⚽ **{player_1}** scored more goals: **{p1_goals}** vs **{p2_goals}**.")
elif p2_goals > p1_goals:
    st.write(f"⚽ **{player_2}** scored more goals: **{p2_goals}** vs **{p1_goals}**.")
else:
    st.write("⚽ Both players scored the same number of goals.")

st.write(f"📈 **Conversion rate:** {player_1} = **{p1_stats['Conversion %']:.1f}%** | {player_2} = **{p2_stats['Conversion %']:.1f}%**.")

st.info('''
**How to read the comparison:**
• Shots = shooting volume
• Goals = actual scoring output
• Total xG = expected goal value generated from all shots
• xG per Shot = average quality of the shots taken
• Conversion % = percentage of shots that became goals
• Outcome rows = what happened to the shots (Saved, Blocked, Off Target, Post, etc.)
''')