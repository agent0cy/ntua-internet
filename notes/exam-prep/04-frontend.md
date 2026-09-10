# 4. HTML, CSS, DOM και Inspect Element

Πηγές: I 16-23 · JS 97-107 · B 13-17, 120-121. Η λεπτομερής CSS και DevTools εξάσκηση είναι εφαρμογή των θεμάτων στην πραγματική εργασία, όχι ξεχωριστή διαθέσιμη διάλεξη CSS.

### Τι είναι το DOM και πώς διαφέρει από τον HTML πηγαίο κώδικα;

Το DOM είναι η ζωντανή αναπαράσταση του εγγράφου ως δέντρο objects/nodes. Προκύπτει από parsing HTML αλλά αλλάζει από JavaScript. Το View Source δείχνει το αρχικό HTML, ενώ το Elements δείχνει το τρέχον DOM μαζί με τις γραμμές που πρόσθεσε το searchMovies. Αλλαγή στο Elements επηρεάζει την τρέχουσα σελίδα και συνήθως χάνεται στο reload. [JS 106, B 14-17]

### Τι κάνει το DOCTYPE, το lang και το charset;

Το <!DOCTYPE html> ενεργοποιεί standards mode. Το lang='en' δηλώνει τη γλώσσα του αγγλικού UI για assistive tools. Το meta charset='UTF-8' καθορίζει encoding για σωστή απεικόνιση χαρακτήρων, π.χ. ελληνικών τίτλων. Δεν είναι HTTP status ή κάποια JavaScript ρύθμιση. Το viewport meta επιτρέπει το layout να προσαρμόζεται στο πλάτος κινητού.

### id και class: πώς χρησιμοποιούνται;

Το id πρέπει να ταυτοποιεί μοναδικό element στο document. Η class μπορεί να χρησιμοποιείται σε πολλά στοιχεία. Στην εφαρμογή getElementById('search-results') εντοπίζει το tbody, ενώ οι .success και .error ορίζουν κοινά styles feedback. CSS #id επιλέγει ID και .class επιλέγει class. Η τιμή ενός id δεν δημιουργεί endpoint. [JS 102, B 16-17]

### getElementById και querySelector: τι επιστρέφουν;

getElementById επιστρέφει το element με το ID ή null. querySelector δέχεται CSS selector και επιστρέφει το πρώτο matching element ή null. querySelectorAll δίνει NodeList. Αν αναζητήσω element πριν δημιουργηθεί ή με λάθος selector, πρόσβαση σε .value πάνω σε null προκαλεί σφάλμα. Στην εφαρμογή το script φορτώνεται μετά το HTML markup. [JS 98, 106 · index.html]

### Γιατί το script βρίσκεται στο τέλος του body; Τι αλλάζει με defer/async;

Ένα ordinary εξωτερικό script εκτελείται όταν το συναντήσει ο parser και μπορεί να σταματήσει το parsing. Στο τέλος του body τα προηγούμενα στοιχεία υπάρχουν ήδη. Με defer στο head γίνεται παράλληλο download και εκτέλεση μετά το parsing, σε σειρά για deferred scripts. Με async η εκτέλεση γίνεται όταν είναι έτοιμο το script, χωρίς εγγυημένη σειρά. Η HTML attribute async και η JavaScript async function είναι διαφορετικές έννοιες. [JS 98, B 120]

### Γιατί χρησιμοποιούμε form και preventDefault;

Το form προσφέρει φυσική υποβολή με Enter και built-in validation. Το submit event της εφαρμογής καλεί preventDefault ώστε να μη γίνει η προεπιλεγμένη navigation/submission. Μετά το addMovie/searchMovies κάνει fetch και ενημερώνει το ίδιο document. Χωρίς preventDefault μπορεί να γίνει reload και να χαθούν οι in-memory ratings. [JS 100-102 · index.html]

### Γιατί required και label δεν αρκούν ως backend validation;

Το label συνδέεται με το input μέσω for/id, βοηθά screen readers και εστίαση. Το required δίνει άμεση καθοδήγηση στον browser. Ο client όμως μπορεί να αλλάξει HTML/JS ή να στείλει request με curl. Επομένως το backend ελέγχει ανεξάρτητα με Pydantic. Τα δύο validation layers έχουν διαφορετικό σκοπό: usability και όριο εμπιστοσύνης. [B 13, 90]

