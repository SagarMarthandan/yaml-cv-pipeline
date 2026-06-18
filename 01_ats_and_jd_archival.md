# Pipeline Step 1: ATS Check & Job Description Archival

## Objective
Analyze the target job description (JD) against the candidate's base resume and project portfolio to detect gaps, classify the role archetype, calculate an ATS score, and structure the clean JD for archival.

## Inputs
- **Job Description (JD):** Paste target JD text at the bottom.
- **Base Resume & Portfolio:** Loaded from `C:\Users\sagar\Documents\YAML-CV\Base Files\<Language>\` (automatically selected based on detected JD language: English or German).

## Execution Rules

### 0. Pre-Scoring: Verify Dependencies & Load Base Files
Before any scoring or analysis, perform the following verification and loading steps:
1. **Dependency Installation:** The agent MUST run the pip install command to guarantee all required packages in `requirements.txt` are installed before execution:
   ```powershell
   C:\Users\sagar\AppData\Local\Programs\Python\Python312\python.exe -m pip install -r "C:\Users\sagar\Documents\YAML-CV\skills\yaml-cv-pipeline\requirements.txt"
   ```
2. **Load base resume:** Load the candidate's base resume from the detected language folder:
   - `resume.md` (use `resume_de.md` for German JDs)
   *(Note: You do not need to load the global project_info.md file in Step 1, because the Zvec search command in Step 1 will dynamically generate a tailored project_info.md file inside the application folder).*

Do not proceed to scoring without first running the dependency installation and loading the base resume file. All gap analysis and keyword comparisons must reference the loaded resume content.

### 1. Requirements & Archetype Detection
- Scan candidate-facing profile requirements.
- Classify the JD into exactly one primary role archetype (e.g., Data Engineering, Analytics Engineering, Data Analyst, AI Engineer, AI/LLMOps, Agentic/Automation, ML Engineering, Backend/Platform Engineering).
- Save selection and a one-sentence rationale under `role_archetype` in the YAML output.
- **Secondary archetype:** If the JD clearly spans two domains (e.g., requires both ML engineering and data platform work), assign a `secondary` archetype with its own one-sentence rationale. If the JD is focused on a single domain, omit the `secondary` field entirely.

### 2. German-Market ATS Scoring Matrix
- Grade the current resume against a German-market calibrated matrix (0-100 total):
  - `keywords_and_terminology` (max 25)
  - `experience_relevance` (max 25)
  - `technical_skills` (max 20)
  - `formatting_and_parse` (max 15)
  - `soft_skills_and_language` (max 15)
- Save details and total score in `ats_score_matrix` in the YAML output.
- **Score Gate:** If `total_score < 85`, set `score_gate_verdict: HOLD` and stop the pipeline. Populate `remedy_suggestions` as a structured list (see schema). Warn the user to review remedies before proceeding to Step 2. If `>= 85`, set `score_gate_verdict: PROCEED`.

### 3. Improvement Blueprint Generation
Populate each field of `improvement_blueprint` as follows:
- **`bullet_point_density_audit`:** For each bullet in the base resume's experience and projects sections, check if it contains a quantified metric (number, percentage, or time unit). List any bullets that are metric-free as items requiring quantification.
- **`project_swap_directive`:** Compare each project in the portfolio against the JD archetype. List projects that are misaligned under `remove_projects`. List archetype-aligned projects from `project_info.md` that are not currently in the base resume under `add_projects`, each with a one-sentence `justification`. Confirm exactly 3 (or 4 if score improves) are selected.
- **`keyword_inventory`:** Extract only JD keywords that are **absent from the base resume** (gap-only approach). Do not list keywords already present. Categorize absences into `hard_skills`, `methodologies`, and `domain_terms`.
- **`technical_skills_tuning`:** List tools/technologies to add (present in JD, absent from resume skills section) and to remove (present in resume skills section but irrelevant or distracting for this role).
- **`quantified_outcomes`:** For each metric-free bullet identified in the density audit, suggest a concrete revised version that adds a plausible quantified outcome.

### 4. Job Description Archival
- Strip web tracking, cookies, duplicate fields, and metadata from the raw JD.
- Structure into clean YAML sections (overview, requirements, responsibilities, stack) for permanent reference.

## Output Target & Directory Structure
Create folder `C:\Users\sagar\Documents\YAML-CV\Applications\[Company Name] — [Job Role]\` and save three files:
- `ATS_Report.yaml`
- `Job_Description.yaml`
- `project_info.md` (tailored project portfolio generated via Zvec search)

### A. `ATS_Report.yaml` Schema
```yaml
type: ats_report
company: "[Company Name]"      # Used by the PDF renderer for the report title
position: "[Job Position Title]"  # Used by the PDF renderer for the report subtitle
role_archetype:
  primary: "[Archetype Name]"
  secondary: "[Secondary Archetype — omit this field if JD is single-domain]"
  archetype_rationale: "[One sentence rationale for primary]"
  secondary_rationale: "[One sentence rationale for secondary — omit if secondary omitted]"
