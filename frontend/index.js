// ============================================================
// MovieLens Explorer - simple frontend logic (vanilla JS)
// ============================================================
//
// THEORY · L3 JavaScript · what this file IS
//   JavaScript is a scripting language parsed in a runtime (the browser's V8
//   engine), not compiled ahead of time. Its runtime is SINGLE-THREADED and
//   EVENT-DRIVEN with NON-BLOCKING I/O: slow work (here, network requests) is
//   handed to the browser's Web APIs and a callback is queued on the event
//   loop, so the one thread is never blocked waiting. Everything below is
//   "client-side programming": code downloaded to and executed in the browser.
// ============================================================

// Address of the backend. Change this one line if it runs somewhere else.
// THEORY · L3 · const = a block-scoped, immutable BINDING (ES6). You cannot
// reassign API_BASE later (TypeError). Use const by default; let only when you
// must reassign. This URL is <scheme>://<host>:<port>/<path> (L2 HTTP).
const API_BASE = "http://localhost:3000/movielens/api";

// Movies the user rated this session. Kept only in memory (cleared on refresh).
// Example: { "1": { title: "Toy Story (1995)", rating: 5 } }
// THEORY · L3 · let = a mutable, block-scoped binding. The value is an OBJECT
// used as an associative array (key → value map), accessed with bracket
// notation myRatings[id]. Keeping it only in a JS variable (not on the server)
// is the client-side answer to HTTP being STATELESS (L2): the page holds the
// session state itself, so it vanishes on refresh.
let myRatings = {};

// Movies from the latest search, so we can look up a title by its id later.
let searchedMovies = {};

// Small helper: send a request to the backend and give back the JSON.
// THEORY · L3/L4 · async / await + the fetch() Promise API  (the headline topic)
//   * fetch(url, options) performs the HTTP request and returns a PROMISE — an
//     object representing the FUTURE result of a single async computation. It
//     does NOT block; the function returns immediately.
//   * Marking the function `async` lets us write `await` inside it. `await`
//     pauses THIS function until the awaited Promise settles, then resumes with
//     its resolved value — while the single JS thread keeps handling other
//     events in the meantime. It is syntactic sugar over Promise .then()
//     chaining: `await fetch(...)` is the linear-looking form of
//     fetch(...).then(response => ...).
//   * response.json() itself returns a Promise (parsing the body is async), so
//     we await it too. An async function always returns a Promise, so callers
//     of callApi() must await it as well.
//   * fetch only REJECTS on a network failure, NOT on an HTTP 4xx/5xx status, so
//     we check response.ok and throw ourselves — otherwise a server error would
//     slip through as "success" (e.g. showing "Added! id: undefined").
async function callApi(path, options) {
	const response = await fetch(API_BASE + path, options);
	if (!response.ok) {
		throw new Error("Request failed with status " + response.status);
	}
	return response.json();
}

// Escape user-controlled text (movie titles, genres, tags) before inserting it
// into the page. Titles are arbitrary — a movie added as "<img src=x
// onerror=...>" would otherwise run as HTML/JS (stored XSS) for anyone who later
// sees it. Escaping the five HTML-significant characters neutralises it.
function escapeHtml(text) {
	return String(text)
		.replaceAll("&", "&amp;")
		.replaceAll("<", "&lt;")
		.replaceAll(">", "&gt;")
		.replaceAll('"', "&quot;")
		.replaceAll("'", "&#39;");
}

// ---------------- 1. Add a movie ----------------
// THEORY · L3 · event handler: addMovie is invoked by an onclick attribute in
// index.html (<button onclick="addMovie()">). Registering a function to run
// when an event fires is the core of event-driven client programming.
async function addMovie() {
	// THEORY · L3 · DOM Web API: document.getElementById reaches into the page's
	// Document Object Model to read the live <input> values the user typed.
	const title = document.getElementById("add-title").value;
	const genres = document.getElementById("add-genres").value;
	const feedback = document.getElementById("add-feedback");

	// make sure both fields are filled in
	// THEORY · L3 · strict equality ===: compares value AND type with NO
	// coercion (unlike ==). "" is also one of JS's falsy values. This is client-
	// side form validation before we bother the server.
	if (title === "" || genres === "") {
		feedback.textContent = "Please type a title and genres.";
		feedback.className = "error";
		return;
	}

	// THEORY · L3 · try/catch around await: this is the async equivalent of a
	// Promise .catch(). If the fetch rejects (server unreachable), control jumps
	// to the catch block instead of crashing.
	try {
		// THEORY · L2/L4 · an HTTP POST with a JSON body:
		//   method "POST"            → the verb for "send data / create" (CRUD Create)
		//   Content-Type header      → declares the body's MIME type, application/json
		//   JSON.stringify({...})    → serialises a JS object into a JSON string
		// JSON is the REST data-interchange format; its syntax is a subset of JS
		// object syntax, which is why the conversion is one function call.
		const data = await callApi("/movies", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ title: title, genres: genres }),
		});
		feedback.textContent = "Added! New movie id: " + data.movieId;
		feedback.className = "success";
		document.getElementById("add-title").value = "";
		document.getElementById("add-genres").value = "";
	} catch (error) {
		feedback.textContent = "Error: could not reach the server.";
		feedback.className = "error";
	}
}

