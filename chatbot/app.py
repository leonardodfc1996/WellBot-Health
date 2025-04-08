from flask import Flask, request, json
import hashlib

app = Flask(__name__)

VERIFY_TOKEN = "wellbot123"

with open('professionals.json') as f:
    professionals = json.load(f)

def generate_secure_link(name, phone):
    ref_code = hashlib.md5(f"{name}{phone}".encode()).hexdigest()[:8]
    return f"https://wellbot.com/agendar?ref={ref_code}"

@app.route("/whatsapp", methods=["GET", "POST"])
def whatsapp():
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge
        return "Token inválido", 403

    user_msg = request.form.get("Body", "").lower().strip()

    if any(word in user_msg for word in ["gracias", "adios", "chao"]):
        return "Gracias por contactarnos. Recibirás los datos de contacto al completar el formulario."

    if user_msg in ["hola", "menu", "inicio"]:
        return (
            "¡Hola! 👋 Bienvenido a WellBot. Estoy aquí para ayudarte a agendar con un especialista.\n\n"
            "Por favor elige una opción:\n\n"
            "1. Dolor o molestias\n"
            "2. Limpieza dental\n"
            "3. Otro procedimiento\n\n"
            "Ejemplo: escribe '1' o describe tu síntoma"
        )

    if any(kw in user_msg for kw in ["duele", "dolor", "molestia", "1"]):
        return show_professionals("extracción")
    elif any(kw in user_msg for kw in ["limpieza", "2"]):
        return show_professionals("limpieza")
    elif any(kw in user_msg for kw in ["otro", "3"]):
        return show_professionals("general")

    return (
        "Por favor selecciona:\n\n"
        "1. Dolor o molestias\n"
        "2. Limpieza dental\n"
        "3. Otro procedimiento\n\n"
        "O describe tu caso con tus palabras."
    )

def show_professionals(specialty):
    response = "Opciones para agendar:\n\n"
    for pro in professionals:
        specialties = [s.lower() for s in pro["specialties"]]
        if specialty == "general" or specialty.lower() in specialties:
            form_link = generate_secure_link(pro["name"], pro["contact"])
            response += (
                f"Profesional: {pro['name']}\n"
                f"Formulario: {form_link}\n"
                f"Ubicación: {pro['location']}\n"
                f"Especializado en: {', '.join(pro['specialties'])}\n\n"
            )
    
    if response == "Opciones para agendar:\n\n":
        return "Actualmente no hay especialistas disponibles para esta necesidad."
    
    return (
        f"{response}"
        "Instrucciones:\n"
        "1. Completa el formulario correspondiente\n"
        "2. Recibirás los datos de contacto directo vía correo/SMS\n"
        "3. Menciona el código de referencia en tu cita"
    )

if __name__ == "__main__":
    app.run(port=5000)
