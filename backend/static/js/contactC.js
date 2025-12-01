// ================================================
//  CONTACT PAGE — PREMIUM JS
//  Namespace: contactC-   (no global overlap)
// ================================================

document.addEventListener("DOMContentLoaded", () => {

    // -------------------------------------------------
    // Fade In on Scroll (Shared Animation Engine)
    // -------------------------------------------------
    const revealOptions = {
        threshold: 0.12
    };

    const revealObserver = new IntersectionObserver(entries => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                e.target.classList.add("in-view");
            }
        });
    }, revealOptions);

    document.querySelectorAll(
        ".fade-section, .fade-in, .fade-in-up"
    ).forEach(el => revealObserver.observe(el));



    // -------------------------------------------------
    // CONTACT FORM HANDLER
    // -------------------------------------------------
    const form = document.getElementById("contactC-form");
    const successBox = document.getElementById("contactC-success");

    if (form) {

        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const formData = new FormData(form);

            // Optional API endpoint: /send-message
            try {
                let response = await fetch("/send-message", {
                    method: "POST",
                    body: formData
                });

                if (response.ok) {
                    successBox.textContent = "Your message has been sent!";
                    successBox.style.display = "block";

                    form.reset();
                } else {
                    successBox.textContent = "Something went wrong. Try again.";
                    successBox.style.display = "block";
                    successBox.style.color = "red";
                }

            } catch (err) {
                successBox.textContent = "Network error. Retry.";
                successBox.style.display = "block";
                successBox.style.color = "red";
            }
        });
    }



    // -------------------------------------------------
    // SMOOTH SCROLL FOR "Learn More" Button
    // -------------------------------------------------
    document.querySelectorAll("a[href^='#']").forEach(link => {
        link.addEventListener("click", e => {
            const target = document.querySelector(link.getAttribute("href"));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: "smooth" });
            }
        });
    });

});
