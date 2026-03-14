# Project Risk Assessment Agent

> **Built from the thesis:**
> *"Understanding Risk Awareness and Decision Making in Early-Stage Project Planning:
> Comparative Study of Project Managers Across Industries"*
> — Devarshi Kansara, HDBW 2026

---

## Why this agent exists

Research shows that **~70% of project failures** stem from decisions made in the **first 20%** of the project lifecycle — *before* major commitments become physically irreversible.  
This agent operationalises the thesis findings into a practical, interactive tool that helps project managers in **Construction**, **Manufacturing**, and **IT** identify, prioritise, and act on risks *before it is too late*.

---

## Key thesis concepts embedded in the agent

| Concept | What it means | How the agent uses it |
|---|---|---|
| **First 20 % Phase** | The critical window where most risk decisions are made | Structures all guidance around early-stage actions |
| **Safety Premium** | 93 % of veteran PMs invest more upfront to avoid costly stoppages | Recommended framework for all projects |
| **Somatic Verification** | Physically inspect instead of trusting digital dashboards | Recommended for Construction/Manufacturing and high time pressure |
| **Bureaucratic Shield** | Formal tools (FMEA, HAZOP) protect against personal liability | Recommended for senior PMs and high-liability contexts |
| **Two-Way Team Model** | Junior (micro-checks) + Senior (strategic shield) = full risk coverage | Recommended for every project |
| **Reverse Training** | German Process Guardians ↔ Indian Resource Navigators can learn from each other | Applied based on detected cultural archetype |
| **Truth-Link Technology** | IoT sensors / digital twins replace untrustworthy manual reports | Recommended for Manufacturing and IT projects |
| **20 % Reality Check** | Mandatory risk-validation workshop at the end of the first 20 % | Included in every report as a structured agenda |

---

## Project structure

```
.
├── agent/
│   ├── __init__.py          # Package marker
│   ├── knowledge_base.py    # All thesis-derived risk data and frameworks
│   ├── models.py            # Data classes (RiskItem, ProjectContext, AssessmentReport)
│   └── risk_agent.py        # Core agent logic (interview + report generation)
├── tests/
│   └── test_agent.py        # 34 pytest tests covering all components
├── app.py                   # Streamlit web interface
├── main.py                  # CLI entry point
└── requirements.txt
```

---

## Quick start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

*(Only `streamlit` is required for the web UI. The CLI works with Python's standard library only.)*

### 2a. Web interface (recommended)

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser. Fill in the form and click **Generate Risk Assessment**.

### 2b. CLI — interactive interview

```bash
python main.py
```

Answer 4 short sections (background, risk focus, decision style, time pressure) to receive a full report.

### 2c. CLI — demo mode (no input required)

```bash
python main.py --demo
```

Runs a pre-filled construction project scenario and prints the report immediately.

### 2d. Programmatic usage

```python
from agent.risk_agent import RiskAssessmentAgent

agent = RiskAssessmentAgent()
ctx = agent.build_context(
    industry="manufacturing",
    years_experience=12,
    projects_managed=25,
    cultural_region="India",
    top_risks=["Supply chain disruption", "Machine calibration drift"],
    risk_locus="external",
    decision_style="intuition",
    time_pressure="medium",
)
report = agent.generate_report(ctx)

# Access structured data
print(report.summary)
for risk in report.risk_register:
    print(f"[{risk.level}] {risk.description} (score={risk.score})")
```

---

## Running tests

```bash
python -m pytest tests/ -v
```

34 tests covering the knowledge base, data models, and agent logic.

---

## Report sections

Every generated report includes:

1. **Summary** — industry, experience level, time pressure, and top-level risk counts
2. **Risk Register** — scored and sorted list (Critical → High → Medium → Low), combining your top risks with industry-specific knowledge-base risks
3. **Industry Context** — primary external/internal risks and blind spots for outsiders
4. **Experience-Level Guidance** — tailored strengths, development areas, and recommended actions for Junior / Mid / Senior PMs
5. **Decision Frameworks** — contextually selected thesis frameworks with when-to-apply guidance and concrete examples
6. **20 % Reality Check Milestone** — structured workshop agenda and expected output
7. **First 20 % Action Checklist** — industry-specific checklist of concrete early-phase actions
8. **Cultural Archetype** *(if detected)* — Process Guardian vs. Resource Navigator characteristics and cross-training recommendations

---

## Risk scoring model

The agent uses a three-factor Risk Priority Number (RPN) model drawn from the thesis findings:

```
Score = Probability × Impact × Detectability
```

| Factor | Low | Medium | High | Critical |
|---|---|---|---|---|
| **Probability** | 1 | 2 | 3 | — |
| **Impact** | 1 | 2 | 3 | 4 |
| **Detectability** | 1 (early) | 2 (late) | 3 (post-occurrence) | — |

| Score range | Level | Recommended action |
|---|---|---|
| 1–4 | 🟢 Low | Monitor only |
| 5–9 | 🟡 Medium | Assign owner; add mitigation task |
| 10–18 | 🟠 High | Immediate mitigation plan; escalate to sponsor |
| 19–36 | 🔴 Critical | Stop-and-fix before proceeding |

---

*Thesis submitted: 09.02.2026 | Supervisor: Prof. Dominik Bösl (HDBW)*
