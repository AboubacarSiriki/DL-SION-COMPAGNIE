import os
from flask import Flask, render_template, request, redirect, url_for,flash, session
import pymysql, string, random
from send_mail import envoicode
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

# Créer une instance de l'application Flask
app = Flask(__name__)

# flash message
app.secret_key = 'message' 

# connexion à la base de donnée

conn = pymysql.connect(
    host='localhost',
    user='root',
    password="",
    db='dl_sion_compagnie',)

# Initialiser l'extension Bcrypt pour le hachage des mots de passe
bcrypt = Bcrypt(app)


UPLOAD_FOLDER = 'static/image/upload'  # Remplacez par le chemin de votre choix
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# hashed_password = bcrypt.generate_password_hash('kra1234')
# print(hashed_password)

# cursor = conn.cursor()
# # Exécutez la requête SQL en utilisant des paramètres pour éviter les injections SQL
# sql = "INSERT INTO administrateur (nom, prenom, email, mot_pass, telephone, login) VALUES (%s, %s, %s, %s, %s, %s)"
# values = ('Kra', 'Adephe', 'adelphekra@gmail.com', hashed_password, '586954455', 'kra1234')

# # Exécutez la requête avec les valeurs
# cursor.execute(sql, values)
# conn.commit()
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
@app.route('/admin/ajouter_membre', methods=['GET', 'POST'])
def ajouter_membre():

    utilisateur = None

    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        mot_pass = request.form['password']
        telephone = request.form['tel']
        login = request.form['login']
        poste = request.form['poste']
        photo = request.files['image']  

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM utilisateur WHERE email = %s", (email,))
        utilisateurs = cursor.fetchone()

        if utilisateur:
            flash('Cet email est déjà utilisé.', 'danger')
            return redirect(url_for('ajouter_membre'))

        if mot_pass != request.form['confmotpass']:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return redirect(url_for('ajouter_membre'))

        mot_pass = bcrypt.generate_password_hash(mot_pass).decode('utf-8')

        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cursor.execute("INSERT INTO utilisateur (nom, prenom, email, mot_pass, telephone, login, poste, photo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                       (nom, prenom, email, mot_pass, telephone, login, poste, filename))
        conn.commit()

        cursor.execute("SELECT * FROM utilisateur WHERE email = %s", (email,))
        utilisateurs = cursor.fetchone()
        cursor.close()
        
        flash('Nouveau membre ajouté avec succès.', 'success')
        
        return redirect('/admin/equipe/')

    return redirect('/admin/equipe/')

@app.route('/admin/equipe/')
def equipe():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM utilisateur")
    utilisateurs = cursor.fetchall()
    cursor.close()

    return render_template('membres/equipe.html', utilisateurs=utilisateurs)




@app.route('/userlogin', methods=['GET', 'POST'])
def userLogin():
    if request.method == 'POST':
        email = request.form['email']
        mot_pass = request.form['password']

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM utilisateur WHERE email = %s", (email,))
        utilisateur = cursor.fetchone()

        if utilisateur and bcrypt.check_password_hash(utilisateur[4], mot_pass):
            # Si les informations sont correctes, l'utilisateur est connecté
            session['logged_in'] = True
            session['utilisateur_id'] = utilisateur[0]
            session['email'] = email
            session['nom'] = utilisateur[1]
            session['poste'] = utilisateur[6]  # Poste de l'utilisateur
            flash('Connexion réussie.', 'success')
            return redirect(url_for('dashboard'))

        else:
            flash('Email ou mot de passe incorrect.', 'danger')

    return render_template('connexion/userlogin.html')

@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session:
        if session['poste'] == 'vendeur':
            return redirect(url_for('dashboard_vendeur'))
        elif session['poste'] == 'gestionnaire':
            return redirect(url_for('dashboard_gestionnaire'))
        else:
            return redirect(url_for('accueil'))  # Redirection par défaut si le poste n'est pas spécifié
    else:
        return redirect(url_for('userlogin'))  # Redirection vers la page de connexion si l'utilisateur n'est pas connecté

@app.route('/dashboard/vendeur')
def dashboard_vendeur():
    return render_template('memebres/dashboard_vendeur.html')

@app.route('/dashboard/gestionnaire')
def dashboard_gestionnaire():
    return render_template('membres/dashboard_gestionnaire.html')


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

@app.route('/achat/')
def achat():
    # Rendre le template index.html
    return render_template('admin/achat.html')

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
