
const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const fileName = document.getElementById("fileName");
const analyseBtn = document.getElementById("analyseBtn");
const removeBtn = document.getElementById("removeBtn");
const statusMessage = document.getElementById("statusMessage");

imageInput.addEventListener("change", function () {

    const file = imageInput.files[0];

    if (!file) return;

    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
        statusMessage.textContent = "Please upload a JPG, PNG or WEBP image.";
        imageInput.value = "";
        return;
    }

    fileName.textContent = file.name;

    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";

    analyseBtn.disabled = false;
    removeBtn.hidden = false;

    statusMessage.textContent = "Image selected successfully.";

});

removeBtn.addEventListener("click", function () {

    imageInput.value = "";
    preview.src = "";
    preview.style.display = "none";

    fileName.textContent = "No image selected";

    analyseBtn.disabled = true;
    removeBtn.hidden = true;

    statusMessage.textContent = "";

});
