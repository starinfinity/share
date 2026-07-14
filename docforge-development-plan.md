# DocForge — Development Plan & Project Structure

**Version:** 3.1 | Companion to DocForge Architecture v1.3 | July 2026
**Team:** 1–2 developers working AI-assisted (agentic coding tools writing most code, human owning design, review, and verification)
**Posture:** full quality scope; NAS Search packaged as a standalone reusable service with its own chat frontend; pipeline steps skippable per run

---

## 1. Re-planning for a Small, AI-Assisted Team — Without Quality Cuts

Three principles drive this version:

1. **Operational simplicity is not a quality cut — keep it.** One backend service with two entrypoints, Entra ID instead of self-hosted Keycloak, one monorepo: these reduce what two people must operate while making the product *more* reliable, not less. They all stay.
2. **AI writes, the human verifies — so verification machinery comes first, not last.** With agentic coding tools authoring most code, raw typing speed stops being the bottleneck; the bottleneck becomes your confidence that what was written is correct. Consequently the eval and test infrastructure that v2.0 deferred moves *earlier*: recorded-fixture graph tests from M1, Langfuse tracing from M0, eval-gated prompt changes from M2. This is the single biggest structural change in v3.0.
3. **Full scope, dependency-ordered.** Nothing is dropped. Multi-ecosystem validation, team RBAC, and eval-gated CI — deferred in v2.0 — return as milestone M7. Repo auto-discovery stays late (M6) purely on dependency and value-ordering grounds: it needs the repo index, and a pasted URL is a ten-second user cost in the meantime. That is sequencing, not compromise.

### What AI-assisted development actually compresses (and what it doesn't)

Compresses well (2–4×): parsers, CRUD/API routes, React components, test scaffolding, Helm/K8s manifests, docxtpl work, the runner. Compresses modestly (~1.5×): agent/graph logic, where design and debugging dominate. Barely compresses at all: infrastructure provisioning and cluster debugging, org dependencies (GitHub App approval, Azure OpenAI quota increases, NAS account issuance — start all three in week 1), prompt-quality iteration (bounded by evaluation, not writing), pilot feedback loops, and your own review bandwidth. The timeline below applies compression only where it's real.

### Timeline

| Milestone | Duration (2 devs + AI) | Cumulative | Solo + AI |
|---|---|---|---|
| M0 Foundations + observability | 2.5 wks | wk 2.5 | 4 wks |
| M1 Converse & Understand | 3 wks | wk 5.5 | 5 wks |
| M2 Plan & Approve (evals live) | 2.5 wks | wk 8 | 4 wks |
| M3 Spec & Download | 1.5 wks | wk 9.5 | 2.5 wks |
| M4 Code, Test & PR | 4 wks | wk 13.5 | 7 wks |
| M5 NAS Search service + RAG | 3.5 wks | wk 17 | 5.5 wks |
| M6 Repo Discovery & Hardening | 3 wks | wk 20 | 5 wks |
| M7 Full-Quality Completion | 3 wks | wk 23 | 5 wks |

≈ **5–5.5 months to full scope with 2 devs + AI; ~9 months solo + AI.** A usable end-to-end product (through M4) lands at ~3.5 months / 2 devs. Note the compression versus v2.0 is real but bounded (~20–25%, not 3×): milestones M0, M4-pilot, and everything gated on org processes shrink the least, and review time grows as authored-code volume grows.

---

## 2. Project Structure

Same monorepo rationale as before — shared schemas are touched by every service — but the deployables are now **four containers** (see Architecture §4.6): `web`, `core` (FastAPI + LangGraph workers, one image, two entrypoints), the **standalone `nas-search` service** (indexer + versioned REST API + its own NAS Chat frontend, reusable org-wide), and the sandbox image. The decomposition rule: a capability gets its own service only when it has a consumer besides DocForge — NAS search does (org-wide NAS chat); planning and doc generation don't yet, so they stay in core.

