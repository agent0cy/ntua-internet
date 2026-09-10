# 1. Αρχιτεκτονική και απαιτήσεις

Πηγές: I 7-30, 31-38, 46-58 · B 4-18, 54-59 · S 1-4. Υψηλή προτεραιότητα εξάσκησης λόγω άμεσης σύνδεσης με την επίδειξη της εργασίας.

### Περιέγραψε την εφαρμογή σου σε ένα λεπτό

«Έφτιαξα ένα MovieLens explorer. Ο browser φορτώνει ένα HTML, ένα CSS και ένα vanilla JavaScript αρχείο από τη θύρα 8080. Το JavaScript στέλνει HTTP requests στο FastAPI στη θύρα 3000. Τα endpoints διαβάζουν ή γράφουν SQLite και επιστρέφουν JSON. Οι προσωπικές βαθμολογίες μένουν μόνο στη μνήμη της σελίδας και στέλνονται για τον υπολογισμό recommendations. Η αναζήτηση tags είναι η διακριτή επέκταση του Ιουνίου.» Δείξε frontend/index.js, backend/src/main.py και backend/src/routes/.

### Ποια είναι η διαφορά Internet και WWW;

Το Internet είναι η δικτυακή υποδομή που συνδέει δίκτυα και μεταφέρει δεδομένα. Το WWW είναι σύστημα πόρων και υπερσυνδέσμων που λειτουργεί πάνω της, χρησιμοποιώντας URLs, HTTP και browsers. Email και άλλες υπηρεσίες χρησιμοποιούν επίσης Internet χωρίς να είναι κατ' ανάγκη Web. Η εφαρμογή μας είναι Web application επειδή προσπελαύνεται με browser και HTTP. [I 7-8, H 3-16]

### HTML, CSS, JavaScript και HTTP: τι κάνει το καθένα;

HTML: δομή και σημασιολογία περιεχομένου. CSS: παρουσίαση και layout. JavaScript: συμπεριφορά, events, τοπική κατάσταση και ενημέρωση DOM. HTTP: κανόνες επικοινωνίας request/response. Το HTTP μπορεί να μεταφέρει HTML, CSS, JS ή JSON· δεν είναι γλώσσα που σχεδιάζει τη σελίδα. Στο Network τα τρία αρχεία είναι ξεχωριστές αποκρίσεις με διαφορετικά Content-Type. [I 16-23, B 8, 15-17]

### Ποιος κώδικας εκτελείται στον browser και ποιος στον server;

Το index.js εκτελείται στον browser. Τα Python modules εκτελούνται στον backend. Ο browser δεν εκτελεί SQL ούτε ανοίγει το movielens.db: καλεί endpoints. Στο Sources βλέπεις τον παραδομένο frontend κώδικα, όχι τον Python πηγαίο κώδικα. Το JSON είναι το αποτέλεσμα του server. Αυτό εξηγεί και γιατί δεν βάζουμε μυστικά σε JavaScript που κατεβάζει ο πελάτης. [I 24-28, B 4, 13-18]

### Χρειάζονται διαφορετικοί υπολογιστές για client και server;

Όχι. Client/server περιγράφει ρόλους. Browser, static server και API μπορούν να τρέχουν στον ίδιο υπολογιστή, σε διαφορετικές διεργασίες και θύρες. Η διαφορά θύρας αρκεί για διαφορετικό origin. Το localhost αναφέρεται πάντοτε στον υπολογιστή που εκτελεί τον client, άρα σε άλλο laptop δεν δείχνει αυτόματα τον δικό μας server. [B 10-12, H 56]

### Ποια είναι τα layers και τα tiers εδώ;

Presentation: HTML/CSS/JS. Application: routes και recommender. Data: SQLite schema και records. Είναι τρία λογικά layers. Δεν ισχυρίζομαι ότι υπάρχουν τρεις ανεξάρτητοι servers: το SQLite είναι embedded στο backend. Η διάκριση layer είναι λειτουργική, ενώ η φυσική κατανομή σε tiers αφορά deployment. [I 56-58, B 98]

### Γιατί υπάρχουν APIRouter, models.py, db.py και recommender.py;

Τα routes αντιστοιχούν requests σε λειτουργίες. Τα Pydantic models περιγράφουν και ελέγχουν input. Το db.py ορίζει κοινά paths και το άνοιγμα/κλείσιμο σύνδεσης. Το recommender.py περιέχει τον αλγόριθμο. Ο διαχωρισμός επιτρέπει να αλλάξω τον αλγόριθμο χωρίς να αλλάξω το HTTP contract. Δεν είναι απαραίτητο να ονομάσω το σχήμα πλήρες MVC· έχει συγγενή διαχωρισμό ευθυνών. [B 54-55, 85-90]

