"""
test_report.py
--------------
Simple tests for report_generator.py.

Run with:  python test_report.py
After it finishes, open the PDFs inside the `reports/` folder.
"""

from pathlib import Path

from PIL import Image, ImageDraw

from report_generator import generate_report

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = BASE_DIR / "sample_images"
SAMPLE_DIR.mkdir(exist_ok=True)

passed = 0
failed = 0


def make_sample_images():
    """Create small test images so you don't need to download anything."""
    # 1. A normal JPG (a simple "face" drawing, landscape shape)
    img = Image.new("RGB", (600, 400), (200, 220, 240))
    draw = ImageDraw.Draw(img)
    draw.ellipse((200, 60, 400, 340), fill=(240, 200, 170))
    draw.ellipse((255, 150, 285, 180), fill="black")
    draw.ellipse((315, 150, 345, 180), fill="black")
    draw.arc((250, 220, 350, 290), 20, 160, fill="black", width=4)
    img.save(SAMPLE_DIR / "test_face.jpg")

    # 2. A PNG with transparency (tall shape)
    png = Image.new("RGBA", (300, 500), (30, 120, 200, 180))
    png.save(SAMPLE_DIR / "test_transparent.png")

    # 3. A fake "image": a text file pretending to be a JPG
    (SAMPLE_DIR / "not_an_image.jpg").write_text("this is not an image")


def check_ok(name, **kwargs):
    """The report SHOULD be created."""
    global passed, failed
    try:
        path = generate_report(**kwargs)
        if Path(path).is_file() and Path(path).stat().st_size > 0:
            print(f"PASS  {name} -> {path}")
            passed += 1
        else:
            print(f"FAIL  {name}: file was not created")
            failed += 1
    except Exception as error:
        print(f"FAIL  {name}: unexpected error: {error}")
        failed += 1


def check_error(name, **kwargs):
    """The function SHOULD raise a ValueError."""
    global passed, failed
    try:
        generate_report(**kwargs)
        print(f"FAIL  {name}: expected a ValueError but none was raised")
        failed += 1
    except ValueError as error:
        print(f"PASS  {name} -> ValueError: {error}")
        passed += 1
    except Exception as error:
        print(f"FAIL  {name}: wrong error type: {error}")
        failed += 1


if __name__ == "__main__":
    make_sample_images()
    print("--- Reports that should be created ---")
    check_ok("Real + JPG image", prediction="Real", confidence=0.9876,
             image_path=SAMPLE_DIR / "test_face.jpg", model_name="CNN v1")
    check_ok("Fake + transparent PNG", prediction="fake", confidence=0.5,
             image_path=str(SAMPLE_DIR / "test_transparent.png"), model_name="EfficientNet")
    check_ok("No image given", prediction="Fake", confidence=0.7)
    check_ok("Missing image path", prediction="Real", confidence=0.8,
             image_path="does/not/exist.jpg")
    check_ok("File is not an image", prediction="Real", confidence=0.8,
             image_path=SAMPLE_DIR / "not_an_image.jpg")
    check_ok("Weird image_path type", prediction="Real", confidence=0.8, image_path=12345)
    check_ok("Special characters in model name", prediction="Fake", confidence=1,
             model_name="<b>Model & Co</b>")

    print("\n--- Bad inputs that should raise ValueError ---")
    check_error("Prediction is 'Maybe'", prediction="Maybe", confidence=0.5)
    check_error("Prediction is a number", prediction=1, confidence=0.5)
    check_error("Confidence above 1", prediction="Real", confidence=93)
    check_error("Confidence is negative", prediction="Real", confidence=-0.2)
    check_error("Confidence is text", prediction="Real", confidence="high")
    check_error("Confidence is None", prediction="Real", confidence=None)

    print(f"\nResult: {passed} passed, {failed} failed")
