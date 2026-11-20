
const themeToggle = document.getElementById("themeToggle");
const html = document.documentElement;

// Load previously selected theme
const savedTheme = localStorage.getItem("deepfake-theme") || "light";

html.setAttribute("data-theme", savedTheme);

updateThemeButton();

themeToggle.addEventListener("click", function () {

    const currentTheme = html.getAttribute("data-theme");

    const newTheme =
        currentTheme === "light" ? "dark" : "light";

    html.setAttribute("data-theme", newTheme);

    localStorage.setItem("deepfake-theme", newTheme);

    updateThemeButton();
});

function updateThemeButton() {

    const currentTheme = html.getAttribute("data-theme");

    themeToggle.textContent =
        currentTheme === "light" ? "☾" : "☀";

    themeToggle.setAttribute(
        "aria-label",
        currentTheme === "light"
            ? "Switch to dark mode"
            : "Switch to light mode"
    );
}
