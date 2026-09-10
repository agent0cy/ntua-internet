# MovieLens: προετοιμασία προφορικής εξέτασης

Ελληνικές εξηγήσεις με English technical terms. Βασίζεται στις τέσσερις διαλέξεις του φακέλου course_material, στις εκφωνήσεις Άνοιξης και Ιουνίου 2026 και στον ελεγμένο κώδικα της εφαρμογής. Έκδοση: 10 Σεπτεμβρίου 2026.

## Πώς να διαβάσεις

Ξεκίνα με [αρχιτεκτονική](01-architecture.md), [HTTP](02-http.md), [JavaScript](03-javascript.md) και [FastAPI](05-backend.md). Συνέχισε με [HTML/CSS/DOM](04-frontend.md), [SQLite](06-database.md) και [recommendations](07-recommendations.md). Ολοκλήρωσε με την [υπόλοιπη θεωρία](08-course-theory.md), τις [ασκήσεις DevTools](09-devtools.md), τα [mock exams](exam-patterns.md) και το [cheatsheet](cheatsheet.md).

Για κάθε ερώτηση: απάντησε δυνατά χωρίς να διαβάζεις, εντόπισε το αντίστοιχο σημείο κώδικα και δείξε μία παρατήρηση στον browser. Μια καλή απάντηση έχει ορισμό, παράδειγμα από την εφαρμογή και μία σημαντική εξαίρεση. Οι ερωτήσεις είναι υλικό εξάσκησης, όχι εγγύηση για το περιεχόμενο της επόμενης εξέτασης.

## Τι γνωρίζουμε για την εξέταση

Ο φοιτητής αναφέρει ότι στην προηγούμενη εξέταση ζητήθηκαν ερωτήσεις όπως «τι επιστρέφει async», «τι είναι BaseModel», λειτουργία API, Inspect Element και Network requests. Αυτή είναι αναφορά εμπειρίας, όχι διαθέσιμο επίσημο πρακτικό. Η εκφώνηση Ιουνίου είναι πραγματικό προηγούμενο πρακτικό θέμα: POST αναζήτηση tags με κανόνα μήκους 5 χαρακτήρων. Όλες οι άλλες προφορικές ερωτήσεις και οι προτεινόμενες επεκτάσεις εδώ είναι προβλέψεις από την ύλη. Δεν υπάρχουν δεδομένα για στατιστικές συχνότητες θεμάτων.

## Κλειδί πηγών

Οι αριθμοί είναι οι φυσικές σελίδες του PDF ή η σειρά διαφάνειας του PPTX, με αρίθμηση από 1.

| Κωδικός | Αρχείο | Έκταση | Ρόλος |
|---|---|---|---|
| I | 1_Introductory_Lecture - v.2.1.pptx | 69 slides | Εισαγωγή, αρχιτεκτονική, τεχνολογίες |
| H | 2_WebDev_HTTP.pdf | 77 σελίδες | HTTP και δίκτυα |
| JS | 3_WebDev_Javascript.pdf | 108 σελίδες | JavaScript και events |
| B | Server-side-programming-REST-Services.pdf | 129 σελίδες | Backend, REST, SQLite, fetch |
| S | WebApp_Dev_Assignment_Spring_2026.pdf | 4 σελίδες | Βασική εργασία |
| J | WebApp_Dev_exams_assignment_2026_06.pdf | 2 σελίδες | Επέκταση Ιουνίου |

Το παλιό Theory-to-Code-Correlation.pdf (17 σελίδες), το αντίστοιχο Markdown και το notes/study-notes.md είναι προϋπάρχοντα βοηθήματα, όχι πρωτογενείς διαλέξεις. Διατηρήθηκαν ως έχουν και μπορεί να περιγράφουν την παλιά υλοποίηση. Για τον σημερινό κώδικα χρησιμοποίησε αυτόν τον οδηγό. Το 20012.zip είναι προηγούμενο παραδοτέο, όχι πρόσθετη θεωρητική πηγή.

