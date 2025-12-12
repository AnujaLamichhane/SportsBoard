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

document.addEventListener("DOMContentLoaded", function () {
    const themeToggle = document.getElementById("themeToggle");

    // Load theme from localStorage
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
        themeToggle.textContent = "☀️";
    }

    themeToggle.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");

        // Swap button icon
        if (document.body.classList.contains("dark-mode")) {
            themeToggle.textContent = "☀️"; // light icon
            localStorage.setItem("theme", "dark");
        } else {
            themeToggle.textContent = "🌙"; // dark icon
            localStorage.setItem("theme", "light");
        }
    });
});



