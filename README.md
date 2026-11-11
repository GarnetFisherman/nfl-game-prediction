🏈 NFL Game Prediction
An end-to-end machine learning project that predicts NFL game winners and win probabilities using recent team performance, advanced play-by-play efficiency metrics, and chronological walk-forward validation.

The project evolved from exploratory modeling in Jupyter into a reusable Python prediction pipeline and Streamlit sports analytics dashboard.

NFL Prediction Dashboard

Project Overview
The goal is simple:

Given only information available before kickoff, estimate each team's probability of winning an NFL game.

The final system:

Loads NFL schedule and play-by-play data
Builds leakage-safe rolling team features
Trains a standardized Logistic Regression model
Identifiesutomatically
Generates home and away win probabilities
Ranks games by model confidence
Saves lightweight prediction output
Displays results in an interactive Streamlit dashboard
The final core model achieved approximately 63.4% average walk-forward accuracy across the 2022–2025 test seasons.

Model Performance
Historical evaluation uses chronological walk-forward validation.

Test Season	Accuracy
2022	60.3%
2023	62.5%
2024	67.4%
2025	63.4%
Average	~63.4%
For each test season, the model was trained only on data from earlier seasons.

For example:

2021–2023 → Train
2024      → Test
This better represents how the system behaves when predicting future NFL games than a random train/test split.

Confidence Analysis
The model also produces win probabilities.

Historical walk-forward predictions were grouped by the minimum confidence assigned to the model's predicted winner.

Minimum Model Confidence	Games	Historical Win Rate
65%+	467	70.4%
70%+	286	70.6%
75%+	173	72.8%
80%+	68	88.2%
These values describe historical cohorts, not guarantees for individual future games.

For example, an individual prediction of 77% is the Logistic Regression model's estimated probability. The historical 75%+ cohort win rate is a separate validation statistic.

Final Model
The final model uses:

StandardScaler
      ↓
Logistic Regression
with an 8-game rolling window.

Final six features
Recent Point-Differential Advantage
Recent Win-Percentage Advantage
Defensive EPA Advantage
Offensive Success-Rate Advantage
Defensive Success-Rate Advantage
Offensive Yards-per-Play Advantage
Feature differences are consistently oriented so that positive values indicate an advantage for the home team.

Preventing Data Leakage
Preventing future information from entering historical predictions was a major design requirement.

Historical rolling features use patterns such as:

x.shift(1).rolling(8).mean()
The shift(1) removes the current game before calculating the team's historical feature.

Conceptually:

Games 1–8
    ↓
Game 9 pregame features
    ↓
Predict Game 9
Game 9's result never contributes to the features used to predict Game 9.

The live prediction implementation was also tested against historical games to verify exact feature parity between:

Historical training pipeline
            vs.
Live prediction pipeline
All six final features matched exactly in the parity test.

Model Development
The final model was selected through controlled feature and algorithm experiments rather than simply adding every available statistic.

Retained
8-game rolling window
Point differential
Win percentage
Defensive EPA
Offensive success rate
Defensive success rate
Offensive yards per play
Logistic Regression
Tested but not retained
Rest differential
Turnover margin
Split passing/rushing EPA
Simple strength of schedule
QB history advantage
QB change indicators
Random Forest
Gradient Boosting
Sigmoid probability calibration
Some rejected features were strongly related to game outcomes but did not improve prediction of future games after accounting for the existing feature set.

Feature-correlation analysis and standardized Logistic Regression coefficients were also used to remove redundant features.

The model improved after being reduced from nine core features to six.

Architecture
NFL Data
   │
   ▼
src/data.py
   │
   │  schedules
   │  team-game records
   │  EPA
   │  success rate
   │  yards per play
   ▼
src/features.py
   │
   │  leakage-safe rolling features
   │  matchup differences
   ▼
src/build_dataset.py
   │
   ▼
Model-Ready Dataset
   │
   ▼
src/model.py
   │
   │  StandardScaler
   │  Logistic Regression
   ▼
Win Probabilities
   │
   ▼
src/run_predictions.py
   │
   ▼
data/latest_predictions.csv
   │
   ▼
Streamlit Dashboard
The prediction refresh and dashboard display are intentionally separated.

