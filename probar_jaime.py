
from agentes.jaime.agente import crear_agente_jaime

# Construir el agente
agente = crear_agente_jaime()

# Enviar una consulta
respuesta = agente.invoke({
    "messages": [
        {
            "role": "user",
            "content": (
                "Consulta tus apuntes sobre criterios y "
                "recomienda tres medidas para reducir las "
                "pérdidas por vencimiento de productos "
                "perecibles en un minimarket."
            )
        }
    ]
})

# Mostrar la respuesta final
print("\nRESPUESTA DEL AGENTE JAIME:\n")
print(respuesta["messages"][-1].content)

# Comprobar si utilizó alguna herramienta
for mensaje in respuesta["messages"]:
    if mensaje.type == "tool":
        print("\nHERRAMIENTA UTILIZADA:", mensaje.name)
        print(mensaje.content)
