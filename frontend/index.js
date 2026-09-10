// Vanilla JavaScript: events update the DOM and fetch JSON from FastAPI.
// const fixes the binding, not the contents of an object.
const API_BASE = "http://localhost:3000/movielens/api";
const myRatings = {}; // Page memory only: refresh clears it. No localStorage/cookies.
let searchedMovies = {};
let ratingsVersion = 0;

function feedback(id, message, isError = false) {
    const element = document.getElementById(id);
    element.textContent = message;
    element.className = isError ? "error" : "success";
}

// The table template is trusted markup; database strings are untrusted text.
// Let the DOM escape text instead of interpreting movie titles/genres as HTML.
function escapeHtml(value) {
    const span = document.createElement("span");
    span.textContent = value;
    return span.innerHTML;
}

// async always returns a Promise. await suspends this function, not the page.
async function callApi(path, options) {
    let response;
    try {
        response = await fetch(API_BASE + path, options);
    } catch (error) {
        throw new Error("Cannot reach the API. Check the backend on port 3000 and the browser Console.");
    }
    // fetch resolves even for 404/422/500; only network/CORS failures reject it.
    // Reading the body is another asynchronous step, separate from receiving headers.
    let data;
    try {
        data = await response.json();
    } catch (error) {
        throw new Error("HTTP " + response.status + ": the API did not return valid JSON.");
    }
    if (!response.ok) {
        const detail = Array.isArray(data.detail)
            ? data.detail.map(item => item.loc.join(".") + ": " + item.msg).join("; ")
            : data.detail || "Request failed.";
        throw new Error("HTTP " + response.status + ": " + detail);
    }
    return data;
}

async function addMovie() {
    const title = document.getElementById("add-title").value.trim();
    const genres = document.getElementById("add-genres").value.trim();
    const button = document.getElementById("add-button");
    if (button.disabled) return;
    if (!title || !genres) {
        feedback("add-feedback", "Please type a title and genres.", true);
        return;
    }
    button.disabled = true; // Prevent duplicate POSTs while this one is pending.
    feedback("add-feedback", "Adding movie...");
    try {
        const data = await callApi("/movies", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, genres }), // Object -> JSON text.
        });
        feedback("add-feedback", "Added! New movie id: " + data.movieId);
        document.getElementById("add-title").value = "";
        document.getElementById("add-genres").value = "";
    } catch (error) {
        // Preserve input on failure. Do not automatically retry a creation POST:
        // the server may have committed even if its response was lost.
        feedback("add-feedback", error.message + " Search for the title before retrying.", true);
    } finally {
        button.disabled = false;
    }
}

async function searchMovies() {
    const keyword = document.getElementById("search-input").value.trim();
    const button = document.getElementById("search-button");
    const tbody = document.getElementById("search-results");
    if (button.disabled) return;
    button.disabled = true;
    feedback("search-feedback", "Searching...");
    try {
        // Encoding keeps &, # and other characters inside this query parameter.
        const data = await callApi("/movies?search=" + encodeURIComponent(keyword));
        searchedMovies = {};
        let html = "";
        for (const movie of data.movies) {
            searchedMovies[movie.movieId] = movie;
            html += "<tr><td>" + movie.movieId + "</td>";
            html += "<td>" + escapeHtml(movie.title) + "</td>";
            html += "<td>" + escapeHtml(movie.genres) + "</td>";
            html += "<td><button type='button' onclick='showAverage(" + movie.movieId + ", this)'>Show</button></td>";
            html += "<td>" + ratingDropdown(movie.movieId) + "</td></tr>";
        }
        tbody.innerHTML = html; // Replace only the results; no page navigation.
        feedback("search-feedback", "Found " + data.movies.length + " movie(s).");
    } catch (error) {
        searchedMovies = {};
        tbody.replaceChildren();
        feedback("search-feedback", error.message, true);
    } finally {
        button.disabled = false;
    }
}

function ratingDropdown(movieId) {
    let html = "<select id='rating-" + movieId + "' aria-label='Rating for movie " + movieId + "'>";
    html += "<option value=''>Rate...</option>";
    for (let r = 0.5; r <= 5; r += 0.5) {
        const selected = myRatings[movieId]?.rating === r ? " selected" : "";
        html += "<option value='" + r + "'" + selected + ">" + r + "</option>";
    }
    return html + "</select> <button type='button' onclick='submitRating(" + movieId + ")'>Submit</button>";
}

