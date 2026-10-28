# eShop: Perth AI workshop, Part 2

A small online store used for the Perth AI "Matt Pocock skills" workshop. The bugs from Part 1 are fixed; Part 2 is about adding features with a disciplined workflow.

## Stack

- `python-eshop/backend`: FastAPI + SQLite, layered as Router → Service → DB client (`db/client.py` holds all SQL).
- `python-eshop/frontend`: React + Vite + Tailwind, talking to the backend over JSON via `src/api/client.js`.

## Commands

- Backend: `cd python-eshop/backend && uv sync && uv run python run.py` (port 8765)
- Frontend: `cd python-eshop/frontend && npm install && npm run dev` (port 4321)
- Tests: `cd python-eshop/backend && uv run pytest`

## Conventions

- Every behaviour change lands with a backend test in `python-eshop/backend/tests/`. Use the `client` fixture; it runs the API against a throwaway database.
- Keep HTTP concerns in `routers/`, rules in `services/`, SQL in `db/client.py`.
- Nothing is public: every route except health and login requires a signed-in user. Users carry a role (`rep`, `organiser`, `supplier`); organiser-only and supplier-only routes go through the `require_role` dependency so a wrong role is always a 403.
- Store times as timezone-aware UTC.
- Show evidence: run the tests and paste the output before saying something works.

## Non-goals

No payment gateway, admin area or real shipping address. Keep changes small enough to review in one sitting.

## Agent skills

### Issue tracker

Issues live in GitHub Issues on `ming-johanson/pai`, driven via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default triage labels are used as-is: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` at the repo root plus `docs/adr/` for decisions. See `docs/agents/domain.md`.
