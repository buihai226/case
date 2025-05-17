from fastapi import FastAPI, File, UploadFile
from fastapi.responses import PlainTextResponse
from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
import io
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/extract-captcha", response_class=PlainTextResponse, responses={200: {"content": {"text/plain": {}}}})
async def extract_captcha(file: UploadFile = File(...)):
    try:
        logger.info("Initializing PaddleOCR")
        ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Khởi tạo PaddleOCR trong endpoint
        logger.info("PaddleOCR initialized successfully")

        logger.info("Reading and processing image")
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        image_np = np.array(image)

        logger.info("Running OCR on image")
        result = ocr.ocr(image_np, cls=True)

        serial_y = None
        captcha_y = None
        captchas = []

        for line in result[0]:
            box, (text, conf) = line
            y_center = sum([pt[1] for pt in box]) / 4
            if "Serial" in text:
                serial_y = y_center
            elif "captcha" in text.lower():
                captcha_y = y_center

        if serial_y and captcha_y:
            min_y, max_y = sorted([serial_y, captcha_y])
            for line in result[0]:
                box, (text, conf) = line
                y_center = sum([pt[1] for pt in box]) / 4
                if min_y < y_center < max_y and text.lower() not in ["serial", "captcha"]:
                    captchas.append(text)

        if captchas:
            logger.info(f"Captcha found: {captchas[0]}")
            return captchas[0]
        else:
            logger.info("No captcha found")
            return "Can't found"
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Running on port {port}")  # Sử dụng logger 
    uvicorn.run("main:app", host="0.0.0.0", port=port)