// ---------------- 2. Search movies ----------------
async function searchMovies() {
	const keyword = document.getElementById("search-input").value;
	const feedback = document.getElementById("search-feedback");
	const tbody = document.getElementById("search-results");

	try {
		// encodeURIComponent makes the keyword safe to put inside a URL
		// THEORY · L2 · URL query string + percent-encoding: a GET request sends
		// input in the query part (?search=...). encodeURIComponent percent-
		// encodes characters that are unsafe in a URL (e.g. a space → %20),
		// exactly the encoding the HTTP lecture describes for URIs.
		const data = await callApi("/movies?search=" + encodeURIComponent(keyword));

		searchedMovies = {}; // forget the previous search
		// THEORY · L3 · for...of iterates the VALUES of an iterable (the array of
		// movie objects). We build an HTML string, then write it once.
		let html = "";
		for (const movie of data.movies) {
			searchedMovies[movie.movieId] = movie; // remember it for rating later
			html += "<tr>";
			html += "<td>" + movie.movieId + "</td>";
			html += "<td>" + escapeHtml(movie.title) + "</td>";
			html += "<td>" + escapeHtml(movie.genres) + "</td>";
			html += "<td><button onclick='showAverage(" + movie.movieId + ", this)'>Show</button></td>";
			html += "<td>" + ratingDropdown(movie.movieId) + "</td>";
			html += "</tr>";
		}
		// THEORY · L3 · DOM mutation: assigning innerHTML re-renders the table
		// body. Updating the page without a full reload is what makes this a
		// dynamic page / Rich Internet Application (L1).
		tbody.innerHTML = html;

		feedback.textContent = "Found " + data.movies.length + " movie(s).";
		feedback.className = "success";
	} catch (error) {
		tbody.innerHTML = "";
		feedback.textContent = "Error: could not reach the server.";
		feedback.className = "error";
	}
}

// Build the 0.5 - 5.0 rating dropdown for one movie (returns HTML text).
// The dropdown only *selects* a value; nothing is saved until the user clicks
// the Submit button beside it (see submitRating) — a deliberate, explicit action.
// THEORY · L3 · functions are first-class values that always RETURN something
// (here a string). The returned markup is embedded into the table by the caller.
function ratingDropdown(movieId) {
	let html = "<select id='rating-" + movieId + "'>";
	html += "<option value=''>Rate...</option>";
	// THEORY · L3 · classic for-loop with a step; works on floats here (0.5 step).
	for (let r = 0.5; r <= 5; r += 0.5) {
		html += "<option value='" + r + "'>" + r + "</option>";
	}
	html += "</select>";
	html += " <button onclick='submitRating(" + movieId + ")'>Submit</button>";
	return html;
}

// ---------------- Submit the chosen rating (deferred, on button click) ----------------
// Reads the current dropdown value for this movie and saves it only now — not on
// every dropdown change.
function submitRating(movieId) {
	const select = document.getElementById("rating-" + movieId);
	const value = select.value;
	const feedback = document.getElementById("search-feedback");

	// nothing chosen yet: the placeholder "Rate..." option has an empty value
	if (value === "") {
		feedback.textContent = "Please choose a rating before submitting.";
		feedback.className = "error";
		return;
	}

	// save it (rateMovie stores it in myRatings and re-renders "Your ratings")
	rateMovie(movieId, value);
	feedback.textContent = "Saved your rating of " + value + " for " + searchedMovies[movieId].title + ".";
	feedback.className = "success";
}

// ---------------- Average rating (GET /ratings/{id}) ----------------
async function showAverage(movieId, button) {
	// THEORY · L3 · the DOM event passes `this` (the clicked button) so we can
	// find its parent <td> and write the result back into that exact cell.
	const cell = button.parentElement; // the <td> the button sits in
	cell.textContent = "...";
	try {
		// THEORY · L2/L4 · GET with a PATH parameter: the movie id is part of the
		// URL path (/ratings/123), matching the server's /ratings/{movie_id}
		// route. GET is the safe, read-only verb (CRUD Read).
		const data = await callApi("/ratings/" + movieId);
		const ratings = data.ratings;
		if (ratings.length === 0) {
			cell.textContent = "no ratings";
			return;
		}
		// average = sum of ratings / how many there are
		let sum = 0;
		for (const r of ratings) {
			sum += r.rating;
		}
		const average = sum / ratings.length;
		cell.textContent = average.toFixed(2) + " (" + ratings.length + ")";
	} catch (error) {
		cell.textContent = "error";
	}
}

