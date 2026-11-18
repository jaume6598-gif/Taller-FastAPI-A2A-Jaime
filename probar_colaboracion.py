

import uuid
import httpx
from agentes.jaime.agente import crear_agente_jaime


def extraer_texto(contenido):
    if isinstance(contenido, str):
        return contenido
    return "\n".join(
        b.get("text", "")
        for b in contenido
        if isinstance(b, dict) and b.get("type") == "text"
    )


# 1. Jaime analiza el problema
jaime = crear_agente_jaime()

resultado = jaime.invoke({
    "messages": [{
        "role": "user",
        "content": (
            "Consulta tus apuntes y define tres requisitos "
            "operacionales para reducir vencimientos en un "
            "minimarket. Sé breve y no inventes cifras."
        )
    }]
})


# 2. DIAGNÓSTICO: trazabilidad del agente Jaime
print("\n=== TRAZABILIDAD JAIME ===")

herramientas_ejecutadas = 0

for numero, mensaje in enumerate(resultado["messages"], 1):

    print(f"\nPaso {numero}: {mensaje.type}")

    if mensaje.type == "ai":
        for llamada in getattr(mensaje, "tool_calls", []):
            print("Herramienta solicitada:", llamada["name"])
            print("Argumentos:", llamada["args"])

    if mensaje.type == "tool":
        herramientas_ejecutadas += 1
        print("Herramienta ejecutada:", mensaje.name)
        print("Información recuperada:", mensaje.content)

print("\nTotal herramientas ejecutadas:", herramientas_ejecutadas)


# 3. Recuperar los requisitos elaborados por Jaime
requisitos = extraer_texto(
    resultado["messages"][-1].content
)

print("\n=== JAIME: REQUISITOS ===\n")
print(requisitos)


# 4. Descubrir a Gerardo mediante A2A
with httpx.Client(timeout=120.0) as cliente:

    tarjeta = cliente.get(
        "http://127.0.0.1:8001/.well-known/agent-card.json"
    )
    tarjeta.raise_for_status()

    url = next(
        i["url"]
        for i in tarjeta.json()["supportedInterfaces"]
        if i["protocolBinding"] == "JSONRPC"
    )

    mensaje = (
        "Soy el agente Jaime. He definido estos requisitos "
        "operacionales:\n" + requisitos +
        "\nPropón una solución tecnológica sencilla "
        "que los considere. Máximo 8 líneas, sin código."
    )

    print("\n=== MENSAJE A2A ENVIADO ===\n")
    print(mensaje)

    solicitud = {
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

    respuesta = cliente.post(
        url,
        json=solicitud,
        headers={"A2A-Version": "1.0"}
    )
    respuesta.raise_for_status()

    datos = respuesta.json()

    if "error" in datos:
        raise RuntimeError(datos["error"])

    partes = datos["result"]["message"]["parts"]

    texto_gerardo = "\n".join(
        p.get("text", "") for p in partes
    )

    print("\n=== GERARDO: RESPUESTA A2A ===\n")
    print(texto_gerardo)
