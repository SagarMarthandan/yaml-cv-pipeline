---
name: yaml-cv-pipeline
description: Use when the user wants to generate an ATS-optimized resume and cover letter from a job description. Runs a 3-step pipeline: ATS analysis & JD archival, resume rewrite & layout audit, and cover letter generation. Trigger on keywords like "job description", "resume", "cover letter", "ATS", "apply", "job application", "tailor resume", "optimize resume".
dependencies: python>=3.10, pyyaml, reportlab, pypdf, stop-slop
---

# YAML CV Pipeline

End-to-end pipeline that takes a **Job Description (JD)** and produces a tailored ATS-optimized resume + cover letter as compiled PDFs, plus an archived JD reference and a visual-optimized alternate version.

## Pipeline Overview

```
                        JD + Base Resume
                               │
                               ▼
  Step 1: Setup & ATS Archival ──► ATS_Report.yaml + Job_Description.pdf
         │
         ├───► [Runs Zvec Offline Search on Master Portfolio (repo info.md)]
         │     └───► Generates: project_info.md (Tailored Projects List)
         │
         ▼
  Step 2: Resume & Visual Audit ──► Reads tailored project_info.md
         │                           └───► Generates: Resume.yaml/pdf/tex
         ▼
  Step 3: Cover Letter ───────────► Reads tailored project_info.md
                                     └───► Generates: Cover_Letter.yaml/pdf/tex
```

## Prerequisites

