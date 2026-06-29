import requests, os, time, threading
from flask import Flask
os.environ.pop('HTTP_PROXY',None); os.environ.pop('HTTPS_PROXY',None)
TOKEN = "8813377784:AAE2y6iklo_HhCyBhzZEs7nPJ-aIGC1ZkGg"
ses = requests.Session()
app = Flask(__name__)
ult=0; arch={}

def h(c,t,b=None):
    d={"chat_id":c,"text":t[:4000]}
    if b: d["reply_markup"]={"inline_keyboard":b}
    ses.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json=d)

def g(txt):
    r=ses.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization":"Bearer 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"},
        json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":txt}],"max_tokens":2000})
    try: return r.json()["choices"][0]["message"]["content"]
    except: return str(r.json())

def gf(fid):
    r=ses.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={fid}")
    r2=ses.get(f"https://api.telegram.org/file/bot{TOKEN}/{r.json()['result']['file_path']}")
    return r2.text[:3000]

ses.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
while True:
    try:
        r=ses.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates",params={"offset":ult+1,"timeout":30},timeout=35)
        if not r.ok: continue
        for x in r.json().get("result",[]):
            ult=x["update_id"]
            if "callback_query" in x:
                q=x["callback_query"]; c=q["message"]["chat"]["id"]; d=q["data"]; fid=arch.get(c)
                if d=="ver": h(c,g(f"Analiza:\n{gf(fid)}"))
                elif d=="resum": h(c,g(f"Resume:\n{gf(fid)}"))
                elif d=="datos": h(c,g(f"Rellena con: Nombre Julian, Ficha 3410233, CC 1104934197, Cel 3134756579\n{gf(fid)}"))
                elif d=="bajar":
                    r=ses.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={fid}")
                    r2=ses.get(f"https://api.telegram.org/file/bot{TOKEN}/{r.json()['result']['file_path']}")
                    ses.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument",data={"chat_id":c},files={"document":(arch.get(f"{c}_n","a.txt"),r2.content)})
                elif d=="pc": h(c,"Enciende el PC.")
                ses.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",json={"callback_query_id":q["id"]})
                continue
            if "message" not in x: continue
            c=x["message"]["chat"]["id"]
            if "document" in x["message"]:
                d=x["message"]["document"]; fid=d["file_id"]
                arch[c]=fid; arch[f"{c}_n"]=d.get("file_name","a.txt")
                h(c,f"Archivo: {d.get('file_name','')}",[
                    [{"text":"📖 Revisar","callback_data":"ver"},{"text":"📝 Resumir","callback_data":"resum"}],
                    [{"text":"📲 Descargar","callback_data":"bajar"},{"text":"📋 Rellenar","callback_data":"datos"}],
                    [{"text":"💻 PC","callback_data":"pc"}]])
                continue
            t=x["message"].get("text","")
            if not t: continue
            if t.startswith("/start"): h(c,"Bot 24/7! 'imagen de...' para fotos, o preguntame cualquier cosa.")
            elif "imagen" in t.lower():
                p=t.lower().replace("/imagen","").replace("imagen de","").replace("imagen","").strip() or "paisaje"
                try:
                    r2=ses.get("https://image.pollinations.ai/prompt/"+requests.utils.quote(p),timeout=60)
                    ses.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",data={"chat_id":c},files={"photo":("i.jpg",r2.content,"image/jpeg")})
                except Exception as e: h(c,str(e))
            else: h(c,g(t))
    except: time.sleep(3)
