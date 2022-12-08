from flask import Flask, request
import os
import sqlite3
import requests

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))



def simple_getter(route, args, json=False, custom_server = None):
    if custom_server is None:
        custom_server = server
    x = requests.get(custom_server+route, params=args)
    if x.status_code == 200 and json:
        return x.json()
    elif x.status_code == 200:
        return x.text
    return None

def uns_resolve (name: str, uns):
    ret = simple_getter("/get/name", {"name": name}, False, uns)
    if ret is None:
        return ""
    return ret

def address_resolve(address: str, uns):
    ret = simple_getter("/get/address", {"address": address}, False, uns)
    if ret is None:
        return ""
    return ret

@app.route("/openuns/get/address", methods=["GET"])
def uns_get():
    conn = sqlite3.connect(basedir+'/uns.db')
    cur = conn.cursor()
    com = "SELECT name from uns WHERE address='"+ request.args.get("address", "")+"'"
    cur.execute(com)
    erg = cur.fetchall()
    if erg == []:
        #print(request.args.get("address", ""))
        return address_resolve(request.args.get("address", ""), "http://localhost:5000/api/uns")
    ret = erg[0][0]
    conn.close()
    return ret+"@openuns"
@app.route("/openuns/get/name", methods=["GET"])
def uns_get_name():
    usr = request.args.get("name", "@").split("@")
    if usr[1] != "openuns":
        if usr[1] == "host":
            return uns_resolve(request.args.get("name", "@"), "http://localhost:5000/api/uns")
    conn = sqlite3.connect(basedir+'/uns.db')
    cur = conn.cursor()
    com = "SELECT address from uns WHERE name='"+usr[0] +"'"
    cur.execute(com)
    erg = cur.fetchall()
    if erg == []:
        return ""
    ret = erg[0][0]
    conn.close()
    return ret

if __name__ == '__main__':
  app.run(host="0.0.0.0", port =69)
