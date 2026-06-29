import requests, os, time, threading
from flask import Flask
os.environ.pop('HTTP_PROXY',None); os.environ.pop('HTTPS_PROXY',None)
TOKEN = "8813377784:AAE2y6iklo_HhCyBhzZEs7nPJ-aIGC1ZkGg"
ses = requests.Session()
app = Flask(__name__)
ult=0

def h(c,t):
    ses.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":c,"text":t[:4000]})

def g(txt):
    r=ses.post("https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization":"Bearer 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"},
        json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":txt}],"max_tokens":2000})
    try: return r.json()["choices"][0]["message"]["content"]
    except: return str(r.json())

@app.route("/")
def home(): return "OK"

def poll():
    global ult
    ses.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    while True:
        try:
            r=ses.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates",params={"offset":ult+1,"timeout":30},timeout=35)
            if r.ok:
                for x in r.json().get("result",[]):
                    ult=x["update_id"]
                    if "message" not in x: continue
                    c=x["message"]["chat"]["id"]
                    t=x["message"].get("text","")
                    if not t: continue
                    if "imagen" in t.lower():
                        p=t.lower().replace("imagen de","").replace("imagen","").strip() or "paisaje"
                        try:
                            r2=ses.get("https://image.pollinations.ai/prompt/"+requests.utils.quote(p),timeout=60)
                            ses.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",data={"chat_id":c},files={"photo":("i.jpg",r2.content,"image/jpeg")})
                        except Exception as e: h(c,str(e))
                    else: h(c,g(t))
        except: time.sleep(3)

t=threading.Thread(target=poll,daemon=True)
t.start()
port=int(os.environ.get("PORT",10000))
app.run(host="0.0.0.0",port=port)
