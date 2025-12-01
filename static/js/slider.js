document.addEventListener("DOMContentLoaded", () => {
    const slides = document.querySelectorAll(".home-slider-img");
    let index = 0;

    setInterval(() => {
        slides[index].style.opacity = 0;
        index = (index + 1) % slides.length;
        slides[index].style.opacity = 1;
    }, 4500);
});
