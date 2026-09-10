# 3. JavaScript: async, τύποι, scope και functions

Πηγές: JS 2-95 · B 120-125. Το async/fetch είναι και θέμα που αναφέρθηκε από την προηγούμενη προφορική εξέταση.

### Τι επιστρέφει μια async function στη JavaScript;

Πάντα Promise. Αν γράψω async function f() { return 5; }, το f() δίνει Promise που γίνεται fulfilled με 5. Το await f() δίνει την τιμή 5. Χωρίς return γίνεται fulfilled με undefined. Αν η συνάρτηση κάνει throw και δεν το χειριστεί, το Promise απορρίπτεται. Στο callApi, η τελική τιμή είναι το parsed JSON object, αλλά ο άμεσος caller λαμβάνει Promise. [B 122-124 · index.js: callApi]

### Τι επιστρέφει μια Python async def;

Η κλήση μιας coroutine function, π.χ. async def f(): return 5, δημιουργεί coroutine object. Ο κώδικας αρχίζει όταν γίνει await ή προγραμματιστεί σε event loop. Αυτό διαφέρει από JavaScript Promise. Επιπλέον async def με yield είναι async generator function: το lifespan χρησιμοποιεί @asynccontextmanager για να μετατραπεί σε async context manager. Δεν ονομάζω όλα αυτά «Promise». [B 85, 92 · main.py: lifespan]

### Τι ακριβώς κάνει await; Παγώνει ο browser;

Αναστέλλει τη συνέχεια της συγκεκριμένης async function μέχρι να settle η awaited τιμή/Promise. Με fulfillment συνεχίζει με την τιμή, με rejection ρίχνει την αιτία ως exception. Ο browser μπορεί να χειριστεί άλλα events όσο περιμένουμε network I/O. Ένας τεράστιος synchronous loop μέσα στην async function εξακολουθεί να μπλοκάρει το main thread· η λέξη async δεν τον μεταφέρει σε άλλο thread. [JS 3-24, B 122-124]

### Τι είναι Promise και ποιες καταστάσεις έχει;

Είναι object για το αποτέλεσμα μίας asynchronous computation: pending, fulfilled ή rejected. Μετά το settlement δεν αλλάζει ξανά αποτέλεσμα. Το then προσθέτει callbacks και επιστρέφει νέο Promise. Το catch χειρίζεται rejection. Το finally εκτελεί cleanup ανεξάρτητα από επιτυχία/αποτυχία· ο callback δεν είναι υποχρεωτικό να επιστρέψει Promise. Ένα throw μέσα του μπορεί να κάνει reject το νέο Promise. [B 123-124]

### Τι επιστρέφει fetch και γιατί έχουμε δύο await;

Το fetch επιστρέφει Promise που γίνεται fulfilled με Response όταν είναι διαθέσιμα status και headers. Το response.json() επιστρέφει άλλο Promise που διαβάζει το body και το κάνει parse. Έτσι στο callApi πρώτα περιμένουμε το Response και μετά το JSON. Response object και parsed data object είναι διαφορετικά πράγματα. Το body κανονικά διαβάζεται μία φορά, εκτός αν προηγηθεί clone. [B 122-125 · callApi]

### Ένα HTTP 404 ή 422 μπαίνει αυτομάτως στο catch του fetch;

Όχι. Είναι έγκυρο HTTP response, οπότε το fetch συνήθως γίνεται fulfilled. Ελέγχω response.ok, που καλύπτει status 200-299, και κάνω throw για αποτυχία. Network/CORS failures απορρίπτουν το fetch. Αποτυχία JSON parsing επίσης μπορεί να κάνει throw. Η εφαρμογή διακρίνει HTTP status, μη έγκυρο JSON και αδυναμία επικοινωνίας. [B 124-125 · callApi]

### Γιατί το return response.json() μπορεί να λειτουργήσει χωρίς δεύτερο await;

Μια async function που επιστρέφει Promise υιοθετεί την κατάστασή του. Άρα ο caller που κάνει await παίρνει τελικά parsed JSON. Όμως αν θέλω το τοπικό try/catch να πιάσει rejection κατά το parsing, πρέπει να το περιμένω μέσα στο try, π.χ. return await response.json(). Στο σημερινό callApi το await βρίσκεται ρητά στο parsing block για χρήσιμο error message. [Συμπλήρωση στην ύλη B 123-125]

### Τι γίνεται αν ξεχάσω await στο callApi;

Το data είναι Promise, όχι JSON object. Πρόσβαση όπως data.movies δεν δίνει το array που περιμένω και ο επόμενος χειρισμός μπορεί να αποτύχει. Η σωστή ακολουθία είναι const data = await callApi(...), έπειτα data.movies. Εναλλακτικά χρησιμοποιώ .then(data => ...). Δεν διορθώνεται με τυχαίο setTimeout. [B 122-125]

