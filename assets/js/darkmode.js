const toggleDarkMode = document.getElementById('btnSwitch')
const darkModeLabel = document.getElementById('darkModeLabel')

const setDarkMode = (active = false) => {
    const wrapper = document.documentElement.classList;
    if (active) {
        wrapper.add('dark');
        toggleDarkMode.checked = true;
        darkModeLabel.textContent = 'Light Mode';
    } else {
        wrapper.remove('dark');
        toggleDarkMode.checked = false;
        darkModeLabel.textContent = 'Dark Mode';
    }
};

toggleDarkMode.addEventListener('click', () => {
    if (document.documentElement.classList.contains('dark')) {
        setDarkMode(false);
        localStorage.setItem("theme", "light");
    } else {
        setDarkMode(true);
        localStorage.setItem("theme", "dark");
    }
});

// Query user preference and see if theme preference has been set
const query = window.matchMedia("(prefers-color-scheme: dark)");
const themePreference = localStorage.getItem("theme");

let active = query.matches;

if (themePreference === "dark") active = true;
if (themePreference === "light") active = false;

// Set theme based on user preference or override
setDarkMode(active);

// Watch for user preference changes
query.addEventListener("change", (e) => setDarkMode(e.matches));
