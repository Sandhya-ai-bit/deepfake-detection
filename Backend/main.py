from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image as PILImage, UnidentifiedImageError

from report_generator import generate_report


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "Frontend"
UPLOADS_DIR = Path(__file__).resolve().parent / "uploads"
MAX_UPLOAD_SIZE = 10 * 1024 * 1024
IMAGE_SUFFIXES = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}

app = FastAPI()

app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")


def predict_image(image_path: Path) -> dict:
    """Placeholder prediction; replace this function with the model inference call."""
    return {
        "prediction": "Real",
        "confidence": 0.5,
        "model_name": "Prediction placeholder",
    }


@app.get("/", include_in_schema=False)
def homepage():
    return FileResponse(FRONTEND_DIR / "index.html", media_type="text/html")


@app.get('/health')
def health_check():
    return {"status": "healthy"}


@app.post("/predict")
async def predict(
    image: UploadFile = File(...),
    keep_image: bool = Form(False),
):
    contents = await image.read(MAX_UPLOAD_SIZE + 1)
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")
    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="The image must be 10 MB or smaller.")

    try:
        with PILImage.open(BytesIO(contents)) as uploaded_image:
            image_format = uploaded_image.format
            uploaded_image.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(status_code=415, detail="Upload a valid JPG, PNG, or WEBP image.")

    suffix = IMAGE_SUFFIXES.get(image_format)
    if suffix is None:
        raise HTTPException(status_code=415, detail="Upload a valid JPG, PNG, or WEBP image.")

    UPLOADS_DIR.mkdir(exist_ok=True)
    image_path = UPLOADS_DIR / f"{uuid4().hex}{suffix}"
    image_path.write_bytes(contents)

    try:
        result = predict_image(image_path)
        report_path = generate_report(
            prediction=result["prediction"],
            confidence=result["confidence"],
            image_path=image_path,
            model_name=result.get("model_name"),
        )
        return FileResponse(
            report_path,
            media_type="application/pdf",
            filename="deepfake_detection_report.pdf",
            headers={
                "X-Prediction": str(result["prediction"]),
                "X-Confidence": str(result["confidence"]),
                "X-Image-Retained": str(keep_image).lower(),
            },
        )
    finally:
        if not keep_image:
            image_path.unlink(missing_ok=True)