// ---------------- Rate a movie (saved in memory only) ----------------
// THEORY · L3 · CLOSURE + shared state: rateMovie, searchMovies and
// getRecommendations are all closures over the module-level `myRatings` and
// `searchedMovies`. A closure is a function bundled with the lexical
// environment it was defined in, so these handlers keep read/write access to
// that shared state across many separate events — the JS way of associating
// data with the functions that operate on it.
function rateMovie(movieId, value) {
	const movie = searchedMovies[movieId];
	// THEORY · L3 · type conversion: select values are strings; parseFloat turns
	// "4.5" into the number 4.5 so later arithmetic (the average, the request
	// body) is numeric, not string concatenation.
	myRatings[movieId] = { title: movie.title, rating: parseFloat(value) };
	showMyRatings();
}

// ---------------- EXAM Q -----------------
// ---------- tag-based movie search starts ----------
async function searchByTag() {
	const keyword = document.getElementById("tag-search-input").value;
	const feedback = document.getElementById("tag-search-feedback");
	const tbody = document.getElementById("tag-search-results");

	try {
		// THEORY · L2/L4 · POST carrying a JSON body even though it "reads" data:
		// the assignment specifies the tag keyword travels in the request body,
		// so we POST {search: keyword} as JSON (same pattern as addMovie).
		const data = await callApi("/tags/movies", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ search: keyword }),
		});

		let html = "";
		for (const movie of data.movies) {
			html += "<tr>";
			html += "<td>" + movie.movieId + "</td>";
			html += "<td>" + escapeHtml(movie.title) + "</td>";
			html += "<td>" + escapeHtml(movie.genres) + "</td>";
			html += "<td>" + escapeHtml(movie.matchingTag) + "</td>";
			html += "</tr>";
		}
		tbody.innerHTML = html;

		feedback.textContent = "Found " + data.movies.length + " movie(s) with matching tags.";
		feedback.className = "success";
	} catch (error) {
		tbody.innerHTML = "";
		feedback.textContent = "Error: could not reach the server.";
		feedback.className = "error";
	}
}
// ---------- tag-based movie search finishes ----------
// END OF EXAM Q

// ---------------- 3. Show the "Your ratings" table ----------------
function showMyRatings() {
	const tbody = document.getElementById("my-ratings");
	// THEORY · L3 · Object.keys returns an array of an object's property names;
	// here the movie ids we have rated. Iterating those rebuilds the table.
	const ids = Object.keys(myRatings);

	let html = "";
	for (const id of ids) {
		const r = myRatings[id];
		html += "<tr>";
		html += "<td>" + escapeHtml(r.title) + "</td>";
		html += "<td>" + r.rating + "</td>";
		html += "<td><button onclick='removeRating(" + id + ")'>Remove</button></td>";
		html += "</tr>";
	}
	tbody.innerHTML = html;

	document.getElementById("ratings-count").textContent = ids.length;
}

function removeRating(movieId) {
	// THEORY · L3 · the `delete` operator removes a property from an object
	// (mutating the myRatings associative array), then we re-render.
	delete myRatings[movieId];
	showMyRatings();
}

// ---------------- 4. Recommendations (POST /recommendations) ----------------
async function getRecommendations() {
	const feedback = document.getElementById("rec-feedback");
	const tbody = document.getElementById("rec-results");

	// build the list of ratings to send to the backend
	const ratings = [];
	for (const id of Object.keys(myRatings)) {
		// THEORY · L3 · parseInt: object keys are always strings, but the server
		// expects movieId as an integer (validated by the Pydantic model), so we
		// convert before sending.
		ratings.push({ movieId: parseInt(id), rating: myRatings[id].rating });
	}

	if (ratings.length === 0) {
		feedback.textContent = "Please rate at least one movie first.";
		feedback.className = "error";
		return;
	}

	try {
		// THEORY · L1/L4 · the REST "stateless" contract in action: we send the
		// FULL list of session ratings in the body every time, because the server
		// keeps no memory of us between requests. The response is the computed
		// recommendations — nothing is stored server-side.
		const data = await callApi("/recommendations", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ ratings: ratings }),
		});

		let html = "";
		for (const rec of data.recommendations) {
			html += "<tr>";
			html += "<td>" + rec.movieId + "</td>";
			html += "<td>" + escapeHtml(rec.title) + "</td>";
			html += "<td>" + escapeHtml(rec.genres) + "</td>";
			html += "<td>" + rec.predictedRating + "</td>";
			html += "</tr>";
		}
		tbody.innerHTML = html;

		feedback.textContent = "Found " + data.recommendations.length + " recommendations.";
		feedback.className = "success";
	} catch (error) {
		tbody.innerHTML = "";
		feedback.textContent = "Error: could not reach the server.";
		feedback.className = "error";
	}
}