- **Base Files Directory:**
  - **English:** `C:\Users\sagar\Documents\YAML-CV\Base Files\English\` (Base resume files)
  - **German:** `C:\Users\sagar\Documents\YAML-CV\Base Files\German\` (Base German files)
  - **Photo:** `C:\Users\sagar\Documents\YAML-CV\Base Files\Photo\` (Photo image files)
  - **Repo Info:** `C:\Users\sagar\Documents\YAML-CV\Base Files\Repo Info\` (Master portfolio `repo info.md` & `zvec_portfolio` vector database index)
- **Python Installation:** Python 3.10+ with dependencies installed from [requirements.txt](file:///c:/Users/sagar/Documents/YAML-CV/skills/yaml-cv-pipeline/requirements.txt) (`pyyaml`, `reportlab`, `pypdf`, `zvec`, `sentence-transformers` installed)
- **Working Directory:** `C:\Users\sagar\Documents\YAML-CV\Applications\`
- **Pipeline Script Structure:**
  - `yaml_to_pdf.py` — entry point; routes YAML files to the correct renderer
  - `renderers/utils.py` — shared utilities (`escape_latex`, color constants, `run_pdflatex`)
  - `renderers/resume.py` — Resume renderer (LaTeX primary, ReportLab fallback)
  - `renderers/cover_letter.py` — Cover Letter renderer (LaTeX primary, ReportLab fallback)
  - `renderers/job_description.py` — Job Description renderer (LaTeX primary, ReportLab fallback)
  - `renderers/ats_report.py` — ATS Report renderer (ReportLab only)

## General Writing & Style Rules (Stop-Slop)

To ensure all generated text sounds authentic and human, the pipeline step outputs (particularly resume bullet points and cover letter prose) must adhere to the **Stop-Slop** writing guidelines:
- **Core Principle:** Strictly eliminate predictable AI tells, structures, and rhythms.
- **Strict Active Voice:** Ensure every sentence leads with active human action. Avoid passive constructions.
- **Absolute Adverb Ban:** Do not use any adverbs ending in `-ly` or softening emphasis crutches (like *successfully*, *effectively*, *genuinely*, *actually*, *really*).
- **Zero Em-Dashes:** Punctuation em-dashes (`—`) are prohibited; use commas or periods.
- **No Throat-Clearing:** Start sentences directly. Cut preview/recap statements (e.g., *"at its core"*, *"it is worth noting"*, *"the reality is"*).

## Input Required

The user must provide:
1. **Job Description** — paste the full JD text
2. (Optional) **Language override** — if the user wants the output in a specific language different from the JD language

## Execution — Run All 3 Steps Sequentially

### STEP 1: Setup, ATS Analysis & Job Description Archival

Read and execute the full instructions in [01_ats_and_jd_archival.md](file:///c:/Users/sagar/Documents/YAML-CV/skills/yaml-cv-pipeline/01_ats_and_jd_archival.md).

- Automatically runs the dependency installation command using the `requirements.txt` file.
- Detects Job Description (JD) language (English or German).
- Classifies the role archetype and sets `role_archetype` in the report.
- Scores the base resume against the 5-category ATS matrix (0–100).
- Applies the **ATS Score Gate** (if score < 85, stop and warn).
- Cleans and formats the raw JD into `Job_Description.yaml`.
- Saves ATS metrics to `ATS_Report.yaml` in the company directory.
- Runs the local offline Zvec search tool on the job description to find the top 4 matching projects from your global portfolio, writing them to a tailored `project_info.md` file in the company folder.
- Compiles `ATS_Report.pdf` and `Job_Description.pdf`.

**Output:** `ATS_Report.yaml`, `ATS_Report.pdf`, `Job_Description.yaml`, `Job_Description.pdf`, and `project_info.md` in `[Company Name] — [Job Role]/` folder.

---

### STEP 2: Resume Rewrite & Visual Layout Audit

Read and execute the full instructions in [02_resume_and_visual_audit.md](file:///c:/Users/sagar/Documents/YAML-CV/skills/yaml-cv-pipeline/02_resume_and_visual_audit.md).

**What this step does:**
- Rewrites the resume to `Resume.yaml` using the Step 1 Improvement Blueprint and the local `project_info.md` tailored project list.
- Compiles the initial PDF from `Resume.yaml` using the python compiler.
- Performs post-processing on the generated LaTeX file `SAGAR_MARTHANDAN_Resume.tex` (or `SAGAR_MARTHANDAN_Lebenslauf.tex` for German) to convert all project entries from bullet-list format to compact single-paragraph format (each <= 300 characters for English, <= 250 for German, tools and metrics woven in).
- Enforces strict styling, bullet length (<= 105 characters for experience bullets), line limits (4 lines for summary), and bullet count constraints.
- Performs a Stop-Slop audit (active voice, adverb ban, etc.) and visual eye-test audit.
- Outputs findings to `Layout_Audit_Report.yaml` and self-corrects any formatting issues directly.
- Runs post-rewrite ATS rescoring, updates the `post_rewrite_ats_score` block in `ATS_Report.yaml`, and rebuilds `ATS_Report.pdf`.
- Recompiles the final `SAGAR_MARTHANDAN_Resume.pdf` (or `SAGAR_MARTHANDAN_Lebenslauf.pdf` for German) from the polished LaTeX file.

**Output:** `Resume.yaml`, `Layout_Audit_Report.yaml`, and `SAGAR_MARTHANDAN_Resume.pdf` / `SAGAR_MARTHANDAN_Lebenslauf.pdf` (and `Resume_v2.pdf` / `Lebenslauf_v2.pdf` if needed).

---

### STEP 3: Cover Letter Generation & Compilation

Read and execute the full instructions in [03_cover_letter.md](file:///c:/Users/sagar/Documents/YAML-CV/skills/yaml-cv-pipeline/03_cover_letter.md).

**What this step does:**
- Generates a formal, metric-grounded cover letter adapted to the German business layout (*Geschäftsbrief*).
- Outputs the structured content to `Cover_Letter.yaml`.
- Respects narrative guidelines and Stop-Slop constraints.
- Compiles the final `SAGAR_MARTHANDAN_Cover_Letter.pdf` (or `SAGAR_MARTHANDAN_Anschreiben.pdf` for German).

**Output:** `Cover_Letter.yaml` and `SAGAR_MARTHANDAN_Cover_Letter.pdf` / `SAGAR_MARTHANDAN_Anschreiben.pdf`.

---

## Error Handling

If the compilation fails:
1. Check stdout/stderr console logs for PyYAML parser errors or ReportLab layout exceptions.
2. Verify YAML formatting is correct (e.g. check for unquoted colons, incorrect indentations).
3. If an image is missing, ensure Sagar.jpg is placed in the designated Base Files path.
4. If there's a layout overflow, trim the text length in the resume YAML.

## Completion Checklist

After all 3 steps complete, verify:
- [ ] `ATS_Report.yaml` exists in the company folder with pre and post rewrite scores
- [ ] `ATS_Report.pdf` is generated and `post_rewrite_ats_score` block is populated
- [ ] `Job_Description.yaml` & `Job_Description.pdf` are generated
- [ ] `project_info.md` (tailored project list) is generated in the company folder
- [ ] `Resume.yaml` & `SAGAR_MARTHANDAN_Resume.pdf` / `SAGAR_MARTHANDAN_Lebenslauf.pdf` are generated
- [ ] `SAGAR_MARTHANDAN_Resume.tex` / `SAGAR_MARTHANDAN_Lebenslauf.tex` & `SAGAR_MARTHANDAN_Cover_Letter.tex` / `SAGAR_MARTHANDAN_Anschreiben.tex` are preserved in the folder
- [ ] `Layout_Audit_Report.yaml` is generated with all eye-test diagnostics at Pass status
- [ ] `Cover_Letter.yaml` & `SAGAR_MARTHANDAN_Cover_Letter.pdf` / `SAGAR_MARTHANDAN_Anschreiben.pdf` are generated
- [ ] Professional Experience bullet points are strictly single-line and <= 105 characters
- [ ] Project entries are in single-paragraph format, with name + `---` + description (no bullets), each <= 300 characters (<= 250 characters for German) and fitting on <= 3 lines
- [ ] Summary section is exactly 4 lines and <= 420 characters (<= 380 characters for German Zusammenfassung)
- [ ] Cover letter fits on exactly one page and has 250–320 words (180–240 words for German Anschreiben)
- [ ] All files match the target JD language and comply with the Stop-Slop guidelines

