# TxLINE + Marcia Sensitiva AI

A real-time sports analytics application focused on monitoring live odds movements and identifying match trends as games unfold.

## Overview

The application provides real-time analysis during football matches, helping users understand market behavior, detect momentum shifts, and project possible match scenarios through AI-powered insights.

## Features

- Monitor live match events and betting odds in real time.
- Detect significant market and odds fluctuations.
- Identify momentum changes and potential opportunities.
- Generate AI-powered contextual insights.
- Organize matches into categories:
  - Live Matches
  - Upcoming Matches
  - Finished Matches
- Track odds evolution through interactive charts.
- Display a complete match event timeline.
- Simple and interactive interface built with Streamlit.

## Main Capabilities

- Real-time market scanning to identify opportunities.
- Historical visualization of odds movements.
- Live match timeline.
- AI-assisted contextual analysis.
- Interactive dashboard for monitoring multiple matches.

## Technologies

- Python
- Streamlit
- Pandas
- Plotly
- TxLINE API
- Artificial Intelligence (LLM)

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd AiHackathon
```

### 2. Install dependencies

```bash
pip install streamlit pandas plotly
```

### 3. Run the application

```bash
streamlit run app.py
```

## Project Structure

```text
AiHackathon/
│
├── app.py                 # Main Streamlit application
├── ai_analyst.py          # AI-powered analysis logic
├── data_processor.py      # Odds and match data processing
├── database.py            # Data persistence layer
├── txline_client.py       # TxLINE API integration
├── worldcup*.json         # Match fixtures and World Cup datasets
└── README.md
```

## How It Works

The application continuously receives live match data and betting odds from the TxLINE API. It processes this information in real time, tracking market movements, match events, and statistical changes.

The AI engine analyzes the evolving context of each match to generate insights about momentum shifts, potential scenarios, and notable market behavior, presenting the information through an intuitive Streamlit dashboard.

## Disclaimer

This application is designed as a decision-support tool for sports analytics and live match monitoring. The AI-generated insights are intended to assist users in understanding market dynamics and match progression and should not be interpreted as guaranteed predictions or financial advice.
