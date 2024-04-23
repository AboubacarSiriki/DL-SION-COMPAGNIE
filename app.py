from flask import Flask, render_template, request, redirect, url_for,flash, session
import pymysql, string, random
from send_mail import envoicode
from flask_bcrypt import Bcrypt

# Créer une instance de l'application Flask
app = Flask(__name__)

# flash message
app.secret_key = 'message' 

# connexion à la base de donnée

conn = pymysql.connect(
    host='localhost',
    user='root',
    password="",
    db='dlsionsarl_db',)

# Initialiser l'extension Bcrypt pour le hachage des mots de passe
bcrypt = Bcrypt(app)

# hashed_password = bcrypt.generate_password_hash('admin')
# print(hashed_password)
# ===================================Admin espace ==============================

# Définir une route et la fonction associée
@app.route('/')
def login():
    # Rendre le template index.html
    return render_template('connexion/login.html')

@app.route('/code/')
def code():
    # Rendre le template index.html
    return render_template('connexion/code.html')

@app.route('/nouveau_mot/')
def nouveau_mot():
    # Rendre le template index.html
    return render_template('connexion/nouveau_mot.html')

@app.route('/recuperation/')
def recuperation():
    # Rendre le template index.html
    return render_template('connexion/recuperation.html')

# conneion de l'admin
@app.route('/admin/', methods=["POST", "GET"])
def adminIndex():
    if request.method == 'POST':
        username = request.form.get('login')
        password = request.form.get('password')
        if not (username and password):
            flash('Please fill all the fields', 'danger')
            return redirect('/')
        else:
            cursor = conn.cursor()
            query = "SELECT * FROM administrateur WHERE login=%s"
            cursor.execute(query, (username,))
            admin = cursor.fetchone()
            cursor.close()
            if admin and bcrypt.check_password_hash(admin[4], password):
                session['admin_id'] = admin[0]
                session['admin_name'] = admin[6]
                flash('Login Successfully', 'success')
                return redirect('/admin/dashboard')
            else:
                flash('Invalid Username or Password', 'danger')
                return redirect('/')
    else:
        return redirect('/')

@app.route('/admin/dashboard', methods=["POST", "GET"])
def base():
    if 'admin_id' in session:  # Vérifie si l'administrateur est connecté
        return render_template('admin/dashboard.html')
    else:
        flash('Please login first', 'danger')  # Message flash indiquant que l'utilisateur doit d'abord se connecter
        return redirect('/admin')  # Redirige vers la page de connexion


# admin logout
@app.route('/admin/logout')
def adminLogout():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if session.get('admin_id'):
        session['admin_id']=None
        session['admin_name']=None
        return redirect('/')


# ================================Admin Mot de passe oublié================================

@app.route('/forgot_password', methods=["GET", "POST"])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Please provide your email address', 'danger')
            return redirect('/recuperation/')

        cursor = conn.cursor()
        query = "SELECT * FROM administrateur WHERE email=%s"
        cursor.execute(query, (email,))
        admin = cursor.fetchone()
        cursor.close()

        if not admin:
            flash('This email is not registered', 'danger')
            return redirect('/recuperation/')
        code = ''.join(random.choices(string.digits, k=5))
        session['code'] = code
        session['email'] = email
        envoicode(code, email)
        flash('A verification code has been sent to your email', 'success')
        return redirect('/code/')

    return redirect('/recuperation/')

@app.route('/forgot_password_code', methods=["GET", "POST"])
def forgot_password_code():
    if request.method == 'POST':
        code = session.get('code')
        email = session.get('email')
        if not (code and email):
            flash('Invalid code or email', 'danger')
            return redirect('/forgot_password')

        codesaisir = request.form.get("code")
        if codesaisir == code:
            return redirect('/nouveau_mot')
        else:
            flash('Incorrect verification code', 'danger')
            return redirect('/code/')

    return redirect('/code/')


