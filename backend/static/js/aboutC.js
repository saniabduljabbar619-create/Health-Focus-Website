// aboutC.js — lightweight modal + intersection observer

document.addEventListener('DOMContentLoaded', () => {
  // Modal elements
  const modal = document.getElementById('aboutC-modal');
  const container = document.getElementById('aboutC-video-container');
  const closeBtn = document.getElementById('aboutC-close');

  function openYouTube(id){
    if(!id) return;
    container.innerHTML = `<iframe src="https://www.youtube.com/embed/${id}?autoplay=1&rel=0" allow="autoplay; encrypted-media; fullscreen" allowfullscreen></iframe>`;
    modal.classList.add('open');
    modal.setAttribute('aria-hidden','false');
  }

  function closeModal(){
    modal.classList.remove('open');
    modal.setAttribute('aria-hidden','true');
    container.innerHTML = '';
  }

  // wire video cards
  document.querySelectorAll('.yt-thumb').forEach(el => {
    el.style.cursor = 'pointer';
    el.addEventListener('click', () => {
      const id = el.dataset.videoId || el.getAttribute('data-video-id');
      openYouTube(id);
    });
  });

  closeBtn && closeBtn.addEventListener('click', closeModal);
  modal && modal.addEventListener('click', (e) => {
    if(e.target === modal) closeModal(); // click outside to close
  });

  // Intersection observer for fade animations
  const io = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if(en.isIntersecting){
        en.target.classList.add('in-view');
      }
    });
  }, { threshold: 0.12 });

  document.querySelectorAll('.fade-section, .fade-in, .fade-in-up').forEach(n => io.observe(n));
});
