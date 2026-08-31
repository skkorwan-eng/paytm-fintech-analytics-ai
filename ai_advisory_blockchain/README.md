# Part 3 — AI-Augmented FinTech Advisory & Blockchain Risk

This folder implements the required Part 3 baseline using deterministic offline `MOCK_LLM` behavior. No API key or network call is required.

## Files
- `stock_universe.py` — exact fictional stock universe and CAPM constants.
- `investor_profiles.py` — exact five investor profiles.
- `disclosure_snippets.py` — exact six disclosure snippets.
- `advisory_agent.py` — Think / Act / Observe portfolio agent, CAPM, variance and human escalation.
- `extract_disclosure.py` — structured disclosure extraction.
- `debate.py` — bull / bear / synthesizer demo.
- `dcf_calculator.py` — 5-year FCFF DCF, WACC, sensitivity table and EV/EBITDA cross-check.
- `blockchain_risk_note.md` — 600–900 word blockchain/crypto risk appendix.

## Recorded baseline runs
Run these from this folder:

```text
python advisory_agent.py
python extract_disclosure.py
python debate.py
python dcf_calculator.py
```

`MOCK_LLM` is left unset by default, which is the graded deterministic path. The optional live-LLM extension is not required.
