from fastapi import FastAPI, File, UploadFile
from fastapi.responses import PlainTextResponse
from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
import io

app = FastAPI()
ocr = PaddleOCR(use_angle_cls=True, lang='en')

@app.post("/extract-captcha", response_class=PlainTextResponse, responses={200: {"content": {"text/plain": {}}}})
async def extract_captcha(file: UploadFile = File(...)):
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    image_np = np.array(image)

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
        return captchas[0]
    else:
        return "Can't found"
    
    
if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 10000))  
    uvicorn.run("main:app", host="0.0.0.0", port=port)


