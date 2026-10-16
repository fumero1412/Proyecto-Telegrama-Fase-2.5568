from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio, threading, os, json
from flask import Flask

API_ID = 32695956
API_HASH = '8d939c8130ea03c01cd9abe6a6e83d7a'
GRUPO = -1003764262854
TOPIC = 717696
CANAL = 'https://t.me/Horny_J'

# Render te pasa la sesion por variable, no por archivo .session
SESSION = os.environ.get("SESSION_STRING")
PROGRESS = "progreso.json"

app = Flask(name)
@app.route('/')
def home(): return "Bot vivo"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000))), daemon=True).start()

def cargar():
    if os.path.exists(PROGRESS):
        try:
            with open(PROGRESS) as f:
                return json.load(f).get("last_id", 0)
        except: return 0
    return 0

def guardar(last_id):
    # Guardado atomico, si se cae escribiendo no se rompe
    with open(PROGRESS+".tmp","w") as f:
        json.dump({"last_id": last_id}, f)
    os.replace(PROGRESS+".tmp", PROGRESS)

async def main():
    last_id = cargar()
    print(f"ARRANCO DESDE ID: {last_id}")
    client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
    await client.start()
    print("CLIENTE CONECTADO OK")
    o = await client.get_entity(CANAL)
    d = await client.get_entity(GRUPO)

    while True:
        try:
            # Ahora si, desde last_id, en orden viejo -> nuevo
            async for m in client.iter_messages(o, min_id=last_id, reverse=True):
                if not (m.media or (m.text or "").startswith("https://telegra.ph")):
                    # Aunque lo saltemos por filtro, avanzamos para no atorarnos
                    last_id = m.id
                    guardar(last_id)
                    continue
                try:
                    if m.media: await client.send_file(d, m.media, caption=m.text, reply_to=TOPIC)
                    else: await client.send_message(d, m.text, reply_to=TOPIC)
                    print(f"Copiado {m.id}")
                    last_id = m.id
                    guardar(last_id) # Guarda AL INSTANTE
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"Error en {m.id}: {e} - reintento mismo mensaje en 5s")
                    await asyncio.sleep(5)
                    continue
            print("HISTORIAL LISTO - EN VIVO, espero 60s")
            break
        except Exception as e:
            print(f"SE CAYO: {e} - Reintento en 10s desde {last_id}")
            await asyncio.sleep(10)

    @client.on(events.NewMessage(chats=CANAL))
    async def h(e):
        if not (e.message.media or (e.message.text or "").startswith("https://telegra.ph")): return
        if e.message.media: await client.send_file(d, e.message.media, caption=e.message.text, reply_to=TOPIC)
        else: await client.send_message(d, e.message.text, reply_to=TOPIC)
        guardar(e.message.id)

    await client.run_until_disconnected()

asyncio.run(main())