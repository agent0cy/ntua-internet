# 9. Πρακτική εξάσκηση με DevTools

Πηγές: H 25-76 · JS 97-107 · B 117-125 · εφαρμογή. Οι ονομασίες παρακάτω ακολουθούν Chromium/Chrome DevTools· σε άλλον browser μπορεί να διαφέρουν λίγο. Πρόκειται για βήματα εξάσκησης και αναμενόμενα αποτελέσματα, όχι ισχυρισμό ότι κάθε panel δοκιμάστηκε αυτόματα.

## Προετοιμασία επίδειξης

Εκκίνησε την εφαρμογή και άνοιξε http://localhost:8080. Άνοιξε DevTools με F12 ή Ctrl+Shift+I. Στο Network ενεργοποίησε recording και Preserve log, επίλεξε All αρχικά και καθάρισε τη λίστα. Για requests που ενδιαφέρουν το API χρησιμοποίησε μετά Fetch/XHR. Το Disable cache αφορά συνήθως το HTTP cache με ανοικτά DevTools· το preflight cache είναι ξεχωριστός μηχανισμός.

Να λες δυνατά τι σκοπεύεις να παρατηρήσεις πριν πατήσεις το κουμπί. Μη σβήνεις requests πριν τα εξηγήσεις. Για POST δημιουργίας χρησιμοποίησε μοναδικό δοκιμαστικό τίτλο ώστε να αναγνωρίσεις το record· κάθε πραγματική εκτέλεση δημιουργεί δεδομένα.

## Άσκηση 1: Άνοιγμα σελίδας και αρχικά requests

Κάνε reload με Network ανοιχτό. Εντόπισε το document /, το index.css και το index.js στη θύρα 8080. Στο Headers δείξε Request URL, Request Method, Status Code και Content-Type. Στο Initiator εξήγησε ότι CSS/script προκύπτουν από HTML references. Τα API endpoints δεν καλούνται αυτόματα στην αρχική φόρτωση της συγκεκριμένης εφαρμογής. Μπορεί να υπάρχει favicon request που δεν ανήκει στις βασικές ροές.

**Απάντηση εξάσκησης:** «Η σελίδα δεν είναι ένα μοναδικό network αντικείμενο. Ο browser παίρνει το HTML, ακολουθεί link/script και στη συνέχεια το JavaScript μπορεί να ζητά JSON όταν ενεργώ.»

## Άσκηση 2: Search και query parameter

Γράψε Toy Story και πάτησε Search. Φίλτραρε Fetch/XHR. Βρες GET προς http://localhost:3000/movielens/api/movies?search=Toy%20Story. Στο Payload/Query String Parameters δείξε τη decoded τιμή. Στο Response δες status:'success' και movies array. Στο Preview εμφανίζεται το ίδιο JSON σε δέντρο. Η συγκεκριμένη έκδοση dataset έχει τρία Toy Story titles.

Στο Elements άνοιξε tbody#search-results και ένα tr. Η API response δεν περιέχει HTML table· το searchMovies κατασκεύασε τα td. Στο Initiator ακολούθησε το index.js και βρες callApi/searchMovies. Το status:'success' μέσα στο JSON είναι διαφορετικό από HTTP 200.

## Άσκηση 3: Show average

Στο Toy Story (movieId 1) πάτησε Show. Το GET /ratings/1 χρησιμοποιεί path parameter. Το response περιέχει individual dataset ratings, όχι έτοιμο average. Η showAverage υπολογίζει sum/count στον browser και εμφανίζει 3.92 (215) στο συγκεκριμένο dataset. Δείξε loop, division και toFixed(2). Για movie χωρίς ratings πρέπει να εμφανιστεί No dataset ratings, όχι διαίρεση με μηδέν.

## Άσκηση 4: Submit rating χωρίς network request

Καθάρισε Network, διάλεξε 5 και πάτησε Submit στο Toy Story. Η γραμμή Your ratings εμφανίζεται και το count αυξάνεται, χωρίς request προς /ratings. Στο Console μπορείς να εξετάσεις myRatings και Object.keys(myRatings). Είναι top-level lexical binding του κλασικού script: δεν χρειάζεται να είναι property του window.

**Απάντηση εξάσκησης:** «Η επιλογή select είναι string, το rateMovie την κάνει number και μεταβάλλει object στη μνήμη. Δεν εκτελείται database INSERT. Το GET ratings αφορά άλλα δεδομένα: τα ιστορικά ratings του dataset.»

