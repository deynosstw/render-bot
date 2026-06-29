import requests, os, time, threading
from flask import Flask
os.environ.pop('HTTP_PROXY',None); os.environ.pop('HTTPS_PROXY',None)
TOKEN = "8813377784:AAE2y6iklo_HhCyBhzZEs7nPJ-aIGC1ZkGg"
ses = requests.Session()
app = Flask(__name__)
ultimo = 0; archivos = {}

def enviar(c,t,b=None):
    for i in range(3):
        try:
            d={"chat_id":c,"text":t[:4000]}
            if b: d["reply_markup"]={"inline_keyboard":b}
            r=ses.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json=d,timeout=10)
            if r.ok: return
        except:
            if i<2: time.sleep(0.5)

def groq(p):
    try:
        r=ses.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":"Bearer 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"},
            json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":p}],"max_tokens":2000})
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e: return f"Error: {e}"

def leer_archivo(fid):
    try:
        f=ses.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={fid}")
        fp=f.json()["result"]["file_path"]
        r=ses.get(f"https://api.telegram.org/file/bot{TOKEN}/{fp}")
        return r.text[:3000]
    except: return ""

def poll():
    global ultimo
    ses.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    while True:
        try:
            r=ses.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates",params={"offset":ultimo+1,"timeout":30},timeout=35)
            if r.ok:
                for x in r.json().get("result",[]):
                    ultimo=x["update_id"]
                    
                    if "callback_query" in x:
                        q=x["callback_query"]; c=q["message"]["chat"]["id"]; d=q["data"]; fid=archivos.get(c)
                        if d=="ver": enviar(c,groq(f"Analiza:\n{leer_archivo(fid)}"))
                        elif d=="resumir": enviar(c,groq(f"Resume:\n{leer_archivo(fid)}"))
                        elif d=="datos": enviar(c,groq(f"Rellena con: Nombre Julian, Ficha 3410233, CC 1104934197, Cel 3134756579\n{leer_archivo(fid)}"))
                        elif d=="bajar":
                            f=ses.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={fid}")
                            fp=f.json()["result"]["file_path"]
                            r=ses.get(f"https://api.telegram.org/file/bot{TOKEN}/{fp}")
                            ses.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument",data={"chat_id":c},files={"document":(archivos.get(f"{c}_n","a.txt"),r.content)})
                        elif d=="pc": enviar(c,"Enciende el PC para ver archivos.")
                        ses.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",json={"callback_query_id":q["id"]})
                        continue
                    
                    if "message" not in x: continue
                    c=x["message"]["chat"]["id"]
                    
                    if "document" in x["message"]:
                        d=x["message"]["document"]; fid=d["file_id"]
                        archivos[c]=fid; archivos[f"{c}_n"]=d.get("file_name","a.txt")
                        enviar(c,f"Archivo: {d.get('file_name','')}",[
                            [{"text":"📖 Revisar","callback_data":"ver"},{"text":"📝 Resumir","callback_data":"resumir"}],
                            [{"text":"📲 Descargar","callback_data":"bajar"},{"text":"📋 Rellenar","callback_data":"datos"}],
                            [{"text":"💻 PC","callback_data":"pc"}]])
                        continue
                    
                    t=x["message"].get("text","")
                    if not t: continue
                    
                    if t.startswith("/start"): enviar(c,"Bot 24/7! Envia archivos o 'imagen de...'")
                    elif "imagen" in t.lower():
                        p=t.lower().replace("/imagen","").replace("imagen de","").replace("imagen","").strip() or "paisaje"
                        try:
                            r2=ses.get("https://image.pollinations.ai/prompt/"+requests.utils.quote(p),timeout=60)
                            ses.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",data={"chat_id":c},files={"photo":("i.jpg",r2.content,"image/jpeg")})
                        except Exception as e: enviar(c,str(e))
                    else: enviar(c,groq(t))
        except: time.sleep(3)

threading.Thread(target=poll,daemon=True).start()
@app.route("/")
def h(): return "OK"
if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