### Ποια δεδομένα επιβιώνουν από refresh ή restart;

Οι ταινίες που προσθέτω αποθηκεύονται στη βάση με commit και επιβιώνουν από refresh και restart. Οι dataset ratings και τα tags είναι επίσης στη βάση. Το myRatings, searchedMovies και το rendered αποτέλεσμα είναι page state: στο refresh ξαναδημιουργούνται. Το API δεν αποθηκεύει τις βαθμολογίες του recommendation request. Δεν χρησιμοποιούνται localStorage, sessionStorage ή cookies. [S 3-4]

### Τι σημαίνει stateless και πώς συνυπάρχει με βάση δεδομένων;

Κάθε αίτημα περιέχει ό,τι χρειάζεται για την εξυπηρέτησή του χωρίς κρυφό conversational session στον server. Η μόνιμη κατάσταση των πόρων επιτρέπεται: π.χ. οι ταινίες στη βάση. Stateless δεν σημαίνει read-only, ούτε ότι ο server δεν έχει μνήμη. Στο recommendations στέλνω όλη τη λίστα ratings κάθε φορά· το «δεν αποθηκεύονται» είναι επιπλέον απαίτηση της εργασίας. [I 51, H 22-23, B 40, S 3]

### Η σελίδα σου είναι static ή dynamic;

Τα τρία frontend αρχεία σερβίρονται στατικά, δηλαδή ο server στέλνει τα αποθηκευμένα αρχεία. Η συμπεριφορά της εφαρμογής είναι δυναμική: JavaScript μεταβάλλει το DOM από API responses χωρίς ολική επαναφόρτωση. Το backend παράγει JSON δυναμικά από queries και υπολογισμούς. «Static files» δεν σημαίνει «μη διαδραστική εφαρμογή». [I 16, 25-30, B 9, 14-17]

### Γιατί vanilla JavaScript και όχι React;

Είναι ρητός περιορισμός της εκφώνησης: ακριβώς index.html, index.js, index.css χωρίς frameworks ή εξωτερικές frontend libraries. Τα απαιτούμενα forms, tables, events και fetch καλύπτονται από native browser APIs. Το ότι React αναφέρεται στις διαλέξεις δεν επιτρέπει να το χρησιμοποιήσω όταν η συγκεκριμένη εργασία το αποκλείει. [S 3-4, I 37]

### Ποια είναι η ελάχιστη ροή εκκίνησης που πρέπει να εξηγήσεις;

Ενεργοποιώ το virtual environment με τις δηλωμένες dependencies και τρέχω ./start.sh both. Το Uvicorn δημιουργεί την εφαρμογή, εκτελεί το lifespan startup και ακούει στη θύρα 3000. Αν λείπει η βάση, το setup την εισάγει από το bundled dataset. Ο static server σερβίρει το frontend στη θύρα 8080. Ανοίγω αυτή τη διεύθυνση στον browser. Το backend /docs είναι βοηθητικό interface ελέγχου. [B 85-93, S 1]

### Ποιες απαιτήσεις καλύπτει η επέκταση Ιουνίου;

Προσθέτει textbox, button και πίνακα για tags, JSON body με search και POST /tags/movies. Για keyword μήκους κάτω από 5 απαιτεί ολόκληρο tag ίσο με το keyword· από 5 και πάνω συγκρίνει τους πρώτους 5 χαρακτήρες. Αγνοεί πεζά/κεφαλαία και εμφανίζει μία γραμμή ανά ταινία με matchingTag. Τα σχετικά blocks έχουν σχόλια με 10 παύλες στην αρχή και το τέλος. [J 1-2]

### Τι δεν πρέπει να ισχυριστείς ότι έχεις υλοποιήσει;

Δεν υπάρχουν login, accounts, sessions στον server, endpoint αποθήκευσης προσωπικών ratings, ORM, React, HTTPS setup, reverse proxy ή production deployment. Το /docs δημιουργείται από FastAPI. Η θύρα 8080 δεν σημαίνει ότι χρησιμοποιώ Tomcat: εδώ τρέχει python http.server. Η ειλικρινής αντιστοίχιση τεχνολογίας και κώδικα είναι σημαντικότερη από μια μεγάλη λίστα ονομάτων. [Κώδικας: start.sh, main.py, index.js]

Συνέχισε: [HTTP](02-http.md) · [FastAPI](05-backend.md) · [DevTools](09-devtools.md).
