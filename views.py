# coding=utf-8
from flask import Flask, render_template, request, redirect, session, make_response
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

def user_admin():
    con = sql.connect(database)
    cursor = con.cursor()
    requete = """SELECT admin FROM users WHERE email=?;"""
    cursor.execute(requete, [session.get('user')[4]]) 
    user_admin = cursor.fetchone()
    con.close()
    return bool(user_admin[0])

def user_logged_in():
    if session.get('logged_in') is None:
        return False
    else:
        return True

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

# Page: Contacter
# Description: Page pour nous rejoindre
@app.route('/contact')
def contacter():

    return render_template('./views/contact.html', user=session.get('user'))

# Page: Login
# Description: Page de connexion d'utilisateur
@app.route('/login', methods=['GET','POST'])
def login():
    result = request.form
    message = ""
    
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
                    return redirect("/login?error=wrong_password")
            else:
                print("[LOG] - Utilisateur introuvable")
                return redirect("/login?error=user_not_found")
        else:
            print("[LOG] - Erreur de connexion")
            return redirect("/login?error=login_error")
    else:
        return render_template('./views/login.html')

# Page: Register
# Description: Permet de se creer un compte
@app.route('/register', methods=['GET','POST'])
def register():
    result = request.form
    if session.get('logged_in') is not None:
        return redirect('/?info=already_logged_in')
    if request.method == 'POST':
        print(result["confirm_password"]== result["password"])
        if (result["name"] != "" or result["lastname"] != "" 
        or result["gender"] != "" 
        or result["email"] != ""
        or result["size"] != ""
        or result["password"] != ""
        or result["confirm_password"] != ""):
            print("[LOG] - Création d'un utilisateur")
            if result["confirm_password"] != result["password"]:
                print("[LOG] - Les mots de passe ne correspondent pas")
                return redirect('/register?error=password_not_match')
            ## VERIFIER que le user n'est pas dans la base de donnée
            con_user_exist = sql.connect(database)
            cursor_user_exist = con_user_exist.cursor()
            requete_user_exist = """SELECT * FROM users WHERE email=?;"""
            cursor_user_exist.execute(requete_user_exist, (result["email"],))
            con_user_exist.commit()
            user_exist = cursor_user_exist.fetchall()
            if user_exist:
                print("[LOG] - L'utilisateur existe déjà")
                return redirect('/register?info=user_exist')

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
            return redirect('/?error=register_error')
    else:
        return render_template('./views/register.html')

# Page: product
# Description: Page de produit, page dynamique
@app.route('/product/<id>', methods=['GET','POST'])
def product(id):
    
    if request.method == 'POST':
        if session.get('logged_in') is None:
            return redirect('/login?info=not_logged_in')
        print("[LOG] - Ajout d'une commande")

        #get user id and add order
        con_user = sql.connect(database)
        cursor_user = con_user.cursor()
        requete_user = """SELECT id FROM users WHERE email=?;"""
        cursor_user.execute(requete_user, [session.get('user')[4]])
        con_user.commit()
        user_id = cursor_user.fetchone()
        print(user_id)
        con_user.close()

        con_order = sql.connect(database)
        cursor_order = con_order.cursor()
        requete_order = """INSERT INTO orders (idUser, idShoes, status) VALUES (?,?,?);"""
        cursor_order.execute(requete_order, (user_id[0], id, 0))
        con_order.commit()
        con_order.close()

        return redirect('/?info=order_success')
    else:
        con = sql.connect(database)
        cursor = con.cursor()
        requete = """SELECT * FROM Shoes WHERE id=?;"""
        cursor.execute(requete, (id,))
        con.commit()
        return render_template('./views/product.html', shoe=cursor.fetchone(), logged_in=session.get('logged_in'))

# Page: account
# Description: Page de compte utilisateur
@app.route('/account')
def account():
    if session.get('logged_in') is None:
        return redirect('/?info=not_logged_in')
    else:
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

        knowAdmin = cursor.execute("SELECT admin FROM users WHERE email=?;", [session.get('user')[4]]).fetchone()

        return render_template('./views/account.html', user=session.get('user'), 
                               logged_in=session.get('logged_in'),
                               orders=orders,
                               admin=bool(knowAdmin[0]))