```
docforge/
├── apps/
│   ├── web/                          # React SPA (Vite + TS + shadcn/ui)
│   │   └── src/
│   │       ├── features/
│   │       │   ├── chat/             # conversation, file drag-and-drop
│   │       │   ├── intake-report/    # inventory, understanding, flow diagram,
│   │       │   │                     #   completeness checks, run-config toggles
│   │       │   ├── plan-review/      # task cards, unachievable list, approve/edit
│   │       │   ├── run-progress/     # WebSocket status timeline, kill switch
│   │       │   └── downloads/
│   │       ├── api/                  # typed client generated from OpenAPI
│   │       └── auth/                 # Entra ID (OIDC/MSAL) integration
│   │
│   └── core/                         # container: docforge-core (two entrypoints)
│       ├── src/docforge/
│       │   ├── api/                  # FastAPI: sessions, uploads, runs, plans, docs, ws
│       │   ├── graph/
│       │   │   ├── state.py          # typed RunState incl. RunConfig (skip toggles)
│       │   │   ├── build.py          # nodes + conditional edges routing around skips
│       │   │   └── checkpointer.py
│       │   ├── agents/
│       │   │   ├── ingestion/        # → Project Intake Report
│       │   │   ├── classifier/
│       │   │   ├── planner/          # six feasibility rules; skip-gap awareness
│       │   │   ├── documentation/    # docxtpl fill; doc updater; skippable
│       │   │   ├── coding/  validation/  pr/
│       │   │   ├── nas_retrieval/    # thin HTTP client of the nas-search service
│       │   │   └── repo_discovery/   # M6
│       │   ├── tools/                # git, github, sandbox client, minio
│       │   ├── prompts/              # versioned prompt files per agent
│       │   ├── llm.py  storage.py
│       │   └── worker.py
│       └── tests/  (unit/ + graph/ replay tests with recorded LLM fixtures)
│
├── services/
│   └── nas-search/                   # container: nas-search — STANDALONE, org-reusable
│       ├── src/nas_search/
│       │   ├── api/                  # /v1: search, answer (RAG + citations),
│       │   │                         #   documents/{id}, index/status — Entra auth
│       │   ├── indexer/              # SMB walk, mtime+hash incremental, chunk,
│       │   │                         #   embedding-003 → pgvector (own schema)
│       │   ├── retrieval/            # hybrid vector+FTS, GPT 5.5 rerank
│       │   └── rag/                  # answer synthesis with file-path citations
│       ├── ui/                       # lightweight NAS Chat SPA, served by the service
│       └── tests/                    # incl. recall@k harness (hand-labeled pairs)
│
├── packages/
│   ├── docforge-schemas/             # Pydantic: RunState, RunConfig, Plan, IntakeReport…
│   └── docforge-parsing/             # pptx/docx/xlsx/txt/image parsers — used by
│                                     #   core ingestion AND nas-search indexer
│
├── sandbox/
│   ├── image/                        # Dockerfile: git + Python toolchain
│   └── runner/                       # in-sandbox executor: edits, commands, results
│
├── templates/tech-spec/              # org template as docxtpl + placeholder schema
├── infra/
│   ├── helm/                         # umbrella chart + independent nas-search chart
│   └── k8s/                          # namespaces, NetworkPolicies, RuntimeClass,
│                                     #   SMB CSI, KEDA
├── fixtures/                         # sample-uploads/ + target-repo/
├── tests/e2e/
├── docs/                             # architecture, ADRs, runbooks
└── .github/workflows/
```

Notes: `nas-search` treats DocForge as an external consumer — versioned API, no shared tables, own Helm chart and release cycle — which is precisely what makes the org-wide NAS Chat use case free. Shared parsing lives in `docforge-parsing` so format fixes land in both consumers. Prompts stay in versioned files. Python 3.12 + uv workspace throughout.

---

## 3. M0 — Foundations (2.5 wks)

| ID | Task | Est |
|---|---|---|
| M0-01 | Scaffold monorepo, uv workspace, lint/type/test config, CI (lint + unit + image build to private registry, HF domains blocked at proxy) | 3d |
| M0-02 | K8s base: namespaces (`platform`, `data`, `sandbox`, later `indexing`), default-deny NetworkPolicies, gVisor RuntimeClass | 3d |
| M0-03 | Data services via Helm: Postgres + pgvector, Redis, MinIO; basic backups | 2d |
| M0-04 | Entra ID app registrations; OIDC validation middleware in FastAPI; login flow stub in web | 2d |
| M0-05 | `llm.py`: Azure GPT 5.5 + embedding-003 client, retries, rate limiter, per-run token budget | 3d |
| M0-06 | GitHub App in the enterprise org (`contents:write`, `pull_requests:write`); client + smoke test | 2d |
| M0-07 | Secrets: External Secrets Operator → Key Vault (AOAI, GitHub, later NAS) | 2d |
| M0-08 | Walking skeleton: queue-consumed 3-node LangGraph run, Postgres-checkpointed, survives pod kill; OTel logs/traces visible | 4d |

