import requests, os, time, threading
from flask import Flask
import os
os.environ.pop('HTTP_PROXY',None); os.environ.pop('HTTPS_PROXY',None)

KEY = "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"
TOKEN = "8813377784:AAE2y6iklo_HhCyBhzZEs7nPJ-aIGC1ZkGg"
ses = requests.Session()
app = Flask(__name__)

def msg(c,t):
    for i in range(3):
        try:
            r = ses.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":c,"text":t[:4000]},timeout=10)
            if r.ok: return
        except:
            if i<2: time.sleep(0.5)

def poll():
    ses.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    u=0
    while True:
        try:
            r = ses.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates",params={"offset":u+1,"timeout":30},timeout=35)
            if r.ok:
                for x in r.json().get("result",[]):
                    u=x["update_id"]
                    if "message" in x and "text" in x["message"]:
                        c=x["message"]["chat"]["id"]; t=x["message"]["text"]
                        if t.startswith("/start"): msg(c,"Bot Cloud 24/7!")
                        else:
                            r2 = ses.post("https://api.groq.com/openai/v1/chat/completions",
                                headers={"Authorization":f"Bearer {KEY}"},
                                json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":t}],"max_tokens":2000})
                            msg(c,r2.json()["choices"][0]["message"]["content"])
        except: time.sleep(3)

threading.Thread(target=poll,daemon=True).start()
@app.route("/")
def h(): return "OK"
if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
