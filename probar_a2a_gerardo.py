
import httpx
import json
import uuid

# 1. Descubrir al agente mediante su Agent Card
base = "http://127.0.0.1:8001"

with httpx.Client(timeout=120.0) as cliente:

    tarjeta = cliente.get(
        f"{base}/.well-known/agent-card.json"
    )
    tarjeta.raise_for_status()
    datos = tarjeta.json()

    print("AGENTE DESCUBIERTO:", datos["name"])

    url = next(
        i["url"] for i in datos["supportedInterfaces"]
        if i["protocolBinding"] == "JSONRPC"
    )

    # 2. Construir el mensaje A2A
    solicitud = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "SendMessage",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "ROLE_USER",
                "parts": [{
                    "text": (
                        "Gerardo, consulta tus apuntes y "
                        "recomienda una solución tecnológica "
                        "simple para gestionar vencimientos "
                        "de alimentos en un minimarket."
                    )
                }]
            }
        }
    }

    # 3. Enviar el mensaje mediante HTTP
    respuesta = cliente.post(
        url,
        json=solicitud,
        headers={"A2A-Version": "1.0"}
    )

    # 4. Mostrar el resultado
    print("\nESTADO HTTP:", respuesta.status_code)
    print("\nRESPUESTA A2A:")
    print(json.dumps(
        respuesta.json(),
        indent=2,
        ensure_ascii=False
    ))
