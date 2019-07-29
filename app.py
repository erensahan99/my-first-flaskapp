
from flask import Flask, render_template, request
import sqlite3 as sql
app = Flask(__name__)

conn = sql.connect('database.db')
conn.execute('CREATE TABLE IF NOT EXISTS students (std_id INTEGER PRIMARY KEY AUTOINCREMENT, first_Name TEXT,last_Name TEXT, addr TEXT, city TEXT)')
conn.close()
@app.route('/')
def home(msg=''):
    try:
       with sql.connect("database.db") as con:
          cur = con.cursor()

          cur.execute("SELECT * FROM students")
          rows = cur.fetchall()
          con.commit()
    finally:
       con.close()
       return render_template("home.html",rows=rows)

@app.route('/new_student')
def yeni_ogrenci():
   return render_template('student.html')
@app.route('/new_entry', methods = ['POST', 'GET'])
def new_entry():
   if request.method == 'POST':
      try:
         fn = request.form['first_Name']
         ln = request.form['last_Name']
         ad = request.form['addr']
         ct = request.form['city']

         with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO students (first_Name,last_Name,addr,city) VALUES (?,?,?,?)",(fn,ln,ad,ct) )
            con.commit()
            msg = "Kayıt ekleme başarılı"
      except:
         con.rollback()
         msg = "Kayıt oluşturulurken bir hata oluştu"

      finally:
         con.close()
         return render_template("student.html",msg = msg)

@app.route('/search')
def search():
    return render_template("getdata.html")
@app.route('/search_entry', methods =['POST','GET'])
def search_entry():
    if request.method=='POST':
        id=request.form['std_id']
        fn=request.form['first_Name']
        ln=request.form['last_Name']
        ct=request.form['city']

        if (id=="" and fn=="" and ln=="" and ct==""):
            return render_template("getdata.html")
        else:
            flag=0
            parameters=[]
            query="SELECT * FROM students WHERE"
            if id!="":
                flag=1
                query=query+" std_id= ?"
                parameters.append(id)
            if fn!="":
                if flag==1:
                    query=query+"AND "
                    flag=0
                flag=1
                query=query+" first_Name = ?"
                parameters.append(fn)
            if ln!="":
                if flag==1:
                    query=query+"AND "
                    flag=0
                flag=1
                query=query+" last_Name = ?"
                parameters.append(ln)
            if ct!="":
                if flag==1:
                    query=query+"AND "
                    flag=0
                query=query+" city = ?"
                parameters.append(ct)
            try:
               with sql.connect("database.db") as con:
                  cur = con.cursor()
                  cur.execute(query,parameters)
                  rows = cur.fetchall()
                  con.commit()
                  if rows==[]:
                      msg="Kayıt bulunmamaktadır"
                      return render_template("getdata.html",msg = msg)
                  else:
                      return render_template("home.html",rows=rows)
            except:
               con.rollback()
               msg = "Arama sırasında bir sorun oluştu."+query
               return render_template("getdata.html",msg = msg)
            finally:
               con.close()

@app.route('/upt_del', methods =['POST','GET'])
def upt_del():
    if request.method=='POST':
        if request.form['select']=='Seçili Olanı Güncelle':
            boxs = request.form.getlist("checked")
            con = sql.connect("database.db")
            con.row_factory = sql.Row

            cur = con.cursor()
            cur.execute("SELECT * FROM students WHERE std_id = ?", [boxs[0]])
            rows = cur.fetchall()
            return render_template("update_student.html",rows=rows,id=boxs[0])

        elif request.form['select']=='Seçili Olanları Sil':
            try:
                boxs = request.form.getlist("checked")
                with sql.connect("database.db") as con:
                    cur = con.cursor()
                    for box in boxs:
                        cur.execute("DELETE FROM students WHERE std_id = ?",[box])
                    cur.execute("SELECT * FROM students")
                    rows = cur.fetchall()
                    con.commit()
                    msg = "Silme işlemi başarılı"
            except:
                con.rollback()
                msg = "Silme işlemi sırasında bir sorun oluştu"
                return render_template("home.html",msg=msg)
            finally:
                con.close()
                return home(msg)
@app.route('/update/<id>',methods=['POST','GET'])
def update(id=0):
    if request.method=='POST':
        try:
            fn=request.form['first_Name']
            ln=request.form['last_Name']
            addr=request.form['addr']
            ct=request.form['city']
            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("UPDATE students SET first_Name=?, last_Name=?,addr=?,city=? WHERE std_id=?", (fn,ln,addr,ct,id))
                cur.execute("SELECT * FROM students")
                rows = cur.fetchall()
                con.commit()
                msg = "Güncelleme işlemi başarılı"
                return render_template("home.html",rows=rows)
        except:
            con.rollback()
            cur.execute("SELECT * FROM students")
            rows = cur.fetchall()
            msg = "Güncelleme işlemi sırasında bir sorun oluştu"
            return render_template("home.html",rows=rows,msg=msg)
        finally:
            con.close()
@app.route('/statistic')
def statistic():
    con = sql.connect("database.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("SELECT city,COUNT(city) AS Total FROM students GROUP BY city ORDER BY city DESC")

    rows = cur.fetchall()
    return render_template("statistics.html", rows = rows)
