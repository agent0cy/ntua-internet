# 8. Υπόλοιπη θεωρία των διαλέξεων

Πηγές: I 9-15, 31-64, 68-69 · B 20-83, 95. Αυτά τα θέματα υπάρχουν στην ύλη αλλά δεν είναι υλοποιημένα όλα στη MovieLens εφαρμογή. Η σύνδεσή τους είναι συγκριτική.

### Τι είναι Java Servlet και ποιος το εκτελεί;

Server-side Java πρόγραμμα που εκτελείται σε servlet container, π.χ. Tomcat. Δέχεται requests και παράγει responses. Το HttpServlet παρέχει doGet/doPost κ.ά., ενώ οι request/response interfaces δίνουν πρόσβαση σε parameters, headers και output. Ο browser βλέπει το αποτέλεσμα, όχι εκτέλεση Java Servlet στον υπολογιστή του. Η αντίστοιχη ευθύνη στην εφαρμογή μας βρίσκεται στα FastAPI routes. [B 20-27]

### Ποιος είναι ο κύκλος ζωής ενός Servlet;

init όταν φορτώνεται/αρχικοποιείται, service για κάθε request και destroy όταν αφαιρείται από λειτουργία. Το HttpServlet δρομολογεί από service σε doGet/doPost ανά μέθοδο. Αν εξυπηρετούνται concurrent requests, mutable instance fields μπορεί να είναι shared και απαιτούν προσοχή. Το lifespan της FastAPI έχει ανάλογο startup/shutdown ρόλο, αλλά δεν είναι Servlet. [B 22-24]

### Τι είναι JSP και πώς γίνεται Servlet;

JSP είναι template με HTML και JSP elements. Ο container μεταφράζει το JSP σε Servlet, το κάνει compile/load και το εκτελεί. Με αλλαγή του JSP μπορεί να ξαναγίνει η translation. Η Java επεξεργάζεται στον server και η παραγόμενη HTML πηγαίνει στον browser. Στη δική μας εφαρμογή το HTML είναι static και το JS δημιουργεί το dynamic περιεχόμενο από JSON. [B 28-32]

### Ποιες JSP scripting μορφές πρέπει να αναγνωρίζεις;

<% ... %> scriptlet με Java statements, <%= ... %> expression που γράφεται στην έξοδο, <%! ... %> declaration. Directives όπως <%@ page ... %> δίνουν metadata για τη μετάφραση. JSP actions είναι άλλη κατηγορία στοιχείων. Δεν μπερδεύω JSP syntax με JavaScript ούτε με JSON. Στην άσκηση αρκεί να εξηγήσω τη διαδικασία και ένα απλό παράδειγμα. [B 30-31]

### Tomcat, WAR και WEB-INF: τι είναι;

Tomcat είναι Java servlet container/web server. WAR είναι archive της web application με συγκεκριμένη δομή. WEB-INF/classes περιλαμβάνει compiled classes και WEB-INF/lib JAR dependencies. Η deployment περιοχή του Tomcat είναι συνήθως webapps. Το frontend μας στη θύρα 8080 σερβίρεται από Python, επομένως δεν έχει WAR ή Tomcat. [I 32, B 35-38]

### Τι είναι JDBC και PreparedStatement;

JDBC είναι το Java API για σύνδεση με databases μέσω κατάλληλου driver. Connection, Statement/PreparedStatement και ResultSet αντιστοιχούν σε σύνδεση, εκτέλεση SQL και αποτέλεσμα. Το PreparedStatement δέχεται bound parameters για data values. Χρειάζεται κλείσιμο resources ή επιστροφή connection στο pool. Στην Python χρησιμοποιούμε sqlite3 με αντίστοιχη ιδέα, όχι JDBC driver. [B 48-52]

### Model 1 και Model 2/MVC: πώς διαφέρουν;

Στο Model 1 το JSP λαμβάνει το request και συνδυάζει παρουσίαση με χρήση JavaBeans/data. Στο Model 2 ένα Servlet Controller χειρίζεται input και ροή, το Model διαχειρίζεται δεδομένα/λογική και το JSP View παρουσιάζει. Το διάγραμμα B 55 δείχνει αυτόν τον διαχωρισμό. Στη MovieLens υπάρχουν παρόμοιες ευθύνες σε JS UI, routes και recommender/DB, αλλά διαφορετική τεχνολογική υλοποίηση.

### Τι είναι web service και API;

API είναι συμβόλαιο μέσω του οποίου λογισμικό ζητά λειτουργίες/δεδομένα. Web service εκθέτει λειτουργίες μέσω δικτύου με συμφωνημένα πρωτόκολλα και representations. Ο client μπορεί να είναι browser JS, command-line πρόγραμμα ή άλλο backend. Το contract της εργασίας περιγράφει method/path, inputs και JSON output· δεν απαιτεί ο client να γνωρίζει την εσωτερική SQL υλοποίηση. [I 46-50, B 57-59]

### SOAP και REST: ποια είναι η ουσιαστική διαφορά;

