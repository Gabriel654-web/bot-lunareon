from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Estou online! Pode fechar essa aba."

def run():
    # O SEGREDO ESTÁ AQUI: 
    # O Render exige host='0.0.0.0' e a porta pega do ambiente (os.environ)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
    
