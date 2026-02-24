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