## Άσκηση 5: Recommendations και JSON body

Κράτησε Toy Story με 5 και αναζήτησε Twelve Monkeys. Βαθμολόγησέ το με 2. Πάτησε Get recommendations και βρες POST /recommendations. Στο Payload πρέπει να υπάρχουν numeric IDs 1 και 32 με ratings 5 και 2. Δείξε Content-Type: application/json. Η σειρά πεδίων στο JSON δεν αλλάζει το νόημα.

```json
{"ratings":[{"movieId":1,"rating":5},{"movieId":32,"rating":2}]}
```

Στο Response υπάρχουν μέχρι 10 records με movieId/title/genres/predictedRating. Δεν θα περιλαμβάνονται τα ήδη rated IDs 1 και 32. Predicted scores μπορεί να είναι πάνω από 5 επειδή η εξίσωση δεν κάνει clamp. Απάντησε ποιο path handler καλείται και πώς περνά τη λίστα στην recommend.

## Άσκηση 6: Preflight και actual POST

Με Network σε All, αναζήτησε OPTIONS για το ίδιο endpoint και ξεχώρισέ το από POST. Στο preflight δείξε Origin: http://localhost:8080, Access-Control-Request-Method: POST και Access-Control-Request-Headers: content-type. Στο response δείξε Access-Control-Allow-Origin και Allow-Methods/Headers. Η CORS άδεια είναι έλεγχος browser πριν από το actual request.

Αν δεν εμφανίζεται OPTIONS, εξήγησε το preflight cache αντί να εφεύρεις αποτυχία. Νέο private browser context ή διαφορετικό endpoint μπορεί να δώσει νέο preflight. Το /docs στην ίδια origin του API δεν αναπαράγει το cross-origin περιβάλλον του frontend.

## Άσκηση 7: Add movie και persistence

Πρόσθεσε π.χ. Exam Demo 2026 με genres Drama. Δείξε POST /movies, JSON body και HTTP 201 με νέο movieId. Αναζήτησε το ίδιο title, κάνε reload και αναζήτησέ το ξανά. Η ταινία παραμένει στη βάση ενώ τα προσωπικά ratings έχουν χαθεί. Στον κώδικα δείξε INSERT, commit και cursor.lastrowid. Μην ξαναστείλεις POST απλώς για να επαναλάβεις τη θέαση του response: δημιουργεί επιπλέον row.

## Άσκηση 8: Backend validation με ελεγχόμενη αποτυχία

Άνοιξε http://localhost:3000/docs και POST /movies → Try it out. Στείλε title με μόνο κενά και genres Drama. Αναμένεις 422 με detail που εντοπίζει body.title, και καμία νέα εγγραφή. Εναλλακτικά από το Console του frontend:

```javascript
const r = await fetch(API_BASE + '/recommendations', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({ratings: [{movieId: 1, rating: 7}]})
});
console.log(r.status, r.ok, await r.json());
// 422, false, validation detail
```

Εξήγησε ότι το fetch fulfilled με Response· το HTTP failure δεν έκανε από μόνο του rejection. Τα DevTools επιτρέπουν να παρακάμψω το frontend, γι' αυτό είναι απαραίτητο το backend validation.

## Άσκηση 9: June tags και exact/prefix rule

Γράψε funny και πάτησε Search tags. Η εφαρμογή πρέπει να κάνει POST /tags/movies με {"search":"funny"}, όχι GET. Στο dataset της δοκιμής βρέθηκαν 22 ταινίες. Δοκίμασε FUNNY και funny-extra: το πενταγράμματο prefix είναι το ίδιο. Με keyword κάτω από 5, π.χ. fun, χρειάζεται ολόκληρο tag ίσο με fun και όχι απλώς prefix του funny.

Δείξε το branch len(keyword)<5 στο tags.py, το substr(tag,1,5), το casefold, το bound ? και το GROUP BY. Για πολλά matching tags επιστρέφεται μία ταινία και ένα representative matchingTag. Τα αποτελέσματα άλλων keywords εξαρτώνται από τη βάση· μην απομνημονεύεις αυθαίρετα counts.

## Άσκηση 10: Inspect Element, Styles και Computed

Inspect στο Search button. Δείξε τη δομή form/button και το submit handler. Στο Styles βρες background, padding και border-radius. Απενεργοποίησε προσωρινά μία declaration και παρατήρησε την αλλαγή. Στο Computed δείξε τελικές τιμές και box model. Βρες το :root και τις --c1/--c2 variables. Το UI change δεν τροποποιεί το αρχείο index.css στον δίσκο.