SOAP είναι protocol μηνυμάτων, συνήθως με XML Envelope και ορισμένους κανόνες επεξεργασίας. REST είναι architectural style με constraints όπως statelessness και uniform interface. JSON δεν είναι υποχρεωτικό για REST· μπορεί να υπάρξει XML representation. SOAP συχνά χρησιμοποιεί HTTP ως transport, ενώ REST χρησιμοποιεί τη σημασιολογία resources/methods/statuses. Η MovieLens υλοποιεί HTTP/JSON API σύμφωνα με την εκφώνηση. [I 48-52, B 58, 67-79]

### SOAP Envelope, Header, Body και Fault: τι περιέχουν;

Envelope περικλείει SOAP message. Το Header μπορεί να έχει metadata για processing, ενώ το Body το κυρίως περιεχόμενο. Fault περιγράφει σφάλμα SOAP processing. Το SOAP Header δεν είναι ίδιο πράγμα με τα HTTP headers που περιβάλλουν ολόκληρο το XML body. Στο slide B 68 φαίνεται ακριβώς αυτό: POST/HTTP headers και μέσα XML Envelope. [B 67-71]

### Τι είναι WSDL και UDDI;

WSDL περιγράφει το service interface: types, operations/messages, bindings και network endpoints. UDDI αφορά registry για δημοσίευση και ανακάλυψη services. Η βασική ροή SOA είναι provider register, consumer find και bind/use. Στο σημερινό project το URL είναι γνωστό από το API_BASE και το OpenAPI περιγράφει το HTTP API· δεν υπάρχει UDDI registry. [I 46, B 69-73]

### Ποιες είναι οι REST constraints;

Client-server, stateless, cacheable, uniform interface, layered system και προαιρετικό code-on-demand. Η uniform interface περιλαμβάνει αναγνώριση πόρων, διαχείριση μέσω representations, self-descriptive messages και hypermedia ως οδηγό κατάστασης. Η εργασία χρησιμοποιεί REST-style JSON endpoints, αλλά δεν υλοποιεί πλήρες hypermedia/HATEOAS. Δεν αποδεικνύεται πλήρης REST συμμόρφωση μόνο επειδή χρησιμοποιώ GET και POST. [I 51, B 75-79]

### XML well-formed και valid: πώς διαφέρουν;

Well-formed σημαίνει συντακτικά σωστό XML: ένα root, σωστό nesting, matching tags, σωστό escaping. Valid σημαίνει επιπλέον συμμόρφωση με συγκεκριμένο DTD ή XML Schema. Ένα syntactically σωστό document μπορεί να έχει λάθος πεδίο/τύπο ως προς το schema. Είναι ανάλογη η διάκριση valid JSON syntax και αποδεκτού request σύμφωνα με Pydantic, χωρίς να είναι ίδια εργαλεία. [I 39-43, B 60-61]

### XML Schema, JSON Schema και Pydantic: ποια η σχέση;

XML Schema/XSD περιγράφει δομή και constraints XML. JSON Schema περιγράφει δομή/constraints JSON. Pydantic είναι Python library που ορίζει models, κάνει runtime validation και μπορεί να παράγει JSON Schema. Το FastAPI ενσωματώνει αυτό το schema στο OpenAPI. Το schema είναι περιγραφή και ο validator είναι μηχανισμός ελέγχου· δεν είναι η ίδια έννοια. [B 60-63, 90]

### YAML, JSON και XML: πώς τα συγκρίνεις;

JSON έχει objects/arrays και λίγους primitive types, με αυστηρή σύνταξη χωρίς comments. XML χρησιμοποιεί elements/attributes και namespaces, χρήσιμο για document structures και SOAP. YAML εκφράζει mappings/sequences συχνά με indentation και υποστηρίζει comments. Το --- είναι marker αρχής YAML document, όχι υποχρεωτική πρώτη γραμμή κάθε YAML file. Η εφαρμογή ανταλλάσσει JSON. [B 62-65]

### Τι είναι Nginx και reverse proxy;

Nginx μπορεί να σερβίρει static files ή να δέχεται requests και να τα προωθεί σε backend όπως Uvicorn. Reverse proxy βρίσκεται μπροστά από servers για κοινό entry point, routing ή TLS termination. Load balancer μοιράζει traffic. Αυτές οι λειτουργίες διαφέρουν από την business logic του recommender. Δεν υπάρχει Nginx configuration στο project. [B 95]

### Authentication, authorization, confidentiality, integrity: εξήγησέ τα

Authentication: ποιος είσαι. Authorization: τι επιτρέπεται να κάνεις. Confidentiality: μη αποκάλυψη σε μη εξουσιοδοτημένους. Integrity: προστασία από μη επιτρεπτή αλλοίωση. Η εφαρμογή έχει validation και ασφαλή χειρισμό text/SQL, αλλά δεν έχει user login/authorization. CORS και Pydantic δεν υποκαθιστούν αυτούς τους ελέγχους. [I 53-55]

