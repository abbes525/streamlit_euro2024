import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Euro 2024 - Attack Patterns",
    layout="wide",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background: linear-gradient(
            180deg,
            #f7f8fb 0%,
            #ffffff 22%,
            #ffffff 100%
        );
    }

    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    .page-title {
        font-size: 42px;
        font-weight: 800;
        color: #1F77B4;
        letter-spacing: -0.03em;
        margin-bottom: 6px;
    }

    .page-subtitle {
        font-size: 16px;
        color: #5b6472;
        margin-bottom: 26px;
        max-width: 720px;
    }

    .kpi-card {
        background: linear-gradient(
            180deg,
            #ffffff 0%,
            #fbfcfe 100%
        );

        border: 1px solid #e7ebf0;
        border-top: 4px solid #0f766e;
        border-radius: 18px;

        padding: 22px 24px;

        min-height: 110px;

        box-shadow:
            0 10px 24px rgba(16, 24, 40, 0.06);

        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease;
    }

    .kpi-card:hover {
        transform: translateY(-2px);

        box-shadow:
            0 14px 28px rgba(16, 24, 40, 0.09);
    }

    .kpi-title {
        font-size: 13px;
        font-weight: 600;
        color: #000000;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .kpi-value {
        font-size: 34px;
        font-weight: 800;
        color: #000000;
        line-height: 1;
    }

    .section-card {
        background: linear-gradient(
            180deg,
            #ffffff 0%,
            #f8fbfc 100%
        );

        border: 1px solid #dbe4ea;
        border-radius: 18px;

        padding: 24px;

        margin-top: 20px;

        box-shadow:
            0 10px 24px rgba(16, 24, 40, 0.05);
    }

    .info-callout {
        background: linear-gradient(
            135deg,
            rgba(15, 118, 110, 0.08) 0%,
            rgba(14, 165, 233, 0.06) 100%
        );

        border: 1px solid rgba(15, 118, 110, 0.14);

        border-radius: 16px;

        padding: 18px 20px;
    }

    .info-callout-title {
        font-size: 16px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 6px;
    }

    .info-callout-body {
        font-size: 15px;
        color: #495260;
        line-height: 1.7;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv(
        "euros_2024_shot_map.csv"
    )

    # Keep only shots
    #
    # Exclude penalty shootout shots
    # because period 5 represents shootouts

    df = df[
        (df["type"] == "Shot") &
        (df["period"] != 5)
    ].copy()

    return df


df = load_data()


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="page-title">Attack Patterns</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="page-subtitle">'
    'Analyze how teams create shots and goals from different '
    'attacking patterns.'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# TEAM FILTER
# ============================================================

team_options = [
    "All Teams"
] + sorted(
    df["team"]
    .dropna()
    .astype(str)
    .unique()
)

selected_team = st.selectbox(
    "Choose a team",
    team_options,
)


# ============================================================
# APPLY TEAM FILTER
# ============================================================

if selected_team == "All Teams":

    filtered_df = df.copy()

else:

    filtered_df = df[
        df["team"] == selected_team
    ].copy()


# ============================================================
# CHECK DATA
# ============================================================

if filtered_df.empty:

    st.warning(
        "No shots match the selected team."
    )

    st.stop()


# ============================================================
# ATTACKING PATTERN LABEL
# ============================================================

# "Other" is treated as Penalty in this dataset.
#
# This allows penalty shots to remain in the analysis
# instead of being removed.

filtered_df = filtered_df.copy()

filtered_df["play_pattern_display"] = (
    filtered_df["play_pattern"]
    .replace(
        {
            "Other": "Penalty"
        }
    )
)


# ============================================================
# BASIC STATISTICS
# ============================================================

total_shots = len(
    filtered_df
)


total_goals = int(
    (
        filtered_df["shot_outcome"]
        == "Goal"
    ).sum()
)


overall_conversion = (
    total_goals / total_shots
    if total_shots > 0
    else 0
)


# Number of different attacking patterns

number_patterns = (
    filtered_df[
        "play_pattern_display"
    ]
    .dropna()
    .nunique()
)


# ============================================================
# KPI CARDS
# ============================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)


with kpi1:

    st.html(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                Total Shots
            </div>

            <div class="kpi-value">
                {total_shots}
            </div>

        </div>
        """
    )


with kpi2:

    st.html(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                Total Goals
            </div>

            <div class="kpi-value">
                {total_goals}
            </div>

        </div>
        """
    )


with kpi3:

    st.html(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                Overall Conversion
            </div>

            <div class="kpi-value">
                {overall_conversion:.1%}
            </div>

        </div>
        """
    )


with kpi4:

    st.html(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                Attack Patterns
            </div>

            <div class="kpi-value">
                {number_patterns}
            </div>

        </div>
        """
    )


# ============================================================
# CALCULATE PATTERN STATISTICS
# ============================================================

pattern_stats = (
    filtered_df
    .groupby("play_pattern_display")
    .agg(

        Shots=(
            "shot_outcome",
            "size"
        ),

        Goals=(
            "shot_outcome",
            lambda x:
            (x == "Goal").sum()
        ),
    )
    .reset_index()
)


# ============================================================
# CALCULATE CONVERSION
# ============================================================

pattern_stats["Conversion"] = (
    pattern_stats["Goals"]
    / pattern_stats["Shots"]
)


# ============================================================
# CALCULATE SHOT SHARE
# ============================================================

pattern_stats["Shot Share"] = (
    pattern_stats["Shots"]
    / total_shots
)


# ============================================================
# CALCULATE GOAL SHARE
# ============================================================

pattern_stats["Goal Share"] = (
    pattern_stats["Goals"]
    / total_goals
    if total_goals > 0
    else 0
)


# ============================================================
# SORT BY NUMBER OF SHOTS
# ============================================================

pattern_stats = (
    pattern_stats
    .sort_values(
        "Shots",
        ascending=False,
    )
    .reset_index(drop=True)
)


# ============================================================
# SHOTS BY ATTACKING PATTERN
# ============================================================

st.subheader(
    "Shots by Attacking Pattern"
)

st.write(
    "How many shots came from each type of attacking situation?"
)


# ============================================================
# SHOTS BAR CHART
# ============================================================

fig1, ax1 = plt.subplots(
    figsize=(11, 5.5)
)


patterns = pattern_stats[
    "play_pattern_display"
]


shots_values = pattern_stats[
    "Shots"
]


bars = ax1.barh(
    patterns,
    shots_values,
)


# Put largest value at top

ax1.invert_yaxis()


ax1.set_xlabel(
    "Number of Shots"
)

ax1.set_ylabel(
    ""
)

ax1.set_title(
    "Number of Shots by Play Pattern",
    fontsize=15,
    fontweight="bold",
)


# Add values at end of bars

for bar, value in zip(
    bars,
    shots_values,
):

    ax1.text(
        bar.get_width() + 1,

        bar.get_y()
        + bar.get_height() / 2,

        str(value),

        va="center",

        fontsize=10,
        fontweight="bold",
    )


# Remove unnecessary borders

ax1.spines[
    "top"
].set_visible(False)

ax1.spines[
    "right"
].set_visible(False)

ax1.spines[
    "left"
].set_visible(False)


# Add grid

ax1.grid(
    axis="x",
    alpha=0.2,
)


st.pyplot(
    fig1,
    use_container_width=True,
)


# ============================================================
# GOALS BY ATTACKING PATTERN
# ============================================================

st.subheader(
    "Goals by Attacking Pattern"
)

st.write(
    "Which attacking patterns produced the most goals?"
)


# Sort by goals

goal_stats = (
    pattern_stats
    .sort_values(
        "Goals",
        ascending=False,
    )
)


fig2, ax2 = plt.subplots(
    figsize=(11, 5.5)
)


patterns_goals = goal_stats[
    "play_pattern_display"
]


goals_values = goal_stats[
    "Goals"
]


bars2 = ax2.barh(
    patterns_goals,
    goals_values,
)


ax2.invert_yaxis()


ax2.set_xlabel(
    "Number of Goals"
)

ax2.set_ylabel(
    ""
)

ax2.set_title(
    "Number of Goals by Play Pattern",
    fontsize=15,
    fontweight="bold",
)


# Add values

for bar, value in zip(
    bars2,
    goals_values,
):

    ax2.text(
        bar.get_width() + 0.2,

        bar.get_y()
        + bar.get_height() / 2,

        str(value),

        va="center",

        fontsize=10,
        fontweight="bold",
    )


# Remove borders

ax2.spines[
    "top"
].set_visible(False)

ax2.spines[
    "right"
].set_visible(False)

ax2.spines[
    "left"
].set_visible(False)


# Add grid

ax2.grid(
    axis="x",
    alpha=0.2,
)


st.pyplot(
    fig2,
    use_container_width=True,
)


# ============================================================
# CONVERSION BY ATTACKING PATTERN
# ============================================================

st.subheader(
    "Efficiency of Each Attacking Pattern"
)

st.write(
    "Conversion rate = Goals ÷ Shots"
)


conversion_stats = (
    pattern_stats
    .sort_values(
        "Conversion",
        ascending=False,
    )
)


fig3, ax3 = plt.subplots(
    figsize=(11, 5.5)
)


patterns_conversion = (
    conversion_stats[
        "play_pattern_display"
    ]
)


conversion_values = (
    conversion_stats["Conversion"] * 100
)


bars3 = ax3.barh(
    patterns_conversion,
    conversion_values,
)


ax3.invert_yaxis()


ax3.set_xlabel(
    "Conversion Rate (%)"
)

ax3.set_ylabel(
    ""
)

ax3.set_title(
    "Shot Conversion by Play Pattern",
    fontsize=15,
    fontweight="bold",
)


# Add percentage labels

for bar, value in zip(
    bars3,
    conversion_values,
):

    ax3.text(
        bar.get_width() + 0.3,

        bar.get_y()
        + bar.get_height() / 2,

        f"{value:.1f}%",

        va="center",

        fontsize=10,
        fontweight="bold",
    )


# Remove borders

ax3.spines[
    "top"
].set_visible(False)

ax3.spines[
    "right"
].set_visible(False)

ax3.spines[
    "left"
].set_visible(False)


# Add grid

ax3.grid(
    axis="x",
    alpha=0.2,
)


st.pyplot(
    fig3,
    use_container_width=True,
)


# ============================================================
# TOP 5 TEAMS BY ATTACKING PATTERN
# ============================================================

st.divider()

st.subheader(
    " Top 5 Teams by Attacking Pattern"
)

st.write(
    "Select an attacking pattern to see which teams "
    "produced the most shots and goals from that pattern."
)


# ============================================================
# PATTERN SELECTOR
# ============================================================

all_patterns = sorted(
    df["play_pattern"]
    .dropna()
    .astype(str)
    .replace(
        "Other",
        "Penalty"
    )
    .unique()
)


selected_pattern = st.selectbox(
    "Choose an attacking pattern",
    all_patterns,
    key="top5_pattern"
)


# ============================================================
# CALCULATE TEAM STATISTICS
# ============================================================

# Start from the COMPLETE dataset.
#
# We deliberately do not use filtered_df here because
# the objective is to compare ALL EURO 2024 teams.

pattern_team_df = df.copy()


# Create the same display name for patterns

pattern_team_df["play_pattern_display"] = (
    pattern_team_df["play_pattern"]
    .replace(
        {
            "Other": "Penalty"
        }
    )
)


# Keep only the selected attacking pattern

pattern_team_df = pattern_team_df[
    pattern_team_df[
        "play_pattern_display"
    ] == selected_pattern
].copy()


# ============================================================
# GROUP BY TEAM
# ============================================================

team_pattern_stats = (
    pattern_team_df
    .groupby("team")
    .agg(

        Shots=(
            "shot_outcome",
            "size"
        ),

        Goals=(
            "shot_outcome",
            lambda x:
            (x == "Goal").sum()
        ),
    )
    .reset_index()
)


# ============================================================
# SORT AND KEEP TOP 5
# ============================================================

team_pattern_stats = (
    team_pattern_stats
    .sort_values(
        by=[
            "Shots",
            "Goals"
        ],
        ascending=[
            False,
            False
        ],
    )
    .head(5)
    .reset_index(drop=True)
)


# Add ranking

team_pattern_stats.insert(
    0,
    "Rank",
    range(
        1,
        len(team_pattern_stats) + 1
    )
)


# Rename columns

team_pattern_stats = (
    team_pattern_stats
    .rename(
        columns={
            "team": "Team",
            "Shots": "Total Shots",
            "Goals": "Goals"
        }
    )
)


# ============================================================
# DISPLAY TOP 5 TABLE
# ============================================================

if team_pattern_stats.empty:

    st.info(
        f"No teams recorded shots from the "
        f"{selected_pattern} pattern."
    )

else:

    st.dataframe(
        team_pattern_stats,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# EXPLANATION
# ============================================================

with st.expander(
    "ℹ️ How to read the Top 5 Teams table?"
):

    st.markdown(
        f"""
### Selected pattern: {selected_pattern}

This table compares all EURO 2024 teams based on
their shooting activity from the selected attacking pattern.

- **Rank** = position based on total shots
- **Total Shots** = number of shots produced from this pattern
- **Goals** = number of goals scored from this pattern

The table displays the **5 teams with the highest number
of shots** for the selected attacking pattern.

For example, if you select **Corner**, the table shows
the five teams that took the most shots following corners,
along with the number of goals they scored from those shots.

The ranking is based primarily on **Total Shots**.
Goals are shown to help compare the final scoring output.
"""
    )


# ============================================================
# DETAILED TABLE
# ============================================================

st.divider()

st.subheader(
    "Detailed Attack Pattern Statistics"
)


display_df = pattern_stats.copy()


# Convert ratios into percentages

display_df["Shot Share"] = (
    display_df["Shot Share"] * 100
)


display_df["Goal Share"] = (
    display_df["Goal Share"] * 100
)


display_df["Conversion"] = (
    display_df["Conversion"] * 100
)


# Select columns

display_df = display_df[
    [
        "play_pattern_display",
        "Shots",
        "Goals",
        "Conversion",
        "Shot Share",
        "Goal Share",
    ]
]


# Rename columns

display_df = display_df.rename(
    columns={
        "play_pattern_display": "Play Pattern",
        "Shots": "Shots",
        "Goals": "Goals",
        "Conversion": "Conversion %",
        "Shot Share": "Shot Share %",
        "Goal Share": "Goal Share %",
    }
)


# Display table

st.dataframe(
    display_df.style.format(
        {
            "Conversion %": "{:.1f}%",
            "Shot Share %": "{:.1f}%",
            "Goal Share %": "{:.1f}%",
        }
    ),
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# EXPLANATION OF SHOT SHARE / GOAL SHARE
# ============================================================

st.markdown(
    """
    <div class="section-card">
        <div class="info-callout">
        <div class="info-callout-title">
            💡How to read Shot Share and Goal Share
        </div>
        <div class="info-callout-body">
            <p style="margin: 0 0 6px 0;"><b>Shot Share</b> means the percentage of all shots that came from each attacking pattern.</p>
            <p style="margin: 0 0 6px 0;"><b>Goal Share</b> means the percentage of all goals that came from each attacking pattern.</p>
            <p style="margin: 0;">A high Shot Share means the pattern creates a lot of shots. A high Goal Share means it produces a lot of goals.</p>
        </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    "</div>",
    unsafe_allow_html=True,
)