# Page: add_shoes
# Description: Page d'ajout de chaussures
@app.route('/add_shoe', methods=['GET','POST'])
def add_shoes():
    result = request.form

    if user_logged_in() == False:
        return redirect('/?info=not_logged_in')
    if user_admin() == False:
        return redirect('/account?info=not_admin')
    if request.method == 'POST':
        if (result["name"] != ""
        or result["size"] != "" 
        or result["price"] != ""
        or result["url"] != ""
        or result["stock"] != ""):
            print("[LOG] - Ajout d'une chaussure")

            con = sql.connect(database)
            cursor = con.cursor()
            requete = """INSERT INTO shoes (nom, taille, prix, image, stock) VALUES (?,?,?,?,?);"""
            
            cursor.execute(requete, (result["name"], 
            result["size"], 
            result["price"], 
            result["url"], 
            result["stock"],)) 
            con.commit()
            return redirect('/add_shoe?info=add_shoe_success')
        else:
            return redirect('/add_shoe?error=add_shoe_incomplete')
    else:
        return render_template('./views/add_shoe.html')
   
# Page: Gérer les utilisateurs
# Description: Page pour modifer les infos des utilisateurs
@app.route('/info_users', methods=['GET'])
def info_users():
    result = request.form

    if user_logged_in() == False:
        return redirect('/?info=not_logged_in')
    if user_admin() == False:
        return redirect('/account?info=not_admin')
    
    if request.method == 'GET':
        con = sql.connect(database)
        cursor = con.cursor()
        requete_all_users = "SELECT * FROM users"
        cursor.execute(requete_all_users)
        con.commit()
        return render_template('./views/info_users.html', users=cursor.fetchall())
    

# Page: Gérer un utilisateur
# Description: Page pour modifer les infos d'un utilisateur
@app.route('/info_user/<id>', methods=['GET','POST'])
def info_user_id(id):

    if user_logged_in() == False:
        return redirect('/?info=not_logged_in')
    if user_admin() == False:
        return redirect('/account?info=not_admin')

    # Récupérer les informations de l'utilisateur
    con = sql.connect(database)
    cursor = con.cursor()
    requete = "SELECT * FROM users WHERE id=?"""
    cursor.execute(requete, (id,))
    con.commit()
    user = cursor.fetchone()
    result = request.form

    # Récupérer toutes les commandes de l'utilisateur
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
        WHERE users.id=?; """
    cursor.execute(requete, [id])
    con.commit()
    orders = cursor.fetchall()


    if request.method == 'POST':
        if (result["name"] != ""
        or result["lastname"] != "" 
        or result["status"] != ""
        or result["email"] != ""):
            print("[LOG] - Mise a jour de l'utilisateur")

            con = sql.connect(database)
            cursor = con.cursor()
            requete = """UPDATE users SET name=?, lastname=?, admin=?, email=? WHERE id=?;"""
            
            cursor.execute(requete, (result["name"], 
            result["lastname"], 
            result["status"], 
            result["email"],
            user[0]))
            con.commit()
            return redirect('/info_users?info=info_user_success')
        else:
            return redirect('/info_users?error=info_user_incomplete')
    else:
        return render_template('./views/info_user.html', user=user, orders = orders)

@app.route('/info_user/<id>', methods=['GET','POST'])
def info_users_id(id):

    if user_logged_in() == False:
        return redirect('/?info=not_logged_in')
    if user_admin() == False:
        return redirect('/account?info=not_admin')

    con = sql.connect(database)
    cursor = con.cursor()
    requete = "SELECT * FROM users WHERE id=?"""
    cursor.execute(requete, (id,))
    con.commit()
    user = cursor.fetchone()
    result = request.form
    if request.method == 'POST':
        if (result["name"] != ""
        or result["lastname"] != "" 
        or result["status"] != ""
        or result["email"] != ""):
            print("[LOG] - Mise a jour de l'utilisateur")

            con = sql.connect(database)
            cursor = con.cursor()
            requete = """UPDATE users SET name=?, lastname=?, admin=?, email=? WHERE id=?;"""
            
            cursor.execute(requete, (result["name"], 
            result["lastname"], 
            result["status"], 
            result["email"],
            user[0]))
            con.commit()
            return redirect('/info_users?info=info_user_success')
        else:
            return redirect('/info_users?error=info_user_incomplete')
    else:
        return render_template('./views/info_user.html', user=user)

