# ⚽ Botola Pro — Football Match Analytics Engine

> **A Python-based football data analysis system built for the Moroccan Botola Pro league.**
> This project models a complete match between **FUS Rabat** and **FAR Rabat** using advanced football analytics metrics including **Expected Goals (xG)**, **Expected Threat (xT)**, and **VAEP** (Valuing Actions by Estimating Probabilities).

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Data Model](#data-model)
- [Analytics Metrics](#analytics-metrics)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Interactive Menu](#interactive-menu)
- [Dependencies](#dependencies)
- [Author](#author)

---

## Overview

This project is a **match analysis engine** developed in Python using an Object-Oriented Programming (OOP) approach. It ingests raw StatsBomb-formatted event data from a CSV file and performs deep analytical computations to evaluate player and team performance at a granular level.

The system processes every **pass**, **shot**, and **dribble** recorded during the match, groups them into **possession sequences**, and assigns advanced performance scores to each player and action.

---

## Features

- **Full OOP Architecture** — Clean separation of concerns across `Ball`, `Player`, `Team`, `Action`, and `Possession` entities
- **StatsBomb CSV Integration** — Reads and parses raw StatsBomb event data
- **Expected Goals (xG)** — Uses StatsBomb pre-computed xG values per shot
- **Expected Threat (xT)** — Evaluates the danger level of each pitch zone using Karun Singh's 12×16 grid model
- **VAEP Computation** — Measures each player's contribution to scoring/preventing goals per possession
- **Delta xG & Delta xT (DXG / DXT)** — Tracks the change in threat and goal probability between consecutive actions
- **Duplicate-Safe Processing** — Deduplication via StatsBomb event IDs
- **Interactive CLI Menu** — Explore player stats, possession chains, top performers, and head-to-head comparisons

---

## Architecture

The system is organized around **5 core domain objects** that mirror real football concepts:

```
                         ┌──────────────┐
                         │    main.py   │  ← Entry point, orchestrates all logic
                         └──────┬───────┘
                                │
          ┌─────────────────────┼────────────────────────┐
          │                     │                        │
   ┌──────▼──────┐       ┌──────▼──────┐        ┌───────▼──────┐
   │  equipe.py  │       │  joueur.py  │        │  action.py   │
   │   (Team)    │◄──────│  (Player)   │◄───────│  (Action)    │
   └─────────────┘       └─────────────┘        └──────┬───────┘
                                                        │
                                              ┌─────────▼──────┐
                                              │ possession.py  │
                                              │  (Possession)  │
                                              └────────────────┘
                                                        │
                                              ┌─────────▼──────┐
                                              │   balle.py     │
                                              │   (Ball)       │
                                              └────────────────┘
```

### Data Flow

```
CSV File (fus_FAR.csv)
        │
        ▼
  Load with pandas
        │
        ▼
  Create Teams & Players   ←──── equipe.py / joueur.py
        │
        ▼
  Parse Actions per Event  ←──── action.py / balle.py
        │
        ▼
  Group into Possessions   ←──── possession.py
        │
        ▼
  Compute xG / xT / VAEP
        │
        ▼
  Display Results + Interactive CLI
```

---

## Project Structure

```
projet_football-botola-pro/
│
├── main.py           # Entry point — orchestrates loading, processing, and display
├── balle.py          # Ball class — tracks position on the pitch
├── joueur.py         # Player class — stores stats (xG, VAEP, position, team)
├── equipe.py         # Team class — manages player roster and team-level stats
├── action.py         # Action class — models a single event (pass/shot/dribble)
├── possession.py     # Possession class — groups sequential actions by one team
├── fus_FAR.csv       # StatsBomb match event data (FUS Rabat vs FAR Rabat)
└── README.md         # Project documentation
```

---

## Data Model

### `Balle` (Ball)
Represents the ball's position at any moment on the pitch.

| Attribute | Type    | Description                          |
|-----------|---------|--------------------------------------|
| `x`       | `float` | Horizontal position (0–120m)         |
| `y`       | `float` | Vertical position (0–80m)            |

---

### `Joueur` (Player)
Represents a player and accumulates their performance metrics.

| Attribute | Type    | Description                            |
|-----------|---------|----------------------------------------|
| `nom`     | `str`   | Player name                            |
| `equipe`  | `str`   | Team name                              |
| `pos_x`   | `float` | Initial x position                     |
| `pos_y`   | `float` | Initial y position                     |
| `xg`      | `float` | Cumulative Expected Goals              |
| `vaep`    | `float` | Cumulative VAEP score                  |

---

### `Equipe` (Team)
Manages the list of players belonging to a team.

| Method             | Description                        |
|--------------------|------------------------------------|
| `ajouter_joueur()` | Adds a player to the squad         |
| `get_joueurs()`    | Returns the full list of players   |
| `get_nom()`        | Returns the team name              |
| `afficher()`       | Prints team-level statistics       |

---

### `Action`
Models a single on-pitch event (Pass, Shot, or Dribble).

| Attribute          | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| `type_action`      | `str`   | Action type: Pass / Shot / Dribble       |
| `joueur`           | `Joueur`| Player who performed the action          |
| `balle`            | `Balle` | Ball at the start position               |
| `start_x/y`        | `float` | Starting coordinates                     |
| `end_x/y`          | `float` | Ending coordinates                       |
| `minute`           | `int`   | Match minute                             |
| `resultat`         | `str`   | Outcome (Goal, Complete, Incomplete...)  |
| `xg`               | `float` | Expected Goals value                     |
| `xt`               | `float` | Expected Threat value                    |
| `dxg`              | `float` | Delta xG (change from previous action)   |
| `dxt`              | `float` | Delta xT (change from previous action)   |
| `vaep`             | `float` | Computed VAEP score                      |
| `marquer_but`      | `bool`  | Whether this action resulted in a goal   |
| `gagner_possession`| `bool`  | Whether the team retained possession     |

---

### `Possession`
Groups a sequence of consecutive actions performed by the same team.

| Attribute  | Type         | Description                            |
|------------|--------------|----------------------------------------|
| `numero`   | `int`        | Possession sequence number             |
| `equipe`   | `Equipe`     | Team in possession                     |
| `actions`  | `list`       | Ordered list of actions                |
| `gagnee`   | `bool`       | Whether possession was retained        |
| `perdue`   | `bool`       | Whether possession was lost            |

---

## Analytics Metrics

### Expected Goals (xG)
Sourced directly from **StatsBomb's pre-computed values** in the CSV. Represents the probability that a given shot results in a goal, based on shot location, angle, and other features.

### Expected Threat (xT)
Based on **Karun Singh's xT model** using a **12 × 16 pitch grid**. Each cell holds a value (0–0.76) representing the likelihood that a team in possession at that zone will score within the next few actions. The model is hardcoded as a 2D matrix calibrated to a 120m × 80m StatsBomb pitch.

### Delta xG (DXG) & Delta xT (DXT)
Measures the **change in xG or xT** between consecutive actions within the same possession — quantifying how much each action increased or decreased the attacking threat.

### VAEP (Valuing Actions by Estimating Probabilities)
Assigns each action a score based on its **contribution to scoring** (or preventing a goal). Computed per possession sequence and aggregated per player across the entire match.

---

## Getting Started

### Prerequisites

- Python **3.8+**
- `pandas` library

### Installation

```bash
# Clone the repository
git clone https://github.com/Hicham-nidali/projet_football-botola-pro-.git
cd projet_football-botola-pro-

# Install dependencies
pip install pandas
```

### Run the Analysis

```bash
python main.py
```

---

## Usage

On launch, the engine automatically:

1. Loads and validates the match CSV (`fus_FAR.csv`)
2. Creates `Team` and `Player` objects from the event data
3. Parses all valid actions (Pass, Shot, Dribble) into `Possession` sequences
4. Computes `xG`, `xT`, `DXG`, `DXT`, and `VAEP` for every action and player
5. Displays a structured match summary in the terminal

---

## Interactive Menu

After the automatic analysis, the system launches an interactive CLI:

```
============================================================
 MENU INTERACTIF
============================================================
1 - Stats d'un joueur spécifique
2 - Liste de tous les joueurs
3 - Détail d'une possession
4 - Meilleures possessions par VAEP
5 - Buts du match
6 - Comparer deux joueurs
7 - Quitter
------------------------------------------------------------
```

| Option | Description                                      |
|--------|--------------------------------------------------|
| `1`    | View detailed stats and actions for any player   |
| `2`    | List all players sorted by VAEP for a given team |
| `3`    | Inspect all actions within a specific possession |
| `4`    | Show the top 10 most valuable possession chains  |
| `5`    | Display all goals scored in the match            |
| `6`    | Side-by-side comparison of two players (xG, VAEP, actions) |
| `7`    | Exit the program                                 |

---

## Dependencies

| Library   | Version  | Purpose                          |
|-----------|----------|----------------------------------|
| `pandas`  | ≥ 1.3.0  | CSV parsing and data manipulation|
| `Python`  | ≥ 3.8    | Core language runtime            |

---

## Author

**Hicham Nidali**
- GitHub: [@Hicham-nidali](https://github.com/Hicham-nidali)

---

*This project was built as part of a football data science initiative focused on the Moroccan Botola Pro league, leveraging open StatsBomb event data and modern football analytics methodologies.*
