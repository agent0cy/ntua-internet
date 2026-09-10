# 2. HTTP, URLs, CORS και browser networking

Πηγές: H 3-76 · B 5-9, 40-45, 75-79. Για την εξέταση, περιέγραψε συγκεκριμένο request της εφαρμογής μαζί με τη θεωρία.

### Πώς είναι δομημένο ένα HTTP request;

Στο HTTP/1.1 έχει request line, headers, κενή γραμμή και προαιρετικό body. Παράδειγμα: GET /movielens/api/movies?search=Toy HTTP/1.1, Host: localhost:3000. Το POST προσθήκης έχει Content-Type: application/json και body με title/genres. Τα DevTools παρουσιάζουν τα ίδια λογικά στοιχεία, ακόμη και όταν άλλη έκδοση HTTP έχει διαφορετική αναπαράσταση στο δίκτυο. [H 25-43]

### Πώς είναι δομημένο ένα HTTP response;

Στο HTTP/1.1 έχει status line όπως HTTP/1.1 201 Created, headers και προαιρετικό body. Εδώ το body της επιτυχούς προσθήκης είναι JSON με status και movieId. Τα response headers περιγράφουν το περιεχόμενο και πολιτικές όπως CORS. Το JSON πεδίο status δεν αντικαθιστά το πραγματικό HTTP status code. [H 44-49, S 2]

### Ανάλυσε ένα URL της εφαρμογής

Στο http://localhost:3000/movielens/api/movies?search=Toy%20Story το http είναι scheme, localhost host, 3000 port, /movielens/api/movies path και search=... query. Ένα #fragment θα χρησιμοποιούνταν από τον browser και δεν αποστέλλεται στο HTTP request target. Η διεύθυνση του frontend έχει άλλη θύρα, άρα άλλο origin. [H 31-36, B 77]

### URI, URL και URN είναι το ίδιο;

URI είναι γενικό αναγνωριστικό πόρου. URL είναι URI που εκφράζει τρόπο/θέση πρόσβασης, όπως ένα https URL. URN ονομάζει πόρο σε namespace, π.χ. urn:isbn:.... Δεν είναι σωστό να πεις «URI και URL είναι πάντα διαφορετικά»: το URL είναι ειδικότερη περίπτωση. [H 32]

### Γιατί encodeURIComponent στο search;

Κωδικοποιεί ένα συστατικό του URL ώστε χαρακτήρες όπως &, #, + ή ελληνικά να παραμείνουν μέρος της τιμής. Χωρίς encoding, το & θα μπορούσε να ξεκινήσει άλλο query parameter και το # να γίνει fragment. Δεν είναι encryption ούτε SQL escaping. Το backend κάνει ανεξάρτητα parameter binding για SQL. [H 32-35 · index.js: searchMovies]

### Τι κάνουν GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS;

GET διαβάζει representation. POST ζητά επεξεργασία δεδομένων, συχνά δημιουργία. PUT δημιουργεί ή αντικαθιστά την κατάσταση στο συγκεκριμένο target URI. PATCH εφαρμόζει μερική τροποποίηση. DELETE ζητά διαγραφή του πόρου. HEAD έχει σημασιολογία GET χωρίς response body. OPTIONS ζητά επιλογές επικοινωνίας και χρησιμοποιείται για CORS preflight. Η εφαρμογή ορίζει GET/POST· τα υπόλοιπα δεν είναι διαθέσιμα επειδή απλώς υπάρχουν στο HTTP. [H 28-29, B 79]

### Τι σημαίνει safe και τι idempotent;

Safe σημαίνει ότι ο client δεν ζητά αλλαγή κατάστασης του πόρου, όπως σε GET/HEAD. Idempotent σημαίνει ότι η επανάληψη του ίδιου αιτήματος έχει το ίδιο επιδιωκόμενο αποτέλεσμα στον πόρο με μία εκτέλεση. PUT/DELETE είναι idempotent ως προς τη σημασιολογία τους· δεν απαιτείται ίδιο response code κάθε φορά. POST /movies δεν είναι: δύο αποστολές μπορούν να δημιουργήσουν δύο records. Αυτός είναι ο λόγος να μην κάνω αυτόματο retry στην προσθήκη. [H 29 · εφαρμογή]

