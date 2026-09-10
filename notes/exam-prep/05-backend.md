# 5. FastAPI, Pydantic και ο κύκλος του request

Πηγές: B 85-95 · main.py, models.py, routes/*.py. Προτεραιότητα: BaseModel, routing, input sources και διαφορά server/framework/database.

### Τι είναι FastAPI, Starlette, Pydantic και Uvicorn;

FastAPI είναι το framework που δηλώνει endpoints και συνδέει types, validation και API documentation. Βασίζεται σε Starlette για ASGI/web υποδομή και Pydantic για data models/validation. Uvicorn είναι ο server που δέχεται HTTP connections και καλεί το ASGI application. SQLite είναι ξεχωριστός ρόλος: αποθήκευση/queries. Το import fastapi δεν ξεκινά από μόνο του listening socket. [B 85, 92-93]

### Τι είναι το BaseModel;

Είναι η βασική κλάση της Pydantic από την οποία κληρονομούν request models όπως MovieAdd. Οι annotated fields ορίζουν αναμενόμενη δομή και validation. Το FastAPI μετατρέπει το request JSON σε instance, ή επιστρέφει validation error. Δεν είναι database base class, δεν δημιουργεί SQL table και δεν αποθηκεύει κάτι αυτομάτως. Η δημιουργία row γίνεται μόνο από το INSERT του add_movie. [B 90]

### Τι σημαίνει class MovieAdd(BaseModel) και title: str;

Το MovieAdd κληρονομεί συμπεριφορά από BaseModel. Το title: str είναι type annotation πεδίου. Η Pydantic το επεξεργάζεται μαζί με το Field(min_length=1). Η απουσία default σημαίνει required field. Το str_strip_whitespace αφαιρεί αρχικά/τελικά κενά πριν ελεγχθεί το μήκος. Άρα ένας τίτλος μόνο με κενά δεν γίνεται αποδεκτός. [B 90 · models.py]

### Τι ακριβώς συμβαίνει όταν στέλνω JSON με λάθος δεδομένα;

Το FastAPI εντοπίζει το route, διαβάζει body και χρησιμοποιεί το model. Αν λείπει title ή ένα rating είναι 7, αποτυγχάνει validation πριν εκτελεστεί η συνάρτηση endpoint. Επιστρέφεται 422 με detail array που δείχνει loc, msg και type. Ο κοινός exception handler αφαιρεί το raw input από τα errors ώστε μη JSON αριθμοί όπως NaN να μη χαλούν και το error response. [models.py, main.py]

### Ποιο validation υπάρχει για recommendations;

Κάθε RatingInput απαιτεί θετικό integer movieId και finite numeric rating από 0.5 έως 5, σε βήμα 0.5. strict=True δεν δέχεται numeric strings ή booleans για αυτά τα πεδία. Το RecommendationRequest απαιτεί list από τέτοια models και απορρίπτει διπλά movieId. Κενή λίστα επιτρέπεται και δίνει κενές recommendations. Ελέγχεται δομή/τιμή, όχι ύπαρξη κάθε ID στη βάση. [models.py]

### Η Pydantic απορρίπτει πάντα επιπλέον πεδία;

Όχι. Το default extra policy είναι ignore. Τα τρέχοντα models δεν ορίζουν extra='forbid', επομένως ένα άγνωστο επιπλέον πεδίο αγνοείται. Αν απαιτούνταν strict schema ως προς τα ονόματα θα το δηλώναμε ρητά. Επίσης η Pydantic μπορεί να κάνει conversions όταν δεν ζητείται strict συμπεριφορά. Δεν συγχέω type annotation, coercion policy και extra-field policy. [B 90 · models.py]

### Μια type annotation στην Python εκτελεί αυτόματα validation;

Όχι γενικά. Μια συνηθισμένη def f(x: int) δεν εγγυάται runtime type check. Οι annotations είναι metadata για εργαλεία και frameworks. Εδώ FastAPI/Pydantic τις χρησιμοποιούν ενεργά στο request boundary. Αν καλέσω ένα route function απευθείας από Python, παρακάμπτω τμήματα της HTTP διαδικασίας. Γι' αυτό οι backend έλεγχοι περνούν από το πραγματικό ASGI app. [B 88-90]

### Τι κάνει ο decorator @router.get('/movies');

Καταχωρεί συνάρτηση ως handler του συγκεκριμένου method/path. Δεν την καλεί για να τρέξει query κατά το import. Το main.py προσθέτει τον router με prefix /movielens/api. Το ίδιο /movies αντιστοιχεί σε άλλη συνάρτηση για POST. Μόνο το όνομα της Python function δεν ορίζει το URL. [B 86-89]

### Τι κάνει το APIRouter και ποια η διαφορά του από το app;

Το APIRouter οργανώνει σχετικές routes ώστε το main.py να τις ενσωματώνει με include_router. Το app είναι το κύριο FastAPI application που καλεί ο server. Το prefix προστίθεται στις διαδρομές του router και δεν αλλάζει τα URL paths των static frontend αρχείων. Οι routers δεν είναι ανεξάρτητοι servers και δεν ακούνε σε δικές τους θύρες. [main.py, routes]

### Γιατί τα endpoints έχουν def αντί async def;

Οι λειτουργίες sqlite3 είναι blocking και δεν παρέχουν await. Το FastAPI εκτελεί normal def path operations σε thread pool. Αν τις γράφαμε async def και καλούσαμε το ίδιο blocking SQL μέσα τους, θα μπορούσαμε να μπλοκάρουμε το event loop. async δεν ισοδυναμεί με ταχύτερο CPU computation. Ο recommender επίσης κάνει Python υπολογισμούς. [B 85, 92 · FastAPI async documentation]

### Τι είναι ASGI και πώς συνδέεται με HTTP;

ASGI είναι interface ανάμεσα σε Python application και server, με scope, receive και send για πληροφορίες και events. Uvicorn μεταφράζει τη δικτυακή επικοινωνία σε αυτό το interface και το response πίσω σε HTTP. Δεν είναι request format που στέλνει ο browser. Το ότι ένα interface υποστηρίζει πολλούς τύπους επικοινωνίας δεν σημαίνει ότι ο συγκεκριμένος server/deployment ενεργοποιεί όλους τους HTTP versions. [B 92]

### Τι είναι lifespan και τι κάνει yield εκεί;

Το lifespan ορίζει startup/shutdown context. Πριν το yield γίνεται init_database. Μετά το yield θα εκτελούνταν shutdown cleanup αν χρειαζόταν. Το @asynccontextmanager εφαρμόζεται σε async generator και δίνει async context manager που το FastAPI διαχειρίζεται. Δεν αποδίδουμε το yield ως «επιστροφή JSON στον browser». Το startup γίνεται πριν η εφαρμογή αρχίσει να εξυπηρετεί requests. [main.py]

### Γιατί if __name__ == '__main__';

Το block εκτελείται όταν τρέχω το module ως κύριο πρόγραμμα, π.χ. python src/main.py. Δεν εκτελείται όταν άλλο module κάνει import main. Έτσι tests ή uvicorn main:app μπορούν να εισαγάγουν το application χωρίς να ξεκινήσει δεύτερος server. Το main:app σημαίνει module main και variable app. [B 93 · main.py]

### Τι κάνει το CORS middleware στη διαδρομή του request;

Περιβάλλει το application και χειρίζεται preflight OPTIONS ή προσθέτει CORS headers σε κατάλληλα responses. Δεν χρειάζεται route /options ούτε manual SQL. Το τελικό URL εξακολουθεί να αντιστοιχίζεται στον ίδιο router. Στην εφαρμογή επιτρέπονται όλα τα origins για μη credentialed requests και οι μέθοδοι GET/POST. [H 58-62 · main.py]

### Πώς ένα Python dict γίνεται JSON response;

Το FastAPI σειριοποιεί την επιστρεφόμενη δομή σε response με application/json. Τα sqlite3.Row μετατρέπονται με dict(row) για πεδία ονοματισμένα όπως movieId/title. Το Python None γίνεται JSON null, οι λίστες arrays. Δεν γράφουμε Python repr μέσα σε HTTP body: ένα Python dict με μονά εισαγωγικά δεν είναι από μόνο του JSON text. [B 62-63, 90-91]

### Τι είναι OpenAPI, Swagger UI και response_model;

OpenAPI είναι περιγραφή του API: paths, methods, inputs και schemas. Το /openapi.json την εκθέτει ως JSON. Το /docs είναι Swagger UI που την παρουσιάζει και μπορεί να στείλει πραγματικά requests. response_model δηλώνει validation/filtering/τεκμηρίωση εξόδου. Τα σημερινά routes επιστρέφουν απλά dicts χωρίς typed response_model, άρα δεν πρέπει να ισχυριστώ ότι έχουν πλήρως τυποποιημένο output schema. [B 85, 90-91]

### Τι διαφορά έχει request model από response model;

Request model ορίζει τι δέχεται ο server, response model τι εκπέμπει. Δεν χρειάζεται να είναι ίδιο: το POST /movies δέχεται title/genres αλλά επιστρέφει status/movieId. Στο παράδειγμα των slides UserIn περιέχει password ενώ UserOut όχι, ώστε να μη διαρρεύσει. Τα μοντέλα δεν είναι αυτομάτως permissions ή encryption. [B 91]

### Πώς θα ακολουθούσες ένα POST /movies από άκρη σε άκρη;

submit event, preventDefault, addMovie, JSON.stringify, fetch με Content-Type, πιθανό OPTIONS, Uvicorn, CORS middleware, POST route, MovieAdd validation, get_db, parameterized INSERT, commit, lastrowid, JSON 201, response.ok/json, feedback στο DOM. Μπορώ να σταματήσω σε κάθε βήμα και να πω τον τύπο των δεδομένων: strings input, JSON text, Python object, SQL parameters, rows/ID, JS object. [S 2 · κώδικας]

### Τι απαντάς αν ένα request φτάνει σε λάθος endpoint;

Ελέγχω πλήρες URL, port, API_PREFIX, method και ακριβές path. GET /movies και POST /movies είναι διαφορετικές operations. /ratings/1 είναι path input, ενώ /ratings?movieId=1 δεν έχει δηλωθεί. Κλήση του API path στη θύρα 8080 πηγαίνει στον static server και πιθανότατα επιστρέφει HTML 404. Το να δω μόνο το όνομα της συνάρτησης δεν αρκεί. [B 86-89]

### Τι χρειάζεται αλλαγή αν ο backend τρέξει αλλού;

Το API_BASE στο index.js πρέπει να δείχνει τον σωστό server και protocol/port. Η listening address 0.0.0.0 επιτρέπει interfaces, αλλά δεν είναι η διεύθυνση που μοιράζω ως host URL. Ελέγχω πρόσβαση δικτύου και CORS. Η εκφώνηση ζητά port 3000 και κοινό /movielens/api prefix· δεν αλλάζω αυτά χωρίς λόγο. [B 93, S 1]

Συνέχισε: [SQLite](06-database.md) · [recommendations](07-recommendations.md).
