// ============================================================
// MovieLens Explorer - simple frontend logic (vanilla JS)
// ============================================================

// Address of the backend. Change this one line if it runs somewhere else.
const API_BASE = "http://localhost:3000/movielens/api";

// Movies the user rated this session. Kept only in memory (cleared on refresh).
// Example: { "1": { title: "Toy Story (1995)", rating: 5 } }
let myRatings = {};

// Movies from the latest search, so we can look up a title by its id later.
let searchedMovies = {};

// Small helper: send a request to the backend and give back the JSON.
async function callApi(path, options) {
  const response = await fetch(API_BASE + path, options);
  return response.json();
}

// ---------------- 1. Add a movie ----------------
async function addMovie() {
  const title = document.getElementById("add-title").value;
  const genres = document.getElementById("add-genres").value;
  const feedback = document.getElementById("add-feedback");

  // make sure both fields are filled in
  if (title === "" || genres === "") {
    feedback.textContent = "Please type a title and genres.";
    feedback.className = "error";
    return;
  }

  try {
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
    const data = await callApi("/movies?search=" + encodeURIComponent(keyword));

    searchedMovies = {}; // forget the previous search
    let html = "";
    for (const movie of data.movies) {
      searchedMovies[movie.movieId] = movie; // remember it for rating later
      html += "<tr>";
      html += "<td>" + movie.movieId + "</td>";
      html += "<td>" + movie.title + "</td>";
      html += "<td>" + movie.genres + "</td>";
      html += "<td><button onclick='showAverage(" + movie.movieId + ", this)'>Show</button></td>";
      html += "<td>" + ratingDropdown(movie.movieId) + "</td>";
      html += "</tr>";
    }
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
function ratingDropdown(movieId) {
  let html = "<select onchange='rateMovie(" + movieId + ", this.value)'>";
  html += "<option value=''>Rate...</option>";
  for (let r = 0.5; r <= 5; r += 0.5) {
    html += "<option value='" + r + "'>" + r + "</option>";
  }
  html += "</select>";
  return html;
}

// ---------------- Average rating (GET /ratings/{id}) ----------------
async function showAverage(movieId, button) {
  const cell = button.parentElement; // the <td> the button sits in
  cell.textContent = "...";
  try {
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
function rateMovie(movieId, value) {
  const movie = searchedMovies[movieId];
  myRatings[movieId] = { title: movie.title, rating: parseFloat(value) };
  showMyRatings();
}

// ---------------- 3. Show the "Your ratings" table ----------------
function showMyRatings() {
  const tbody = document.getElementById("my-ratings");
  const ids = Object.keys(myRatings);

  let html = "";
  for (const id of ids) {
    const r = myRatings[id];
    html += "<tr>";
    html += "<td>" + r.title + "</td>";
    html += "<td>" + r.rating + "</td>";
    html += "<td><button onclick='removeRating(" + id + ")'>Remove</button></td>";
    html += "</tr>";
  }
  tbody.innerHTML = html;

  document.getElementById("ratings-count").textContent = ids.length;
}

function removeRating(movieId) {
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
    ratings.push({ movieId: parseInt(id), rating: myRatings[id].rating });
  }

  if (ratings.length === 0) {
    feedback.textContent = "Please rate at least one movie first.";
    feedback.className = "error";
    return;
  }

  try {
    const data = await callApi("/recommendations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ratings: ratings }),
    });

    let html = "";
    for (const rec of data.recommendations) {
      html += "<tr>";
      html += "<td>" + rec.movieId + "</td>";
      html += "<td>" + rec.title + "</td>";
      html += "<td>" + rec.genres + "</td>";
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
