# Lessons

Written by /aar-loop after each session's After Action Review. Read this file before starting a new task in this project. Every entry should be concrete and checkable, never vague.

## 2026-09-03 -- When the browser console reports an XHR as blocked by CORS, test the endpoint directly with Invoke-WebRequest/curl including an Origin header before touching CORS config; FastAPI returns HTTP 500 without CORS headers, so a backend crash (C0 jobs/all NameError, C4 applied-jobs ImportError) looks identical to a CORS misconfiguration in the console.
- Expected: CORS-blocked console errors mean the CORS middleware is misconfigured.
- Actual: Two of the failures were HTTP 500s from backend bugs; the missing CORS header on the error response made them indistinguishable from real CORS rejections.
- Why: Starlette CORSMiddleware only adds headers on paths it handles; unhandled exceptions bypass it, so the browser reports CORS instead of the true 500.
- tags: frontend,cors,debugging

## 2026-09-03 -- Manually started uvicorn servers in this repo run without --reload and serve stale code after a file edit; after every backend fix, restart that specific service (Stop-Process by port owner or fresh Start-Process) and re-hit its endpoint directly before re-testing the frontend page.
- Expected: Saving a backend file takes effect immediately via --reload.
- Actual: C4 kept returning 500 after the skill_gap.py import fix until the process was restarted; the running worker predated the edit.
- Why: The C4/C1/C3 workers were launched with bare 'uvicorn main:app' (no --reload flag), so file mtime changes never triggered a reload.
- tags: backend,uvicorn,restart

## 2026-09-03 -- New React pages must pass 'npm run build' in frontend/ before being declared done; the build catches undefined identifiers at compile time (e.g. missing useSearchParams import in Ranking.jsx crashed the page at runtime under dev HMR).
- Expected: Pages created by parallel agents render correctly as written.
- Actual: Ranking.jsx referenced useSearchParams without importing it; caught only by Playwright console sweep, not at creation time.
- Why: No build or lint step ran between page creation and verification; Vite dev mode surfaces the ReferenceError only when the route renders.
- tags: frontend,build,react
