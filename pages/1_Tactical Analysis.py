# ============================================================
# EURO 2024 - TACTICAL ANALYSIS
# Version 8 - Cached Data & Tactical Dashboards
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
# 2. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Euro 2024 - Tactical Analysis",
    layout="wide"
)


# ============================================================
# 3. PAGE TITLE
# ============================================================

st.title("🗺️ Euro 2024 - Tactical Analysis")

st.subheader(
    "Analyze shooting zones, chance quality, and shot distances"
)


# ============================================================
# 4. LOAD AND CACHE DATA
# ============================================================

@st.cache_data
def load_and_preprocess_tactical_data():
    
    # Load raw data
    data = pd.read_csv("euros_2024_shot_map.csv")
    
    # Keep only real match shots.
    # Remove: non-shot events, penalty shots, and penalty shootout events (period 5)
    data = data[
        (data["type"] == "Shot") &
        (data["period"] != 5) &
        (data["shot_type"] != "Penalty")
    ].reset_index(drop=True)
    
    # Prepare location
    data["location"] = data["location"].apply(
        lambda x: json.loads(x) if isinstance(x, str) else x
    )
    
    # Extract X and Y
    data["x"] = data["location"].apply(
        lambda loc: loc[0] if isinstance(loc, list) and len(loc) >= 2 else np.nan
    )
    data["y"] = data["location"].apply(
        lambda loc: loc[1] if isinstance(loc, list) and len(loc) >= 2 else np.nan
    )
    
    # Remove shots without coordinates
    data = data.dropna(subset=["x", "y"]).copy()
    
    return data

# Execute the cached function
df = load_and_preprocess_tactical_data()


# ============================================================
# 8. TEAM SELECTION FOR MAIN TACTICAL ANALYSIS
# ============================================================

teams = sorted(
    df["team"]
    .dropna()
    .unique()
)


selected_team = st.selectbox(
    "Select a team",
    teams,
    index=None,
    key="main_team"
)


# ============================================================
# 9. PLAYER SELECTION FOR MAIN TACTICAL ANALYSIS
# ============================================================

if selected_team:

    players = sorted(
        df[
            df["team"] == selected_team
        ]["player"]
        .dropna()
        .unique()
    )

else:

    players = []


selected_player = st.selectbox(
    "Select a player",
    ["All Players"] + players
    if selected_team
    else [],
    index=None,
    key="main_player"
)


# ============================================================
# 10. APPLY TEAM + PLAYER FILTER
# ============================================================

filtered_df = df.copy()


# Team filter

if selected_team:

    filtered_df = filtered_df[
        filtered_df["team"] == selected_team
    ]


# Player filter

if selected_player and selected_player != "All Players":

    filtered_df = filtered_df[
        filtered_df["player"] == selected_player
    ]


# ============================================================
# 11. CHECK DATA
# ============================================================

if len(filtered_df) == 0:

    st.warning(
        "No shots match the selected team/player."
    )

    st.stop()


# ============================================================
# ============================================================
# VERSION 7C
# TACTICAL SHOT ZONES
# ============================================================
# ============================================================

st.divider()

st.header(
    "🗺️ Tactical Shot Zones"
)

st.write(
    """
    The attacking half is divided into tactical areas based on
    distance from the goal and horizontal position. This allows
    us to understand where shots are taken and what happens to
    those shots.
    """
)


# ============================================================
# 12. CREATE TACTICAL ZONES
# ============================================================

def classify_tactical_zone(row):

    x = row["x"]
    y = row["y"]


    # --------------------------------------------------------
    # PENALTY BOX
    # --------------------------------------------------------

    if x >= 102 and y < 30:

        return "Left Box"

    elif x >= 102 and 30 <= y <= 50:

        return "Central Box"

    elif x >= 102 and y > 50:

        return "Right Box"


    # --------------------------------------------------------
    # AREA JUST OUTSIDE THE BOX
    # --------------------------------------------------------

    elif x >= 90 and y < 30:

        return "Left Outside Box"

    elif x >= 90 and 30 <= y <= 50:

        return "Central Outside Box"

    elif x >= 90 and y > 50:

        return "Right Outside Box"


    # --------------------------------------------------------
    # WIDER / FARTHER AREAS
    # --------------------------------------------------------

    elif y < 40:

        return "Left Wide Area"

    else:

        return "Right Wide Area"


# Create tactical zone column

filtered_df["tactical_zone"] = filtered_df.apply(
    classify_tactical_zone,
    axis=1
)


# ============================================================
# 13. TACTICAL ZONE STATISTICS
# ============================================================

