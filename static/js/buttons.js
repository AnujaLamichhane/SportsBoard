      const matchCards = document.querySelectorAll('.match-card');
      const modal = document.getElementById('matchModal');
      const modalTitle = document.getElementById('modalTitle');
      const modalDesc = document.getElementById('modalDesc');
      const closeModal = document.getElementById('closeModal');

      matchCards.forEach(card => {
        card.addEventListener('click', () => {
          modal.style.display = 'flex';
          modalTitle.textContent = card.getAttribute('data-title');
          modalDesc.innerHTML = card.getAttribute('data-desc');
        });
      });

      closeModal.addEventListener('click', () => modal.style.display = 'none');
      window.addEventListener('click', e => { if (e.target === modal) modal.style.display = 'none'; });

    const bookButtons = document.querySelectorAll('.book-btn');
        bookButtons.forEach(btn => {
        btn.addEventListener('click', () => {
      // If user is not logged in, redirect to login page
      window.location.href = "{% url 'login' %}";
    //     if (isLoggedIn) {
    //      window.location.href = "/book/";
    //   } else {
    //     window.location.href = "/accounts/login/";
    //   }
    });
  });

document.addEventListener("DOMContentLoaded", () => {
  // Navbar toggle
  const menuToggle = document.querySelector(".menu-toggle");
  const navLinks = document.querySelector(".nav-links");
  if (menuToggle) {
      menuToggle.addEventListener("click", () => {
      navLinks.classList.toggle("active");
  });
  }
});
  document.addEventListener("DOMContentLoaded", () => {
    const scrollContainer = document.querySelector(".match-cards");
    const btnNext = document.querySelector(".scroll-btn.next");
    const btnPrev = document.querySelector(".scroll-btn.prev");

    if (btnNext && btnPrev && scrollContainer) {
      btnNext.addEventListener("click", () => {
        scrollContainer.scrollBy({ left: 300, behavior: "smooth" });
      });

      btnPrev.addEventListener("click", () => {
      scrollContainer.scrollBy({ left: -300, behavior: "smooth" });
      });
    }
  });

  // Scroll buttons
  // const scrollContainer = document.querySelector(".match-cards");
  // const scrollLeft = document.getElementById("scrollLeft");
  // const scrollRight = document.getElementById("scrollRight");

  // if (scrollContainer && scrollLeft && scrollRight) {
  //   scrollLeft.addEventListener("click", () => {
  //     scrollContainer.scrollBy({ left: -300, behavior: "smooth" });
  //   });
  //   scrollRight.addEventListener("click", () => {
  //     scrollContainer.scrollBy({ left: 300, behavior: "smooth" });
  //   });
  // }

  // Book button
//   const isLoggedIn = window.isUserLoggedIn || false;
//   document.querySelectorAll(".book-btn").forEach((btn) => {
//     btn.addEventListener("click", () => {
//       if (isLoggedIn) {
//         window.location.href = "/book/";
//       } else {
//         window.location.href = "/login/";
//       }
//     });
//   });


