document.addEventListener("DOMContentLoaded", () => {
  function updateDateTime() {
    const now = new Date();
    const options = { 
      weekday: 'short', 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    };
    const date = now.toLocaleDateString('en-NP', options);
    const time = now.toLocaleTimeString('en-NP');
    document.getElementById('datetime').innerText = `${date} ${time}`;
  }

  // Update every second
  setInterval(updateDateTime, 1000);
  updateDateTime();

  const matchCards = document.querySelectorAll('.match-card');
  const modal = document.getElementById('matchModal');
  const modalTitle = document.getElementById('modalTitle');
  const modalDesc = document.getElementById('modalDesc');
  const closeModal = document.getElementById('closeModal');

  if (matchCards && modal) {
      matchCards.forEach(card => {
        card.addEventListener('click', () => {
          modal.style.display = 'flex';
          modalTitle.textContent = card.getAttribute('data-title');
          modalDesc.innerHTML = card.getAttribute('data-desc');
        });
      });
  }
  modal.addEventListener("click", (e) => {
      if (e.target === modal) {          // works only inside modal
        modal.style.display = "none";
      }
  });
  if (closeModal) {
    closeModal.addEventListener('click', () => modal.style.display = 'none');
  }
    // Login Redirect
  const bookButtons = document.querySelectorAll('.book-btn');
  bookButtons.forEach(btn => {
    btn.addEventListener('click', () => {      
      window.location.href = "{% url 'login' %}";
    //     if (isLoggedIn) {
    //      window.location.href = "/book/";
    //   } else {
    //     window.location.href = "/accounts/login/";
    //   }
    });
  });

  // Navbar toggle
  
  const menuToggle = document.getElementById("menuToggle");
  const navLinks = document.getElementById("navLinks");
  
  menuToggle.addEventListener("click", () => {
      navLinks.classList.toggle("active");
  });
  
  const sportsDropdown = document.getElementById("sportsDropdown");
  const sportsMenu = document.getElementById("sportsMenu");

  sportsDropdown.addEventListener("click", (e) => {
    // Prevent page jumping
    e.preventDefault();

    // Only activate on mobile
    if (window.innerWidth <= 850) {
      sportsMenu.classList.toggle("open");
    }
  });
  

});
// document.addEventListener("DOMContentLoaded", () => {
  //   const scrollContainer = document.querySelector(".match-cards");
  //   const btnNext = document.querySelector(".scroll-btn.next");
  //   const btnPrev = document.querySelector(".scroll-btn.prev");

  //   if (btnNext && btnPrev && scrollContainer) {
  //     btnNext.addEventListener("click", () => {
  //       scrollContainer.scrollBy({ left: 300, behavior: "smooth" });
  //     });

  //     btnPrev.addEventListener("click", () => {
  //     scrollContainer.scrollBy({ left: -300, behavior: "smooth" });
  //     });
  //   }
  // });


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


