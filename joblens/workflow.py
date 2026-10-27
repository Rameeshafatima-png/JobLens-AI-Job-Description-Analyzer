import json
import os
import re
from typing import Any, TypedDict
from langgraph.graph import END, START, StateGraph
from joblens.schemas import JobInformation, JobClassification, SkillAnalysis, HiringReport


class JobState(TypedDict, total=False):
    job_description: str
    information: dict[str, Any]
    classification: dict[str, Any]
    skills: dict[str, Any]
    report: dict[str, Any]


def _get_llm():
    provider = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    model = os.getenv("LLM_MODEL", "").strip()
    if provider == "groq":
        from langchain_groq import ChatGroq
        if not os.getenv("GROQ_API_KEY"):
            raise ValueError("GROQ_API_KEY is missing from .env")
        return ChatGroq(model=model or "llama-3.3-70b-versatile", temperature=0.1, api_key=os.getenv("GROQ_API_KEY"))
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY is missing from .env")
        return ChatGoogleGenerativeAI(model=model or "gemini-2.5-flash", temperature=0.1, google_api_key=os.getenv("GEMINI_API_KEY"))
    raise ValueError("LLM_PROVIDER must be 'groq' or 'gemini'.")


def _json_response(content: Any) -> dict:
    if isinstance(content, list):
        content = "\n".join(str(x.get("text", x)) if isinstance(x, dict) else str(x) for x in content)
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", str(content).strip(), flags=re.I)
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            raise ValueError("AI response was not valid JSON. Please retry.")
        value = json.loads(match.group())
    if not isinstance(value, dict):
        raise ValueError("AI returned an unexpected response format.")
    return value


def ask(system: str, prompt: str) -> dict:
    response = _get_llm().invoke([
        ("system", system + "\nReturn only valid JSON, without markdown fences. Do not invent details; use 'Not specified' or empty arrays."),
        ("human", prompt),
    ])
    return _json_response(response.content)


def information_extraction_node(state: JobState) -> JobState:
    data = ask(
        "You are a precise recruitment information extraction assistant.",
        "Extract job_title, company_name, required_experience, required_skills. Return those exact JSON keys; required_skills is an array.\nJOB DESCRIPTION:\n" + state["job_description"]
    )
    return {"information": JobInformation.model_validate(data).model_dump()}


def job_classification_node(state: JobState) -> JobState:
    data = ask(
        "You classify job postings conservatively.",
        "Return JSON keys job_category, employment_type, work_arrangement. Category examples: Artificial Intelligence, Data Science, Web Development, DevOps, Design, Marketing, Finance, Other. Employment type: Full-time, Part-time, Contract, Internship, Freelance, Not specified. Work arrangement: Remote, Hybrid, On-site, Not specified.\nJOB DESCRIPTION:\n" + state["job_description"]
    )
    return {"classification": JobClassification.model_validate(data).model_dump()}


def skill_analysis_node(state: JobState) -> JobState:
    data = ask(
        "You are a job skills analyst. Distinguish technical skills from interpersonal skills.",
        "Return JSON arrays technical_skills, soft_skills, top_3_skills. Choose the three most central skills based on explicit emphasis and requirements.\nExtracted information:\n" + json.dumps(state.get("information", {})) + "\nJOB DESCRIPTION:\n" + state["job_description"]
    )
    skills = SkillAnalysis.model_validate(data)
    if not skills.top_3_skills:
        skills.top_3_skills = (skills.technical_skills or skills.soft_skills)[:3]
    return {"skills": skills.model_dump()}


def hiring_report_node(state: JobState) -> JobState:
    data = ask(
        "You write concise, factual hiring reports for job seekers.",
        "Return JSON keys summary (2-3 sentences), responsibilities (array), qualifications (array). Only include details supported by the job post.\nInformation:\n" + json.dumps(state.get("information", {})) + "\nClassification:\n" + json.dumps(state.get("classification", {})) + "\nSkills:\n" + json.dumps(state.get("skills", {})) + "\nJOB DESCRIPTION:\n" + state["job_description"]
    )
    report = {
        **state.get("information", {}),
        **state.get("classification", {}),
        **state.get("skills", {}),
        "summary": str(data.get("summary", "Summary not available.")),
        "responsibilities": data.get("responsibilities", []) if isinstance(data.get("responsibilities", []), list) else [],
        "qualifications": data.get("qualifications", []) if isinstance(data.get("qualifications", []), list) else [],
        "analysis_note": "AI-generated analysis. Verify important details against the original job posting.",
    }
    return {"report": HiringReport.model_validate(report).model_dump()}


def build_graph():
    graph = StateGraph(JobState)
    graph.add_node("information_extraction", information_extraction_node)
    graph.add_node("job_classification", job_classification_node)
    graph.add_node("skill_analysis", skill_analysis_node)
    graph.add_node("hiring_report", hiring_report_node)
    graph.add_edge(START, "information_extraction")
    graph.add_edge("information_extraction", "job_classification")
    graph.add_edge("job_classification", "skill_analysis")
    graph.add_edge("skill_analysis", "hiring_report")
    graph.add_edge("hiring_report", END)
    return graph.compile()


workflow = build_graph()


def analyze_job_description(description: str) -> dict:
    if not description or len(description.strip()) < 40:
        raise ValueError("Please provide a job description with at least 40 characters.")
    result = workflow.invoke({"job_description": description.strip()})
    if not result.get("report"):
        raise ValueError("Workflow completed without producing a report.")
    return result["report"]
