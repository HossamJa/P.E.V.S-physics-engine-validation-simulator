document.addEventListener("DOMContentLoaded", () => {

    if (document.getElementById("simulation-form")) {
        initSimulationPage();
    }

    if (document.getElementById("history-body")) {
        initHistoryPage();
    }

});

document.querySelector(".nav-toggle")?.addEventListener("click", () => {
    document.querySelector(".nav-links").classList.toggle("show");
});