**Demo:** kill the worker mid-run; the run resumes.

## 4. M1 — Converse & Understand (3 wks)

| ID | Task | Est |
|---|---|---|
| M1-01 | API: sessions, presigned uploads, run create/query; OpenAPI → generated TS client | 3d |
| M1-02 | Web: app shell + login, chat with streaming, multi-file drag-and-drop (type/size validation) | 6d |
| M1-03 | WebSocket bridge (Redis pub/sub → per-run channel) + run-progress timeline in web | 4d |
| M1-04 | Parsers: pptx/docx/xlsx/txt → normalized markdown + metadata; golden-file tests on fixtures | 5d |
| M1-05 | Images: GPT 5.5 vision + Tesseract fallback; embedded-image extraction from decks/docs | 3d |
| M1-06 | Ingestion agent → **Project Intake Report**: file inventory with parse/OCR quality, understanding summary (process candidates, systems, requirements), proposed process-flow diagram, completeness checks with missing-info questions, complexity/risk assessment | 5d |
| M1-07 | Classifier (new vs existing, LLM-only for now) + repo-URL prompt with clone/branch validation | 3d |
| M1-08 | Web intake-report card: inventory, flow diagram render, questions answerable in chat, **run-config toggles** (skip NAS search / skip spec / upload own spec / paste repo URL); report regenerates on new uploads or answers | 4d |

**Demo:** upload a messy pile of ppt/xlsx/images; DocForge presents an intake report an engineer would trust — what it understood, the proposed flow, what's missing — and the user tunes the run with toggles before anything else executes.

## 5. M2 — Plan & Approve (2.5 wks)

| ID | Task | Est |
|---|---|---|
| M2-01 | Plan/Task schemas + the six feasibility rules as a tested rule engine | 4d |
| M2-02 | Planner agent: repo tree + key-file reading → ordered tasks (acceptance criteria, affected files, risk) + unachievable list with reasons — including gaps caused by skipped steps | 5d |
| M2-03 | Human gate: LangGraph `interrupt()`; approve resumes, edits re-validate feasibility; run-config still adjustable at the gate | 3d |
| M2-04 | Web plan-review pane: editable cards, unachievable section, approve/edit/reject; per-run RBAC + approval audit records | 5d |
| M2-05 | **RunConfig + conditional graph edges**: skip/substitute routing for NAS search, tech spec (generate / skip / user-provided — uploaded spec ingested as planning context), and repo (auto vs pasted URL); choices audited and echoed in the PR body; graph replay tests cover every routing combination | 4d |

**Demo:** a plan a skeptical engineer would sign off on — including honest "can't do, because…" items.

## 6. M3 — Spec & Download (1.5 wks, skippable per run)

| ID | Task | Est |
|---|---|---|
| M3-01 | Convert the official template to docxtpl; placeholder schema documented; versioned in MinIO | 3d |
| M3-02 | Documentation agent: fill from Brief + approved plan → presigned download; audit record | 3d |
| M3-03 | Web downloads pane + document-ready notifications | 2d |

**Demo:** a downloadable spec indistinguishable in styling from a hand-made one.

## 7. M4 — Code, Test & PR (4 wks) — the risk center

| ID | Task | Est |
|---|---|---|
| M4-01 | Sandbox image + Job template: gVisor, non-root, egress allow-list (GitHub, package mirror, AOAI), 2h/CPU/mem caps | 4d |
| M4-02 | Runner: apply edits, run commands, stream results; archive diffs/logs to MinIO on teardown | 4d |
| M4-03 | Coding agent: clone → branch → per-task loop (implement → lint → self-review → next); fully autonomous per requirements | 7d |
| M4-04 | Validation agent (Python): pytest/ruff/build detection + execution; structured failure feedback; 3-retry loop; "needs human attention" downgrade | 4d |
| M4-05 | PR agent: CHANGELOG.md, conventional commits, PR body (plan, task statuses, test summary, requester, doc link); kill switch wired end-to-end | 3d |
| M4-06 | E2e in CI against `fixtures/target-repo` + failure-path tests (429s, timeout, pod kill, abort) | 4d |
| M4-07 | Pilot: 3–5 friendly users on a real repo; buffer week for the rework the pilot will surface | 5d+ |

**Demo / product milestone:** DocForge is usable end-to-end. Everything after this is enrichment.

