from fastapi import FastAPI, Request, Response
from PIL import Image
from io import BytesIO

app = FastAPI()

@app.post("/convert")
async def convert_to_bmp(request: Request):
    data = await request.body()
    try:
        img = Image.open(BytesIO(data)).convert("RGB")
        img = img.resize((320, 240))
        out = BytesIO()
        img.save(out, format="BMP")
        return Response(
            content=out.getvalue(),
            media_type="image/bmp",
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        return Response(
            content=str(e),
            media_type="text/plain",
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )
