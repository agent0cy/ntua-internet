# 11. Τελευταία επανάληψη και αναφορές

## Οι απαντήσεις που πρέπει να βγαίνουν αμέσως

| Ερώτηση | Απάντηση μίας πρότασης |
|---|---|
| JS async return; | Promise, του οποίου την τιμή παίρνω με await/then. |
| Python async def call; | Coroutine object· async def με yield δίνει async generator. |
| fetch return; | Promise που γίνεται fulfilled με Response, όχι απευθείας JSON. |
| response.json return; | Promise για διάβασμα/parsing του body. |
| HTTP 422 κάνει fetch reject; | Όχι, ελέγχω response.ok/status. |
| BaseModel; | Pydantic base class για validation/schema, όχι ORM/table. |
| Type hints μόνο; | Δεν εγγυώνται γενικό Python runtime validation. |
| Origin; | Scheme, host, port. |
| Γιατί OPTIONS; | Preflight για cross-origin JSON POST, πιθανόν cached. |
| CORS = authentication; | Όχι, είναι browser response-sharing policy. |
| Το Submit rating κάνει POST; | Όχι, αλλάζει μόνο myRatings. |
| Μέσος όρος πού; | Στο browser από τις GET dataset ratings. |
| Recommendations πού; | Στον backend από request ratings και dataset. |
| Stateless = χωρίς DB; | Όχι, χωρίς remembered conversational client session. |
| SQL injection defense; | Bound parameters, όχι concatenation user values. |
| XSS defense εδώ; | Escape untrusted text πριν από table innerHTML. |
| with conn κλείνει DB; | Όχι· transaction management και close είναι διαφορετικά. |
| const object immutable; | Όχι· immutable binding, mutable contents. |
| Σε νέο reload; | Χάνεται page memory, παραμένει committed DB. |
| Pearson με ένα item; | Undefined· η εφαρμογή το θεωρεί μη usable signal. |

## Πού δείχνω στον κώδικα

| Θέμα | Αρχείο και σύμβολο |
|---|---|
| async/HTTP/errors | frontend/index.js: callApi |
| POST JSON / 201 feedback | frontend/index.js: addMovie |
| query encoding / DOM | frontend/index.js: searchMovies |
| memory / number conversion | frontend/index.js: rateMovie, showMyRatings |
| average / path | frontend/index.js: showAverage |
| async stale result | frontend/index.js: getRecommendations, ratingsVersion |
| markup safety | frontend/index.js: escapeHtml |
| form / labels / tables | frontend/index.html |
| cascade / box model / mobile | frontend/index.css |
| CORS / lifecycle / routing | backend/src/main.py |
| BaseModel / Field / validators | backend/src/models.py |
| connection / casefold | backend/src/db.py: get_db |
| schema / import / transaction | backend/src/setup_db.py: initialize_db |
| GET / POST / INSERT | backend/src/routes/movies.py |
| request-local computation | backend/src/routes/recommendations.py |
| June POST / JOIN / prefix | backend/src/routes/tags.py |
| Pearson / weighted prediction | backend/src/recommender.py |

## Ελάχιστος έλεγχος πριν την εξέταση

- Ξεκινά η εφαρμογή από τις οδηγίες README, χωρίς internet για το bundled dataset.
- Κάνω Search, Show, Add, Submit/Remove, Recommendations και Search tags.
- Ξέρω να δείξω Request URL, method, query/body, status, response και initiator.
- Δείχνω DOM mutation, CSS rule και έναν breakpoint μετά από await.
- Ξεχωρίζω browser memory, persistent DB και request-local variables.
- Έχω επαναφέρει Online, αφαιρέσει breakpoints και κλείσει περιττά test tabs.
- Δεν χρησιμοποιώ το παλιό 20012.zip ως απόδειξη του σημερινού κώδικα: δεν ανανεώθηκε αυτόματα.

## Πρωτογενείς online αναφορές για διευκρινίσεις

Οι τοπικές διαλέξεις είναι η κύρια βάση του οδηγού. Οι παρακάτω επίσημες αναφορές χρησιμοποιούνται για τις λεπτομέρειες που διορθώνουν/συμπληρώνουν σύντομες διατυπώσεις των slides. Έλεγχος αναφορών: 10/09/2026.

- [MDN: async function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)
- [MDN: Using Fetch](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)
- [MDN: Promise.finally](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/finally)
- [MDN: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
- [MDN: Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)
- [MDN: const](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/const)
- [MDN: null](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/null)
- [FastAPI: async and def](https://fastapi.tiangolo.com/async/)
- [Pydantic: Models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic: Fields](https://docs.pydantic.dev/latest/concepts/fields/)
- [Python: sqlite3](https://docs.python.org/3/library/sqlite3.html)
- [SQLite: Datatypes and affinity](https://www.sqlite.org/datatype3.html)

## Πώς επαληθεύτηκε ο οδηγός

Ελέγχθηκαν οι τέσσερις διαλέξεις και οι δύο εκφωνήσεις, με επιλεγμένα διαγράμματα και code-image slides οπτικά. Διασταυρώθηκαν η έννοια origin στο H 56, το BaseModel στο B 90 και το Pearson/weighted formula στο S 3. Η παγίδα με context-manager/connection ελέγχθηκε στα B 102/108 και στην επίσημη sqlite3 τεκμηρίωση. Το αριθμητικό παράδειγμα του κεφαλαίου 7 είναι executable regression check.

Το περιεχόμενο αντιστοιχεί στον σημερινό κώδικα. Το test script χρησιμοποιεί προσωρινή βάση. Η browser δοκιμή χρησιμοποιεί αντίγραφο της βάσης, όχι αλλαγή του υπάρχοντος dataset του φοιτητή. Οι χρόνοι επανάληψης/mock exams είναι προτάσεις μελέτης, όχι επίσημη διάρκεια προφορικής εξέτασης.

Επιστροφή: [ευρετήριο](00-index.md).