### Ποια είναι η διαφορά value, textContent και innerHTML;

value διαβάζει την τρέχουσα τιμή input/select. textContent διαβάζει/γράφει κείμενο. innerHTML διαβάζει/γράφει serialized markup και κατά την ανάθεση το κάνει parse ως HTML. Αν ο τίτλος περιέχει <b>Film</b>, textContent τον εμφανίζει κυριολεκτικά ενώ raw innerHTML θα δημιουργούσε bold element. Η εφαρμογή χρησιμοποιεί escapeHtml για τα database strings μέσα στα table templates.

### Πώς θα μπορούσε να προκύψει stored XSS;

Κακόβουλο markup θα μπορούσε να αποθηκευτεί ως movie title και να ερμηνευτεί ως HTML σε μεταγενέστερη αναζήτηση. Δεν αρκεί ότι το JSON είναι valid ούτε ότι το SQL είναι parameterized. Το escapeHtml χρησιμοποιεί textContent και παίρνει escaped HTML για το text context των κελιών. Αυτός ο helper δεν είναι γενικό sanitizer για URLs, CSS ή JavaScript attributes. Τα δυναμικά IDs στους handlers προέρχονται από integer database IDs.

### Πώς ενημερώνεται ο πίνακας μετά το Search;

searchMovies διαβάζει input, κάνει encoded GET, περιμένει JSON, γεμίζει το searchedMovies map και κατασκευάζει rows. Τα title/genres γίνονται escaped text. Η ανάθεση tbody.innerHTML αντικαθιστά τις παλιές γραμμές. Δεν αλλάζει το HTML αρχείο στον δίσκο. Στο Elements βλέπεις νέους tr/td nodes, ενώ στο Network υπάρχει fetch JSON και όχι νέο document navigation.

### Τι είναι event, callback και event handler;

Event είναι γνωστοποίηση ενέργειας/κατάστασης, π.χ. click, submit, change, keydown. Callback είναι function που περνάω για μεταγενέστερη κλήση. Event handler είναι callback συνδεδεμένο με συγκεκριμένο event. Η εφαρμογή χρησιμοποιεί inline handlers στο HTML. Η εναλλακτική addEventListener κρατά wiring στο JS και επιτρέπει πολλούς listeners. [JS 100-102, B 121]

### Capturing, target, bubbling: ποια είναι η σειρά;

Το event κατεβαίνει από ancestors προς το target στη capturing phase, φτάνει στο target και, αν bubbles, ανεβαίνει στη bubbling phase. event.target είναι το στοιχείο όπου ξεκίνησε, currentTarget αυτό του listener που τρέχει. preventDefault ακυρώνει default action· stopPropagation εμποδίζει περαιτέρω propagation. Δεν είναι το ίδιο. Το διάγραμμα JS 104 δείχνει τις αντίθετες διαδρομές στο DOM tree.

### Τι είναι event delegation και πότε θα το χρησιμοποιούσες;

Βάζω έναν listener σε ancestor όπως tbody και εξετάζω το target του event που ανεβαίνει. Έτσι χειρίζομαι και δυναμικές γραμμές χωρίς listener ανά button. Η τρέχουσα εφαρμογή χρησιμοποιεί απλά inline handlers ώστε να είναι άμεσα ορατή η αντιστοίχιση. Δεν ισχυρίζομαι ότι έχει ήδη delegation. Είναι πιθανή μικρή εξεταστική επέκταση του event bubbling. [JS 102-104]

### Πώς εντοπίζεις το CSS που δίνει χρώμα σε ένα button;

Inspect στο button, μετά Styles: βρίσκω button και το background linear-gradient με var(--c1), var(--c2). Ακολουθώ τις custom properties στο :root. Στο Computed βλέπω τις τελικές τιμές. Μια διαγραμμένη declaration χάνει στο cascade ή έχει υπερκαλυφθεί· ελέγχω selector, specificity, source order, active pseudo-class και media query.

### Πώς λειτουργεί το CSS cascade και η specificity;

