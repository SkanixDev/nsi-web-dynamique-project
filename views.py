from flask import Flask, render_template, request
import sqlite3 as sql
app = Flask(__name__)

# Variables
#database = "database/nsi.db"

@app.route('/')
def index():

    return render_template('./views/index.html')

@app.route('/fm')
def fm():

    con = sql.connect("database/nsi.db")
    cursor = con.cursor()

    requete = "SELECT * FROM `users`"
    cursor.execute(requete)
    con.commit()
    print(cursor)
    return render_template('./views/fm.html')


app.run(debug=True)