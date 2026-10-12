
function getToken() {
    return localStorage.getItem("token");
}

function isLoggedIn() {
    const token = getToken();
    return token !== null && token !== "";
}

function authFetch(url, options = {}) {
    const token = getToken();

    if (!token) {
        console.error("Nem található JWT-token a localStorage-ban.");
        window.location.replace("login.html");
        return Promise.reject(new Error("Hiányzó JWT-token"));
    }

    return fetch(url, {
        ...options,
        headers: {
            ...options.headers,
            Authorization: `Bearer ${token}`
        }
    });
}

async function loadCurrentUser() {
    try {
        const response = await authFetch("/kaptarweb/api/me");

        if (response.status === 401) {
            logout();
            return;
        }

        if (!response.ok) {
            throw new Error(
                `Nem sikerült lekérni a felhasználói adatokat: ${response.status}`
            );
        }

        const user = await response.json();

        console.log("Bejelentkezett felhasználó:", user);

        const nameElement = document.getElementById("userName");
        const emailElement = document.getElementById("userEmail");
        const picElement=document.getElementById("profile_pic");
        const apiaryElement=document.getElementById("apiary");

        if (nameElement) {
            nameElement.textContent = user.given_name || user.username || "";
        }

        if (emailElement) {
            emailElement.textContent = user.email || "";
        }
        if(picElement){
            picElement.src=user.picture_url || "";
        }
        if(apiaryElement)
        {
            apiaryElement.textContent=user.apiary_id ||"";
        }

        return user;
    } catch (error) {
        console.error("Hiba a felhasználói adatok lekérésekor:", error);
    }
}

function logout() {
    localStorage.removeItem("token");
    window.location.replace("login.html");
}

// Google OAuth után érkező token kezelése
const params = new URLSearchParams(window.location.search);
const token = params.get("token");

if (token) {
    localStorage.setItem("token", token);
    window.history.replaceState(
        {},
        document.title,
        window.location.pathname
    );
}

// Bejelentkezés ellenőrzése
const publicPages = ["login.html"];
const currentPage =
    window.location.pathname.split("/").pop() || "index.html";

if (!publicPages.includes(currentPage) && !isLoggedIn()) {
    window.location.replace("login.html");
} else if (!publicPages.includes(currentPage)) {
    // Csak a védett oldalakon kérjük le a felhasználót.
    document.addEventListener("DOMContentLoaded", () => {
        loadCurrentUser();
    });
}