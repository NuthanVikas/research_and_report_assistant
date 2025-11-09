# Research & Report Assistant

Research & Report Assistant is a FastAPI service that orchestrates a LangGraph-powered multi-agent workflow specialized for health and pharmaceutical research. It coordinates domain-specific research, multi-format reporting, and PDF generation so product teams can turn open-ended questions into decision-ready deliverables with a single API call.

## Highlights
- **Multi-agent workflow** – Supervisor, research, health, pharma, summary, and document agents collaborate through LangGraph with explicit routing logic.
- **Live domain research** – Health and pharma specialists use Tavily search results plus GPT-4o reasoning to ground every answer in fresh evidence.
- **Reporting automation** – Summary and document agents transform findings into executive briefs or fully formatted PDFs stored under `reports/`.
- **FastAPI interface** – A single `POST /ask` endpoint kicks off the workflow, making it easy to embed inside dashboards, chatbots, or analyst tooling.
- **Configurable LLM stack** – Swap OpenAI models or extend the workflow with additional agents without touching the API surface.

## Architecture
### Workflow at a glance
```text
User → Supervisor → Research Agent → (Health Agent | Pharma Agent) → Research Agent
            ↓                                                ↘
            └──────────────→ Report Agent ← (Summary Agent | Document Agent)
                                      ↓
                               Final answer + optional PDF
```

### Key components
| Component | Location | Responsibility |
| --- | --- | --- |
| Supervisor Agent | `app/agents/supervisor.py` | Decides which specialist should act next and when to end the workflow. |
| Research Agent | `app/agents/research.py` | Routes domain questions to health or pharma specialists via structured LLM decisions. |
| Health & Pharma Agents | `app/agents/subagents/` | Run Tavily-powered research and return structured findings. |
| Report Agent | `app/agents/report.py` | Chooses between summary, document creation, or finalizing the response. |
| Summary Agent | `app/agents/subagents/summary_agent.py` | Produces concise executive summaries. |
| Document Agent | `app/agents/subagents/document_agent.py` | Formats reports and exports PDFs with ReportLab. |
| LangGraph State | `app/core/agent_state.py` | Tracks conversation messages and completion flags. |
| Tools & LLMs | `app/tools/search_tool.py`, `app/utils/llms.py` | Provide Tavily search access and configured ChatOpenAI models. |

## Project layout
```
app/
├─ main.py                # FastAPI entrypoint
├─ agents/
│  ├─ supervisor.py
│  ├─ research.py
│  ├─ report.py
│  └─ subagents/
│     ├─ health_agent.py
│     ├─ pharma_agent.py
│     ├─ summary_agent.py
│     └─ document_agent.py
├─ core/
│  ├─ agent_state.py
│  ├─ graph.py
│  └─ routing_models.py
├─ tools/search_tool.py
└─ utils/llms.py
reports/                 # PDF outputs (created on demand)
```

## Prerequisites
- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/) or `pip` for dependency management
- OpenAI account with an API key (default model: `gpt-4o`)
- Tavily Search API key for grounded reseach
- (Optional) `make`, `curl`, or tools you prefer for local workflows

## Installation & setup
```bash
git clone https://github.com/<your-org>/research_and_report_assistant.git
cd research_and_report_assistant

# Using uv (recommended)
uv sync

# Or using pip
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment variables
Create a `.env` file (or export the variables) before running the app:
```bash
OPENAI_API_KEY=sk-********************************
TAVILY_API_KEY=tvly-******************************
OPENAI_MODEL=gpt-4o            # Optional override
```

### Running the API
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# or: uvicorn app.main:app --reload
```
Visit `http://127.0.0.1:8000/docs` for interactive Swagger documentation.

## API reference
### `GET /`
Health check that confirms the service is running.

### `POST /ask`
Kick off the entire research-and-report workflow with one question.

Request:
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
        "question": "Summarize recent GLP-1 obesity studies and produce a short report."
      }'
```

Response (truncated):
```json
{
  "question": "Summarize recent GLP-1 obesity studies and produce a short report.",
  "answer": "SUMMARY:\n• GLP-1 receptor agonists ...\n\nReport saved to reports/health_report_20240209_153211.pdf"
}
```
The `answer` field always contains the supervisor's final message, which may include summary text and the file path of any generated PDF.

## Generated reports
- PDF files are stored under `reports/health_report_<timestamp>.pdf`.
- Each document agent run reformats LLM output into headings (`Title`, `Abstract`, `Key Findings`, `Recommendations`, `Conclusion`) using ReportLab.
- Paths to created files are echoed in the final API response so you can stream or attach them downstream.

## Extending the workflow
1. **Add a new specialist** – create another agent function under `app/agents/subagents/` and register it in `app/core/graph.py`.
2. **Wire routing** – update the relevant routing Pydantic model in `app/core/routing_models.py` and adjust the prompts to include the new option.
3. **Swap LLMs** – override `LLMModel(model_name="...")` or inject Anthropic/Groq clients while keeping the same LangChain interface.
4. **Customize output formats** – modify `document_agent.py` to change templates, add charts, or export DOCX/HTML.

## Troubleshooting
- `OPENAI_API_KEY` or `TAVILY_API_KEY` missing → ensure `.env` is loaded (the app raises helpful runtime errors otherwise).
- No PDFs are produced → confirm `reportlab` is installed and the process has write access to the `reports/` directory.
- Repeated routing loops → inspect console logs; each agent prints its activation and routing decision to help trace the LangGraph state.

Research & Report Assistant turns complex healthcare questions into evidence-backed summaries and reports with minimal glue code—perfect for analytics portals, conversational interfaces, or internal knowledge tools. Happy automating!