tactical_stats = (
    filtered_df
    .groupby("tactical_zone")
    .agg(

        Shots=(
            "tactical_zone",
            "size"
        ),

        Goals=(
            "shot_outcome",
            lambda x: (x == "Goal").sum()
        ),

        xG=(
            "shot_statsbomb_xg",
            "sum"
        ),

        Saved=(
            "shot_outcome",
            lambda x: (x == "Saved").sum()
        ),

        Blocked=(
            "shot_outcome",
            lambda x: (x == "Blocked").sum()
        ),

        Post=(
            "shot_outcome",
            lambda x: (x == "Post").sum()
        ),

        Off_Target=(
            "shot_outcome",
            lambda x: (x == "Off T").sum()
        ),

        Wayward=(
            "shot_outcome",
            lambda x: (x == "Wayward").sum()
        ),

        Saved_to_Post=(
            "shot_outcome",
            lambda x: (x == "Saved to Post").sum()
        ),

        Saved_Off_Target=(
            "shot_outcome",
            lambda x: (x == "Saved Off Target").sum()
        )

    )
    .reset_index()
)


# ============================================================
# 14. CALCULATE ADDITIONAL METRICS
# ============================================================

tactical_stats["Conversion %"] = np.where(
    tactical_stats["Shots"] > 0,
    tactical_stats["Goals"]
    / tactical_stats["Shots"]
    * 100,
    0
)


# Round xG

tactical_stats["xG"] = (
    tactical_stats["xG"]
    .round(2)
)


# Round conversion

tactical_stats["Conversion %"] = (
    tactical_stats["Conversion %"]
    .round(1)
)


# ============================================================
# 15. REORDER COLUMNS
# ============================================================

tactical_stats = tactical_stats[
    [
        "tactical_zone",

        "Shots",
        "Goals",
        "xG",
        "Conversion %",

        "Saved",
        "Blocked",
        "Post",
        "Off_Target",
        "Wayward",
        "Saved_to_Post",
        "Saved_Off_Target"
    ]
]


# ============================================================
# 16. SORT BY xG
# ============================================================

tactical_stats = tactical_stats.sort_values(
    "xG",
    ascending=False
)


# ============================================================
# 17. DISPLAY TACTICAL ZONE TABLE
# ============================================================

st.subheader(
    "📊 Tactical Zone Statistics"
)

st.caption(
    "Shot outcomes are broken down by tactical zone."
)


