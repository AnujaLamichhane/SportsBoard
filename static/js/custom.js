document.addEventListener("DOMContentLoaded", () => {
  const slides = document.querySelectorAll(".carousel .list .item");
  const thumbnails = document.querySelectorAll(".carousel .thumbnail .item");
  const nextBtn = document.getElementById("next");
  const prevBtn = document.getElementById("prev");
  let current = 0; // index of active slide
  // Function to update the visible slide and thumbnail
  function showSlide(index) {
    // Remove "active" from all
    slides.forEach((slide,i) => slide.classList.remove("active"));
    thumbnails.forEach((thumb) => thumb.classList.remove("active"));
    // Add "active" to the current index
    slides[index].classList.add("active");
    thumbnails[index].classList.add("active");
  }
  // Next button click
//   nextBtn.addEventListener("click", () => {
//     current = (current + 1) % slides.length;
//     showSlide(current);
//   });
//   // Previous button click
//   prevBtn.addEventListener("click", () => {
//     current = (current - 1 + slides.length) % slides.length;
//     showSlide(current);
//   });
  // Thumbnail click
  thumbnails.forEach((thumb, index) => {
    thumb.addEventListener("click", () => {
      current = index;
      showSlide(current);
    });
  });
  // Optional auto-slide (every 5 seconds)
  // setInterval(() => {
  //   current = (current + 1) % slides.length;
  //   showSlide(current);
  // }, 5000);
});





