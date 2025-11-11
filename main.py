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
# 2️⃣ PROXY HTTP → HTTPS (100 % compatible con PyPortal)
# ============================================================

@app.get("/proxy")
def proxy_image(url: str):
    """
    Proxy HTTP simple y 100 % compatible con PyPortal.
    Descarga una imagen HTTPS y la sirve como HTTP plano
    (sin gzip, sin keep-alive, sin chunked).
    """
    try:
        # Fuerza cabeceras simples en la petición al servidor origen
        headers = {
            "User-Agent": "PyPortalProxy/1.0",
            "Accept-Encoding": "identity",   # evita compresión gzip
            "Connection": "close"            # fuerza cierre inmediato
        }

        # Descarga la imagen original
        r = requests.get(url, headers=headers, timeout=15, stream=True)
        if r.status_code != 200:
            return Response(
                content=f"Error al obtener la imagen: {r.status_code}",
                media_type="text/plain",
                status_code=r.status_code
            )

        # Lee todo el contenido en memoria (sin chunked)
        content = r.content

        # Cabeceras limpias y compatibles con el ESP32-SPI
        resp_headers = {
            "Content-Type": "image/bmp",
            "Content-Length": str(len(content)),
            "Connection": "close",
            "Access-Control-Allow-Origin": "*"
        }

        return Response(content=content, headers=resp_headers)

    except Exception as e:
        return Response(
            content=f"Error en proxy: {e}",
            media_type="text/plain",
            status_code=500,
            headers={"Access-Control-Allow-Origin": "*"}
        )

# ============================================================
# 3️⃣ ENDPOINT RAÍZ (informativo)
# ============================================================

@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Servidor PyPortal Converter & Proxy activo 🚀",
        "endpoints": {
            "/convert": "POST → Convierte imagen a BMP 320x240",
            "/proxy?url=<https_url>": "GET → Sirve imagen HTTPS como HTTP sin TLS (PyPortal-safe)"
        }
    }
