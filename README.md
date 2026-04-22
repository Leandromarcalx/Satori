# Satori: AI Projects Workspace

Welcome to **Satori**, the central monolithic repository for all ongoing AI, automation, and data exploration projects.

This meticulously organized repository houses a wide array of experimental and functional applications built over time. By maintaining strict structural integrity, each project lives in isolated modular bounds while sharing high-level tooling and exploratory documentation.

## 📂 Repository Structure

```text
Satori/
├── README.md               <-- You are here!
├── data_study/             <-- Data analysis and Airflow DAGs
├── notebooks/              <-- Jupyter Notebooks and general experiments
├── scripts/                <-- Global utility executable scripts (e.g., upload_all.ps1, code_1.py)
└── project/                <-- Isolated full-stack applications and bots
    ├── crawler_prices/     <-- Automated web scrapers
    ├── marcal-llm-lab/     <-- General LLM Playground and R&D 
    ├── meal-planner-api/   <-- FastAPI Google GenAI backend agent for receipt OCR and Planning
    ├── meal-planner-web/   <-- Premium React Vite frontend for the AI Meal Planner
    ├── nihongo_bot/        <-- AI Language or Discord Bot modules
    └── schedulers/         <-- Central cron/automation deployment apps
```

## 🚀 Getting Started

If you are cloning this repository, note that you will primarily navigate into specific `project/` subdirectories to execute code relative to their respective environments. 

Look inside individual project directories for further local Setup & `README.md` instruction files (especially when configuring specific `.env` dependencies required for AI interactions!).