@app.route('/change_password', methods=["GET", "POST"])
def change_password():
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = session.get('email')

        if not (password and confirm_password):
            flash('Please fill all the fields', 'danger')
            return redirect('/change_password')

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect('/change_password')

        cursor = conn.cursor()
        mot_pass = bcrypt.generate_password_hash(password).decode('utf-8')
        query = "UPDATE administrateur SET mot_pass=%s WHERE email=%s"
        cursor.execute(query, (mot_pass, email))
        conn.commit()
        cursor.close()

        flash('Password updated successfully', 'success')
        session.pop('email', None)
        session.pop('code', None)
        return redirect('/')
        
    return render_template('connexion/nouveau_mot.html')

# ==========================Gestion des membres========================

# @app.route('/index')
# def index():
#     # Rendre le template index.html
#     return render_template('index.html')

@app.route('/Produit/', methods=["post", "get"])
def Produit():
    if request.method == 'POST':
        nom = request.form['nom']
        categorie = request.form['categorie']
        description = request.form['description']
        prix = request.form['prix']
        image = request.form['image']

        curso = conn.cursor()
        curso.execute('INSERT INTO produit(categorie, nom_produit, designation, prix, image) VALUES (%s, %s, %s, %s, %s)',
                      (categorie, nom, description, prix, image))
        conn.commit()
        flash('Produit ajouté avec succès', 'success')
        curso.close()
        return redirect(url_for("Produit"))  # Redirection vers la même page Produit après ajout
    else:
        # Récupération des éléments de la table produit
        curso = conn.cursor()
        curso.execute("SELECT * FROM produit")
        resultat = curso.fetchall()
        curso.close()

        return render_template("Produit.html", resultat=resultat)

@app.route('/clients/', methods=["post", "get"])
def clients():
    if request.method == 'POST':
        nom = request.form['nom']
        telephone = request.form['tel']  # Correction de la clé 'tel' à 'telephone'
        email = request.form['email']
        adresse = request.form['adresse']

        curso = conn.cursor()
        curso.execute('INSERT INTO client (`nom et prénoms`, adresse, telephone, email) VALUES (%s, %s, %s, %s)',
                      (nom, adresse, telephone, email))  # Correction de la requête SQL
        conn.commit()
        flash('Client ajouté avec succès', 'success')  # Correction du message flash
        curso.close()
        return redirect(url_for("clients"))  # Redirection vers la même page clients après ajout
    else:
        # Récupération des éléments de la table client
        curso = conn.cursor()
        curso.execute("SELECT * FROM client")
        resultat = curso.fetchall()
        curso.close()

        return render_template("clients.html", resultat=resultat)

@app.route('/profil/')
def profil():
    # Rendre le template index.html
    return render_template('profil.html')

@app.route('/equipe/')
def equipe():
    # Rendre le template index.html
    return render_template('equipe.html')


from flask import request, redirect, url_for, flash

from flask import request, redirect, url_for, flash

@app.route('/fournisseurs/', methods=["post", "get"])
def fournisseurs():
    if request.method == 'POST':
        nom_et_prenoms = request.form['nom']
        telephone = request.form['tel']
        email = request.form['email']
        adresse = request.form['adresse']

        curso = conn.cursor()
        curso.execute('INSERT INTO fournisseur (nom_et_prenoms, adresse, telephone, email) VALUES (%s, %s, %s, %s)',
                      (nom_et_prenoms, adresse, telephone, email))
        conn.commit()
        flash('Fournisseur ajouté avec succès', 'success')
        curso.close()
        return redirect(url_for("fournisseurs"))
    else:
        # Récupération des éléments de la table fournisseur
        curso = conn.cursor()
        curso.execute("SELECT * FROM fournisseur")
        resultat = curso.fetchall()
        curso.close()

        return render_template("fournisseurs.html", resultat=resultat)


@app.route('/ventes/')
def ventes():
    # Rendre le template index.html
    return render_template('ventes.html')

@app.route('/stock/')
def stock():
    # Rendre le template index.html
    return render_template('stock.html')

@app.route('/commandes/')
def commandes():
    # Rendre le template index.html
    return render_template('commandes.html')

@app.route('/modifier_client/', methods=["post", "get"])
def modifier_client():
    # Rendre le template index.html
    return render_template('client.html')

# Point d'entrée de l'application
if __name__ == '__main__':
    # Lancer l'application sur le serveur local
    app.run(debug=True)