## 8. M5 — NAS Search Service + RAG (3.5 wks)

Built as a **standalone, org-reusable service** from day one (versioned `/v1` API, own Helm chart, Entra auth, no shared internals with core — see Architecture §4.6).

| ID | Task | Est |
|---|---|---|
| M5-01 | SMB CSI + read-only NAS mount with read-only service account; `indexing` namespace | 2d |
| M5-02 | Indexer: walk roots, mtime+hash incremental, tombstoning → chunk (~800 tok, heading-aware) → embedding-003 → pgvector HNSW in the service's own schema (2–3k docs: full reindex in hours, nightly + hourly incremental) | 5d |
| M5-03 | `nas-search` API: `/v1/search` (hybrid vector+FTS + GPT 5.5 rerank), `/v1/answer` (RAG answer with file-path citations), `/v1/documents/{id}`, `/v1/index/status`; Entra ID auth (user tokens + client-credentials); OpenAPI published for other org teams | 5d |
| M5-04 | Retrieval quality harness: recall@k on 30–50 hand-labeled process→document pairs; wired into CI | 3d |
| M5-05 | **NAS Chat frontend**: lightweight SPA served by the service — search, conversational Q&A with citations linking to file paths, index-status view | 4d |
| M5-06 | DocForge integration: `nas_retrieval` agent as thin HTTP client; classifier similarity evidence; NAS context injection into planning | 3d |
| M5-07 | Existing-process doc updater: fetch NAS source via the service, apply approved changes preserving styles, change-summary section, download-only | 6d |

**Demo (two audiences):** DocForge pulls the right NAS documents unaided for a real existing process — and, separately, a colleague with no DocForge involvement opens NAS Chat and gets cited answers from the same index.

## 9. M6 — Repo Discovery & Hardening (3 wks)

| ID | Task | Est |
|---|---|---|
| M6-01 | Repo indexer (READMEs, metadata, CODEOWNERS) + Repo Discovery agent with confidence-thresholded candidate confirmation in chat | 5d |
| M6-02 | Load/soak test at 15 concurrent runs; KEDA + sandbox node-pool tuning; AOAI quota headroom confirmed with Azure | 3d |
| M6-03 | Security pass: NetworkPolicy audit, prompt-injection red-team on upload/NAS content, secrets scan | 4d |
| M6-04 | Operability: runbooks, alerts (queue depth, token budget, failure rate), per-run cost view; add Langfuse now if prompt regressions have started to bite | 4d |
| M6-05 | GA (initial): onboarding doc, template-update procedure; publish NAS Search API docs to org teams | 2d |

## 10. M7 — Full-Quality Completion (3 wks)

The items a lean plan would defer — restored per the no-compromise posture:

| ID | Task | Est |
|---|---|---|
| M7-01 | Multi-ecosystem validation: Node (jest/eslint) and Java (maven/gradle) detection + sandbox image variants; e2e per ecosystem | 6d |
| M7-02 | Team-level RBAC via Entra ID groups → run-visibility scopes (DocForge and NAS Search both) | 3d |
| M7-03 | Eval-gated CI for prompts: Langfuse scored datasets (classifier, planner feasibility, retrieval, intake-report accuracy) as merge gates; regression baselines from the pilot corpus | 5d |
| M7-04 | Full GA: soak test rerun with NAS Chat traffic included, cost dashboards per service, support/runbook completion | 3d |

---

## 11. Working Agreements for a Two-Person Team

Ship behind the walking skeleton from week 3 onward — every milestone merges into a deployable main branch, no long-lived integration branches. When there are two developers, split by milestone-internal seams (e.g., in M4: one on sandbox/runner, one on the coding agent) rather than by frontend/backend ownership, so either person can cover the whole stack. Timebox agent-quality tuning: prompt iteration is a bottomless pit, so each agent gets a fixed tuning budget per milestone and further quality work goes to a backlog with eval evidence. And protect the pilot buffer in M4-07 — it is the only slack in the plan, and it will be used.

## 12. Top Risks

Unchanged in kind from v1.0, sharpened for team size: (1) the coding-agent loop is the widest estimate — the M4 pilot buffer exists to absorb it; (2) Word-style fidelity in M5-05 is fiddly — the change-summary section keeps user trust even when formatting is imperfect; (3) with 1–2 people, any extended absence stalls the project — mitigate with the deployable-main discipline and runbooks written as you go, not at the end; (4) AOAI TPM quota — raise with Azure before M6-02, not during.
