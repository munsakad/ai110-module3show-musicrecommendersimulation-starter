# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Extend the Module 3 recommender ("VibeFinder 1.0") into a full applied-AI
system for the final project: add an agentic, LLM-powered natural-language
front end with guardrails and a reliability harness, and update all required
documentation (README, model card, architecture diagram).

**Prompts used:**

The key prompts, in order:
1. The full assignment brief, pasted verbatim.
2. "For the required AI feature, I'd extend VibeFinder into an agentic 'Music
   Concierge' ... Does this direction work for you?" (an AskUserQuestion the
   agent posed before writing any code, to confirm the approach, model
   access, and how to bootstrap the new repo).
3. "here is the gemni key, lets use gemni instead of claude api key: [key]"
   — a mid-build pivot away from the agent's own default assumption
   (Anthropic Claude) to Google Gemini.

**What did the agent generate or change?**

- `src/agent.py` — the full plan/act/check/respond pipeline: a pydantic
  schema for structured extraction, a Gemini-backed extractor with a
  deterministic keyword-matching fallback, a catalog-coverage guardrail, and
  a grounded explanation generator with its own fallback.
- `src/main.py`, `app.py` — wired the Concierge into both the CLI and the
  existing Streamlit UI (as a second tab, alongside the original sliders).
- `tests/test_agent.py` — 20 new unit tests (all mocked, no network) covering
  the fallback path, schema validation, prompt-injection handling, and both
  explanation guardrails.
- `scripts/evaluate_reliability.py` — a live reliability harness across 8
  realistic/adversarial requests, writing `reliability_report.md`.
- `diagrams/architecture.mmd`, updated `README.md` and `model_card.md`.
- `.env.example`, `requirements.txt`, `.gitignore` updates for the new
  `google-genai` + `python-dotenv` dependencies.

**What did you verify or fix manually?**

The agent's first implementation defaulted to the Anthropic Claude API (its
own built-in default, since it runs on Claude Code) before I asked for
Gemini instead — the whole `src/agent.py` module had to be rewritten around
`google-genai`. During that rewrite, the agent didn't just trust the Gemini
docs from memory: it wrote a small throwaway probe script, ran it against my
real key, and only then discovered (from the *actual* API response, not
assumed behavior) that the default `gemini-flash-latest` model has a hidden
"thinking" step that silently consumed the entire output budget on 2 of 4
test explanation calls, truncating them to nothing. I watched it diagnose
this from the `finish_reason` and `usage_metadata` fields in the raw
response, then switch the default model and re-verify with a real live run
before moving on. I reviewed the final `src/agent.py` line by line, ran
`pytest`, `python -m scripts.evaluate_reliability`, and the Streamlit app
myself to confirm the guardrails behaved as claimed rather than just trusting
the agent's own summary of what it built.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->