# Page: /info_user/<id>/orders
# Description: Page pour mettre à jour les commandes d'un utilisateur (post)
@app.route('/info_user/<id>/orders', methods=['POST'])
def info_user_orders(id):
    result = list(request.form.listvalues())
    if user_logged_in() == False:
        return redirect('/?info=not_logged_in')
    if user_admin() == False:
        return redirect('/account?info=not_admin')

    if request.method == 'POST': 
        print("[LOG] - Mise a jour de la commande")
        
        con = sql.connect(database)
        cursor = con.cursor()
        for x in range(len(result[0])):
            requete = """UPDATE orders SET status=? WHERE idOrder=?;"""
            cursor.execute(requete, (result[1][x], result[0][x]))
            con.commit()
        con.close()
        return redirect('/info_user/'+id+'?info=info_user_success')
    

# Page: manage_shoes
# Description: Page pour gérer l'ensemble des chaussures
@app.route('/manage_shoes', methods=['GET'])
def manage_shoes():
    result = request.form

    if user_logged_in() == False:
        return redirect('/?info=not_logged_in')
    if user_admin() == False:
        return redirect('/account?info=not_admin')
    
    if request.method == 'GET':
        con = sql.connect(database)
        cursor = con.cursor()
        requete_all_users = "SELECT * FROM Shoes"
        cursor.execute(requete_all_users)
        con.commit()
        return render_template('./views/manage_shoes.html', shoes=cursor.fetchall())
    
   
# Page: manage_shoe
# Description: Page pour gerer une paire de chaussure
@app.route('/manage_shoe/<id>', methods=['GET','POST'])
def manage_shoe(id):
    result = request.form

    
    if user_logged_in() == False:
        return redirect('/?info=not_logged_in')
    if user_admin() == False:
        return redirect('/account?info=not_admin')
    con = sql.connect(database)
    cursor = con.cursor()
    requete = "SELECT * FROM Shoes WHERE id=?"""
    cursor.execute(requete, (id,))
    con.commit()
    shoe = cursor.fetchone()

    if request.method == "POST":
        if (result["nom"] != ""
        or result["taille"] != "" 
        or result["prix"] != ""
        or result["image"] != ""
        or result["stock"] != ""):
            print("[LOG] - Mise a jour d'une chaussure")

            con = sql.connect(database)
            cursor = con.cursor()
            requete = """UPDATE Shoes SET nom=?, taille=?, prix=?, image=?, stock=? WHERE id=?;"""
            
            cursor.execute(requete, (result["nom"], 
            result["taille"], 
            result["prix"], 
            result["image"], 
            result["stock"],
            id))
            con.commit()
            return redirect('/manage_shoes?info=info_user_success')
        else:
            return redirect('/manage_shoes?error=info_user_incomplete')
    else:
        return render_template('./views/manage_shoe.html', shoe=shoe)


# Page: logout
# Description: Page de déconnexion
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/?info=logout_success')

# Page: Script - Popups
# Description: Fichier js pour la gestion des popups
@app.route('/script/js/erreur.js')
def script():
    response = make_response(open("static/js/erreur.js", mode="r", encoding="utf-8"), 200)
    response.mimetype = "application/javascript"
    return response


# Lancement du site
app.run(debug=True)


# SQLITE Documentation
# https://www.tutorialspoint.com/sqlite/sqlite_python.htm





