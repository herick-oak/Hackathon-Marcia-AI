# TxLINE + Marcia Sensitiva AI

An AI-powered sports analytics platform built for real-time football match monitoring. The application tracks live odds, analyzes in-game events, and identifies market trends to help users better understand match momentum and evolving scenarios.

## Overview

TxLINE + Marcia Sensitiva AI combines live sports data with artificial intelligence to provide contextual insights during football matches. By continuously monitoring odds movements, match events, and market behavior, the application highlights significant changes and generates intelligent analyses in real time.

The project is designed as a decision-support tool, allowing users to visualize market dynamics rather than simply displaying raw statistics.

---

## Features

- ⚽ Monitor live football matches in real time.
- 📈 Track betting odds and market movements.
- 🔍 Detect significant odds fluctuations and momentum shifts.
- 🤖 Generate AI-powered contextual analysis.
- 📊 Visualize historical odds evolution with interactive charts.
- 🕒 Display a complete timeline of match events.
- 🎯 Identify potential market opportunities.
- 📂 Organize matches into:
  - Live Matches
  - Upcoming Matches
  - Finished Matches
- 💻 Interactive dashboard built with Streamlit.

---

## Tech Stack

### Backend

- Python

### Data Processing

- Pandas
- Requests

### Artificial Intelligence

- LangChain
- LangChain Core
- LangChain Community
- LangChain Groq
- Groq LLM

### Visualization

- Streamlit
- Plotly

### Configuration

- Python Dotenv

### Data Source

- TxLINE API

---

## Installation

### Clone the repository

```bash
git clone https://github.com/<your-username>/AiHackathon.git
cd AiHackathon
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
streamlit run app.py
```

---

## Project Structure

```text
AiHackathon/
│
├── json/                     # Match fixtures and JSON datasets
├── app.py                    # Main Streamlit application
├── ai_analyst.py             # AI analysis engine
├── data_processor.py         # Match and odds processing
├── database.py              # Data persistence layer
├── requirements.txt         # Project dependencies
└── README.md
```

---

## How It Works

1. The application connects to the TxLINE API.
2. Live fixtures, odds, and match events are continuously collected.
3. The data processing layer detects relevant market movements.
4. The AI engine analyzes the current match context, statistics, and odds behavior.
5. Insights are generated and displayed through an interactive Streamlit dashboard.

---

## AI Analysis

The AI module evaluates multiple aspects of each match, including:

- Match momentum
- Offensive and defensive pressure
- Odds variations
- Market sentiment
- Contextual game events
- Potential trend reversals

The generated insights help users understand how the match is evolving and identify noteworthy situations as they happen.

---

## Dependencies

```text
requests
pandas
streamlit
plotly
python-dotenv

langchain
langchain-core
langchain-community
langchain-groq

txline
```

---

## Future Improvements

- Historical match database
- Performance analytics dashboard
- Advanced market trend detection
- Custom alerts and notifications
- Multi-league support
- Predictive analytics using machine learning
- Exportable reports and insights

---

## Disclaimer

This project is intended for sports analytics, research, and educational purposes. The AI-generated insights are designed to support decision-making by analyzing live match context and market behavior. They should not be interpreted as guaranteed predictions or financial advice.

---

## License

This project is licensed under the MIT License.
