# Assignment check - 10 September 2026

Checked against all four pages of `WebApp_Dev_Assignment_Spring_2026.pdf` and
both pages of `WebApp_Dev_exams_assignment_2026_06.pdf`. The supplied Downloads
copy of the spring sheet is byte-identical to the repository copy. The June
extension is retained at the user's request. No new exam-period specification
was supplied, so the Spring sheet remains the base contract.

| Requirement | Implementation and evidence |
|---|---|
| FastAPI, port 3000, `/movielens/api` | `main.py`; real browser requests recorded at these paths |
| SQLite tables mirror CSVs and contain dataset | `setup_db.py`; fresh import verifies 9742 / 100836 / 3683 records |
| Case-insensitive title substring search, all matches | `routes/movies.py`; Unicode/literal-special-character and all-results checks |
| Get all ratings for movie | `routes/movies.py`; known, unrated and invalid-ID checks |
| Create movie with unique ID and feedback | SQLite primary key, commit, HTTP 201; API and browser creation checks |
| Pearson, top-K, weighted formula, top-N | `recommender.py`; hand-computed positive/negative-neighbour example |
| Request ratings not stored | Byte-for-byte database comparison before/after recommendations |
| CORS enabled | Middleware preflight check and actual browser OPTIONS/POST logs |
| Exactly three frontend files, no external libraries | `frontend/index.html`, `index.js`, `index.css`; no new frontend dependencies |
| In-memory ratings | Submit/Remove update JS object; refresh clears it; browser and logic checks |
| Display dataset average | Browser sums GET ratings; Toy Story shows 3.92 from 215 ratings |
| Clear labels, guidance, errors, tables | Labelled native forms, live feedback, scrollable tables, keyboard focus |
| JSON errors distinguished from network errors | Shared `callApi` and non-finite-safe 422 handler; regression checks |
| June tag POST + matching rule + matchingTag | Marked route/model/UI; exact/prefix/case/deduplication checks |
| Setup/readme/dependencies/import scripts | Updated `backend/README.md`, tested dependency versions and setup/reset |
| Explain and extend code | Concise code comments, 168-question Greek guide, 16 DevTools drills, mock extensions |

## Documented interpretations

- Empty title-search keyword returns all movies. `%` and `_` are literal keyword
  characters. Unicode case folding is shared through the DB connection helper.
- Creation returns 201 with the specified JSON body; other successful endpoints
  return 200. Validation failures return 422. Empty ratings results return 200/[]
  rather than introducing an unspecified movie-existence endpoint check.
- MovieLens input ratings use half-star steps. Duplicate request movie IDs are
  invalid. Empty recommendation lists remain accepted by the API.
- Pearson requires two co-rated items and nonzero variance. Zero weights are
  omitted. K=30 and N=10 are allowed choices. Negative nonzero correlations are
  retained when they fall within top-K. Both prediction sums use only neighbours
  with a rating for the candidate; scores are ranked before rounding and are not
  clipped. The previous support filter and positive-only/clamped outputs were
  additional behaviour beyond the supplied formula and have been removed.
- Surrounding spaces in add/tag input are stripped. No new authentication,
  persistent user ratings, frontend libraries or unrelated product features
  were added. The backend dependencies already installed in the environment are
  pinned directly; this is not a full transitive dependency lockfile.
- The bundled tags CSV has 3683 data rows. The June sheet says 3684; importing the
  actual records faithfully takes precedence over inventing a record.

## Verification

Executed successfully: 8 backend unittest cases, the Node frontend logic check,
JavaScript syntax check, Python compilation and shell syntax checks. Backend
cases invoke ASGI with temporary databases. The environment's socket restriction
prevented the first thread-pool test run from completing; rerunning outside that
restriction completed successfully.

Browser checks used `http://localhost:8080` with a temporary copy of the database
behind port 3000. Verified title search, 3.92/215 average, local rating submission,
10 recommendations, June tag search, 201 creation, escaped stored markup and
clearing ratings on reload. API logs show the expected GETs and preflight
OPTIONS followed by POST. Browser console showed no errors in these flows.
After intentionally stopping the temporary API, search showed the expected
backend-unavailable message and restored the Search button.
Responsive layout was inspected at 375, 768 and 1280 pixels. No external
submission, commit, push, publication or rebuild of the user's working database
was performed. PDF pages were rendered and checked separately.

The existing `20012.zip`, old study notes and old UML diagrams are historical
artifacts; they are not a freshly packaged submission. The current instructions
and code map are in the updated README and `notes/exam-prep/`.