Το cascade επιλύει ανταγωνιστικούς κανόνες λαμβάνοντας υπόψη προέλευση/importance, layers όπου υπάρχουν, specificity και σειρά. Μέσα στην ίδια κατηγορία, ID selectors έχουν μεγαλύτερο βάρος από classes/pseudo-classes και αυτές από element selectors. Σε ισοβαθμία συνήθως κερδίζει ο μεταγενέστερος κανόνας. Η inheritance μεταφέρει επιλεγμένες properties από parent· δεν μεταφέρονται όλες. Δεν αντιμετωπίζω το !important ως κανονικό εργαλείο για κάθε σύγκρουση.

### Τι είναι το box model και το box-sizing: border-box;

Το box έχει content, padding, border και εξωτερικό margin. Με content-box το width αφορά κυρίως content· padding/border αυξάνουν το τελικό κουτί. Με border-box περιλαμβάνονται στο δηλωμένο width. Η εφαρμογή εφαρμόζει border-box σε όλα τα στοιχεία. Στο Computed/box model δείχνω πού βρίσκονται τα 10px padding ενός td και το border του.

### display:none, visibility:hidden και opacity:0: διαφέρουν;

display:none αφαιρεί το box από το layout. visibility:hidden το κρύβει κρατώντας τον χώρο. opacity:0 το κάνει διαφανές, αλλά μπορεί να παραμένει διαδραστικό και να καταλαμβάνει χώρο. Δεν αρκεί οπτική απόκρυψη για να αλλάξω δικαιώματα ή να προστατέψω δεδομένα. [Σχετική βάση: B 17, dynamic style example]

### Πώς προσαρμόζεται το UI σε μικρή οθόνη;

Το viewport meta ορίζει σωστή κλίμακα. Το @media (max-width:600px) μειώνει περιθώρια και βάζει τα form controls σε στήλη. Τα tables βρίσκονται σε wrapper με overflow-x:auto ώστε να γίνεται scroll μόνο εκεί. Το main document δεν πρέπει να βγαίνει οριζόντια εκτός οθόνης. Ελέγχω device toolbar σε 375px και δείχνω τον ενεργό media rule στο Styles.

### Τι σημαίνουν :hover, :focus-visible, :disabled και nth-child;

Είναι pseudo-classes: επιλέγουν ανά κατάσταση/θέση. :hover αντιδρά σε pointer, :focus-visible δείχνει ορατό keyboard focus, :disabled δηλώνει μη ενεργό control, nth-child(even) χρωματίζει εναλλάξ γραμμές. Δεν απαιτείται JS για απλές αλλαγές εμφάνισης. Το button.disabled αλλάζει DOM property και επομένως την αντιστοίχιση του :disabled selector.

### Ποια στοιχεία accessibility μπορείς να δείξεις;

lang, labels, semantic headings/main, πραγματικά button/form elements, th scope='col', labels για rating selects, visible keyboard focus και status messages με role='status'/aria-live. Τα table wrappers εστιάζονται με keyboard για scroll. Δεν βασίζομαι μόνο στο χρώμα error/success: το μήνυμα εξηγεί τι συνέβη. Δοκιμή μόνο με ποντίκι δεν αρκεί για keyboard λειτουργία.

### Γιατί ένα button γίνεται disabled κατά το request;

Για αποφυγή επαναλαμβανόμενων clicks και διπλών requests όσο υπάρχει εκκρεμότητα. Το finally το επαναφέρει τόσο σε επιτυχία όσο και σε αποτυχία. Δεν δίνει απόλυτη server-side εγγύηση μοναδικής δημιουργίας, επειδή άλλος client μπορεί να στείλει POST. Η εφαρμογή κρατά επίσης το input σε failure και δεν ξαναστέλνει αυτόματα το POST.

### Πώς διαφέρουν αλλαγή select, Submit, Remove και refresh;

Η αλλαγή select απλώς επιλέγει τιμή. Submit καλεί rateMovie, μετατρέπει σε number και γράφει myRatings. Remove κάνει delete το property και καθαρίζει αντίστοιχο select. Κανένα από αυτά δεν στέλνει rating στη βάση. Refresh ξαναφορτώνει το script και αδειάζει τη μνήμη. Στο Network πρέπει να μπορείς να αποδείξεις την απουσία rating request.

Συνέχισε: [FastAPI](05-backend.md) · [DevTools](09-devtools.md).
