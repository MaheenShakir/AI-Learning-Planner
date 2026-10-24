# 🎓 AI Personalized Learning Planner

An AI-powered Streamlit app that creates personalized learning roadmaps, weekly study schedules, and progress dashboards.

> 🚧 Work in progress: being built step by step.

## Planned Features
- Learning goal form (goal, level, hours/day, days/week, target date, learning style)
- AI-generated roadmap with phases, topics, exercises, mini-projects, and resources
- Realistic weekly study planner
- AI learning assistant (Gemini or Groq)
- Progress tracking saved in SQLite
- Plotly dashboard

## Tech Stack
Python, Streamlit, Pandas, Plotly, SQLite, Gemini API

## Run Locally
```bash
git clone <your-repo-url>
cd ai-learning-planner
python -m venv venv
# Windows: venv\Scripts\activate   |   Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add your API key
streamlit run app.py
```

## Project Structure
```
ai-learning-planner/
├── app.py
├── requirements.txt
├── .streamlit/config.toml
├── data/
├── src/
└── pages/
```
