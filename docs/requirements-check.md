# Assignment check - september-exam - 11 September 2026

Checked against all four pages of `WebApp_Dev_Assignment_Spring_2026.pdf`.
This branch implements the Spring assignment without exam extensions. The June
tag-search router, request model, JavaScript handler and UI have been removed.
The three-table database remains intact: Spring page 1 explicitly requires
`movies`, `ratings` and `tags`. The extended version remains on `main`.

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
| Only the four Spring API operations | Exact OpenAPI method/path check; former tag endpoint returns 404 |
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
- Pearson requires two co-rated items and nonzero variance; undefined values
  are excluded, valid zeros are ranked. K=30 and N=10 are allowed choices.
  Negative correlations are retained when they fall within top-K; candidates
  whose total weight is zero are skipped. Both prediction sums use only neighbours
  with a rating for the candidate; scores are ranked before rounding and are not
  clipped. The previous support filter and positive-only/clamped outputs were
  additional behaviour beyond the supplied formula and have been removed.
- Surrounding spaces in add-movie input are stripped. No new authentication,
  persistent user ratings, frontend libraries or unrelated product features
  were added. The backend dependencies already installed in the environment are
  pinned directly; this is not a full transitive dependency lockfile.
- The bundled tags CSV has 3683 data rows, all retained as required by Spring.

## Verification

Executed successfully: 8 backend unittest cases, the Node frontend logic check,
JavaScript syntax check, Python compilation and shell syntax checks. Backend
cases invoke ASGI with temporary databases. The environment's socket restriction
prevented the first thread-pool test run from completing; rerunning outside that
restriction completed successfully.

On `september-exam`, all 9 backend cases and the frontend/syntax checks were
rerun successfully. OpenAPI exposes exactly the four required method/path
operations; GET and POST to the former tag-search URL return 404. A fresh browser
preview confirmed that the tag-search section is absent and the remaining
recommendation guidance works, with no console errors or warnings. The full
browser CRUD/recommendation flow was not repeated for this removal-only change.

The original browser checks on the shared Spring functionality used
`http://localhost:8080` with a temporary copy of the database
behind port 3000. Verified title search, 3.92/215 average, local rating submission,
10 recommendations, 201 creation, escaped stored markup and
clearing ratings on reload. API logs show the expected GETs and preflight
OPTIONS followed by POST. Browser console showed no errors in these flows.
After intentionally stopping the temporary API, search showed the expected
backend-unavailable message and restored the Search button.
Responsive layout was inspected at 375, 768 and 1280 pixels before branching.
The user's working database has not been rebuilt. PDF pages were rendered and
checked when the guide was created.

`20012.zip` was rebuilt on 11 September from the current `september-exam` source,
including the Pearson zero-correlation fix. It contains the required frontend
and backend files, bundled dataset, launch scripts, tests and license. Archive
integrity and source-byte comparisons passed. The packaged backend README omits
links to repository-only study material. Generated databases, virtual
environments, caches and study files are excluded.

After extraction into a clean folder, all 9 backend tests, frontend logic checks
and JavaScript/shell syntax checks passed using the existing installed runtimes.
This check exposed a test that depended on previously extracted CSVs; its rebuild
fixture now uses the temporary dataset created by the test suite. The packaged
setup script also created a fresh database with 9742 movies, 100836 ratings and
3683 tags, and SQLite's integrity check passed. No clean dependency installation
or new browser walkthrough was performed for packaging. The archive has not
been submitted to the course.

Old study notes and UML diagrams remain historical material. The Greek guide
also covers the June extension on `main`; skip its June sections and tag-search
exercise here.
