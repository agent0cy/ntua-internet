# 6. SQLite, SQL και διαχείριση δεδομένων

Πηγές: B 98-114 · S 1 · db.py, setup_db.py και routes.

### Τι είναι SQLite και πού βρίσκεται η βάση;

Embedded relational database engine. Δεν χρειάζεται ξεχωριστή υπηρεσία database server: η Python χρησιμοποιεί sqlite3 για να ανοίξει το backend/movielens.db. Το αρχείο είναι persistent storage. Οι διαδρομές υπολογίζονται από το __file__ ώστε να μη δημιουργείται κατά λάθος άλλη βάση επειδή άλλαξε ο τρέχων φάκελος εκτέλεσης. [B 98, 102 · db.py]

### Ποιο schema ζητά η εκφώνηση και πόσα δεδομένα περιέχει;

movies(movieId,title,genres), ratings(userId,movieId,rating,timestamp), tags(userId,movieId,tag,timestamp), με στήλες όπως στα CSV. Το bundled αρχείο εισάγει 9.742 movies, 100.836 ratings και 3.683 tag records. Το J αναφέρει 3.684 tags, αλλά οι πραγματικές data rows του bundled CSV είναι 3.683· header δεν είναι record. Μια υπάρχουσα βάση μπορεί να έχει πρόσθετες ταινίες. [S 1, J 1 · επαληθευμένο import]

### Τι είναι primary key και composite primary key;

Primary key προσδιορίζει μοναδικά row. Στο movies, movieId INTEGER PRIMARY KEY είναι alias του SQLite rowid και όταν παραλείπεται στο INSERT η βάση επιλέγει ID. Στο ratings το σύνθετο key (userId,movieId) επιτρέπει μία βαθμολογία ανά dataset χρήστη/ταινία. Στο tags το (userId,movieId,tag) επιτρέπει διαφορετικά tags για την ίδια ταινία. Δεν μπερδεύω primary key με αριθμό γραμμής του CSV. [B 99 · setup_db.py]

### Χρησιμοποιείς AUTOINCREMENT; Είναι αναγκαίο για unique IDs;

Όχι. INTEGER PRIMARY KEY αρκεί για μοναδικό ID μεταξύ υπαρχόντων rows. AUTOINCREMENT είναι ειδική επιλογή της SQLite που αλλάζει την πολιτική επαναχρησιμοποίησης IDs με πρόσθετο κόστος· δεν είναι συνώνυμο του primary key. Το cursor.lastrowid επιστρέφει το ID της δικής μας επιτυχούς εισαγωγής. Δεν υπολογίζουμε MAX(id)+1 στον client. [setup_db.py, add_movie]

### Connection, cursor, execute, fetchone, fetchall: εξήγησέ τα

Connection εκπροσωπεί τη σύνδεση με τη βάση και διαχειρίζεται transactions. Cursor εκτελεί SQL και κρατά το αποτέλεσμα για ανάκτηση. conn.execute είναι συντόμευση που δημιουργεί/επιστρέφει cursor. fetchone δίνει επόμενη row ή None, fetchall όλες τις υπόλοιπες rows. Το row_factory=sqlite3.Row επιτρέπει πρόσβαση με όνομα στήλης και dict(row). [B 102-105]

### Τι κάνει το with get_db() και τι το with conn;

Το get_db είναι generator context manager που κάνει yield μια connection και την κλείνει σε finally. Δεν κάνει αυτόματο commit. Το native with conn διαχειρίζεται commit/rollback για transaction, αλλά δεν κλείνει τη connection. Στο setup χρησιμοποιούνται with conn και closing(conn) για δύο διαφορετικές ευθύνες. Αυτή η διαφορά διορθώνει παραπλανητικό σχόλιο των slides. [B 102, 107-109 · db.py/setup_db.py]

### Τι είναι transaction, commit και rollback;

Transaction ομαδοποιεί database αλλαγές. Commit τις οριστικοποιεί, rollback ακυρώνει τις μη οριστικοποιημένες αλλαγές. Το add_movie κάνει commit μετά το INSERT. Το setup ξεκινά BEGIN πριν από DDL και inserts, ώστε να συμμετέχουν στο ίδιο transaction. Το απλό close δεν είναι commit: μη committed αλλαγές μπορεί να χαθούν. [B 104, 107]

### Τι σημαίνουν ACID και atomicity στο setup;

Atomicity: όλες οι αλλαγές της συναλλαγής ή καμία. Consistency: διατήρηση των δηλωμένων κανόνων. Isolation: περιορισμός αλληλεπίδρασης ταυτόχρονων συναλλαγών. Durability: τα committed δεδομένα επιβιώνουν σύμφωνα με τις εγγυήσεις του συστήματος αποθήκευσης. Το setup επιπλέον χτίζει temporary DB και μόνο μετά την επιτυχία κάνει os.replace στο target. Έτσι αποτυχία εισαγωγής δεν αντικαθιστά τη λειτουργική βάση. [B 107 · setup_db.py]

### Γιατί csv.DictReader και όχι split(',');

