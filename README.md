# ⚽ UEFA Euro 2024 - Tactical Shot Analysis & Player Hub

An interactive football analytics dashboard built with **Streamlit**, **Plotly**, and **mplsoccer**. This project leverages open event data to explore shot locations, expected goals (xG), finishing efficiency, penalty placement, and attacking play patterns across UEFA Euro 2024.

---

## 📌 Project Overview

Traditional football statistics focus heavily on raw output (goals and shots). This dashboard looks deeper into the **geometry and quality** of chance creation:
- How clinical were teams compared to their expected output ($Goals - xG$)?
- From which pitch zones were teams taking their highest-value chances?
- How do individual attackers compare when matched head-to-head?
- Where were penalties placed in the frame of the goal, and which attacking phases (open play, corners, transitions) generated the most threat?

---

## 🚀 Key Features

### 1. Interactive Shot Dashboard (`Home.py`)
- **Dynamic Half-Pitch Map:** Built with Plotly to provide interactive hover tooltips displaying player name, shot outcome, and exact StatsBomb xG values[cite: 11].
- **Executive KPIs:** Live metrics for total shots, goals, tournament/team conversion rate, average shot distance, and penalty goals[cite: 11].
- **Global Team Overview:** Unfiltered tournament-wide leaderboard comparing total goals and cumulative xG across all participating nations[cite: 11].

### 2. Tactical Analysis (`pages/1_Tactical_Analysis.py`)
- **Spatial Zone Breakdown:** Attacking third partitioned into 8 distinct tactical corridors (Central Box, Wide Channels, Outside Box)[cite: 7].
- **Shot Quality & Distance Tables:** Shots segmented by distance brackets (<12m, 12–20m, 20m+) and xG difficulty tiers (Very Low to High)[cite: 7].
- **Pitch Overlay:** Dual-layer vectorized pitch map highlighting tactical zones and individual chance locations[cite: 7].

### 3. Player Hub & Comparison (`pages/2_Player_Hub.py`)
- **Tournament Leaderboards:** Filterable player rankings sorted by scoring output, xG generation, and conversion efficiency[cite: 9].
- **Head-to-Head Comparison:** Compare any two players across separate teams with side-by-side pitch maps, outcome profiles, and quality-per-shot metrics[cite: 9].

### 4. Penalty Placement (`pages/3_Penalty_Shots.py`)
- **Custom Goal-Mouth Visualizer:** Plots shot trajectories into the cage coordinates ($Y$ and $Z$ planes) to analyze shot placement against the posts and crossbar[cite: 8].
- **Success Metrics:** Penalty conversion tracking and conversion rates filtered by team or individual taker[cite: 8].

### 5. Attack Patterns (`pages/4_Attack_Patterns.py`)
- **Phase of Play Breakdown:** Analyzes shot volume, goal production, and efficiency across regular play, set pieces, corners, counter-attacks, and throw-ins[cite: 10].
- **Top 5 Team Rankings:** Explores which nations generated the highest volume of threat from specific buildup patterns[cite: 10].

---

## 🛠️ Tech Stack

- **Core:** Python 3.10+
- **Application Framework:** [Streamlit](https://streamlit.io/)
- **Data Manipulation:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Visualizations:** [Plotly](https://plotly.com/python/), [mplsoccer](https://mplsoccer.readthedocs.io/), [Matplotlib](https://matplotlib.org/)

---

## 📂 Project Structure

```text
euro2024-shot-analysis/
├── Home.py                       # Main application entrypoint
├── euros_2024_shot_map.csv       # Match event & shot dataset
├── requirements.txt              # Project dependencies
├── README.md                     # Project documentation
└── pages/
    ├── 1_Tactical_Analysis.py    # Zone classification & distance analytics
    ├── 2_Player_Hub.py           # Player leaderboards & head-to-head comparison
    ├── 3_Penalty_Shots.py        # Goal-cage coordinates visualizer
    └── 4_Attack_Patterns.py      # Play pattern analysis & phase breakdown