## Κάλυψη πηγών

- I 7-30: Web, HTML/CSS/JS, client/server. I 31-52: servers, frameworks, XML/JSON, SOA/SOAP/REST. I 53-64: ασφάλεια, layers, virtualization, cloud/edge. I 68-69: Web evolution. Οι διοικητικές/εισαγωγικές διαφάνειες 1-6 και 65-67 δεν προσθέτουν τεχνικές ερωτήσεις.
- H 3-23: δίκτυα, WWW, servers. H 25-49: μηνύματα, μέθοδοι, URLs, headers, MIME. H 51-68: cookies, CORS, caching, chunking. H 69-76: HTTP/2 και εργαλεία.
- JS 2-24: runtime/event loop. JS 25-51: types, scope, equality, hoisting, loops. JS 52-95: objects, functions, closures, this, prototypes/classes. JS 97-107: DOM/events και ασκήσεις. Οι επαναλαμβανόμενες διαφάνειες animation ενοποιήθηκαν.
- B 4-18: client/server και περιεχόμενο. B 20-55: Servlets/JSP/Tomcat, cookies/sessions, JDBC, MVC. B 57-83: formats, SOAP, REST. B 85-95: FastAPI/Uvicorn/Nginx. B 98-114: SQLite. B 117-125: API clients, fetch, Promises.
- S 1-4: όλοι οι περιορισμοί και απαιτούμενες ροές. J 1-2: endpoint, matching, UI και σήμανση επέκτασης. Τα διαγράμματα και επιλεγμένα παραδείγματα κώδικα σε εικόνες ελέγχθηκαν οπτικά, όχι μόνο με εξαγωγή κειμένου.

Τα PDF διαλέξεων έχουν αναγνώσιμο text layer. Μεταδεδομένα: H και JS δημιουργήθηκαν από Google, B από PowerPoint 2010, S/J από LaTeX. Μετρήθηκαν περίπου H 3.226, JS 4.792, B 5.970, S 589 και J 343 λέξεις στο text layer· εικόνες κώδικα δεν περιλαμβάνονται σε αυτούς τους αριθμούς. Τα slides χρησιμοποιούν κυρίως ενσωματωμένες γραμματοσειρές. Δεν εντοπίστηκαν μη αναγνώσιμα σημεία στις σελίδες που χρησιμοποιούνται ως τεκμήρια.

## Τι ακριβώς υλοποιεί η εφαρμογή

| Κίνηση χρήστη | HTTP endpoint | Backend | Αποτέλεσμα |
|---|---|---|---|
| Άνοιγμα σελίδας | GET / στη θύρα 8080 | Python static server | HTML, μετά CSS και JS |
| Search | GET /movielens/api/movies?search=... | routes/movies.py: search_movies | JSON movies και πίνακας |
| Show average | GET /movielens/api/ratings/{id} | routes/movies.py: get_ratings | JSON ratings, μέσος όρος στον browser |
| Add | POST /movielens/api/movies | MovieAdd, add_movie | INSERT, commit, HTTP 201 και movieId |
| Submit/Remove rating | Κανένα request | Κανένα endpoint | Μεταβολή myRatings στη μνήμη |
| Get recommendations | POST /movielens/api/recommendations | RecommendationRequest, recommend | Υπολογισμός χωρίς αποθήκευση input |
| Search tags | POST /movielens/api/tags/movies | TagMoviesRequest, get_movies_for_tag | JOIN, GROUP BY, matchingTag |

Ο API server ακούει στη θύρα 3000. Οι συναρτήσεις των routes είναι κανονικά def επειδή χρησιμοποιούν το σύγχρονο sqlite3. Ο browser κάνει asynchronous fetch. Η εφαρμογή έχει λογικό διαχωρισμό presentation, application και data layer, αλλά το SQLite εκτελείται μέσα στη διεργασία backend, όχι σε ξεχωριστό database server.
