Necesitamos dos cosas menajear un check si queremos que se active el grounding para que busque info en linea, importante notar que aca no podemos recibir datos estructurados en el schema.


Neceistamos una forma de manejar las respuestas NO-GROUNDING donde al final de la respuesta general, se nos muestren en unos code snippets, ya sea con código o comandos con un boton de copiar para que podamos copiarlos conveneintemente.


    # To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""como puedo buscar en mi pc en linux, las carpetas que se llamen augment o tengan esa palabra en su nombre?"""),
            ],
        ),
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(text="""{\"suggested_code_snippets\":[],\"suggested_comands\":[\"find / -type d -name \\\"*augment*\\\" 2>/dev/null\"],\"general__answer\":\"Puedes usar el comando \\\"find\\\" en la terminal para buscar carpetas. La opción \\\"-type d\\\" especifica que estás buscando directorios (carpetas), y \\\"-name \\\"*augment*\\\"\\\" busca nombres que contengan la palabra \\\"augment\\\". \\\"2>/dev/null\\\" redirige los errores para que no se muestren.\"}"""),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=0,
        ),
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["suggested_comands", "suggested_code_snippets"],
            properties = {
                "general__answer": genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
                "suggested_comands": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.STRING,
                    ),
                ),
                "suggested_code_snippets": genai.types.Schema(
                    type = genai.types.Type.ARRAY,
                    items = genai.types.Schema(
                        type = genai.types.Type.STRING,
                    ),
                ),
            },
        ),
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()






# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""crees que haya fichajes para el barcelona?"""),
            ],
        ),
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(text="""Sí, es muy probable que haya fichajes en el Barcelona. El club suele ser un actor importante en el mercado de transferencias, buscando reforzar su plantilla constantemente.

Aquí te presento un resumen de las altas y rumores más recientes para el Barcelona de cara a la temporada 2025/2026:

**Altas Confirmadas:**

*   **Joan García:** El Barcelona comunicó la contratación de Joan García el 18 de junio, abonando su cláusula de rescisión de 25 millones de euros y firmándolo hasta 2031.
*   **Roony Bardghji:** El 14 de julio, el club anunció el fichaje de Roony Bardghji, extremo sueco de 19 años proveniente del FC Copenhague, por 2 millones de euros.
*   **Dani Olmo:** Regresó al club como agente libre en enero de 2025 para reforzar el ataque.
*   **Pau Víctor:** El joven delantero también se sumó al primer equipo en enero de 2025.
*   **Wojciech Szczęsny:** El experimentado portero llegó a finales de 2024 sin coste de traspaso desde la Juventus, aunque su continuidad podría depender de la situación de Ter Stegen.

**Rumores y Posibles Fichajes:**

*   **Marcus Rashford:** A pesar de ser vinculado con la Juventus, Marcus Rashford está interesado en llegar al Barcelona, y el entrenador Hansi Flick ha dado el visto bueno para su incorporación. El Manchester United buscaría una cifra cercana a los 40 millones de euros por el jugador.
*   **Laterales izquierdos:** El Barcelona busca reforzar esta posición, con nombres como Álvaro Carreras (Benfica) y Hugo Bueno (Wolverhampton) en la mira.
*   **Nico Williams:** Aunque fue un objetivo el pasado verano, Nico Williams finalmente renovó su contrato con el Athletic Club hasta 2035, aumentando su cláusula de rescisión a 90 millones de euros, lo que dificulta su fichaje. A pesar de esto, su agente se reunió con Deco, el director de fútbol del Barcelona.
*   **Otros nombres en seguimiento:** El Barça sigue a jugadores como Nusa, Yildiz, Ben Seghir y Akliouche.
*   **Martín Zubimendi:** Se le ha rumoreado en relación con el club en mayo de 2025.

**Posibles Bajas/Salidas:**

*   **Marc-André Ter Stegen:** El guardameta no estaría en los planes de Hansi Flick y el Napoli ha mostrado interés, además de posibilidades en Arabia. Su salida podría estar en consideración, al menos hasta enero.
*   **Clément Lenglet:** Regresa de cesión del Atlético de Madrid, pero su futuro podría estar fuera del club, ya que se le ha vinculado con una rescisión o salida.
*   **Otros jugadores que vuelven de cesión:** Álex Valle (Como) y Oriol Romeu (Girona) también regresan de sus cesiones y su futuro en el club no está asegurado.
*   **Pablo Torre:** Se ha rumoreado su salida rumbo al Mallorca.
*   **Ronald Araújo:** A pesar de haber renovado, hubo interés de la Juventus en él anteriormente.

El mercado de fichajes de La Liga para la temporada 2025-2026 funciona del 1 de julio al 30 de agosto. Además, hubo una \"ventana de inscripción excepcional\" del 1 al 10 de junio para los equipos participantes del Mundial de Clubes."""),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config = types.ThinkingConfig(
            thinking_budget=0,
        ),
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()


memoria de la sesion, vamos a ir agregando los mensajes de ida y vuelta, a un array en memoria y lso añadiremos como contexto para que pueda ser conversacional, no importan los tokens, tenemos barra libre, pero habrá un boton que tenga una escoba que será limpiar contexto para que empecemos con otro tema.