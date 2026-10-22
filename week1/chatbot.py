import os
from dotenv import load_dotenv
import anthropic

# Cargamos las variables del archivo .env (la API key)
load_dotenv()

# Inicializamos el cliente de Anthropic
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# -------------------------------------------------------
# CARGA DEL SYSTEM PROMPT DESDE ARCHIVO EXTERNO
# En producción el comportamiento del asistente se separa
# del código para que el equipo de negocio pueda editarlo
# sin tocar el código Python
# -------------------------------------------------------
def cargar_system_prompt():
    # Construimos la ruta al archivo de configuración
    ruta = os.path.join("config", "system_prompt.txt")
    # Abrimos y leemos el contenido del archivo
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()

# -------------------------------------------------------
# FUNCIÓN PRINCIPAL DEL CHATBOT
# -------------------------------------------------------
def chatbot():
    # Cargamos el system prompt al iniciar
    system_prompt = cargar_system_prompt()
    
    # El historial empieza vacío — aquí guardamos toda la conversación
    historial = []
    
    print("=" * 50)
    print("  HRBot — Asistente de Recursos Humanos")
    print("  Comandos: 'salir' para terminar")
    print("            'reset' para limpiar el historial")
    print("=" * 50)
    print()

    # Bucle principal — el chat sigue hasta que el usuario escriba 'salir'
    while True:
        # Capturamos el input del usuario
        user_input = input("Tú: ").strip()
        
        # Comando para salir
        if user_input.lower() == "salir":
            print("\nHRBot: ¡Hasta luego! Fue un placer ayudarte.")
            break
        
        # Comando para resetear el historial sin cerrar el chat
        if user_input.lower() == "reset":
            historial = []
            print("\nHRBot: Historial limpiado. Empezamos de nuevo.\n")
            continue
        
        # Si el usuario no escribió nada, ignoramos y volvemos al inicio
        if not user_input:
            continue
        
        # Añadimos el mensaje del usuario al historial
        historial.append({"role": "user", "content": user_input})
        
        print("\nHRBot: ", end="", flush=True)
        
        # Variables para contar tokens al final de cada respuesta
        respuesta_completa = ""
        input_tokens = 0
        output_tokens = 0
        
        # -------------------------------------------------------
        # LLAMADA A LA API CON STREAMING
        # Usamos streaming para que el texto aparezca progresivamente
        # igual que en Claude.ai o ChatGPT
        # -------------------------------------------------------
        with client.messages.stream(
            model="claude-haiku-4-5",
            max_tokens=300,
            system=system_prompt,      # personalidad cargada desde archivo
            messages=historial         # todo el historial para mantener contexto
        ) as stream:
            # Recibimos el texto fragmento a fragmento
            for text in stream.text_stream:
                print(text, end="", flush=True)
                respuesta_completa += text
            
            # Al finalizar el streaming obtenemos los datos de uso de tokens
            mensaje_final = stream.get_final_message()
            input_tokens = mensaje_final.usage.input_tokens
            output_tokens = mensaje_final.usage.output_tokens
        
        # Añadimos la respuesta completa de PyBot al historial
        historial.append({"role": "assistant", "content": respuesta_completa})
        
        # -------------------------------------------------------
        # RESUMEN DE TOKENS Y COSTE ESTIMADO
        # Haiku cuesta $0.00025 por 1000 tokens de entrada
        # y $0.00125 por 1000 tokens de salida
        # -------------------------------------------------------
        coste = (input_tokens * 0.00025 / 1000) + (output_tokens * 0.00125 / 1000)
        print(f"\n\n[Tokens — entrada: {input_tokens} | salida: {output_tokens} | coste: ${coste:.6f}]\n")

# Punto de entrada del programa
if __name__ == "__main__":
    chatbot()