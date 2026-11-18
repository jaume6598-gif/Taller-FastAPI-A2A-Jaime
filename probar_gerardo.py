
from agentes.gerardo.agente import crear_agente_gerardo

# Construir el agente
agente = crear_agente_gerardo()

# Enviar una consulta
respuesta = agente.invoke({
    "messages": [
        {
            "role": "user",
            "content": (
                "Consulta tus apuntes sobre criterios y "
                "recomienda una arquitectura tecnológica "
                "sencilla para controlar los vencimientos "
                "de productos perecibles en un minimarket."
            )
        }
    ]
})

# Mostrar la respuesta final
print("\nRESPUESTA DEL AGENTE GERARDO:\n")

contenido = respuesta["messages"][-1].content
if isinstance(contenido, str):
    print(contenido)
else:
    for bloque in contenido:
        if isinstance(bloque, dict) and bloque.get("type") == "text":
            print(bloque.get("text", ""))

# Comprobar las herramientas utilizadas
for mensaje in respuesta["messages"]:
    if mensaje.type == "tool":
        print("\nHERRAMIENTA UTILIZADA:", mensaje.name)
        print(mensaje.content)