st.dataframe(
    tactical_stats,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 18. EXPLAIN THE ZONE STRUCTURE
# ============================================================

with st.expander("ℹ️ How are the tactical zones defined?"):

    st.write(
        """
    
        • Left Box = close to the goal and on the left side

        • Left Outside Box = just outside the penalty area
          and on the left side

        • Left Wide Area = farther away from the penalty area
          on the left side

        The same logic applies to the right side.

        This classification is a simplified tactical model based
        on the shot coordinates, not an official StatsBomb
        tactical-zone classification.
        """
    )


# ============================================================
# 18B. SHOT QUALITY ANALYSIS TABLE (FROM DASHBOARD)
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

filtered_df["xg_zone"] = filtered_df["shot_statsbomb_xg"].apply(classify_xg)

xg_zone_stats = (
    filtered_df
    .groupby("xg_zone")
    .agg(
        Shots=("xg_zone", "size"),
        Goals=("shot_outcome", lambda x: (x == "Goal").sum()),
        xG=("shot_statsbomb_xg", "sum")
    )
    .reset_index()
)

xg_zone_stats["xG"] = xg_zone_stats["xG"].round(2)

st.subheader("⭐ Shot Quality Analysis")

st.dataframe(
    xg_zone_stats,
    use_container_width=True,
    hide_index=True
)

with st.expander("ℹ️ How to read the Shot Quality Analysis?"):
    st.markdown(
        """
### What is xG?

**xG (Expected Goals)** estimates how likely a shot is
to result in a goal.

For example:
- **0.05 xG** ≈ 5% chance of becoming a goal
- **0.50 xG** ≈ 50% chance
- **0.80 xG** ≈ 80% chance

### xG categories used in this dashboard

| Category | xG value | Simple interpretation |
|---|---:|---|
| **Very Low** | Less than 5% | Very difficult chance |
| **Low** | 5% – 14% | Difficult chance |
| **Medium** | 15% – 29% | Reasonable chance |
| **High** | 30% or more | Very good chance |
"""
    )


# ============================================================
# 18C. SHOT DISTANCE ANALYSIS TABLE (FROM DASHBOARD)
# ============================================================

filtered_df["shot_distance"] = np.sqrt(
    (120 - filtered_df["x"]) ** 2 +
    (40 - filtered_df["y"]) ** 2
)

def classify_distance(distance):
    if distance < 12:
        return "Close"
    elif distance < 20:
        return "Medium"
    else:
        return "Long"

filtered_df["shot_zone"] = filtered_df["shot_distance"].apply(classify_distance)

zone_stats = (
    filtered_df
    .groupby("shot_zone")
    .agg(
        Shots=("shot_zone", "size"),
        xG=("shot_statsbomb_xg", "sum"),
        Goals=("shot_outcome", lambda x: (x == "Goal").sum())
    )
    .reset_index()
)

zone_stats["xG"] = zone_stats["xG"].round(2)

st.subheader("📏 Shot Distance Analysis")

st.dataframe(
    zone_stats,
    use_container_width=True,
    hide_index=True
)

with st.expander("ℹ️ How to read the Shot Distance Analysis?"):
    st.markdown(
        """
### What does shot distance mean?

Shot distance represents the approximate distance
between the location of the shot and the **center of
the opponent's goal**.

| Distance Zone | Distance from goal | Simple interpretation |
|---|---:|---|
| **Close** | Less than 12 m | Shots taken close to the goal |
| **Medium** | 12 m – 20 m | Shots taken at a medium distance |
| **Long** | 20 m or more | Shots taken from far away |
"""
    )


# ============================================================
# ============================================================
# 19. TACTICAL SHOT MAP
# ============================================================
# ============================================================

st.subheader(
    "🎯 Shot Locations by Tactical Area"
)

st.caption(
    "Marker color represents the shot outcome. "
    "Marker size represents the xG of the individual shot."
)


pitch_6c = VerticalPitch(
    pitch_type="statsbomb",
    half=True,
    pitch_color="grass",
    line_color="white"
)


fig_6c, ax_6c = pitch_6c.draw(
    figsize=(9, 7)
)


# ============================================================
# 20. DRAW TACTICAL ZONE LINES
# ============================================================

# Vertical dividers across pitch width (y from 0 to 80)
pitch_6c.lines(90, 0, 90, 80, ax=ax_6c, ls="--", color="white", alpha=0.6)
pitch_6c.lines(102, 0, 102, 80, ax=ax_6c, ls="--", color="white", alpha=0.6)

# Horizontal lane dividers (x from 90 to 120)
pitch_6c.lines(90, 30, 120, 30, ax=ax_6c, ls="--", color="white", alpha=0.6)
pitch_6c.lines(90, 50, 120, 50, ax=ax_6c, ls="--", color="white", alpha=0.6)

# ============================================================
# 21. DRAW INDIVIDUAL SHOTS (VECTORIZED FOR SPEED)
# ============================================================

# Split into goals and non-goals so goals always render on top
goals_df = filtered_df[filtered_df["shot_outcome"] == "Goal"].copy()
non_goals_df = filtered_df[filtered_df["shot_outcome"] != "Goal"].copy()

# --- PLOT NON-GOALS ---
if not non_goals_df.empty:
    
    # Calculate colors instantly using numpy
    conditions = [
        non_goals_df["shot_statsbomb_xg"] >= 0.30,
        non_goals_df["shot_statsbomb_xg"] >= 0.15,
        non_goals_df["shot_statsbomb_xg"] >= 0.05
    ]
    choices = ["red", "orange", "white"]
    non_goals_colors = np.select(conditions, choices, default="lightgray")
    
    # Calculate sizes instantly
    non_goals_sizes = np.maximum(40, 900 * non_goals_df["shot_statsbomb_xg"])
    
    # Draw all non-goals in one single command
    pitch_6c.scatter(
        non_goals_df["x"], 
        non_goals_df["y"], 
        ax=ax_6c,
        s=non_goals_sizes,
        c=non_goals_colors,
        edgecolors="black",
        linewidth=0.8,
        alpha=0.95,
        zorder=3
    )

# --- PLOT GOALS ---
if not goals_df.empty:
    
    goals_sizes = np.maximum(40, 900 * goals_df["shot_statsbomb_xg"])
    
    # Draw all goals in one single command
    pitch_6c.scatter(
        goals_df["x"], 
        goals_df["y"], 
        ax=ax_6c,
        s=goals_sizes,
        c="blue",
        edgecolors="black",
        linewidth=0.8,
        alpha=1.0,
        zorder=4  # Higher z-order keeps them visibly on top
    )


# ============================================================
# 22. CREATE MAP LEGEND
# ============================================================

legend_handles = [

    Line2D(
        [0],
        [0],
        marker="o",
        linestyle="",
        markerfacecolor="blue",
        markeredgecolor="black",
        markersize=9,
        label="Goal"
    ),

    Line2D(
        [0],
        [0],
        marker="o",
        linestyle="",
        markerfacecolor="red",
        markeredgecolor="black",
        markersize=11,
        label="High xG (≥ 0.30)"
    ),

    Line2D(
        [0],
        [0],
        marker="o",
        linestyle="",
        markerfacecolor="orange",
        markeredgecolor="black",
        markersize=10,
        label="Medium xG (0.15–0.29)"
    ),

    Line2D(
        [0],
        [0],
        marker="o",
        linestyle="",
        markerfacecolor="white",
        markeredgecolor="black",
        markersize=8,
        label="Low xG (0.05–0.14)"
    ),

    Line2D(
        [0],
        [0],
        marker="o",
        linestyle="",
        markerfacecolor="lightgray",
        markeredgecolor="black",
        markersize=7,
        label="Very Low xG (< 0.05)"
    )
]


ax_6c.legend(
    handles=legend_handles,
    title="Shot Legend",
    loc="upper center",
    bbox_to_anchor=(0.5, 0.04),
    ncol=3,
    frameon=True,
    fontsize=8
)


# ============================================================
# 23. DISPLAY MAP
# ============================================================

st.pyplot(
    fig_6c,
    use_container_width=True
)