The expensive modeling workflow runs independently:

python -m src.run_predictions
That command refreshes:

data/latest_predictions.csv
The Streamlit application only reads the saved prediction file, keeping dashboard startup fast.

Dashboard
Weekly Predictions
The dashboard automatically identifies the next upcoming NFL week and displays:

Featured highest-confidence picks
Full weekly prediction slate
Predicted winner
Home and away win probabilities
Confidence classifications
Matchup deep dives
Model feature advantages
Supplemental game context
Market lines, quarterback names, stadium information, and other game metadata may be displayed for context but are not inputs to the six-feature model.

assets/dashboard.png

Matchup Deep Dive
The matchup view compares both teams' predicted win probabilities and shows the six model feature advantages that contributed to the matchup representation.

assets/matchup-deep-dive.png

Model Performance
The application also exposes the historical walk-forward results and confidence-tier analysis rather than presenting predictions without validation context.

assets/model-performance.png

Project Structure
nfl-game-prediction/
│
├── app/
│   └── app.py
│
├── assets/
│   ├── dashboard.png
│   ├── matchup-deep-dive.png
│   └── model-performance.png
│
├── data/
│   └── latest_predictions.csv
│
├── notebooks/
│   └── 01_explore_nfl_data.ipynb
│
├── src/
│   ├── __init__.py
│   ├── build_dataset.py
│   ├── data.py
│   ├── evaluate.py
│   ├── features.py
│   ├── model.py
│   ├── predict.py
│   ├── run_predictions.py
│   └── validate_live.py
│
├── .gitignore
├── README.md
└── requirements.txt
Local Setup
1. Clone the repository
git clone <YOUR-REPOSITORY-URL>
cd nfl-game-prediction
2. Create a virtual environment
Windows PowerShell:

python -m venv .venv
.\.venv\Scripts\Activate.ps1
3. Install dependencies
pip install -r requirements.txt
Generate Predictions
Refresh the prediction dataset with:

python -m src.run_predictions
This:

Loads the latest available NFL schedule
Determines available seasons dynamically
Loads historical play-by-play
Builds team-level efficiency metrics
Builds the final six matchup features
Trains the model on completed games
Identifies the next upcoming NFL week
Generates win probabilities
Ranks games by model confidence
Saves the results to:
data/latest_predictions.csv
Launch the Dashboard
Run:

streamlit run app\app.py
The dashboard reads the saved prediction file rather than retraining the model during page startup.

Research Notebook
The original modeling work remains available in:

notebooks/01_explore_nfl_data.ipynb
The notebook documents the exploratory process, including:

Data exploration
Feature engineering
Leakage prevention
Rolling-window comparison
Logistic Regression
Random Forest
Gradient Boosting
EPA experiments
Turnover experiments
Success-rate experiments
Yards-per-play experiments
QB features
Strength-of-schedule experiments
Correlation analysis
Feature reduction
Probability calibration analysis
The notebook serves as the research record, while src/ contains the reusable implementation.

Technology
Python
pandas
Polars
nflreadpy
scikit-learn
Streamlit
JupyterLab
Matplotlib
Seaborn
Git / GitHub
Key Engineering Decisions
Chronological validation
NFL games are temporal data. The project therefore uses walk-forward validation instead of random train/test splitting.

Training-serving parity
Historical and live feature calculations were explicitly compared before live predictions were trusted.

Lightweight application architecture
The expensive data and ML workflow is separated from the dashboard.

Prediction refresh
       ↓
Saved CSV
       ↓
Fast Streamlit UI
Simple model over unnecessary complexity
Random Forest and Gradient Boosting were tested but did not outperform Logistic Regression.

The final model favors the simplest approach that generalized well.

Future Work
Potential future improvements include:

Automated prediction refreshes using GitHub Actions
Deployed Streamlit application
Reliable pregame starting-QB integration
Expanded early-season handling
Automated historical prediction tracking
Additional probability-calibration monitoring
Longer-term model-performance tracking across future NFL seasons
Disclaimer
This project is an independent machine learning and sports analytics project.

Model probabilities are statistical estimates based on historical NFL performance and are not guaranteed outcomes.

The project is not affiliated with or endorsed by the National Football League or its teams.