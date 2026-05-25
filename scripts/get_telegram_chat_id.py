import httpx
import asyncio
import sys

async def main():
    token = input("Ingresa el TOKEN de tu Bot de Telegram: ").strip()
    if not token:
        print("El token es requerido.")
        return

    url = f"https://api.telegram.org/bot{token}/getUpdates"
    print("\n--- 📝 Instrucciones ---")
    print("1. Abre Telegram y busca tu bot.")
    print("2. Presiona /start o envíale cualquier mensaje.")
    print("3. Una vez lo hayas hecho, presiona ENTER aquí.")
    input("\nPresiona ENTER cuando hayas enviado el mensaje...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
            if not data.get("ok"):
                print(f"Error: {data.get('description')}")
                return
            
            results = data.get("result", [])
            if not results:
                print("No se encontraron mensajes. Asegúrate de haberle escrito al bot recientemente.")
                return
            
            # Obtener el chat_id del último mensaje
            last_msg = results[-1]
            chat_id = last_msg.get("message", {}).get("chat", {}).get("id")
            first_name = last_msg.get("message", {}).get("chat", {}).get("first_name", "María")
            
            print("\n" + "═"*40)
            print(f"✨ ¡ÉXITO! Hola {first_name}")
            print(f"Tu CHAT_ID es: {chat_id}")
            print("═"*40)
            print("\nAhora copia estos valores en tu archivo .env del backend:")
            print(f"TELEGRAM_BOT_TOKEN={token}")
            print(f"TELEGRAM_CHAT_ID={chat_id}")
            
    except Exception as e:
        print(f"Error conectando con Telegram: {e}")

if __name__ == "__main__":
    asyncio.run(main())
