window.addEventListener("load", function() {

    // For each HOD card, cycle images inside its own box
    const hodCards = document.querySelectorAll(".hod-card");

    hodCards.forEach(card => {
        const images = card.querySelectorAll(".hod-img");
        let index = 0;

        setInterval(() => {
            images.forEach(img => img.classList.remove("active-hod"));
            images[index].classList.add("active-hod");
            index = (index + 1) % images.length;
        }, 3500);

    });

});