function submitRating(movieId) {
    const value = document.getElementById("rating-" + movieId).value;
    if (value === "") {
        feedback("search-feedback", "Please choose a rating before submitting.", true);
        return;
    }
    rateMovie(movieId, value);
    feedback("search-feedback", "Saved your rating of " + value + " for " + searchedMovies[movieId].title + ".");
}

async function showAverage(movieId, button) {
    const cell = button.parentElement; // Inline handler's `this` is the clicked button.
    button.disabled = true;
    try {
        const data = await callApi("/ratings/" + movieId); // Path parameter.
        if (data.ratings.length === 0) {
            cell.textContent = "No dataset ratings";
            return;
        }
        let sum = 0;
        for (const r of data.ratings) sum += r.rating;
        cell.textContent = (sum / data.ratings.length).toFixed(2) + " (" + data.ratings.length + ")";
    } catch (error) {
        // Keep the button so this read-only operation can be retried.
        feedback("search-feedback", error.message, true);
    } finally {
        button.disabled = false;
    }
}

function rateMovie(movieId, value) {
    const rating = Number(value); // A select's value is a string; JSON needs a number.
    if (!searchedMovies[movieId] || !Number.isFinite(rating) || rating < 0.5 || rating > 5 || rating % 0.5 !== 0) return;
    myRatings[movieId] = { title: searchedMovies[movieId].title, rating };
    showMyRatings(); // No HTTP request, INSERT, or persistent browser storage.
}

function showMyRatings() {
    const ids = Object.keys(myRatings); // Object property names (IDs) are strings.
    let html = "";
    for (const id of ids) {
        const r = myRatings[id];
        html += "<tr><td>" + escapeHtml(r.title) + "</td><td>" + r.rating + "</td>";
        html += "<td><button type='button' onclick='removeRating(" + id + ")'>Remove</button></td></tr>";
    }
    document.getElementById("my-ratings").innerHTML = html;
    document.getElementById("ratings-count").textContent = ids.length;
    // Previously computed (or pending) results belong to an older rating set.
    ratingsVersion += 1;
    document.getElementById("rec-results").replaceChildren();
    feedback("rec-feedback", "Ratings changed. Request new recommendations.");
}

function removeRating(movieId) {
    delete myRatings[movieId]; // Remove an object property; not a database DELETE.
    const select = document.getElementById("rating-" + movieId);
    if (select) select.value = "";
    showMyRatings();
}

async function getRecommendations() {
    const button = document.getElementById("rec-button");
    const tbody = document.getElementById("rec-results");
    if (button.disabled) return;
    const ratings = Object.keys(myRatings).map(id => ({ movieId: Number(id), rating: myRatings[id].rating }));
    // Pearson needs at least two co-rated items with variation. This is guidance;
    // the API still accepts smaller lists and returns [] when no signal exists.
    if (ratings.length < 2 || new Set(ratings.map(r => r.rating)).size < 2) {
        tbody.replaceChildren();
        feedback("rec-feedback", "Rate at least two movies with different scores. Several familiar titles work best.", true);
        return;
    }
    button.disabled = true;
    const version = ratingsVersion;
    feedback("rec-feedback", "Finding recommendations...");
    try {
        const data = await callApi("/recommendations", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ratings }), // Send the complete rating set each time.
        });
        if (version !== ratingsVersion) return; // User edited ratings during await.
        let html = "";
        for (const rec of data.recommendations) {
            html += "<tr><td>" + rec.movieId + "</td>";
            html += "<td>" + escapeHtml(rec.title) + "</td>";
            html += "<td>" + escapeHtml(rec.genres) + "</td>";
            html += "<td>" + rec.predictedRating + "</td></tr>";
        }
        tbody.innerHTML = html;
        feedback("rec-feedback", data.recommendations.length
            ? "Found " + data.recommendations.length + " recommendations."
            : "No usable neighbours or unseen movies. Try rating more familiar titles with varied scores.");
    } catch (error) {
        if (version !== ratingsVersion) return;
        tbody.replaceChildren();
        feedback("rec-feedback", error.message, true);
    } finally {
        button.disabled = false;
    }
}
