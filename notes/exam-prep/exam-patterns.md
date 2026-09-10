# 10. Mock exams και πιθανές μικρές επεκτάσεις

Δεν υπάρχει πλήρης κατάλογος προηγούμενων προφορικών θεμάτων. Τα παρακάτω είναι προσομοιώσεις με βάση τις διαλέξεις και την αναφορά του φοιτητή. Η μόνη διαθέσιμη προηγούμενη επίσημη πρακτική εκφώνηση είναι η επέκταση tags του Ιουνίου 2026.

## Mock A: βασική κατανόηση, 15 λεπτά

- 2 λεπτά: εξήγησε client/server/data flow και δείξε τους φακέλους.
- 3 λεπτά: Search, Network URL/query/response και DOM update.
- 3 λεπτά: τι επιστρέφουν async, fetch και response.json; γιατί 422 δεν απορρίπτει fetch;
- 3 λεπτά: BaseModel, fields, validation, query/path/body.
- 2 λεπτά: Show average έναντι τοπικού Submit rating.
- 2 λεπτά: εξήγησε refresh και persistence χωρίς να κοιτάς σημειώσεις.

**Κριτήριο επιτυχίας:** ο εξεταστής μπορεί να ακολουθήσει μία συγκεκριμένη ενέργεια από click μέχρι SQL και πίσω. Δεν αρκεί να επαναλάβεις ότι «καλώ το API».

## Mock B: debugging και network, 20 λεπτά

- Δείξε OPTIONS/POST και εξήγησε το origin tuple.
- Στείλε invalid rating και εντόπισε το 422 body χωρίς να το πεις network failure.
- Εντόπισε τον πραγματικό CSS rule ενός button και το box model.
- Δείξε closure example, var/let timer loop και διαφορά arrow this.
- Εξήγησε SQL placeholders και γιατί ένα αποθηκευμένο title πρέπει να γίνει escaped.
- Κάνε offline request, επανάφερε Online και εξήγησε την αλυσίδα διάγνωσης.

**Κριτήριο επιτυχίας:** ξεχωρίζεις λάθος URL, μη διαθέσιμο server, CORS block, HTTP validation error και JS rendering error με συγκεκριμένα τεκμήρια.

## Mock C: αλγόριθμος και ευρύτερη ύλη, 20 λεπτά

- Γράψε Pearson και εξήγησε co-rated means έναντι global means.
- Κάνε το αριθμητικό παράδειγμα του κεφαλαίου 7 χωρίς να διαβάζεις τη λύση.
- Εξήγησε cold start, zero variance και score πάνω από 5.
- Σύγκρινε Servlet/JSP/FastAPI, JDBC/sqlite3 και WSDL/OpenAPI.
- Δώσε REST constraints, cookies/session διαφορά και παράδειγμα caching.
- Εξήγησε πώς θα επέκτεινες ένα endpoint διατηρώντας το frontend contract.

## Πιθανή επέκταση: φίλτρο genre

Πρόβλεψη εξάσκησης, όχι επίσημο μελλοντικό θέμα. Πρόσθεσε προαιρετικό query parameter genre στο GET /movies και ένα select στο frontend. Μελέτησε πρώτα τη μορφή pipe-separated genres ώστε Action να μη γίνει αυθαίρετο substring match άλλου token. Δέσε το value σε parameterized SQL και κράτησε το υπάρχον search. Έλεγξε συνδυασμό title/genre, κενό genre και απουσία αποτελεσμάτων. Μην προσθέσεις νέο framework.

## Πιθανή επέκταση: ταξινόμηση αποτελεσμάτων

Ο client μπορεί να ταξινομήσει το ήδη ληφθέν array με sort και comparator για title. Αν ζητηθεί backend sorting, επιτρεπόμενα fields πρέπει να επιλεγούν από μικρό σταθερό mapping· ένα SQL identifier δεν μπορεί να δεθεί ως απλό ? value. Έλεγξε ties και αν η ταξινόμηση είναι numeric ή lexical. Πρόκειται για επέκταση, όχι ήδη διαθέσιμο control.

## Πιθανή επέκταση: average στο backend

Μπορεί να ζητηθεί νέο endpoint με AVG(rating) και COUNT(*). Πρέπει να διατηρήσεις το ήδη απαιτούμενο GET /ratings/{id} που επιστρέφει όλες τις ratings, εκτός αν η νέα εκφώνηση το αλλάζει ρητά. Για μηδέν ratings το AVG δίνει NULL, όχι 0. Σχεδίασε σαφές JSON {average:null,count:0} και UI μήνυμα. Εξήγησε πού μεταφέρθηκε ο υπολογισμός και τι αλλάζει στο Network payload.

## Πιθανή επέκταση: DELETE ή PATCH movie

Συμφώνησε πρώτα path/body/status. Έλεγξε existence, validation, parameterized SQL και συνέπειες για συνδεδεμένα ratings/tags. Η επιβεβαίωση διαγραφής στο UI δεν αντικαθιστά server authorization σε πραγματικό προϊόν. Μη δημιουργήσεις destructive endpoint απλώς επειδή υπάρχει στις διαλέξεις. Στην τρέχουσα εργασία δεν έχει υλοποιηθεί.

## Πιθανή επέκταση: pagination

Αν ζητηθεί, όρισε offset/limit με bounds και σταθερό ORDER BY. Το contract πρέπει να εξηγεί αν επιστρέφονται count/next πληροφορίες. Έλεγξε κενή σελίδα και τελευταία σελίδα. Η υπάρχουσα spring απαίτηση ζητά όλα τα matching movies, άρα δεν προσθέτουμε σιωπηλό LIMIT που κρύβει αποτελέσματα. [S 2]

## Μικρές ασκήσεις JavaScript από τη διάλεξη

- Counter με αρχική τιμή/step, increase/decrease/getValue, πρώτα με closure και μετά class. [JS 77-78, 92-93]
- Εξήγησε τα αποτελέσματα του quiz των τριών IIFEs: 12, 10, 15 αντίστοιχα, με lexical scope. [JS 95]
- Object με τρία αριθμητικά properties και μέθοδο sum, με literal/constructor/class. [JS 107]
- Δημιούργησε input click handler και link mouseover handler, έπειτα δείξε bubbling. [JS 105]

## Αυτοαξιολόγηση

Βαθμολόγησε κάθε απάντηση 0-2: 0 δεν μπορώ να την εξηγήσω, 1 σωστός ορισμός χωρίς απόδειξη, 2 σωστός ορισμός και επίδειξη/παράδειγμα. Επανέλαβε μόνο τα 0/1. Στόχος είναι να απαντάς σε μεταβολή του παραδείγματος, όχι να απομνημονεύσεις ένα κείμενο. Η βαθμολογία αυτή είναι προσωπικό εργαλείο μελέτης, όχι πρόβλεψη βαθμού μαθήματος.

Επιστροφή: [ευρετήριο](00-index.md) · [cheatsheet](cheatsheet.md).