### Ποια είναι η σειρά εκτύπωσης σε αυτό το παράδειγμα;

```javascript
console.log('A');
setTimeout(() => console.log('B'), 0);
Promise.resolve().then(() => console.log('C'));
console.log('D');
// A, D, C, B
```

Ο synchronous κώδικας ολοκληρώνει πρώτα το τρέχον task. Η Promise continuation είναι microtask και εκτελείται πριν από το επόμενο timer task. Το timeout 0 σημαίνει προγραμματισμό για αργότερα, όχι άμεση εκτέλεση. [JS 6-24, B 123 · microtasks ως συμπλήρωση]

### Πώς συνεχίζει μια async function μετά από await μιας έτοιμης τιμής;

```javascript
async function f() {
  console.log('A');
  await 5;
  console.log('B');
}
f();
console.log('C');
// A, C, B
```

Ακόμη και μια μη-Promise τιμή μπορεί να γίνει await. Η συνέχεια εκτελείται asynchronous. Ο κώδικας πριν από το πρώτο await τρέχει αμέσως στην κλήση της JavaScript async function. [Συμπλήρωση: async semantics]

### Τι είναι event loop, call stack και heap;

Call stack: οι ενεργές κλήσεις συναρτήσεων. Heap: χώρος objects. Το host περιβάλλον διαχειρίζεται network/timers και προγραμματίζει callbacks. Το event loop οργανώνει την εκτέλεση tasks και microtasks όταν η προηγούμενη synchronous εργασία επιτρέπει συνέχεια. Το διάγραμμα των slides δείχνει timer callback στην queue όσο άλλες συναρτήσεις παραμένουν στο stack. [JS 4-24]

### Single-threaded σημαίνει ότι δεν υπάρχουν race conditions;

Δεν εκτελούνται δύο JS callbacks ταυτόχρονα στο ίδιο main thread, αλλά υπάρχει race ως προς τη σειρά asynchronous αποτελεσμάτων. Μπορεί να αλλάξω ratings ενώ περιμένω recommendations. Το ratingsVersion καταγράφει ποια έκδοση χρησιμοποιήθηκε· αν αλλάξει πριν έρθει η απάντηση, η παλιά απάντηση αγνοείται. Αυτό είναι πρόβλημα χρονικής σειράς, όχι ταυτόχρονης εγγραφής από δύο threads. [JS 6 · index.js: getRecommendations]

### var, let, const: ποιες είναι οι διαφορές;

var έχει function scope, επιτρέπει επαναδήλωση και αρχικοποιείται σε undefined πριν εκτελεστεί η assignment. let/const έχουν block scope και temporal dead zone πριν τη δήλωση. let επιτρέπει reassignment, const όχι. Στο const myRatings = {} επιτρέπεται myRatings[1] = ... γιατί μεταβάλλω το object, όχι το binding. Δεν επιτρέπεται myRatings = {}. [JS 28-31, 47-49]

### Τι είναι hoisting και τι βγάζει το παράδειγμα foo των slides;

Hoisting είναι περιγραφή του ότι declarations λαμβάνονται υπόψη πριν από την εκτέλεση των statements· δεν μεταφέρονται πραγματικά γραμμές. Στο var foo=1; function bar(){ if(!foo){var foo=10;} alert(foo); } bar(); τυπώνεται 10. Η τοπική var foo σκιάζει την εξωτερική και αρχικά είναι undefined, άρα !foo είναι true. [JS 47-49]

### Τι είναι temporal dead zone;

Το διάστημα από την είσοδο στο scope μέχρι την εκτέλεση της δήλωσης let/const, όπου το binding υπάρχει αλλά δεν επιτρέπεται πρόσβαση. console.log(x); let x=1; προκαλεί ReferenceError. Ακόμη και typeof x μέσα σε αυτό το διάστημα προκαλεί ReferenceError. Το typeof ενός πραγματικά αδήλωτου ονόματος επιστρέφει 'undefined'. [JS 28-31, 39, 47-49 · διευκρίνιση]

### Ποιοι είναι οι primitive types;

string, number, bigint, boolean, undefined, symbol και null. Τα objects είναι μη primitive. typeof null επιστρέφει 'object' λόγω ιστορικής ιδιομορφίας, αλλά το null είναι primitive και διαφορετικό από undefined. Τα arrays είναι objects: Array.isArray([]) δίνει true, ενώ typeof [] δίνει 'object'. Το number περιλαμβάνει NaN και Infinity. [JS 26-27, 37-46]

### Ποια είναι τα truthy και falsy;

