import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import textwrap

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Euro 2024 - Penalty Shots",
    layout="wide",
)


# ============================================================
# CUSTOM STREAMLIT CSS
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       GENERAL PAGE
    -------------------------------------------------------- */

    .main {
        background-color: #ffffff;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }


    /* --------------------------------------------------------
       TITLE
    -------------------------------------------------------- */

    .page-title {
        font-size: 38px;
        font-weight: 750;
        color: #20242c;
        margin-bottom: 4px;
    }

    .page-subtitle {
        font-size: 17px;
        color: #60656f;
        margin-bottom: 28px;
    }


    /* --------------------------------------------------------
       FILTER LABELS
    -------------------------------------------------------- */

    .filter-label {
        font-size: 15px;
        font-weight: 600;
        color: #30343b;
        margin-bottom: 5px;
    }


    /* --------------------------------------------------------
       KPI CARDS
    -------------------------------------------------------- */

    .kpi-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 22px 24px;
        min-height: 115px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.035);
    }

    .kpi-title {
        font-size: 15px;
        font-weight: 600;
        color: #555b66;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 32px;
        font-weight: 750;
        line-height: 1;
    }

    .kpi-penalties {
        color: #2457a6;
    }

    .kpi-goals {
        color: #239b3b;
    }

    .kpi-missed {
        color: #e62d35;
    }

    .kpi-conversion {
        color: #7047c7;
    }


    /* --------------------------------------------------------
       PLOT CONTAINER
    -------------------------------------------------------- */

    .plot-container {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 10px 10px 0px 10px;
        margin-top: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.035);
    }


    /* --------------------------------------------------------
       BOTTOM STATISTICS PANEL
    -------------------------------------------------------- */

    .bottom-panel {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 30px 40px;
        margin-top: 18px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.035);
    }

    .bottom-stat {
        text-align: center;
    }

    .bottom-circle {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        font-weight: 750;
        margin-bottom: 8px;
    }

    .circle-penalties {
        background: #e9f0fc;
        color: #2457a6;
    }

    .circle-goals {
        background: #e4f7e7;
        color: #239b3b;
    }

    .circle-missed {
        background: #fde7e8;
        color: #e62d35;
    }

    .bottom-number {
        font-size: 28px;
        font-weight: 750;
        margin-bottom: 2px;
    }

    .bottom-label {
        font-size: 14px;
        font-weight: 600;
        color: #4e535c;
    }

    .vertical-separator {
        border-left: 1px solid #d9dce1;
        height: 85px;
        margin: auto;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_penalties() -> pd.DataFrame:

    df = pd.read_csv("euros_2024_shot_map.csv")

    df = df[df["type"] == "Shot"].reset_index(drop=True)

    df["location"] = df["location"].apply(
        lambda value:
        json.loads(value)
        if isinstance(value, str)
        else value
    )

    df["shot_end_location"] = df["shot_end_location"].apply(
        lambda value:
        json.loads(value)
        if isinstance(value, str)
        else value
    )

    df["is_penalty"] = (
        df["shot_type"]
        .fillna("")
        .astype(str)
        .str.contains(
            "Penalty",
            case=False,
            na=False,
        )
    )

    return df[df["is_penalty"]].copy()


def sorted_values(series: pd.Series) -> list[str]:

    return sorted(
        series
        .dropna()
        .astype(str)
        .unique()
    )


# ============================================================
# STATSBOMB GOAL COORDINATES
# ============================================================

POST_LEFT = 36.0
POST_RIGHT = 44.0

GROUND = 0.0
CROSSBAR = 2.67


def end_yz_from_location(value):

    if isinstance(value, list) and len(value) >= 3:

        return (
            float(value[1]),
            float(value[2]),
        )

    if isinstance(value, list) and len(value) == 2:

        return (
            float(value[1]),
            0.0,
        )

    return None, None


def map_to_goal_mouth(
    y: float,
    z: float,
    goal_box: tuple[
        float,
        float,
        float,
        float,
    ],
) -> tuple[float, float]:

    goal_left, goal_right, goal_bottom, goal_top = goal_box

    draw_x = (
        goal_left
        + (
            (y - POST_LEFT)
            / (POST_RIGHT - POST_LEFT)
        )
        * (goal_right - goal_left)
    )

    draw_y = (
        goal_bottom
        + (
            (z - GROUND)
            / (CROSSBAR - GROUND)
        )
        * (goal_top - goal_bottom)
    )

    return draw_x, draw_y


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="page-title">Penalty Shots</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="page-subtitle">'
    'Pick a team and a player to inspect penalty placement in the cage.'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# LOAD PENALTY DATA
# ============================================================

penalties_df = load_penalties()


# ============================================================
# FILTERS
# ============================================================

filter_col1, filter_col2 = st.columns(2)


with filter_col1:

    st.markdown(
        '<div class="filter-label">Choose a team</div>',
        unsafe_allow_html=True,
    )

    team_options = [
        "All Teams"
    ] + sorted_values(
        penalties_df["team"]
    )

    selected_team = st.selectbox(
        "Team",
        team_options,
        label_visibility="collapsed",
    )


with filter_col2:

    team_df = (
        penalties_df
        if selected_team == "All Teams"
        else penalties_df[
            penalties_df["team"]
            == selected_team
        ]
    )

    st.markdown(
        '<div class="filter-label">Choose a player</div>',
        unsafe_allow_html=True,
    )

    player_options = [
        "All Players"
    ] + sorted_values(
        team_df["player"]
    )

    selected_player = st.selectbox(
        "Player",
        player_options,
        label_visibility="collapsed",
    )


# ============================================================
# APPLY PLAYER FILTER
# ============================================================

filtered_df = (
    team_df
    if selected_player == "All Players"
    else team_df[
        team_df["player"]
        == selected_player
    ]
)


if filtered_df.empty:

    st.warning(
        "No penalty shots match the selected filters."
    )

    st.stop()


# ============================================================
# CALCULATE STATISTICS
# ============================================================

shots = len(filtered_df)

goals = int(
    (
        filtered_df["shot_outcome"]
        == "Goal"
    ).sum()
)

missed_saved = shots - goals

conversion = (
    goals / shots
    if shots
    else 0
)


# ============================================================
# KPI CARDS
# ============================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)


with kpi1:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Penalties</div>
            <div class="kpi-value kpi-penalties">
                {shots}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with kpi2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Goals</div>
            <div class="kpi-value kpi-goals">
                {goals}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with kpi3:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Missed/Saved</div>
            <div class="kpi-value kpi-missed">
                {missed_saved}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with kpi4:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Conversion</div>
            <div class="kpi-value kpi-conversion">
                {conversion:.1%}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# GOAL / CAGE GEOMETRY
# ============================================================

goal_left = 3.5
goal_right = 16.5

goal_bottom = 3.0
goal_top = 8.0

goal_box = (
    goal_left,
    goal_right,
    goal_bottom,
    goal_top,
)


# ============================================================
# COMPUTE ALL SHOT POSITIONS
# ============================================================

points = []


for shot in filtered_df.to_dict(
    orient="records"
):

    y, z = end_yz_from_location(
        shot.get(
            "shot_end_location"
        )
    )

    if y is None or z is None:
        continue

    draw_x, draw_y = map_to_goal_mouth(
        y,
        z,
        goal_box,
    )

    points.append(
        (
            draw_x,
            draw_y,
            shot["shot_outcome"]
            == "Goal",
        )
    )


if not points:

    st.warning(
        "No shot end-location data available for the selected filters."
    )

    st.stop()


# ============================================================
# AXIS LIMITS
# ============================================================

xs = [
    point[0]
    for point in points
]

ys = [
    point[1]
    for point in points
]

margin = 1.5

xlim_min = (
    min(
        goal_left,
        min(xs),
    )
    - margin
)

xlim_max = (
    max(
        goal_right,
        max(xs),
    )
    + margin
)

ylim_min = (
    min(
        goal_bottom,
        min(ys),
    )
    - margin
)

ylim_max = (
    max(
        goal_top,
        max(ys),
    )
    + margin
)


# ============================================================
# CREATE GOAL FIGURE
# ============================================================

fig, ax = plt.subplots(
    figsize=(12, 6.4)
)

fig.patch.set_facecolor(
    "white"
)

ax.set_facecolor(
    "white"
)

ax.set_xlim(
    xlim_min,
    xlim_max,
)

ax.set_ylim(
    ylim_min,
    ylim_max,
)

ax.set_aspect(
    "equal"
)

ax.axis(
    "off"
)


# ============================================================
# LIGHT GOAL BACKGROUND
# ============================================================

ax.add_patch(
    Rectangle(
        (
            goal_left,
            goal_bottom,
        ),

        goal_right - goal_left,

        goal_top - goal_bottom,

        facecolor="#f7f7f7",

        edgecolor="none",

        zorder=0,
    )
)


# ============================================================
# NET GRID
# ============================================================

for x in np.linspace(
    goal_left,
    goal_right,
    8,
)[1:-1]:

    ax.plot(
        [x, x],
        [
            goal_bottom,
            goal_top,
        ],
        color="#d6d6d6",
        linewidth=0.8,
        zorder=1,
    )


for y in np.linspace(
    goal_bottom,
    goal_top,
    6,
)[1:-1]:

    ax.plot(
        [
            goal_left,
            goal_right,
        ],
        [y, y],
        color="#d6d6d6",
        linewidth=0.8,
        zorder=1,
    )


# ============================================================
# GOAL POSTS
# ============================================================

# Left post
ax.plot(
    [
        goal_left,
        goal_left,
    ],
    [
        goal_bottom,
        goal_top,
    ],
    color="#555555",
    linewidth=7,
    solid_capstyle="round",
    zorder=4,
)


# Right post
ax.plot(
    [
        goal_right,
        goal_right,
    ],
    [
        goal_bottom,
        goal_top,
    ],
    color="#555555",
    linewidth=7,
    solid_capstyle="round",
    zorder=4,
)


# Crossbar
ax.plot(
    [
        goal_left,
        goal_right,
    ],
    [
        goal_top,
        goal_top,
    ],
    color="#555555",
    linewidth=7,
    solid_capstyle="round",
    zorder=4,
)


# ============================================================
# GOAL TITLE
# ============================================================

ax.text(
    (
        goal_left
        + goal_right
    ) / 2,

    goal_top + 0.7,

    "GOAL",

    ha="center",
    va="center",

    fontsize=15,

    fontweight="bold",

    color="#30343b",
)


# ============================================================
# SHOTS
# ============================================================

for draw_x, draw_y, is_goal in points:

    ax.scatter(
        draw_x,
        draw_y,

        s=105,

        facecolors=(
            "#0bf01e"
            if is_goal
            else "#ff1f2d"
        ),

        edgecolors="black",

        linewidths=1.2,

        zorder=5,

        clip_on=False,
    )


# ============================================================
# LEGEND
# ============================================================

legend_handles = [

    Line2D(
        [0],
        [0],

        marker="o",

        color="w",

        label="Goal",

        markerfacecolor="#0bf01e",

        markeredgecolor="black",

        markersize=10,
    ),

    Line2D(
        [0],
        [0],

        marker="o",

        color="w",

        label="Missed/Saved",

        markerfacecolor="#ff1f2d",

        markeredgecolor="black",

        markersize=10,
    ),
]


ax.legend(
    handles=legend_handles,

    loc="lower center",

    bbox_to_anchor=(
        0.5,
        -0.06,
    ),

    ncol=2,

    frameon=False,

    fontsize=11,
)


# ============================================================
# DISPLAY GOAL CONTAINER
# ============================================================

st.markdown(
    '<div class="plot-container">',
    unsafe_allow_html=True,
)

st.pyplot(
    fig,
    use_container_width=True,
)

st.markdown(
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# BOTTOM STATISTICS PANEL
# ============================================================

st.html(
    f"""
    <div class="bottom-panel">

        <div style="
            display: grid;
            grid-template-columns: 1fr 1px 1fr 1px 1fr;
            align-items: center;
            gap: 30px;
        ">

            <div class="bottom-stat">

                <div class="bottom-circle circle-penalties">
                    ⚽
                </div>

                <div class="bottom-number kpi-penalties">
                    {shots}
                </div>

                <div class="bottom-label">
                    penalties
                </div>

            </div>

            <div class="vertical-separator"></div>

            <div class="bottom-stat">

                <div class="bottom-circle circle-goals">
                    ⚽
                </div>

                <div class="bottom-number kpi-goals">
                    {goals}
                </div>

                <div class="bottom-label">
                    goals
                </div>

            </div>

            <div class="vertical-separator"></div>

            <div class="bottom-stat">

                <div class="bottom-circle circle-missed">
                    ✋
                </div>

                <div class="bottom-number kpi-missed">
                    {missed_saved}
                </div>

                <div class="bottom-label">
                    missed/saved
                </div>

            </div>

        </div>

    </div>
    """
)