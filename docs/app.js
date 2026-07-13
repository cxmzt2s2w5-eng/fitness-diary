const AUTH_URL = "http://127.0.0.1:8100";
const DIARY_URL = "http://127.0.0.1:8200";

const authSection = document.getElementById("authSection");
const diarySection = document.getElementById("diarySection");
const userStatus = document.getElementById("userStatus");
const message = document.getElementById("message");
const entriesList = document.getElementById("entriesList");
const logoutButton = document.getElementById("logoutButton");

function getToken() {
  return localStorage.getItem("access_token");
}

function setMessage(text, type = "success") {
  message.textContent = text;
  message.className = `message ${type}`;
}

async function request(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }

  return data;
}

function updateScreen() {
  const token = getToken();

  if (token) {
    authSection.classList.add("hidden");
    diarySection.classList.remove("hidden");
    logoutButton.classList.remove("hidden");
    userStatus.textContent = "Signed in";
    loadEntries();
  } else {
    authSection.classList.remove("hidden");
    diarySection.classList.add("hidden");
    logoutButton.classList.add("hidden");
    userStatus.textContent = "Not signed in";
    entriesList.innerHTML = "";
  }
}

document.getElementById("registerForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  try {
    await request(`${AUTH_URL}/register`, {
      method: "POST",
      body: JSON.stringify({
        name: document.getElementById("registerName").value,
        email: document.getElementById("registerEmail").value,
        password: document.getElementById("registerPassword").value,
      }),
    });

    setMessage("Account created. Now login.");
    event.target.reset();
  } catch (error) {
    setMessage(error.message, "error");
  }
});

document.getElementById("loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  try {
    const data = await request(`${AUTH_URL}/login`, {
      method: "POST",
      body: JSON.stringify({
        email: document.getElementById("loginEmail").value,
        password: document.getElementById("loginPassword").value,
      }),
    });

    localStorage.setItem("access_token", data.access_token);
    setMessage("Logged in.");
    event.target.reset();
    updateScreen();
  } catch (error) {
    setMessage(error.message, "error");
  }
});

document.getElementById("entryForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  try {
    await request(`${DIARY_URL}/entries`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
      body: JSON.stringify({
        title: document.getElementById("entryTitle").value,
        content: document.getElementById("entryContent").value,
        mood: document.getElementById("entryMood").value || null,
      }),
    });

    setMessage("Entry saved.");
    event.target.reset();
    loadEntries();
  } catch (error) {
    setMessage(error.message, "error");
  }
});

document.getElementById("refreshButton").addEventListener("click", loadEntries);

logoutButton.addEventListener("click", () => {
  localStorage.removeItem("access_token");
  setMessage("Logged out.");
  updateScreen();
});

async function loadEntries() {
  try {
    const entries = await request(`${DIARY_URL}/entries`, {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (entries.length === 0) {
      entriesList.innerHTML = "<p>No entries yet.</p>";
      return;
    }

    entriesList.innerHTML = entries
      .map(
        (entry) => `
          <article class="entry">
            <h3>${entry.title}</h3>
            <p>${entry.content}</p>
            <div class="entry-meta">
              ${entry.mood ? `Mood: ${entry.mood} - ` : ""}
              ${new Date(entry.created_at).toLocaleString()}
            </div>
          </article>
        `
      )
      .join("");
  } catch (error) {
    setMessage(error.message, "error");
  }
}

updateScreen();