### SSL/TLS και HTTPS: τι προστατεύουν;

HTTPS είναι HTTP πάνω από ασφαλή μεταφορά TLS, που προστατεύει επικοινωνία ως προς confidentiality/integrity και συνήθως πιστοποιεί τον server μέσω certificate. Τα slides χρησιμοποιούν τον παλιό όρο SSL· η σύγχρονη πρακτική είναι TLS. Δεν σημαίνει αυτόματα ότι ο χρήστης έχει γίνει authenticated στην εφαρμογή ή ότι το περιεχόμενο είναι ασφαλές από XSS/SQL injection. Το demo τρέχει σε HTTP localhost. [I 54-55]

### Web 1.0, 2.0, 3.0: είναι versions του HTTP;

Όχι. Είναι όροι για τάσεις χρήσης/αρχιτεκτονικής του Web. Τα slides αντιπαραβάλλουν static/document consumption, συμμετοχικές/διαδραστικές υπηρεσίες και ιδέες semantic data, decentralization και AI. Δεν αποτελούν ακριβή protocol version negotiation όπως HTTP/1.1 ή HTTP/2. Η MovieLens είναι διαδραστική Web εφαρμογή· recommendations δεν την κάνουν από μόνα τους «Web 3.0». [I 9-15, 68-69]

### Client-server και P2P: τι δείχνει το διάγραμμα;

Στο client-server οι clients απευθύνονται σε server που παρέχει υπηρεσία. Στο peer-to-peer οι κόμβοι μπορούν να έχουν και τους δύο ρόλους και να επικοινωνούν μεταξύ τους. Η εφαρμογή μας έχει κεντρικό API/database, άρα client-server. Δεν υπάρχει ανταλλαγή ratings μεταξύ browsers. [I 29]

### Virtual machine, container και virtualenv: διαφέρουν;

VM συνήθως περιλαμβάνει guest OS πάνω σε hypervisor. Container απομονώνει διεργασίες με κοινό host kernel και πακετάρει εφαρμογή/dependencies. Python virtualenv απομονώνει Python packages/interpreter environment, όχι ολόκληρο OS ή kernel. Το backend/venv του project δεν είναι Docker container ούτε virtual machine. [I 62]

### Τι είναι cloud, edge και η μεταξύ τους κατανομή;

Cloud παρέχει υπολογιστικούς πόρους ως υπηρεσίες με δυνατότητα κλιμάκωσης. Edge μεταφέρει μέρος της επεξεργασίας κοντύτερα στην πηγή δεδομένων/χρήστη, συχνά μειώνοντας latency ή δικτυακή κίνηση. Στο διάγραμμα I 64 sensors στέλνουν σε edge nodes και cloud για διαφορετική επεξεργασία. Αυτό δεν είναι μέρος του local MovieLens deployment. [I 63-64]

## Διορθώσεις και προσεκτικές διατυπώσεις των slides

- JS 26/39: null είναι ξεχωριστή primitive τιμή, όχι undefined. Το typeof null παραμένει 'object'.
- JS 31: const απαγορεύει reassignment, όχι μεταβολή properties. JS 48: hoisting είναι μοντέλο κατανόησης, όχι κυριολεκτική μετακίνηση γραμμών.
- JS 54: eval δεν χρειάζεται για object literals/JSON και το εμφανιζόμενο m.model είναι 'Mustang', όχι 'Ford'. JS 67: constructor use χρειάζεται new για τα αναμενόμενα instances.
- JS 89: όχι όλα τα objects έχουν .prototype property· αναζήτηση γίνεται μέσω του εσωτερικού prototype link. Object.create(null) δεν έχει Object.prototype ancestor.
- H 43/49: η σημασιολογία body εξαρτάται από μέθοδο/status· το 201 μπορεί κανονικά να έχει body, όπως το δικό μας POST. Το 204 δεν έχει content.
- H 63: το browser Origin header είναι αυτό που χρησιμοποιεί το CORS, όχι inference από Referer. Τα δύο headers είναι διαφορετικά.
- B 102/108: with sqlite3.connect(...) δεν κλείνει από μόνο του connection. B 124: το .finally() επιστρέφει Promise, ο callback του δεν υποχρεούται να επιστρέψει Promise.
- Το HTTP/2 server push παρουσιάζεται ως δυνατότητα πρωτοκόλλου στα slides. Δεν το θεωρούμε εγγυημένη λειτουργία του σημερινού browser ή της εφαρμογής μας. Παλιές usage percentages/ημερομηνίες των slides δεν είναι σημερινά στατιστικά.

Οι παραπάνω διατυπώσεις διασταυρώνονται με την εκτέλεση του κώδικα και τις επίσημες συμπληρωματικές αναφορές του τελευταίου παραρτήματος. Στην εξέταση εξηγείς ήρεμα την ακριβή έννοια, όχι απλώς ένα σύνθημα.

Συνέχισε: [DevTools](09-devtools.md) · [mock exams](exam-patterns.md).
