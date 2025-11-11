from fastapi import FastAPI, Request, Response
from PIL import Image
from io import BytesIO
import requests

app = FastAPI()

# --- 1️⃣ Endpoint para convertir imágenes a BMP ---
@app.post("/convert")
async def convert_to_bmp(request: Request):
    data = await request.body()
    try:
        # Abre la imagen recibida (PNG, JPG, etc.)
        img = Image.open(BytesIO(data)).convert("RGB")

        # Redimensiona a 320x240 (tamaño de PyPortal)
        img = img.resize((320, 240))

        # Guarda en formato BMP real
        out = BytesIO()
        img.save(out, format="BMP")

        # Devuelve contenido BMP binario
        return Response(
            content=out.getvalue(),
            media_type="image/bmp",
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        return Response(
            content=f"Error en conversión: {e}",
            media_type="text/plain",
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )


# --- 2️⃣ Endpoint proxy para servir imágenes sin HTTPS (PyPortal seguro) ---
@app.get("/proxy")
def proxy_image(url: str):
    """
    Endpoint que actúa como proxy HTTP → HTTPS
    Ejemplo:
      http://pyportal-converter.onrender.com/proxy?url=https://...supabase.co/...bmp
    """
    try:
        # Descarga la imagen original desde la URL HTTPS (Supabase)
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return Response(
                content=f"Error al obtener la imagen: {r.status_code}",
                media_type="text/plain",
                status_code=r.status_code
            )

        # Devuelve la imagen sin modificar, como HTTP simple
        return Response(
            content=r.content,
            media_type=r.headers.get("Content-Type", "image/bmp"),
            headers={"Access-Control-Allow-Origin": "*"}
        )

    except Exception as e:
        return Response(
            content=f"Error en proxy: {e}",
            media_type="text/plain",
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )
