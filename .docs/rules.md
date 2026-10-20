# Rules: How We Build This Project

## A. Working Rules (Assistant and User)

1. **One step at a time.** The assistant gives only one step. The user completes it and replies `Done`. Only then the next step begins.
2. **Beginner level.** Explain every new term in simple words. No unexplained jargon.
3. **Say what and why.** Every step states its goal and why it matters.
4. **Show expected output.** After each command or code, say what the user should see.
5. **Errors are normal.** If something fails, the user pastes the full error message and the assistant fixes it before moving on.
6. **No skipping.** Do not jump ahead or add features not in `task.md` without updating `PRD.md`.
7. **Update memory.** After each completed step, update `memory.md` and tick `task.md`.
8. **Ask before big changes.** Changing the stack, database, or folder structure needs an explicit decision recorded in `memory.md`.

## B. General Coding Rules

1. Write simple, readable code over clever code.
2. One function does one job, and stays under about 30 lines.
3. Use meaningful names: `calculate_monthly_total`, not `calc` or `x`.
4. Add a short comment for any non-obvious logic.
5. No duplicated code: if used twice, move it to a helper.
6. No hard-coded values: put limits and paths in `config.py`.
7. Remove unused code and `print` debugging before finishing a step.

## C. Python Rules

- Follow PEP 8 (4-space indent, `snake_case` for functions and variables, `PascalCase` for classes).
- Use a virtual environment (`venv`) for every install.
- Keep dependencies in `requirements.txt` (`pip freeze > requirements.txt`).
- Use type hints where they help readability.
- Handle errors with `try/except` around file reading, DB calls, and parsing; return clear messages.
- Never use string formatting to build SQL; use parameters or the ORM.
- Routes only handle requests and responses. Logic goes in `services/`.

## D. HTML Rules

- Use semantic tags: `header`, `nav`, `main`, `section`, `footer`, `table`.
- Every `input` has a matching `label`.
- Use lowercase, hyphenated class names: `stat-card`, `btn-primary`.
- Do not use inline styles or inline `onclick`; attach events in JS files.

## E. CSS Rules

- Use CSS variables for colors, defined in `:root` (see `design.md`).
- Mobile-first: base styles for phones, `@media (min-width: ...)` for larger screens.
- Use Flexbox and Grid for layout, avoid fixed pixel widths for containers.
- Avoid `!important`.
- Keep one shared `style.css` until it grows too large.

## F. JavaScript Rules

- Use `const` and `let`, never `var`.
- Use `async/await` with `try/catch` for API calls.
- All `fetch` calls live in `api.js`, not scattered in page scripts.
- Never trust data: escape or use `textContent` when inserting user text into the page (avoid `innerHTML` with user input).
- Name event handlers clearly: `handleAddTransaction`.
- Keep one JS file per page plus shared files.

## G. Data and Security Rules

- Validate every input on the backend: date format, positive amount, allowed type, existing category.
- Accept only `.csv`, `.xlsx`, `.xls` uploads, max 5 MB, safe file names.
- Never store passwords or API keys in code; use `.env`.
- Never commit real bank statements or personal data to Git.
- Use sample or dummy data for tests and screenshots.
- Money is handled with care: round to 2 decimals, never compare floats with `==`.

## H. API Rules

- Routes are prefixed with `/api` and use plural nouns (`/api/transactions`).
- Use correct methods: GET read, POST create, PUT update, DELETE remove.
- Always return JSON in the shape `{ "success": bool, "data": ..., "error": ... }`.
- Use proper status codes: 200, 201, 400 (bad input), 404 (not found), 500 (server error).

## I. Git Rules

- Commit after each completed step with a clear message, e.g. `Step 7: add transaction CRUD`.
- Keep `.gitignore` updated (`venv/`, `data/`, `uploads/`, `exports/`, `.env`, `__pycache__/`).
- Do not commit broken code to `main`.

## J. Testing Rules

- Test every new feature manually in the browser before saying `Done`.
- Test edge cases: empty input, negative amount, huge number, wrong file type, empty file.
- Add simple `pytest` tests for services (parser, analytics) once the basics work.

## K. Definition of Done (per step)

A step is `Done` only when:

- [ ] The code or setup runs without errors
- [ ] The expected output was seen
- [ ] Edge cases were tried (where relevant)
- [ ] `task.md` is ticked and `memory.md` is updated
- [ ] Changes are committed to Git (from Step 3 onward)
