# coding=utf-8
from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql
from flask_bcrypt import Bcrypt
from flask_session import Session

# Initialisations
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
bcrypt = Bcrypt(app)

# Variables
database = "database/nsi.db"

# Fonction utile
def add_connect_cookies(user):
    session['logged_in'] = True
    session['user'] = user

# Page: Main
# Description: Page d'accueil/principale du site web
@app.route('/')
def index():

    con = sql.connect(database)
    cursor = con.cursor()
    requete_all_shoes = "SELECT * FROM Shoes"
    cursor.execute(requete_all_shoes)
    con.commit()

    return render_template('./views/index.html', shoes=cursor.fetchall(), logged_in=session.get('logged_in'), user=session.get('user'))

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
    
    if session.get('logged_in') is not None:
        return redirect('/?info=already_logged_in')
    
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
                    user_for_cookie = (user[0][1], user[0][2], user[0][3], user[0][5], user[0][6])
                    add_connect_cookies(user_for_cookie)
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
            user_for_cookie = (result["name"], result["lastname"], result["gender"], result["size"], result["email"])
            add_connect_cookies(user_for_cookie)
            return redirect('/?info=register_success')
        else:
            message = "Une erreur c'est produite."
            return render_template('./views/register.html')
    else:
        return render_template('./views/register.html')

# Page: product
# Description: Page de produit, page dynamique
@app.route('/product/<id>')
def product(id):
    con = sql.connect(database)
    cursor = con.cursor()
    requete = """SELECT * FROM Shoes WHERE id=?;"""
    cursor.execute(requete, (id,))
    con.commit()
    return render_template('./views/product.html', shoes=cursor.fetchall())

# Page: account
# Description: Page de compte utilisateur
@app.route('/account')
def account():
    if session.get('logged_in') is None:
        return redirect('/?info=not_logged_in')
    else:
        # Tu dois:
        # 1. Récuperer l'id de l'utilisateur dans `user`
        # 2. Récuperer les commandes de l'utilisateur
        # 3. Faire une joiture entre les commandes et les chaussures pour recuperer les informations des chaussures

        # Utilise JOIN pour faire la jointure entre les tables
        con = sql.connect(database)
        cursor = con.cursor()
        requete = """
        SELECT 
            orders.idOrder,
            orders.status,
            Shoes.nom, 
            Shoes.taille, 
            Shoes.prix, 
            Shoes.image
        FROM orders
        INNER JOIN shoes 
        ON orders.idShoes = Shoes.id
        INNER JOIN users
        ON orders.idUser = users.id 
        WHERE users.email=?; """
        cursor.execute(requete, [session.get('user')[4]])
        con.commit()
        orders = cursor.fetchall()
        return render_template('./views/account.html', user=session.get('user'), 
                               logged_in=session.get('logged_in'),
                               orders=orders)

# Page: add_shoes
# Description: Page d'ajout de chaussures
@app.route('/add_shoes', methods=['GET','POST'])
def add_shoes():
    return render_template('./views/add_shoes.html')

# Page: logout
# Description: Page de déconnexion
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/?info=logout_success')



# Lancement du site
app.run(debug=True)


# SQLITE Documentation
# https://www.tutorialspoint.com/sqlite/sqlite_python.htm





