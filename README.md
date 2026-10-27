# JobLens AI — AI Job Description Analyzer

JobLens AI turns natural-language job descriptions into structured hiring reports. This version uses Streamlit for the interactive UI, LangGraph for a four-node workflow, Pydantic for validation, and Groq or Google Gemini as the LLM provider.

## Features

- Extracts job title, company, experience, and required skills
- Classifies job category, employment type, and work arrangement
- Separates technical skills from soft skills
- Highlights the top three priority skills
- Generates a summary, responsibilities, and qualifications
- Downloads reports as JSON and Markdown
- Responsive, polished dark dashboard with sample job posts and progress feedback
- Handles missing API keys, invalid inputs, provider quota/rate-limit errors, and unavailable models

## LangGraph workflow

1. **Information Extraction** — role, company, experience, and required skills.
2. **Job Classification** — category, employment type, and work arrangement.
3. **Skill Analysis** — technical skills, soft skills, and top three priorities.
4. **Hiring Report** — a structured report validated with Pydantic.

Each node updates the shared graph state, and the final report is validated before being shown in Streamlit.

## Tech stack

Python, Streamlit, LangGraph, Groq API or Google Gemini API, Pydantic, python-dotenv.

## Project structure

```text
JobLens_AI_Streamlit/
├── app.py
├── joblens/
│   ├── __init__.py
│   ├── schemas.py
│   └── workflow.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Run locally (Windows)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and add your real provider API key. For Groq:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_real_key_here
LLM_MODEL=llama-3.3-70b-versatile
```

Get a key from [Groq Console](https://console.groq.com/keys). Keep `.env` private and never commit it to GitHub.

Start the app:

```powershell
streamlit run app.py
```

Streamlit opens the app in your browser, usually at `http://localhost:8501`.

## Use Gemini instead

Set `LLM_PROVIDER=gemini`, add `GEMINI_API_KEY`, and choose a model currently available to your account, such as `gemini-2.5-flash`. Restart Streamlit after changing `.env`.

## Troubleshooting

- **Missing API key:** check `.env` and restart Streamlit.
- **Invalid key:** verify the key and remove accidental spaces.
- **Rate limit/quota:** wait and retry, or check your provider's limits.
- **Model unavailable:** select a model available to your API account.
- **PowerShell activation blocked:** run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate the environment.
- **Packages not found:** ensure `.venv` is activated and install `requirements.txt` again.

## Important note

AI output may be incomplete or inaccurate. Verify details against the original posting. The app analyzes job descriptions; it does not rank candidates.
