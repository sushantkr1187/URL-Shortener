from flask import Flask,redirect,render_template,request
import random as rd
import string as st
import sqlite3

app=Flask(__name__)

conn=sqlite3.connect('urls.db')
cur=conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS urls(short_code TEXT PRIMARY KEY,original_url TEXT NOT NULL)')
conn.commit()
conn.close()

@app.route('/', methods=['GET','POST'])
def home():
    if request.method == "POST":
        url=request.form.get("url")
        conn = sqlite3.connect('urls.db')
        cur = conn.cursor()
        while True:
            code = ''.join(rd.choices(st.ascii_letters + st.digits,k=6))
            cur.execute("SELECT 1 FROM urls WHERE short_code=?",(code,))
            if cur.fetchone() is None: break
        cur.execute("INSERT INTO urls VALUES (?, ?)",(code, url))
        conn.commit()
        conn.close()
        # print(url)
        return render_template('result.html',code=code)
    return render_template('index.html')



@app.route('/<code>')
def visit(code):
    conn = sqlite3.connect('urls.db')
    cur = conn.cursor()
    cur.execute("SELECT original_url FROM urls WHERE short_code=?",(code,))
    p=cur.fetchone()
    conn.commit()
    conn.close()
    if p:
        return redirect(p[0])

    return "URL not found", 404
    
if __name__=="__main__":
    app.run(debug=True)