ats_score_matrix:
  keywords_and_terminology: { max_score: 25, current_score: 0, evaluation_criteria: "..." }
  experience_relevance: { max_score: 25, current_score: 0, evaluation_criteria: "..." }
  technical_skills: { max_score: 20, current_score: 0, evaluation_criteria: "..." }
  formatting_and_parse: { max_score: 15, current_score: 0, evaluation_criteria: "..." }
  soft_skills_and_language: { max_score: 15, current_score: 0, evaluation_criteria: "..." }
  total_score: 0
core_score_detractors: []
improvement_blueprint:
  target_language_confirmation: "German/English"
  bullet_point_density_audit:
    - bullet: "[Exact bullet text from base resume]"
      issue: "No quantified metric"
  project_swap_directive:
    remove_projects: []
    add_projects: [{ name: "...", justification: "..." }]
    volume_constraint_check: "3 projects selected"
  keyword_inventory:
    hard_skills: []      # JD keywords absent from resume only
    methodologies: []    # JD methodologies absent from resume only
    domain_terms: []     # JD domain terms absent from resume only
  technical_skills_tuning:
    add: []
    remove: []
  quantified_outcomes:
    - original: "[Metric-free bullet]"
      suggested: "[Revised bullet with quantified outcome]"
  ats_threshold_calibration:
    meets_target: false
    score_gate_verdict: "HOLD/PROCEED"
    remedy_suggestions:
      - "[Specific action: e.g., swap Project X for Project Y from portfolio]"
      - "[Specific action: e.g., add missing keyword 'dbt' to Technical Skills]"
      - "[Specific action: e.g., rewrite IBM bullet 3 to include a throughput metric]"
# --- Populated by Step 2 only. Do not fill during Step 1. ---
post_rewrite_ats_score:
  ats_score_matrix:
    keywords_and_terminology: { max_score: 25, current_score: null, evaluation_criteria: "..." }
    experience_relevance: { max_score: 25, current_score: null, evaluation_criteria: "..." }
    technical_skills: { max_score: 20, current_score: null, evaluation_criteria: "..." }
    formatting_and_parse: { max_score: 15, current_score: null, evaluation_criteria: "..." }
    soft_skills_and_language: { max_score: 15, current_score: null, evaluation_criteria: "..." }
    total_score: null
  score_delta: null
  score_gate_verdict: null
  remaining_gaps: []
```

### B. `Job_Description.yaml` Schema
```yaml
type: job_description
company: "[Company Name]"
position: "[Job Position Title]"
sections:
  - title: "Core Role Overview & Context"
    content: "[Overview paragraph]"
  - title: "Target Profile Requirements"
    bullets:
      - "[Requirement]"
  - title: "Primary Responsibilities"
    bullets:
      - "[Responsibility]"
  - title: "Tech Stack & Tooling"
    bullets:
      - "[Tool/Skill]"
```

## Compilation & Portfolio Search Commands
Run the Zvec search and the compiler immediately after writing the files to generate the assets:
```powershell
cd "C:\Users\sagar\Documents\YAML-CV\Applications\[Company Name] — [Job Role]\"

# 1. Search and generate the tailored project list using Zvec (fully offline)
C:\Users\sagar\AppData\Local\Programs\Python\Python312\python.exe "C:\Users\sagar\Documents\YAML-CV\skills\yaml-cv-pipeline\zvec_portfolio_search.py" "Job_Description.yaml" "project_info.md"

# 2. Compile ATS Report
C:\Users\sagar\AppData\Local\Programs\Python\Python312\python.exe "C:\Users\sagar\Documents\YAML-CV\skills\yaml-cv-pipeline\yaml_to_pdf.py" "ATS_Report.yaml" "ATS_Report.pdf"

# 3. Compile Job Description
C:\Users\sagar\AppData\Local\Programs\Python\Python312\python.exe "C:\Users\sagar\Documents\YAML-CV\skills\yaml-cv-pipeline\yaml_to_pdf.py" "Job_Description.yaml" "Job_Description.pdf"
```

---
### ATTACHMENTS FOR PROCESSING
[PASTE JOB DESCRIPTION HERE]
