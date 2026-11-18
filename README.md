
# Sistema Multiagente Jaime–Gerardo

## 1. Objetivo

Implementar un sistema de dos agentes de IA que colaboran
para proponer soluciones de gestión de vencimientos
de alimentos perecibles en un minimarket.

Proyecto desarrollado como parte del Taller de
Implementación de Agentes - Curso Agentic AI.

**Modalidad:** Servicio FastAPI con comunicación A2A.
**Entorno:** Ejecución local.
**Responsable:** Jaime Vidal.
**Base:** Agentes del Taller A2A, Grupo 3.

## 2. Arquitectura

Usuario (Swagger)
    |
    v
FastAPI (puerto 8000)
    |
    v
Agente Jaime (operaciones alimentarias)
    |
    | HTTP / Protocolo A2A
    v
Agente Gerardo (puerto 8001)
    |
    v
Respuesta conjunta al usuario

### Responsabilidades

- Jaime: define requisitos operacionales, inocuidad,
  trazabilidad y control de vencimientos.
- Gerardo: propone una solución tecnológica basada
  en los requisitos recibidos.

Ambos utilizan Gemini, LangChain y herramientas
locales de consulta de apuntes.

## 3. Requisitos

- Python 3.12
- Conexión a internet para utilizar Gemini
- API Key de Gemini válida
- Dependencias incluidas en requirements.txt

## 4. Instalación

Abrir PowerShell en la carpeta raíz del proyecto.

Instalar las dependencias:

    py -3.12 -m pip install -r requirements.txt

Copiar el archivo .env.example como .env.

Completar las variables:

    GOOGLE_API_KEY=CLAVE_PERSONAL
    MODELO=MODELO_GEMINI_DISPONIBLE
    APP_API_TOKEN=TOKEN_PRIVADO

Utilizar un modelo Gemini compatible y autorizado
para la cuenta de prueba.

El archivo .env contiene credenciales privadas.
Nunca debe publicarse en GitHub.

## 5. Ejecución local

### Terminal 1: servidor A2A Gerardo

    py -3.12 servidor_a2a.py

Servidor disponible en:

    http://127.0.0.1:8001

Agent Card:

    http://127.0.0.1:8001/.well-known/agent-card.json

### Terminal 2: FastAPI

    py -3.12 -m uvicorn main:app --host 127.0.0.1 --port 8000

Abrir en el navegador:

    http://127.0.0.1:8000/docs

## 6. Prueba funcional

En Swagger, utilizar POST /consultar.

Primero seleccionar Authorize e introducir
el valor de APP_API_TOKEN.

Ejemplo de solicitud:

    {
      "pregunta": "¿Cómo reducir las pérdidas por vencimiento de productos perecibles en un minimarket?"
    }

Resultado esperado:

- Jaime genera requisitos operacionales.
- Los requisitos se envían mediante A2A.
- Gerardo propone una solución tecnológica.
- FastAPI devuelve una respuesta JSON con ambos aportes.

La respuesta debe conservar los requisitos
transmitidos entre agentes.

## 7. Pruebas de seguridad

Operación: POST /prueba-acceso.

- Sin token: HTTP 401, acceso rechazado.
- Con token válido: HTTP 200, acceso autorizado.

La operación POST /consultar también requiere token.

No mostrar tokens en capturas ni registros compartidos.

## 8. Evidencias

Las pruebas deben documentarse con:

- Fecha y entorno LOCAL.
- Solicitud realizada.
- Resultado esperado y resultado obtenido.
- Capturas de Swagger y registros del servidor A2A.
- Pruebas de acceso autorizado y rechazado.
- Observaciones o limitaciones detectadas.

## 9. Detener el sistema

En cada terminal donde funciona un servidor,
presionar Ctrl + C.

## 10. Limitaciones conocidas

- Aplicación diseñada para ejecución local.
- Requiere conexión externa con Gemini.
- La comunicación A2A implementada es de Jaime
  hacia Gerardo; no existe diálogo autónomo continuo.
- El almacenamiento de tareas es temporal.
- Las recomendaciones del LLM requieren validación.
- No existe integración con inventarios reales.
- El servidor A2A de Gerardo no tiene autenticación
  propia y debe mantenerse accesible solo localmente.
- No está preparada para uso en producción.

## 11. Integrantes y aportes

- Jaime Vidal: adaptación de los agentes,
  integración, pruebas y documentación.
- Agentes originales: Grupo 3 del Taller A2A.

Completar la atribución de los demás autores
originales antes de entregar el proyecto.
