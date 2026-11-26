const analyseBtn = document.getElementById("analyseBtn");
const imageInput = document.getElementById("imageInput");
const statusMessage = document.getElementById("statusMessage");
const resultSection = document.getElementById("resultSection");
const prediction = document.getElementById("prediction");
let reportUrl;

analyseBtn.addEventListener("click", analyseImage);

async function analyseImage() {
    const image = imageInput.files[0];

    // Make sure an image has been selected
    if (!image) {
        statusMessage.textContent = "Please upload an image first";
        return;
    }

    // Show the loading state
    analyseBtn.disabled = true;
    analyseBtn.textContent = "Analysing...";
    statusMessage.textContent = "Preparing image for analysis...";

    prediction.textContent = "Please wait while your image is analysed";

    resultSection.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

    try {
        // Send the image to the FastAPI backend
        const formData = new FormData();
        formData.append("image", image);

        const response = await fetch("/predict", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Unable to analyse the image. Please try again.");
        }

        const confidence = Number(response.headers.get("X-Confidence"));
        const resultLabel = response.headers.get("X-Prediction") || "Unknown";
        const report = await response.blob();
        if (reportUrl) URL.revokeObjectURL(reportUrl);
        reportUrl = URL.createObjectURL(report);

        prediction.textContent =
            `Prediction: ${resultLabel} | Confidence: ${
                (confidence * 100).toFixed(2)
            }%`;

        let reportLink = document.getElementById("reportDownload");
        if (!reportLink) {
            reportLink = document.createElement("a");
            reportLink.id = "reportDownload";
            reportLink.textContent = "Download PDF report";
            resultSection.appendChild(reportLink);
        }
        reportLink.href = reportUrl;
        reportLink.download = "deepfake_detection_report.pdf";

        statusMessage.textContent = "Analysis completed successfully";

    } catch (error) {
        console.error("Analysis error:", error);

        prediction.textContent =
            "Analysis could not be completed.";

        statusMessage.textContent = error.message ||
            "Could not connect to the AI server. Please check that the backend is running";
    } finally {
        analyseBtn.disabled = false;
        analyseBtn.innerHTML = 'Analyse image <span>→</span>';
    }
}
