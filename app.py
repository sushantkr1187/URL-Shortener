from flask import Flask,redirect,render_template,request
import random as rd
import string as st
import psycopg
import os

app=Flask(__name__)

DATABASE_URL = "postgresql://urlshortener_6fl7_user:l38fIwxo86ocLHcf25s63OFTmGFrdusw@dpg-d8f7n06gvqtc7390tieg-a.oregon-postgres.render.com/urlshortener_6fl7"

conn=psycopg.connect(DATABASE_URL)
cur=conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS urls (short_code TEXT PRIMARY KEY,original_url TEXT NOT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);')
conn.commit()
conn.close()

@app.route('/', methods=['GET','POST'])
def home():
    if request.method == "POST":
        url=request.form.get("url")
        conn = psycopg.connect(DATABASE_URL)
        cur = conn.cursor()
        while True:
            code = ''.join(rd.choices(st.ascii_letters + st.digits,k=6))
            cur.execute("SELECT 1 FROM urls WHERE short_code=%s",(code,))
            if cur.fetchone() is None: break
        cur.execute("INSERT INTO urls(short_code, original_url) VALUES (%s, %s)",(code, url))
        conn.commit()
        conn.close()
        # print(url)
        return render_template('result.html',code=code)
    return render_template('index.html')



@app.route('/<code>')
def visit(code):
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT original_url FROM urls WHERE short_code=%s",(code,))
    p=cur.fetchone()
    conn.commit()
    conn.close()
    if p:
        return redirect(p[0])

    return "URL not found", 404
    
if __name__=="__main__":
    app.run(debug=True)