### Γιατί το tag search είναι POST παρότι μόνο διαβάζει;

Το απαιτεί ρητά το προηγούμενο εξεταστικό θέμα. Η μέθοδος POST δεν σημαίνει υποχρεωτικό INSERT. Το endpoint δέχεται structured input και εκτελεί SELECT/JOIN. Η ίδια η εκφώνηση λέει ότι συνήθως η αναζήτηση θα υλοποιούνταν με GET. Αυτό είναι επιλογή του συγκεκριμένου contract. [J 1]

### Τι διαφορά έχουν path, query και body parameters;

Path: /ratings/1, όπου το 1 ταυτοποιεί το ζητούμενο movie. Query: /movies?search=Toy, όπου η τιμή καθορίζει φίλτρο αναζήτησης. Body: POST /movies με JSON title/genres. Στο FastAPI το {movie_id} και η παράμετρος της συνάρτησης συνδέουν το path, μια απλή παράμετρος search εκτός path γίνεται query, και ένα BaseModel parameter δηλώνει body. [B 87-90]

### Έχει ένα GET body; Είναι το POST πιο ασφαλές;

Το GET body δεν έχει γενικά καθορισμένη σημασιολογία και το browser fetch δεν επιτρέπει body για GET/HEAD. Στην εφαρμογή βάζουμε GET inputs στο URL. POST body δεν σημαίνει απόρρητο: στο απλό HTTP και URL και body είναι χωρίς κρυπτογράφηση. HTTPS προστατεύει τη μεταφορά. Το URL μπορεί επιπλέον να εμφανιστεί σε history/logs. [H 43 · συμπλήρωση: Fetch API]

### Τι είναι MIME, Content-Type και Accept;

MIME/media type περιγράφει τον τύπο δεδομένων, π.χ. text/html, text/css, text/javascript, application/json. Content-Type λέει τι περιέχει το συγκεκριμένο body. Accept δηλώνει ποια response formats δέχεται ο client. JSON.stringify δημιουργεί JSON text, ενώ το Content-Type το δηλώνει ως JSON· το header μόνο του δεν μετατρέπει ένα object σε JSON. [H 38-41, B 6-8]

### Ποιοι status codes έχουν σημασία εδώ;

200: επιτυχής ανάγνωση/υπολογισμός. 201: δημιουργήθηκε ταινία. 422: το request δεν περνά validation. 404: ανύπαρκτη διαδρομή. 405: η διαδρομή υπάρχει αλλά όχι για τη ζητούμενη μέθοδο, π.χ. GET /tags/movies. 500: απρόσμενο server error. Το /ratings/999999 επιστρέφει 200 και [] στη συγκεκριμένη υλοποίηση, όχι 404. 204 σημαίνει χωρίς body και δεν το διαβάζω με response.json(). [H 45, 49 · routes]

### Γιατί μία σελίδα δημιουργεί πολλά requests;

Το αρχικό GET φέρνει HTML. Ο parser εντοπίζει link και script και ζητά CSS και JavaScript ξεχωριστά. Μετά οι ενέργειες χρήστη δημιουργούν fetch requests προς το API. Μπορεί να εμφανιστεί και favicon request. Ένα κλικ Submit rating δεν δημιουργεί request, ενώ ένα JSON POST μπορεί να προηγείται από OPTIONS. Δεν μετρώ μηχανικά «ένα κλικ ίσον ένα request». [B 14-17, H 61]

### Τι είναι origin και Same-Origin Policy;