Στο device toolbar βάλε 375px. Βρες τον ενεργό media rule που αλλάζει flex-direction σε column. Με αποτελέσματα σε table, το οριζόντιο scroll πρέπει να περιορίζεται στον wrapper και όχι σε ολόκληρη τη σελίδα.

## Άσκηση 11: Ασφαλές text και DOM mutation

Σε δοκιμαστική βάση πρόσθεσε title <b>Exam</b> και αναζήτησέ το. Πρέπει να φαίνεται το κυριολεκτικό text μαζί με τα tags, χωρίς bold element στο td. Στο Elements έλεγξε ότι δεν δημιουργήθηκε b node. Δείξε escapeHtml και εξήγησε γιατί το textContent προσφέρει ασφάλεια στο text context. Δεν χρειάζεται να εκτελέσεις κακόβουλο script για να αποδείξεις τη διαφορά.

## Άσκηση 12: Breakpoint και τύποι δεδομένων

Στο Sources άνοιξε index.js και βάλε breakpoint στη γραμμή μετά το await callApi της searchMovies. Κάνε Search. Όταν σταματήσει, δείξε keyword ως string, data ως object και data.movies ως array. Χρησιμοποίησε Step over για τον loop και Resume για ολοκλήρωση. Με breakpoint πριν το fetch μπορείς να ακολουθήσεις call stack προς το event handler. Το await δεν σημαίνει ότι ο χρήστης παγώνει όλο τον browser μέχρι το δίκτυο.

## Άσκηση 13: Offline ή request blocking

Μετά τη φόρτωση του frontend, από το Network επίλεξε προσωρινά Offline ή block το συγκεκριμένο API request. Κάνε Search. Πρέπει να εμφανιστεί error message και να ξεμπλοκάρει το button. Επανέφερε Online/unblock και δοκίμασε ξανά. Σύγκρινε με HTTP 422: στην offline περίπτωση δεν υπάρχει κανονικό server response με status 422. Μην αφήσεις το browser σε Offline πριν την επίδειξη.

## Άσκηση 14: Slow network και αλλαγή state κατά την αναμονή

Ενεργοποίησε throttling, ζήτησε recommendations και αφαίρεσε ή άλλαξε rating πριν ολοκληρωθεί. Η παλιά response δεν πρέπει να εμφανιστεί ως recommendation για τη νέα λίστα. Δείξε ratingsVersion και σύγκριση version μετά το await. Το disabled rec button εμποδίζει δεύτερη παράλληλη υποβολή recommendations, ενώ ο version check καλύπτει αλλαγές input state.

## Άσκηση 15: Network Timing και διάγνωση

Στο request Timing δείξε queueing/stalled, connection setup όπου υπάρχει, waiting/TTFB και content download. TTFB δεν είναι καθαρός χρόνος SQL: περιλαμβάνει δικτυακές και server αναμονές. Το waterfall δείχνει χρονική σχέση requests, όχι τη σειρά των Python functions. Στη localhost επίδειξη οι χρόνοι δεν αντιπροσωπεύουν production performance.

## Άσκηση 16: Copy as cURL και αναπαραγωγή

Επίλεξε το GET search και Copy as cURL. Αναγνώρισε URL, headers και method. Για POST έλεγξε το body πριν το εκτελέσεις, επειδή replay του Add δημιουργεί νέο movie. Το curl είναι HTTP client και δεν δημιουργεί DOM ούτε εφαρμόζει browser CORS policy. Η αναπαραγωγή του ίδιου request βοηθά να ξεχωρίσεις frontend bug από backend συμπεριφορά.

## Ελάχιστη αφήγηση 90 δευτερολέπτων

«Πατάω Search, το submit event ακυρώνει την κανονική φόρμα και καλεί JavaScript. Το keyword κωδικοποιείται στο query και το fetch δίνει Promise. Στο Network βλέπω GET, URL, 200 και JSON movies. Η FastAPI συνδέει τη διαδρομή με search_movies, που εκτελεί bound SQL και επιστρέφει dict. Με await διαβάζω Response και μετά JSON, ελέγχω status και γράφω ασφαλές text σε νέο tbody. Οι προσωπικές μου βαθμολογίες είναι ξεχωριστό object στη μνήμη και δεν αποθηκεύονται στον server.»

Επιστροφή: [ευρετήριο](00-index.md) · [mock exams](exam-patterns.md).