Οι τίτλοι συχνά περιέχουν κόμμα μέσα σε quoted πεδίο. Το csv module χειρίζεται quoting, escaped quotes και γραμμές σωστά. Το DictReader διαβάζει το header και δίνει dict ανά data row. Τα CSV values είναι strings, γι' αυτό μετατρέπουμε IDs/timestamps με int και ratings με float. Τα title/genres/tag μένουν strings. [setup_db.py]

### Τι κάνει executemany; Είναι ένα τεράστιο SQL statement;

Εκτελεί το ίδιο parameterized statement για πολλές ακολουθίες parameters. Στο setup εισάγει τις λίστες από tuples με χαμηλότερο overhead από χειροκίνητο Python loop με πολλά commits. Δεν σημαίνει κατ' ανάγκη ένα μοναδικό INSERT statement για ολόκληρο τον πίνακα. Το transaction κρατά την εισαγωγή συνεπή και αποδοτική. [B 104]

### Πώς αποτρέπεις SQL injection;

Τα SQL values δένονται με ? placeholders και ξεχωριστά parameters. Ένα title με εισαγωγικά αντιμετωπίζεται ως δεδομένο, όχι ως SQL σύνταξη. Στον recommender δημιουργούμε μόνο το πλήθος placeholders για IN (...), όχι τα ίδια τα IDs μέσα στο SQL string. Στο tags επιλέγεται ένα από δύο σταθερά WHERE fragments. Τα placeholders δεν χρησιμοποιούνται για table/column identifiers. [B 104, 111]

### Γιατί το title search δεν χρησιμοποιεί απλώς LIKE;

Η εκφώνηση ζητά substring keyword. Το LIKE δίνει ειδική σημασία στα % και _, ενώ το instr(casefold(title), ?) τα χειρίζεται ως κανονικούς χαρακτήρες. Η Python str.casefold καταχωρείται ως SQLite function στο get_db και επιτρέπει case-insensitive Unicode σύγκριση. Η built-in SQLite LOWER/LIKE δεν προσφέρει πλήρες Unicode case folding χωρίς πρόσθετη υποστήριξη. Πρόκειται για συγκεκριμένη επιλογή της υλοποίησης.

### Τι κάνουν JOIN, GROUP BY και MIN στο tag search;

JOIN συνδέει tags με movies μέσω movieId. Το WHERE κρατά μόνο matching tags. GROUP BY συγκεντρώνει τις γραμμές ανά ταινία και αποτρέπει επανάληψη movie με πολλά matching tags. MIN(t.tag) επιλέγει ένα πραγματικό tag από εκείνα που πέρασαν το WHERE· δεν υπολογίζει «καλύτερο semantic match». ORDER BY σταθεροποιεί την παρουσίαση. [routes/tags.py]

### Dynamic typing σημαίνει ότι η SQLite αγνοεί πάντα τον τύπο της στήλης;

Όχι. Κάθε value έχει storage class NULL, INTEGER, REAL, TEXT ή BLOB, και οι στήλες συνήθως έχουν type affinity που μπορεί να μετατρέψει τιμές. Τα ordinary tables δεν έχουν strict typing όπως πολλοί άλλοι DBMS. INTEGER PRIMARY KEY έχει ειδική συμπεριφορά. SQLite υποστηρίζει και STRICT tables, αλλά δεν χρησιμοποιούνται εδώ. Δεν υπάρχει ξεχωριστή storage class Boolean ή datetime. [B 98-100, 112]

### Έχεις foreign keys και indexes;

Το τρέχον schema έχει primary keys αλλά δεν δηλώνει foreign-key constraints μεταξύ ratings/tags και movies. Η σχέση εκφράζεται στα δεδομένα και στα JOINs· δεν ισχυρίζομαι ότι η βάση αποτρέπει κάθε orphan row. Τα primary keys προσφέρουν σχετική indexing/uniqueness υποστήριξη. Ένα ειδικό index σε ratings(movieId) θα μπορούσε να βοηθήσει σε μεγαλύτερη κλίμακα, αλλά θέλει μέτρηση και δεν είναι απαιτούμενο feature.

### Γιατί μια SELECT δεν αλλάζει προσωπικά ratings; Πώς το αποδεικνύεις;

Η GET ratings διαβάζει dataset rows. Η POST recommendations εκτελεί μόνο SELECTs και υπολογισμό. Οι submitted ratings γίνονται list από tuples στη μνήμη της συγκεκριμένης κλήσης. Μπορώ να συγκρίνω counts ή snapshot της βάσης πριν/μετά. Οι αυτοματοποιημένοι έλεγχοι επιβεβαιώνουν ακριβώς ίδια bytes βάσης μετά από recommendations.

### Πώς χειρίζεσαι setup, reset και αποτυχία import;

Κανονικό setup κρατά υπάρχουσα βάση και δεν εισάγει δεύτερη φορά τα ίδια primary keys. Explicit reset απαιτεί stopped backend και αντικαθιστά τα δεδομένα με το dataset, χάνοντας τις πρόσθετες ταινίες. Η αντικατάσταση γίνεται μόνο όταν ολοκληρωθεί το νέο import. Δεν τρέχω reset στην εξέταση για να διορθώσω κάθε σφάλμα· πρώτα διαβάζω logs και προστατεύω τα υπάρχοντα δεδομένα.

Συνέχισε: [αλγόριθμος](07-recommendations.md) · [DevTools](09-devtools.md).
