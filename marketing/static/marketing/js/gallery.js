document.addEventListener("DOMContentLoaded", () => {
  const gallery = document.getElementById("marketing-gallery");

  // IntersectionObserver to watch when the gallery hits 50% of the viewport
  const io = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        gallery.classList.add("expanded");
        io.disconnect();
      }
    },
    { threshold: 0.5 }
  );

  io.observe(gallery);
});
