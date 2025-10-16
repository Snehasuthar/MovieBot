const input = document.getElementById("movieInput");
const suggestBox = document.getElementById("suggestions");
const recList = document.getElementById("recommendations");
const movieDetails = document.getElementById("movieDetails");

input.addEventListener("input", async () => {
    const query = input.value.trim();
    if (query.length < 2) {
        suggestBox.innerHTML = "";
        return;
    }
    const res = await fetch(`/search?q=${query}`);
    const movies = await res.json();

    suggestBox.innerHTML = "";
    movies.forEach(title => {
        const div = document.createElement("div");
        div.textContent = title;
        div.classList.add("suggestion-item");
        div.addEventListener("click", () => {
            input.value = title;
            suggestBox.innerHTML = "";
        });
        suggestBox.appendChild(div);
    });
});

document.getElementById("recommendBtn").addEventListener("click", async () => {
    const movieName = input.value.trim();
    if (movieName === "") {
        alert("Please enter a movie name!");
        return;
    }

    await getRecommendations(movieName);
});

// 🔥 Reusable function for both “Get Recommendations” and clicking movie items
async function getRecommendations(movieName) {
    const res = await fetch("/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `movie_name=${movieName}`
    });
    const data = await res.json();

    recList.innerHTML = "";
    if (data.error) {
        const li = document.createElement("li");
        li.innerHTML = `<strong>${data.error}</strong>`;
        recList.appendChild(li);
        return;
    }

    // 🧠 Show details of the searched/clicked movie
    const info = data.movie_info;
    document.getElementById("movieTitle").textContent = info.title;
    document.getElementById("movieRating").textContent = info.rating;
    document.getElementById("movieRelease").textContent = info.release_date;
    document.getElementById("movieOverview").textContent = info.overview;
    movieDetails.classList.remove("hidden");

    // 🎬 Show recommended movies (clickable)
    data.recommendations.forEach(movie => {
        const li = document.createElement("li");
        li.textContent = movie;
        li.classList.add("movie-item");
        li.addEventListener("click", () => getRecommendations(movie)); // 👈 load new details on click
        recList.appendChild(li);
    });
}