Origin είναι το tuple scheme, host, port. http://localhost:8080 και http://localhost:3000 έχουν διαφορετικό port. localhost και 127.0.0.1 είναι επίσης διαφορετικά host strings. Same-Origin Policy περιορίζει πώς script από ένα origin προσπελαύνει πόρους άλλου. Το CORS επιτρέπει επιλεγμένη διαμοίραση responses με HTTP headers. Δεν αρκεί να βρίσκονται οι εφαρμογές στον ίδιο υπολογιστή. [H 56-59]

### Τι συμβαίνει σε CORS simple request;

Ένα cross-origin GET χωρίς μη επιτρεπόμενα custom headers συνήθως αποστέλλεται απευθείας. Ο server επιστρέφει Access-Control-Allow-Origin και ο browser ελέγχει αν το JS επιτρέπεται να διαβάσει το response. Απουσία preflight δεν σημαίνει απουσία CORS. Ακόμη και αν ο browser μπλοκάρει την ανάγνωση, ένα simple request μπορεί ήδη να έχει φτάσει στον server. [H 59-60]

### Γιατί βλέπω OPTIONS πριν από POST;

Το application/json δεν είναι CORS-safelisted Content-Type. Ο browser πρώτα στέλνει preflight OPTIONS με Origin, Access-Control-Request-Method: POST και Access-Control-Request-Headers: content-type. Το middleware απαντά με επιτρεπόμενα origins/methods/headers. Αν ο έλεγχος πετύχει, ακολουθεί το πραγματικό POST. Δεν γράψαμε χειροκίνητο fetch για OPTIONS. Η άδεια μπορεί να είναι cached, οπότε OPTIONS δεν εμφανίζεται υποχρεωτικά κάθε φορά. [H 60-62 · main.py]

### Το CORS προστατεύει τη βάση από μη εξουσιοδοτημένους χρήστες;

Όχι. Είναι browser policy για πρόσβαση από διαφορετικά origins, όχι authentication ούτε authorization. Ένα πρόγραμμα όπως curl δεν εφαρμόζει την πολιτική ανάγνωσης του browser. Η εργασία έχει δημόσιο classroom API χωρίς accounts. Σε πραγματικό deployment χρειάζονται ανεξάρτητοι έλεγχοι πρόσβασης· η αλλαγή allow_origins δεν τους αντικαθιστά. [H 56-62 · main.py]

### Γιατί δεν λύνει το πρόβλημα το mode: 'no-cors';

Επιτρέπει μόνο περιορισμένα requests και δίνει opaque response που το JavaScript δεν μπορεί να διαβάσει ως το επιθυμητό JSON. Δεν «απενεργοποιεί το CORS» ώστε να λειτουργήσει το UI. Η λύση είναι σωστό origin/URL και σωστά headers από τον server. Στο Network/Console ελέγχω preflight, τελικό response και τυχόν browser block. [H 56-62 · συμπλήρωση: Fetch API]

### Γιατί λειτουργεί στο curl και αποτυγχάνει στον browser;

Ελέγχω πρώτα αν τα δύο εργαλεία καλούν ακριβώς το ίδιο URL/method/body. Αν ναι, πιθανή αιτία είναι CORS ή browser περιορισμός, επειδή curl δεν επιβάλλει Same-Origin Policy. Αν αποτυγχάνουν και τα δύο, εξετάζω αν τρέχει ο server, τη θύρα, το route και server logs. Το μήνυμα «Failed to fetch» μόνο του δεν αποδεικνύει ποια αιτία ισχύει. [H 56-62, 76]

### Cookies και sessions: ποιος αποθηκεύει τι;

Το Set-Cookie είναι response header προς τον browser. Ο browser αποθηκεύει cookie και αποστέλλει κατάλληλα cookies με Cookie request header. Σε κλασικό server session το cookie συχνά κρατά μόνο session ID, ενώ τα δεδομένα βρίσκονται στον server. Cookie και session δεν είναι συνώνυμα. Το myRatings είναι απλό JS object στη μνήμη, όχι cookie ή server session. [H 53-54, B 41-45]

### Τι σημαίνουν HttpOnly, Secure, SameSite, Max-Age;

