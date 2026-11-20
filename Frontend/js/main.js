
const analyseBtn = document.getElementById("analyseBtn");
const imageInput = document.getElementById("imageInput");
const statusMessage = document.getElementById("statusMessage");
const resultSection = document.getElementById("resultSection");
const prediction = document.getElementById("prediction");

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
        // Send the image to the Flask backend
        const formData = new FormData();
        formData.append("image", image);

        const response = await fetch("/predict", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Unable to analyse the image. Please try again.");
        }

        const result = await response.json();

        // Display the actual model prediction
        prediction.textContent =
            `Prediction: ${result.prediction} | Confidence: ${
                (Number(result.confidence) * 100).toFixed(2)
            }%`;

        statusMessage.textContent = "Analysis completed successfully";

    } catch (error) {
        console.error("Analysis error:", error);

        prediction.textContent =
            "Analysis could not be completed.";

        statusMessage.textContent =
            "Could not connect to the AI server. Please check that the backend is running";
    } finally {
        analyseBtn.disabled = false;
        analyseBtn.innerHTML = 'Analyse image <span>→</span>';
    }
}
