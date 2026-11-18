
import os
import uuid
import secrets
import httpx

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from functools import lru_cache

from agentes.jaime.agente import crear_agente_jaime


# ==========================================
# 1. CONFIGURACION Y SEGURIDAD
# ==========================================

load_dotenv()

TOKEN_ESPERADO = os.getenv("APP_API_TOKEN")

if not TOKEN_ESPERADO or TOKEN_ESPERADO == "TU_TOKEN_PRIVADO":
    raise RuntimeError("Configura APP_API_TOKEN en .env")

app = FastAPI(
    title="Sistema de Agentes Jaime-Gerardo",
    version="1.0.0"
)

cabecera_token = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)


def verificar_acceso(
    token: str | None = Depends(cabecera_token)
):
    if not token or not secrets.compare_digest(
        token, TOKEN_ESPERADO
    ):
        raise HTTPException(
            status_code=401,
            detail="Acceso no autorizado"
        )


# ==========================================
# 2. MODELO DE CONSULTA
# ==========================================

class Consulta(BaseModel):
    pregunta: str = Field(min_length=5, max_length=2000)


def extraer_texto(contenido):
    if isinstance(contenido, str):
        return contenido

    if isinstance(contenido, list):
        return "\n".join(
            bloque.get("text", "")
            for bloque in contenido
            if isinstance(bloque, dict)
            and bloque.get("type") == "text"
        )

    return ""


@lru_cache(maxsize=1)
def obtener_jaime():
    return crear_agente_jaime()


# ==========================================
# 3. COMPROBACIONES BASICAS
# ==========================================

@app.get("/salud")
def comprobar_salud():
    return {"estado": "funcionando"}


@app.post("/prueba-acceso")
def probar_acceso(
    consulta: Consulta,
    autorizado=Depends(verificar_acceso)
):
    return {
        "acceso": "autorizado",
        "pregunta_recibida": consulta.pregunta
    }


# ==========================================
# 4. CONSULTAR SISTEMA DE AGENTES
# ==========================================

@app.post("/consultar")
async def consultar_agentes(
    consulta: Consulta,
    autorizado=Depends(verificar_acceso)
):

    pregunta = consulta.pregunta.strip()

    if len(pregunta) < 5:
        raise HTTPException(
            status_code=422,
            detail="La pregunta es demasiado corta"
        )

    # PASO 1: JAIME ANALIZA LA CONSULTA

    agente_jaime = obtener_jaime()

    try:
        resultado = await agente_jaime.ainvoke({
            "messages": [{
                "role": "user",
                "content": (
                    "Consulta tus apuntes y analiza esta "
                    "solicitud desde tu especialidad "
                    "en operaciones alimentarias. "
                    "Define tres requisitos operacionales "
                    "relevantes. No inventes cifras. "
                    "Si faltan datos, indicalo.\n\n"
                    f"Solicitud: {pregunta}"
                )
            }]
        })
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="El agente Jaime no pudo procesar la consulta"
        )

    requisitos = extraer_texto(
        resultado["messages"][-1].content
    )

    if not requisitos.strip():
        raise HTTPException(
            status_code=502,
            detail="Jaime no entrego requisitos"
        )

    herramientas_jaime = [
        mensaje.name
        for mensaje in resultado["messages"]
        if mensaje.type == "tool"
    ]

    # PASO 2: DESCUBRIR A GERARDO

    try:
        async with httpx.AsyncClient(timeout=180.0) as cliente:

            tarjeta = await cliente.get(
                "http://127.0.0.1:8001/.well-known/agent-card.json"
            )

            tarjeta.raise_for_status()

            datos_tarjeta = tarjeta.json()

            url = next(
                interfaz["url"]
                for interfaz in datos_tarjeta["supportedInterfaces"]
                if interfaz["protocolBinding"] == "JSONRPC"
            )

            # PASO 3: ENVIAR MENSAJE A2A

            mensaje = (
                "Soy el agente Jaime. "
                "Estos son los requisitos operacionales "
                "identificados para la solicitud del usuario:\n\n"
                f"{requisitos}\n\n"
                "Propón una solución tecnológica sencilla "
                "basada en estos requisitos. "
                "Distingue los supuestos no validados. "
                "Responde brevemente y sin codigo."
            )

            solicitud_a2a = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "SendMessage",
                "params": {
                    "message": {
                        "messageId": str(uuid.uuid4()),
                        "role": "ROLE_USER",
                        "parts": [{"text": mensaje}]
                    }
                }
            }

            respuesta = await cliente.post(
                url,
                json=solicitud_a2a,
                headers={"A2A-Version": "1.0"}
            )

            respuesta.raise_for_status()
            datos = respuesta.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Tiempo de espera agotado al consultar Gerardo"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="No se pudo conectar con Gerardo"
        )

    except (httpx.HTTPStatusError, KeyError, StopIteration, ValueError):
        raise HTTPException(
            status_code=502,
            detail="Error al comunicarse con el servidor A2A"
        )

    # PASO 4: PROCESAR LA RESPUESTA A2A

    if "error" in datos:
        raise HTTPException(
            status_code=502,
            detail="Gerardo devolvio un error A2A"
        )

    try:
        partes = datos["result"]["message"]["parts"]

        respuesta_gerardo = "\n".join(
            parte.get("text", "")
            for parte in partes
            if isinstance(parte, dict)
        )

    except (KeyError, TypeError):
        raise HTTPException(
            status_code=502,
            detail="La respuesta A2A no tiene el formato esperado"
        )

    if not respuesta_gerardo.strip():
        raise HTTPException(
            status_code=502,
            detail="Gerardo devolvio una respuesta vacia"
        )

    # PASO 5: DEVOLVER RESULTADO A FASTAPI

    return {
        "estado": "completado",
        "pregunta": pregunta,
        "requisitos_jaime": requisitos,
        "herramientas_jaime": herramientas_jaime,
        "respuesta_gerardo": respuesta_gerardo,
        "comunicacion": "A2A"
    }
