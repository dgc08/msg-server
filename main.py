from flask import Flask, request, jsonify
from hashlib import sha256
import os
import sqlite3


def salter(msg: str):
    return msg

def hasher(msg: str):
    return sha256(salter(msg).encode("utf-8")).hexdigest()

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

@app.route('/api', methods=['GET'])
def api_ver():
    return "v0.0"

@app.route('/api/getusr', methods=['GET'])
def get_usr():
    return hasher(request.args.get("password", ""))

@app.route('/api/check', methods=['GET'])
def api_check():
    pas = request.args.get("password", None)
    if pas is None:
        return 1
    usr = hasher(pas)
    if not os.path.exists(basedir+"/messages/"+usr+".hx"):
        with open(basedir+"/messages/"+usr+".hx", "w") as f:
            pass
    with open(basedir+"/messages/"+usr+".hx", "r") as f:
        msgs = f.read().split(chr(4))
        ret = []
        for i in msgs:
            ispl = i.split(chr(2))
            if len(ispl) < 2:
                continue
            ret.append({"from":ispl[0], "content": ispl[1]})
    os.remove(basedir+"/messages/"+usr+".hx")
    return jsonify(ret)

@app.route("/api/uns/get/address", methods=["GET"])
def uns_get():
    conn = sqlite3.connect('uns.db')
    cur = conn.cursor()
    com = "SELECT name from uns WHERE address='"+ request.args.get("address", "")+"'"
    cur.execute(com)
    erg = cur.fetchall()
    if erg == []:
        return ""
    ret = erg[0][0]
    conn.close()
    return ret+"@host"
@app.route("/api/uns/get/name", methods=["GET"])
def uns_get_name():
    usr = request.args.get("name", "@").split("@")
    if usr[1] != "host":
        return ""
    conn = sqlite3.connect('uns.db')
    cur = conn.cursor()
    com = "SELECT address from uns WHERE name='"+usr[0] +"'"
    cur.execute(com)
    erg = cur.fetchall()
    if erg == []:
        return ""
    ret = erg[0][0]
    conn.close()
    return ret

@app.route('/api/send', methods=['GET'])
def api_send():
    msg = request.args.get("msg", None)
    part = request.args.get("recipient", None)
    pas = request.args.get("password", None)
    if msg is None or part is None or pas is None:
        return "1"
    if chr(4) in msg:
        return "403"
    usr = hasher(pas)
    with open (basedir+"/messages/" + part+".hx", "a+") as f:
        f.write(usr)
        f.write(chr(2))
        f.write(msg)
        f.write(chr(4))
    return "0"

@app.route("/code", methods=["GET"])
def get_code():
    with open("client/main.py", "r") as f:
        r = f.read()
    return r

if __name__ == '__main__':
  app.run(host="0.0.0.0")
