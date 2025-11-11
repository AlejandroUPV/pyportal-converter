from fastapi import FastAPI, Request, Response
from PIL import Image
from io import BytesIO
import requests

app = FastAPI()

# ============================================================
# 1️⃣ CONVERTIR IMÁGENES A BMP PARA PYPORTAL
# ============================================================

@app.post("/convert")
async def convert_to_bmp(request: Request):
    """
    Recibe una imagen (PNG, JPG, etc.), la convierte a BMP 320x240 RGB
    y la devuelve lista para PyPortal.
    """
    data = await request.body()
    try:
        # Abre la imagen recibida
        img = Image.open(BytesIO(data)).convert("RGB")

        # Redimensiona al tamaño exacto de la pantalla PyPortal
        img = img.resize((320, 240))

        # Guarda en formato BMP real
        out = BytesIO()
        img.save(out, format="BMP")

        # Devuelve el contenido BMP binario
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

# ============================================================
# 2️⃣ PROXY HTTP → HTTPS (para PyPortal sin TLS)
# ============================================================

@app.get("/proxy")
def proxy_image(url: str):
    """
    Proxy HTTP simple que descarga una imagen HTTPS y la sirve sin TLS.
    Esto evita los errores de "ESP32 not responding" por certificados modernos.
    """
    try:
        # Descarga la imagen original desde Supabase (HTTPS)
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return Response(
                content=f"Error al obtener la imagen: {r.status_code}",
                media_type="text/plain",
                status_code=r.status_code
            )

        # Prepara el contenido con longitud fija
        content = r.content
        headers = {
            "Content-Type": r.headers.get("Content-Type", "image/bmp"),
            "Content-Length": str(len(content)),
            "Access-Control-Allow-Origin": "*"
        }

        # Devuelve el contenido como HTTP simple
        return Response(content=content, headers=headers)

    except Exception as e:
        return Response(
            content=f"Error en proxy: {e}",
            media_type="text/plain",
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )

# ============================================================
# 3️⃣ ENDPOINT RAÍZ (opcional)
# ============================================================

@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Servidor PyPortal Converter & Proxy activo 🚀",
        "endpoints": {
            "/convert": "POST - Convierte imagen a BMP",
            "/proxy?url=<https_url>": "GET - Sirve imagen HTTPS como HTTP sin TLS"
        }
    }
