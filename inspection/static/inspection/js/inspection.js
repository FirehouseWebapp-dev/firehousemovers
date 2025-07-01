document.addEventListener("DOMContentLoaded", () => {
  const video     = document.getElementById("video");
  const snapBtn   = document.getElementById("snap");
  const previews  = document.getElementById("previews");
  const fileInput = document.getElementById("id_photos");
  const flash     = document.getElementById("flash");

  if (video && snapBtn) {
    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: "environment" } })
      .then(stream => { video.srcObject = stream; })
      .catch(err => console.error("Camera error:", err));

    snapBtn.addEventListener("click", () => {
      // flash effect
      flash.style.animation = "flash 0.3s ease-out";
      flash.addEventListener("animationend", () => flash.style.animation = "", { once: true });

      // grab frame
      const canvas = document.createElement("canvas");
      canvas.width  = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext("2d").drawImage(video, 0, 0);

      // to Blob → File
      canvas.toBlob(blob => {
        const timestamp = Date.now();
        const filename  = `inspection_${timestamp}.jpg`;
        const file      = new File([blob], filename, { type: "image/jpeg" });

        // update DataTransfer
        const dt = new DataTransfer();
        Array.from(fileInput.files).forEach(f => dt.items.add(f));
        dt.items.add(file);
        fileInput.files = dt.files;

        // create preview wrapper
        const wrapper = document.createElement("div");
        wrapper.className = "preview-item";
        wrapper.dataset.name = filename;      // use to identify file on delete

        // img element
        const img = document.createElement("img");
        img.src = URL.createObjectURL(blob);
        wrapper.appendChild(img);

        // delete button
        const btn = document.createElement("button");
        btn.className = "delete-btn";
        btn.innerText = "×";
        wrapper.appendChild(btn);

        // delete handler
        btn.addEventListener("click", () => {
          // rebuild DataTransfer without this file
          const newDt = new DataTransfer();
          Array.from(fileInput.files)
            .filter(f => f.name !== wrapper.dataset.name)
            .forEach(f => newDt.items.add(f));
          fileInput.files = newDt.files;

          // remove preview from DOM
          wrapper.remove();
        });

        previews.appendChild(wrapper);
      }, "image/jpeg", 0.9);
    });
  }
});

// ─── Progress‐bar Truck Animation ─────────────────────────
// ─── Animate progress fill & truck ─────────────────────────function updateProgressBar() {
// … your camera + star code above …

// ─── PROGRESS BAR + SLIDING TRUCK ────────────────────────────────────────
// … your camera + star logic above …

document.addEventListener("DOMContentLoaded", () => {
  const bar   = document.getElementById("progressBar");
  const truck = document.getElementById("truckIcon");
  const steps = bar ? parseInt(bar.dataset.steps, 10) : 0;
  const curr  = window.STEP_NUMBER || 1;
  if (!bar || !truck || steps < 2) return;

  // compute fill percentage
  const pct = ((curr - 1) / (steps - 1)) * 100;
  bar.style.setProperty("--percent", pct + "%");

  // helper to position the truck
  function position(step) {
    const targetPct = ((step - 1) / (steps - 1)) * 100;
    truck.style.left = targetPct + "%";
    let xform;
    if (step === 1)          xform = "translate(0, -100%)";
    else if (step === steps) xform = "translate(-100%, -100%)";
    else                     xform = "translate(-50%, -100%)";
    truck.style.transform = xform;
  }

  // slide from prev → current:
  const prev = curr > 1 ? curr - 1 : curr;
  // 1) snap to prev (no transition)
  truck.style.transition = "none";
  position(prev);

  // 2) on next frame, enable transition & move to curr
  requestAnimationFrame(() => {
    truck.style.transition = "left 0.5s ease-in-out, transform 0.5s ease-in-out";
    position(curr);
  });

  // hide only the current circle so the truck visually replaces it
  document.querySelectorAll(".progress-bar .step").forEach((li, idx) => {
    li.style.visibility = idx === curr - 1 ? "hidden" : "visible";
  });
});


document.addEventListener("DOMContentLoaded", () => {
  // … your existing capture & star-rating code …

  // finally: position the truck
  moveProgressCar(window.STEP_NUMBER);
  steps.forEach((li, idx) => {
    if (idx === window.STEP_NUMBER - 1) {
      li.style.visibility = "hidden";
    } else {
      li.style.visibility = "visible";
    }
  });
});
