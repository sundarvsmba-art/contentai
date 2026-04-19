## Purpose

This file directs AI coding agents on how to quickly become productive in this repository.
It focuses on discovery steps, concrete heuristics, and repository-specific decisions discovered so far.

## Repository status (auto-detected)

- No source files or common manifests were found at the time this file was created.
- Because the repo is empty, the first goal is to discover any newly added files and then re-run these steps.

## Immediate actions for an agent

1. List top-level files. Prefer these checks (stop early when found):
   - `README.md`, `package.json`, `pyproject.toml`, `requirements.txt`, `pom.xml`, `go.mod`, `Cargo.toml`, `Dockerfile`, `.github/workflows/`
2. If none exist, open a quick issue/PR template: propose a minimal scaffold (README + LICENSE + CI) and ask the human for preferred stack.
3. When files appear, re-run the discovery checklist below.

## Discovery checklist (how to learn the "big picture")

- Read `README.md` or top-level docs for high-level purpose.
- Find the language/runtime via manifests (see Immediate actions). Map to build/test commands.
- Locate entry points: `src/main*`, `app/`, `cmd/`, `server/`, `index.js`, `manage.py`, `main.go`.
- Inspect `.github/workflows/` for CI steps (these often show build/test commands and env variables).
- Search for infra/config: `Dockerfile`, `docker-compose.yml`, `k8s/`, `infra/`, `terraform/`.

## Build & test heuristics (examples)

- Node.js: presence of `package.json` -> use `npm ci` then `npm test` (or `npm run build`). Check `scripts` for exact commands.
- Python: `pyproject.toml` or `requirements.txt` -> create venv; `pip install -r requirements.txt`; run `pytest` if `tests/` exists.
- Java/Maven: `pom.xml` -> `mvn -q -DskipTests=false test`.
- Go: `go.mod` -> `go test ./...`.

Run commands appropriately for Windows PowerShell when presenting examples.

## Code patterns and conventions to look for

- Monorepo layout: look for `packages/`, `services/`, or `workspace:` fields.
- Config-by-env: presence of `.env`, `config/*.yaml` indicates runtime config via env vars—do not hardcode secrets.
- API-first services: look for `openapi/`, `spec/`, or `schema/` folders.

## Making changes (agent workflow rules)

- Make minimal, focused edits with tests. If no tests, add a tiny smoke test demonstrating behavior.
- When proposing new files, add a short README or comment explaining intent and run the discovery checklist again.
- If you need credentials or external services, add mocks and document required env vars in `.env.example`.

## When unsure or blocked

- If the repository remains empty or the human hasn't specified the stack, create a tiny scaffold proposal and request confirmation. Example PR: `README.md` describing intended language + `src/hello` + test harness.

## What I looked for when authoring this file

- Searched for existing AI guidance files (no matches found).
- No project manifests or source files were present to extract concrete examples.

---

If you want, I can:
- Tailor this file to a specific language (Node/Python/Go/Java) and add example commands and CI jobs.
- Create a minimal scaffold (choose language) and run the discovery checks end-to-end.

Please tell me which language/framework you expect or upload the repository contents; I'll iterate the instructions accordingly.
