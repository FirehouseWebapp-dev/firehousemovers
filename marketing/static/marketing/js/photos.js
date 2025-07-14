document.addEventListener("DOMContentLoaded", () => {
  // ── ELEMENTS ─────────────────────────────
  const video       = document.getElementById("video");
  const snapBtn     = document.getElementById("snap");
  const flash       = document.getElementById("flash");
  const previews    = document.getElementById("previews");
  const fileInput   = document.getElementById("id_photos");
  const addFilesBtn = document.getElementById("add-files-btn");

  // ── CAMERA + PREVIEWS (unchanged) ────────
  let dt = new DataTransfer();
  navigator.mediaDevices
    .getUserMedia({ video: { facingMode: "environment" } })
    .then(stream => video.srcObject = stream)
    .catch(console.error);

  function createPreview(file) {
    const wrap = document.createElement("div");
    wrap.className = "preview-item";
    const img = document.createElement("img");
    img.src = URL.createObjectURL(file);
    wrap.appendChild(img);
    const btn = document.createElement("button");
    btn.type        = "button";
    btn.className   = "remove-btn";
    btn.textContent = "×";
    wrap.appendChild(btn);
    btn.addEventListener("click", () => {
      const newDt = new DataTransfer();
      Array.from(dt.files)
           .filter(f => f.name !== file.name || f.lastModified !== file.lastModified)
           .forEach(f => newDt.items.add(f));
      dt = newDt;
      fileInput.files = dt.files;
      wrap.remove();
    });
    return wrap;
  }

  snapBtn.addEventListener("click", () => {
    flash.style.opacity = 1;
    setTimeout(() => flash.style.opacity = 0, 200);
    const canvas = document.createElement("canvas");
    canvas.width  = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    canvas.toBlob(blob => {
      const file = new File([blob], `mkt_${Date.now()}.jpg`, { type:"image/jpeg" });
      dt.items.add(file);
      fileInput.files = dt.files;
      previews.appendChild(createPreview(file));
    }, "image/jpeg", 0.9);
  });

  addFilesBtn.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", e => {
    Array.from(e.target.files).forEach(f => {
      dt.items.add(f);
      previews.appendChild(createPreview(f));
    });
    fileInput.files = dt.files;
  });

  // ── CAROUSEL SETUP ────────────────────────
  const carousel = document.querySelector(".carousel");
  const card     = carousel.querySelector(".carousel-card");
  const style    = getComputedStyle(carousel);
  const gap      = parseFloat(style.gap) || 0;
  const cardW    = card.getBoundingClientRect().width + gap;

  let lastWheel = 0, lastTouch = 0, startY = 0;

  // MOUSE WHEEL → half‐card jump
  carousel.addEventListener("wheel", e => {
    e.preventDefault();
    const now = Date.now();
    if (now - lastWheel < 300) return;
    lastWheel = now;
    const dir = e.deltaY > 0 ? 1 : -1;
    carousel.scrollBy({ left: dir * (cardW/2), behavior: "smooth" });
  }, { passive: false });

  // TOUCH SWIPE → half‐card jump
  carousel.addEventListener("touchstart", e => {
    startY = e.touches[0].clientY;
  }, { passive: true });

  carousel.addEventListener("touchmove", e => {
    e.preventDefault();
    const now = Date.now();
    if (now - lastTouch < 300) return;
    const y = e.touches[0].clientY;
    const dY = startY - y;
    if (Math.abs(dY) < 20) return;
    lastTouch = now;
    const dir = dY > 0 ? 1 : -1;
    carousel.scrollBy({ left: dir * (cardW/2), behavior: "smooth" });
    startY = y;
  }, { passive: false });

  // ── MODAL PREVIEW ─────────────────────────
  const modal    = document.getElementById("modal");
  const modalImg = document.getElementById("modal-img");
  document.querySelectorAll(".carousel-card img")
    .forEach(img => img.addEventListener("click", () => {
      modalImg.src = img.src;
      modal.classList.add("active");
    }));
  modal.addEventListener("click", () => modal.classList.remove("active"));
});
