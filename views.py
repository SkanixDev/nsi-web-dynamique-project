# coding=utf-8
from flask import Flask, render_template, request, redirect
import sqlite3 as sql
from flask_bcrypt import Bcrypt

# Initialisations
app = Flask(__name__)
bcrypt = Bcrypt(app)

# Variables
database = "database/nsi.db"

# Page: Main
# Description: Page d'accueil/principale du site web
@app.route('/')
def index():

    con = sql.connect(database)
    cursor = con.cursor()
    requete_all_shoes = "SELECT * FROM Shoes"
    cursor.execute(requete_all_shoes)
    con.commit()

    return render_template('./views/index.html', shoes=cursor.fetchall())

# Page: FM
# Description: Page de test pour FM (a supprimer)
@app.route('/fm')
def fm():

    con = sql.connect(database)
    cursor = con.cursor()
    requete = """

    """
    cursor.execute(requete)
    con.commit()
    print(cursor.fetchall())
    return render_template('./views/fm.html')

# Page: Login
# Description: Page de connexion d'utilisateur
@app.route('/login', methods=['GET','POST'])
def login():
    result = request.form
    message = ""
    # A FAIRE: Ajouter les cookies
    if request.method == 'POST':
        if (result["email"] != "" or result["password"] != ""):
            print("[LOG] - Connexion d'un utilisateur")
            con = sql.connect(database)
            cursor = con.cursor()
            requete = """SELECT * FROM users WHERE email=?;"""
            cursor.execute(requete, (result["email"],))
            con.commit()
            user = cursor.fetchall()
            print(user)
            if user:
                if bcrypt.check_password_hash(user[0][7], result["password"]):
                    print("[LOG] - Connexion réussie")
                    return redirect('/?info=login_success')
                else:
                    print("[LOG] - Mot de passe incorrect")
                    message = "Mot de passe incorrect"
                    return render_template('./views/login.html', message=message)
            else:
                print("[LOG] - Utilisateur introuvable")
                message = "Utilisateur introuvable"
                return render_template('./views/login.html', message=message)
        else:
            print("[LOG] - Erreur de connexion")
            message = "Erreur de connexion"
            return render_template('./views/login.html', message=message)
    else:
        return render_template('./views/login.html')

# Page: Register
# Description: Permet de se creer un compte
@app.route('/register', methods=['GET','POST'])
def register():
    result = request.form
    message = ""
    print(request.method)
    if request.method == 'POST':
        if (result["name"] != "" or result["lastname"] != "" 
        or result["gender"] != "" 
        or result["email"] != ""
        or result["size"] != ""
        or result["password"] != ""
        or result["confirm_password"] != ""
        or result["confirm_password"] == result["password"]):
            print("[LOG] - Création d'un utilisateur")
            ## A FAIRE : VERIFIER que l'user n'est pas dans la bdd
            gender = "m"
            if result['gender'] == "gender_f":
                gender = "f"
            hashed_password = bcrypt.generate_password_hash(result["password"]).decode('utf-8')
            con = sql.connect(database)
            cursor = con.cursor()
            requete = """INSERT INTO users (name, lastname, gender,admin,size,email,password) VALUES (?,?,?,?,?,?,?);"""
            
            cursor.execute(requete, (result["name"], 
            result["lastname"], 
            gender, 
            0, 
            result["size"], 
            result["email"], 
            hashed_password))
            con.commit()
            return redirect('/?info=register_success')
        else:
            message = "Une erreur c'est produite."
            return render_template('./views/register.html')
    else:
        return render_template('./views/register.html')


# Lancement du site
app.run(debug=True)


# SQLITE Documentation
# https://www.tutorialspoint.com/sqlite/sqlite_python.htm