Falsy: false, 0, -0, 0n, '', null, undefined και NaN, καθώς και το ειδικό legacy document.all. Άδεια arrays και objects είναι truthy. Το string '0' είναι truthy. Στο form η τιμή '' της placeholder option ελέγχεται ρητά. Δεν χρησιμοποιώ if(!value) για να αποφασίσω αν μια μεταβλητή έχει δηλωθεί. [JS 35-39]

### == και ===: τι επιστρέφουν τα παραδείγματα;

'1200' == 1200 δίνει true λόγω coercion· '1200' === 1200 false. null == undefined true, null === undefined false. NaN === NaN false, γι' αυτό χρησιμοποιώ Number.isNaN. [] === [] false επειδή είναι διαφορετικά objects. Η strict equality δεν συγκρίνει αναδρομικά περιεχόμενα objects. [JS 34, 40-46, 52]

### Γιατί κάνουμε Number(value) στα ratings;

Τα DOM input/select values είναι strings. Η εφαρμογή θέλει αριθμητικό rating και integer movieId στο JSON. Το Number('4.5') δίνει 4.5. Number('') δίνει 0, γι' αυτό ελέγχεται προηγουμένως το κενό. parseInt('4.5') δίνει 4 και θα έχανε το μισό αστέρι. parseFloat('4.5abc') δέχεται prefix ενώ Number δίνει NaN. [JS 35 · rateMovie/getRecommendations]

### Τι κάνει JSON.stringify και τι JSON.parse;

stringify μετατρέπει JavaScript value σε JSON text, parse μετατρέπει έγκυρο JSON text σε JS value. JSON δεν υποστηρίζει functions, undefined, comments ή trailing commas. Στην εφαρμογή stringify φτιάχνει request body· response.json διαβάζει και κάνει parse το response. Δεν χρησιμοποιώ eval για να διαβάσω JSON. [I 44-45, B 62-63]

### Είναι τα objects pass by reference;

Περνάμε τιμές· για ένα object η τιμή είναι αναφορά στο object, που μπορεί να μοιράζονται πολλά bindings. Με const a=[1]; const b=a; b.push(2); το a γίνεται [1,2]. Αν μια παράμετρος επαναδεθεί σε νέο object, δεν αλλάζει αυτόματα το binding του caller. Η μετάλλαξη κοινόχρηστου object και το reassignment διαφέρουν. [JS 26]

### Τι κάνουν Object.keys, for...of και for...in;

Object.keys δίνει τα δικά του enumerable string keys ως array. Στο myRatings αυτά είναι movie IDs σε μορφή string. for...of διατρέχει τιμές iterable, όπως ένα array από movies. for...in διατρέχει enumerable property names, περιλαμβάνοντας ενδεχομένως inherited properties. Ένα απλό object δεν είναι εξ ορισμού iterable με for...of. [JS 51, 55, 94]

### Τι σημαίνει ότι functions είναι first-class;

Μπορούν να αποθηκευτούν σε μεταβλητές, να περάσουν ως arguments και να επιστραφούν. Το map δέχεται callback και επιστρέφει νέο array. Το sort δέχεται comparator και μεταβάλλει το array. Ένας event handler είναι επίσης function value που καλείται όταν συμβεί event. Μια ordinary function χωρίς return επιστρέφει undefined. [JS 60-69]

### Τι είναι closure και lexical scope;

Closure είναι συνάρτηση μαζί με πρόσβαση στο lexical environment στο οποίο δημιουργήθηκε. Δεν απαιτείται να αντιγράψει τις τιμές· κρατά πρόσβαση στα bindings. Παράδειγμα: function makeAdder(x){return y => x+y;} και makeAdder(5)(2) δίνει 7. Το x παραμένει προσβάσιμο μετά το return του makeAdder. Οι handlers της εφαρμογής προσπελαύνουν τη shared κατάσταση του εξωτερικού script. [JS 73-79]

### Τι τυπώνει ο timer loop με var και πώς διορθώνεται;

Στο for(var i=0;i<5;i++){setTimeout(()=>console.log(i),1000);} όλοι οι callbacks βλέπουν το ίδιο binding αφού ο loop ολοκληρωθεί: πέντε φορές 5. Με let i δημιουργείται binding ανά iteration και τυπώνεται 0,1,2,3,4. Στο δεύτερο quiz των slides, function(i) έχει δική του παράμετρο χωρίς να περάσουμε argument, άρα τυπώνει undefined. [JS 70-71]

### Πώς καθορίζεται το this;

Για ordinary function εξαρτάται από τον τρόπο κλήσης: obj.method() έχει this=obj, new F() δίνει νέο instance, call/apply/bind καθορίζουν receiver. Σε standalone strict function το this είναι undefined. Arrow function δεν ορίζει δικό της this, το παίρνει lexical. Στο onclick='showAverage(id, this)' το this της inline handler είναι το button και περνά ως argument. [JS 56-59, 81, 86-87]

