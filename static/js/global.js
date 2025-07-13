// plik: static/js/global.js

/**
 * Pokazuje toast z opcjonalnym typem.
 * @param {string} message – tekst komunikatu
 * @param {'success'|'error'} [type='success'] – typ toastu (domyślnie success)
 */
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    // Wymuś reflow, żeby CSS-transition zadziałał
    void toast.offsetWidth;
    toast.classList.add('show');

    // Po 2 sekundach usuń klasę .show, a po zakończeniu animacji usuń element
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300); // Czas musi pasować do transition w CSS
    }, 2000);
}


// Czekamy, aż cały dokument HTML będzie gotowy
document.addEventListener('DOMContentLoaded', () => {

    // --- Logika dla rozwijanego menu bocznego (sidebar) ---
    document.querySelectorAll('.submenu-toggle').forEach(item => {
        item.addEventListener('click', function(event) {
            event.preventDefault(); // Zapobiega domyślnej akcji linku (przejściu do #)
            const parentLi = this.closest('.has-submenu');
            parentLi.classList.toggle('active');
        });
    });

    // --- NOWA, POPRAWIONA LOGIKA OZNACZANIA AKTYWNEGO LINKU ---
    const allLinks = document.querySelectorAll('.sidebar-nav .sidebar-link');
    const currentPath = window.location.pathname;

    // 1. Reset: Najpierw usuwamy klasę 'active' ze wszystkich linków i ich rodziców.
    allLinks.forEach(link => {
        link.classList.remove('active');
    });
    document.querySelectorAll('.has-submenu').forEach(item => {
        item.classList.remove('active');
    });

    // 2. Znajdź jeden, właściwy link, który pasuje do obecnego adresu URL.
    const activeLink = document.querySelector(`.sidebar-nav .sidebar-link[href="${currentPath}"]`);

    // 3. Jeśli znaleziono pasujący link, nadaj klasy 'active'.
    if (activeLink) {
        // Podświetl sam link.
        activeLink.classList.add('active');

        // Jeśli link jest w podmenu, rozwiń to podmenu.
        const parentSubmenu = activeLink.closest('.submenu');
        if (parentSubmenu) {
            parentSubmenu.closest('.has-submenu').classList.add('active');
        }

        // Ustaw tytuł strony w górnym pasku.
        const pageTitleElement = document.querySelector('.page-title');
        if (pageTitleElement) {
            pageTitleElement.textContent = activeLink.innerText.trim();
        }
    }
});