from flask import Flask, render_template, request
import sqlite3 as sql
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('./views/index.html')

@app.route('/fm')
def fm():
    return render_template('./views/fm.html')


app.run(debug=True)