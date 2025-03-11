document.addEventListener("DOMContentLoaded", function () {
    const fetchButton = document.querySelector("button");
    const progressContainer = document.getElementById("progress-container");
    const progressBar = document.getElementById("progress");
    const resultContainer = document.getElementById("result");
    const videoTitle = document.getElementById("videoTitle");
    const thumbnail = document.getElementById("thumbnail");
    const resolutionSelect = document.getElementById("resolutionSelect");

    fetchButton.addEventListener("click", async function () {
        const videoUrl = document.getElementById("videoUrl").value.trim();
        if (!videoUrl) {
            alert("⚠️ Please enter a YouTube URL!");
            return;
        }

        progressContainer.classList.remove("hidden");
        progressBar.style.width = "80%";

        try {
            const response = await fetch("http://127.0.0.1:5000/fetch_video", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: videoUrl })
            });

            const data = await response.json();
            progressBar.style.width = "100%";

            if (data.error) {
                alert("❌ Error: " + data.error);
                progressContainer.classList.add("hidden");
                return;
            }

            videoTitle.textContent = data.title;
            thumbnail.src = data.thumbnail;
            resolutionSelect.innerHTML = "";

            if ((!data.resolutions || data.resolutions.length === 0) && (!data.audio_formats || data.audio_formats.length === 0)) {
                alert("❌ No valid formats found.");
                progressContainer.classList.add("hidden");
                return;
            }

            // ✅ Video Formats (480p, 720p, 1080p & Sound Ones)
            data.resolutions.forEach(format => {
                const option = document.createElement("option");
                option.value = format.url;
                option.textContent = `${format.resolution} (${format.ext})`;
                resolutionSelect.appendChild(option);
            });

            // ✅ M4A Audio Format (If Available)
            if (data.audio_formats && data.audio_formats.length > 0) {
                data.audio_formats.forEach(audio => {
                    const option = document.createElement("option");
                    option.value = audio.url;
                    option.textContent = `Audio 🔊 (M4A)`;
                    resolutionSelect.appendChild(option);
                });
            }

            resultContainer.classList.remove("hidden");
        } catch (error) {
            alert("❌ Server error: " + error.message);
        }
    });
});

function downloadVideo() {
    const selectedUrl = document.getElementById("resolutionSelect").value;
    if (selectedUrl) {
        window.location.href = selectedUrl;
    } else {
        alert("⚠️ Please select a resolution first!");
    } 
}
