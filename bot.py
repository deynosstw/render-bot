import requests, os, time, threading, io, tempfile
from flask import Flask
os.environ.pop('HTTP_PROXY',None); os.environ.pop('HTTPS_PROXY',None)
TOKEN = "8813377784:AAE2y6iklo_HhCyBhzZEs7nPJ-aIGC1ZkGg"
ses = requests.Session()
app = Flask(__name__)
ultimo = 0
files_cache = {}

def msg(c,t,btns=None):
    for i in range(3):
        try:
            d = {"chat_id":c,"text":t[:4000]}
            if btns: d["reply_markup"] = {"inline_keyboard":btns}
            r = ses.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json=d,timeout=10)
            if r.ok: return r.json()["result"]["message_id"]
        except:
            if i<2: time.sleep(0.5)

def poll():
    global ultimo
    ses.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    while True:
        try:
            r = ses.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates",params={"offset":ultimo+1,"timeout":30},timeout=35)
            if r.ok:
                for x in r.json().get("result",[]):
                    ultimo = x["update_id"]
                    
                    # Callback queries
                    if "callback_query" in x:
                        q = x["callback_query"]
                        cid = q["message"]["chat"]["id"]
                        mid = q["message"]["message_id"]
                        data = q["data"]
                        fid = files_cache.get(cid)
                        
                        if data == "revisar":
                            if fid:
                                try:
                                    f = ses.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={fid}")
                                    fp = f.json()["result"]["file_path"]
                                    r = ses.get(f"https://api.telegram.org/file/bot{TOKEN}/{fp}")
                                    txt = r.text[:3000]
                                    r2 = ses.post("https://api.groq.com/openai/v1/chat/completions",
                                        headers={"Authorization":"Bearer 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"},
                                        json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":f"Analiza este archivo:\n{txt}"}],"max_tokens":2000})
                                    msg(cid,r2.json()["choices"][0]["message"]["content"])
                                except Exception as e: msg(cid,f"Error: {e}")
                            else: msg(cid,"No hay archivo en cache")
                        
                        elif data == "resumir":
                            if fid:
                                try:
                                    f = ses.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={fid}")
                                    fp = f.json()["result"]["file_path"]
                                    r = ses.get(f"https://api.telegram.org/file/bot{TOKEN}/{fp}")
                                    txt = r.text[:3000]
                                    r2 = ses.post("https://api.groq.com/openai/v1/chat/completions",
                                        headers={"Authorization":"Bearer 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"},
                                        json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":f"Resume este texto en max 5 parrafos:\n{txt}"}],"max_tokens":2000})
                                    msg(cid,r2.json()["choices"][0]["message"]["content"])
                                except Exception as e: msg(cid,f"Error: {e}")
                            else: msg(cid,"No hay archivo en cache")
                        
                        elif data == "descargar":
                            if fid:
                                try:
                                    f = ses.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={fid}")
                                    fp = f.json()["result"]["file_path"]
                                    r = ses.get(f"https://api.telegram.org/file/bot{TOKEN}/{fp}")
                                    nm = files_cache.get(f"{cid}_name","archivo.txt")
                                    ses.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument",data={"chat_id":cid},files={"document":(nm,r.content)})
                                except Exception as e: msg(cid,f"Error: {e}")
                            else: msg(cid,"No hay archivo")
                        
                        elif data == "rellenar":
                            if fid:
                                try:
                                    f = ses.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={fid}")
                                    fp = f.json()["result"]["file_path"]
                                    r = ses.get(f"https://api.telegram.org/file/bot{TOKEN}/{fp}")
                                    txt = r.text[:3000]
                                    datos = "Nombre: Julian. Ficha: 3410233. CC: 1104934197. Cel: 3134756579"
                                    r2 = ses.post("https://api.groq.com/openai/v1/chat/completions",
                                        headers={"Authorization":"Bearer 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"},
                                        json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":f"Tengo estos datos: {datos}. Rellena este formulario con ellos:\n{txt}"}],"max_tokens":2000})
                                    msg(cid,r2.json()["choices"][0]["message"]["content"])
                                except Exception as e: msg(cid,f"Error: {e}")
                            else: msg(cid,"No hay archivo")
                        
                        elif data == "pc":
                            msg(cid,"Enciende el PC y usa el bot local con /workspace para ver archivos.")
                        
                        ses.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",json={"callback_query_id":q["id"]})
                        continue
                    
                    # Messages
                    if "message" not in x: continue
                    c = x["message"]["chat"]["id"]
                    
                    if "document" in x["message"]:
                        doc = x["message"]["document"]
                        fid = doc["file_id"]
                        fn = doc.get("file_name","archivo")
                        files_cache[c] = fid
                        files_cache[f"{c}_name"] = fn
                        btns = [[
                            {"text":"📖 Revisar","callback_data":"revisar"},
                            {"text":"📝 Resumir","callback_data":"resumir"}
                        ],[
                            {"text":"📲 Descargar","callback_data":"descargar"},
                            {"text":"📋 Rellenar datos","callback_data":"rellenar"}
                        ],[
                            {"text":"💻 Enviar al PC","callback_data":"pc"}
                        ]]
                        msg(c,f"Archivo recibido: {fn}. Que hago?",btns)
                        continue
                    
                    t = x["message"].get("text","")
                    if not t: continue
                    
                    if t.startswith("/start"):
                        msg(c,"Bot 24/7! Envia archivos, 'imagen de...', o preguntame.")
                    elif "imagen" in t.lower():
                        p = t.lower().replace("/imagen","").replace("imagen de","").replace("imagen","").strip() or "paisaje"
                        msg(c,"Generando imagen...")
                        try:
                            r2 = ses.get("https://image.pollinations.ai/prompt/"+requests.utils.quote(p),timeout=60)
                            ses.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",data={"chat_id":c},files={"photo":("i.jpg",r2.content,"image/jpeg")})
                        except Exception as e: msg(c,str(e))
                    else:
                        r2 = ses.post("https://api.groq.com/openai/v1/chat/completions",
                            headers={"Authorization":"Bearer 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"},
                            json={"model":"llama-3.3-70b-versatile","messages":[{"role":"system","content":"Eres asistente IA."},{"role":"user","content":t}],"max_tokens":2000})
                        msg(c,r2.json()["choices"][0]["message"]["content"])
        except: time.sleep(3)

threading.Thread(target=poll,daemon=True).start()
@app.route("/")
def h(): return "OK"
if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