### Τι διαφορά έχουν call, apply και bind;

call εκτελεί συνάρτηση με δοσμένο this και ξεχωριστά arguments. apply εκτελεί με this και array-like arguments. bind επιστρέφει νέα function με δεσμευμένο this/προκαθορισμένα arguments, χωρίς να την εκτελεί εκείνη τη στιγμή. Arrow this δεν αλλάζει με αυτά. Το Person.call(this, ...) των slides εκτελεί τον constructor ως ordinary function για αρχικοποίηση πεδίων, δεν συνδέει μόνο του όλο το prototype chain. [JS 81, 90]

### Τι είναι prototype και class;

Objects μπορούν να αναζητούν properties κατά μήκος του prototype chain. Οι constructor functions έχουν συνήθως .prototype που γίνεται prototype των instances. Δεν έχουν όλα τα objects δική τους property με όνομα prototype. Η class syntax οργανώνει constructor/methods πάνω σε αυτό το μοντέλο. extends δημιουργεί σχέση κληρονομικότητας και super καλεί την υπερκλάση. Η εφαρμογή δεν χρειάζεται frontend classes. [JS 58, 89-93]

### Υπάρχουν private πεδία στη σύγχρονη JavaScript;

Ναι, class private fields/methods με #, όπως #value. Οι closures μπορούν επίσης να κρύβουν κατάσταση μέσα σε lexical scope. Το παλιό slide που λέει «no standard way» πρέπει να διαβαστεί μαζί με το μεταγενέστερο slide που δείχνει #privateField. Δεν προσπαθώ να διαβάσω ένα private field έξω από το class. [JS 78, 93]

### Τι είναι IIFE και singleton;

IIFE είναι function expression που καλείται αμέσως, π.χ. (()=>{...})(). Δημιουργεί δικό της scope. Το singleton παράδειγμα των slides κρατά ένα instance σε closure και επιστρέφει πάντα το ίδιο object από getInstance. Είναι θεωρητικά patterns, όχι απαραίτητα βήματα για κάθε μικρή εφαρμογή. Το δικό μας myRatings δεν είναι υλοποίηση singleton class. [JS 63, 79]

### Τι επιστρέφει generator function;

Μια function* επιστρέφει Generator object. Το next() εκτελεί ως το επόμενο yield και δίνει object με value και done. Στο παράδειγμα generator(10), τα πρώτα next().value είναι 10 και 20· στο τέλος done είναι true. Generator δεν είναι Promise. Python generator, JS generator και async function είναι διαφορετικοί μηχανισμοί, παρότι μπορούν να σχετίζονται με αναστολή εκτέλεσης. [JS 64-65]

### Ποια λάθη μπορούν να προκύψουν σε κλήσεις και callbacks;

Αν γράψω addEventListener('click', f()) καλώ τη f αμέσως και περνώ το αποτέλεσμά της· συνήθως θέλω f ή () => f(arg). Αν γράψω forEach(async ...) δεν περιμένει το forEach όλα τα async callbacks. Για σειριακές εργασίες προτιμώ for...of με await, για ανεξάρτητες εργασίες Promise.all. Η εφαρμογή έχει απλές κλήσεις με await και δεν χρειάζεται πρόσθετη concurrency βιβλιοθήκη. [JS 60, 102 · B 123]

### Τι είναι optional chaining και γιατί υπάρχει στο ratingDropdown;

Το myRatings[movieId]?.rating επιστρέφει undefined αν δεν υπάρχει αντίστοιχη εγγραφή, αντί να πετάξει TypeError. Μετά το συγκρίνω με r ώστε προηγούμενη προσωπική βαθμολογία να εμφανιστεί selected. Δεν είναι μηχανισμός validation ούτε θεραπεία για κάθε λάθος· χρησιμοποιείται εκεί που η απουσία εγγραφής είναι φυσιολογική. [Κώδικας: ratingDropdown · συμπληρωματική σύνταξη]

### Είναι η JavaScript απλώς interpreted και είναι ίδιο πράγμα με Java;

JavaScript και Java είναι διαφορετικές γλώσσες. Οι browser engines εκτελούν JavaScript με τεχνικές interpretation και συχνά JIT compilation. Το ECMAScript είναι η προδιαγραφή της γλώσσας· το DOM/fetch παρέχονται από το host. Το Node.js είναι άλλο host με διαφορετικά APIs. Δεν υπάρχει αυτόματα document στο Node. [I 19, JS 2-4, 25, 106]

Συνέχισε: [DOM και CSS](04-frontend.md) · [DevTools](09-devtools.md).