HttpOnly αποκλείει ανάγνωση του cookie από JavaScript. Secure περιορίζει την αποστολή σε ασφαλή μεταφορά σύμφωνα με τους browser κανόνες. SameSite περιορίζει αποστολή σε ορισμένα cross-site contexts. Max-Age/Expires ορίζουν διάρκεια. Αυτά δεν κάνουν αυθαίρετα cookie περιεχόμενα έμπιστα. Η εφαρμογή δεν θέτει cookies· η ερώτηση αφορά συμπληρωματική θεωρία, όχι κρυμμένο feature. [B 43 · συμπλήρωση: browser cookies]

### Cache-Control, ETag και 304: τι εξηγείς στο Network;

Caching επαναχρησιμοποιεί responses. Cache-Control δηλώνει πολιτική, π.χ. max-age χρόνο φρεσκάδας. ETag είναι validator συγκεκριμένης representation. Με If-None-Match ο client ρωτά αν άλλαξε· αν όχι, μπορεί να λάβει 304 και να χρησιμοποιήσει cached body. Last-Modified/If-Modified-Since βασίζονται σε χρόνο. no-cache επιτρέπει αποθήκευση αλλά απαιτεί revalidation· no-store ζητά να μην αποθηκευτεί. Δεν ισχυρίζομαι ότι τα custom API endpoints μας υλοποιούν ETag. [H 65-67]

### Τι είναι Content-Length και chunked transfer;

Content-Length μετρά bytes του body, όχι χαρακτήρες ούτε αριθμό JSON πεδίων. Σε HTTP/1.1 chunked transfer στέλνει τμήματα με μήκος και τελικό zero-length chunk, όταν δεν είναι γνωστό εξαρχής το συνολικό μήκος. Δεν είναι το ίδιο με application pagination ούτε με JSON array. HTTP/2 και HTTP/3 έχουν δικό τους framing και δεν χρησιμοποιούν αυτόν τον μηχανισμό Transfer-Encoding: chunked. [H 49, 68]

### HTTP/1.1, HTTP/2, HTTP/3: τι αλλάζει;

HTTP/1.1: text-based messages και persistent connections, με περιορισμούς ordering. HTTP/2: binary frames, πολλαπλά streams σε μία TCP σύνδεση και HPACK headers. Περιορίζει το HTTP-level head-of-line blocking αλλά παραμένει το TCP loss blocking. HTTP/3 χρησιμοποιεί QUIC πάνω από UDP και ανεξάρτητη παράδοση streams. Οι μέθοδοι/status codes κρατούν σημασιολογία. Το συγκεκριμένο Uvicorn demo εξυπηρετεί HTTP/1.1. [H 30, 69-74]

### Είναι το keep-alive ίδιο με user session;

Όχι. Keep-alive επαναχρησιμοποιεί δικτυακή σύνδεση. User session διατηρεί εφαρμογική σχέση ανάμεσα σε αιτήματα, συνήθως μέσω session ID. Μια εφαρμογή μπορεί να είναι stateless και να χρησιμοποιεί persistent TCP connections. Αντίστροφα, ένα session μπορεί να συνεχίζεται ενώ ανοίγουν νέες συνδέσεις. [H 22-23, 47, 74]

### TCP, IP, DNS και ports: πού ανήκει το HTTP;

HTTP είναι application-layer protocol. IP αφορά διευθυνσιοδότηση/δρομολόγηση πακέτων. TCP δίνει αξιόπιστη, διατεταγμένη ροή bytes· ports διαχωρίζουν υπηρεσίες στο ίδιο host. DNS αντιστοιχίζει ονόματα σε δικτυακές πληροφορίες, συχνά IP addresses. Το διάγραμμα encapsulation βάζει application data μέσα σε TCP, IP και link frames. Δεν είναι κάθε HTTP request ένα TCP packet. [H 4-8, 14]

Συνέχισε: [JavaScript](03-javascript.md) · [DevTools](09-devtools.md).
