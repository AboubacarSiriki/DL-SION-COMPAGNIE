import os
from flask import Flask, render_template, request, redirect, url_for,flash, session
import pymysql, string, random
from send_mail import envoicode
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import jsonify

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


UPLOAD_FOLDER = 'static/image/upload'  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

cursor = conn.cursor()

#hashed_password = bcrypt.generate_password_hash('soum1234')
#print(hashed_password)


# # Exécutez la requête SQL en utilisant des paramètres pour éviter les injections SQL
#sql = "INSERT INTO administrateur (nom, prenom, telephone, email,login, mot_pass) VALUES (%s, %s, %s, %s, %s, %s)"
#values = ('Kra', 'Adephe', '56545678', 'sidiksoum344@gmail.com', 'soum1234', hashed_password)

# # Exécutez la requête avec les valeurs
#cursor.execute(sql, values)
#conn.commit()
# ===================================Admin espace ==============================

# Définir une route et la fonction associée

@app.route('/')
def accueil():
    # Rendre le template index.html
    return render_template('accueil.html')

@app.route('/login')
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

# connexion de l'admin
@app.route('/admin/', methods=["POST", "GET"])
def adminIndex():
    if request.method == 'POST':
        username = request.form.get('login')
        password = request.form.get('password')
        if not (username and password):
            flash('Please fill all the fields', 'danger')
            return redirect('/admin/')
        else:
            cursor = conn.cursor()
            query = "SELECT * FROM administrateur WHERE login=%s"
            cursor.execute(query, (username,))
            admin = cursor.fetchone()
            cursor.close()
            if admin and bcrypt.check_password_hash(admin[6], password):
                session['admin_id'] = admin[0]
                session['admin_name'] = admin[1]
                # flash('Login Successfully', 'success')
                return redirect('/admin/dashboard')
            else:
                flash('Invalid Username or Password', 'danger')
                return redirect(url_for('adminIndex'))
    else:
        return render_template('admin/login.html')

@app.route('/admin/dashboard', methods=["POST", "GET"])
def base():
    if 'admin_id' in session:  # Vérifie si l'administrateur est connecté
        return render_template('admin/dashboard.html')
    else:
        flash('Please login first', 'danger') 
        return redirect('/admin')


# admin logout
@app.route('/admin/logout')
def adminLogout():
    if 'admin_id' in session:
        session.pop('admin_id')
        session.pop('admin_name')
        session.pop('_flashes', None)
        # flash('You have been logged out', 'success')
    return redirect('/admin/')


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
# ==========================Admin update=======================================

@app.route('/admin/modifier_profil', methods=['GET', 'POST'])
def modifier_profil():
    if 'admin_id' not in session:
        flash('Veuillez vous connecter d\'abord.', 'danger')
        return redirect(url_for('adminIndex'))

    admin_id = session['admin_id']
    cursor = conn.cursor()

    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        tel = request.form['tel']
        email = request.form['email']
        image = request.files['image']

        # Sécurisez le nom du fichier
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)

        # Mettez à jour les informations dans la base de données
        cursor.execute('UPDATE administrateur SET nom = %s, prenom = %s, telephone = %s, email = %s, image = %s WHERE id_admin = %s',
                       (nom, prenom, tel, email, filename, admin_id))
        conn.commit()

        flash('Profil mis à jour avec succès.', 'success')
        return redirect(url_for('base'))

    # Récupérez les informations actuelles de l'administrateur pour les afficher dans le formulaire
    cursor.execute('SELECT * FROM administrateur WHERE id_admin = %s', (admin_id,))
    admin_info = cursor.fetchone()
    cursor.close()

    return render_template('profil.html', admin_info=admin_info)

@app.route('/admin/modifier_access', methods=['GET', 'POST'])
def modifier_access():
    if 'admin_id' not in session:
        flash('Veuillez vous connecter d\'abord.', 'danger')
        return redirect(url_for('adminIndex'))

    admin_id = session['admin_id']
    cursor = conn.cursor()

    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        confmotpass = request.form['confmotpass']

        # Vérifiez que les mots de passe correspondent
        if password != confmotpass:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return redirect(url_for('modifier_access'))

        # Hash du mot de passe pour la sécurité
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Mettez à jour le login et le mot de passe dans la base de données
        cursor.execute('UPDATE administrateur SET login = %s, mot_pass = %s WHERE id_admin = %s',
                       (login, hashed_password, admin_id))
        conn.commit()

        flash('Les informations de connexion ont été mises à jour avec succès.', 'success')
        return redirect(url_for('base'))

    # Récupérez les informations actuelles de l'administrateur pour les afficher dans le formulaire
    cursor.execute('SELECT login FROM administrateur WHERE id_admin = %s', (admin_id,))
    admin_login = cursor.fetchone()[0]
    cursor.close()

    return render_template('profil.html', admin_login=admin_login)


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
        utilisateur = cursor.fetchone()

        if utilisateur:
            flash('Cet email est déjà utilisé.', 'danger')
            return redirect(url_for('ajouter_membre'))

        if mot_pass != request.form['confmotpass']:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return redirect(url_for('ajouter_membre'))

        mot_pass = bcrypt.generate_password_hash(mot_pass).decode('utf-8')

        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cursor.execute("INSERT INTO utilisateur (nom, prenom,poste,telephone, email, login, mot_pass,image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                       (nom, prenom, poste,telephone,email,login, mot_pass, filename))
        conn.commit()

        cursor.execute("SELECT * FROM utilisateur WHERE email = %s", (email,))
        utilisateurs = cursor.fetchone()
        cursor.close()
        
        # flash('Nouveau membre ajouté avec succès.', 'success')
        
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
        email = request.form.get('email')
        print ('Email: %s' % email)
        mot_pass = request.form.get('password')
        print ('Password: %s' % mot_pass)

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM utilisateur WHERE email = %s", (email,))
        utilisateur = cursor.fetchone()

        if utilisateur and bcrypt.check_password_hash(utilisateur[7], mot_pass):
            # Si les informations sont correctes, l'utilisateur est connecté
            session['logged_in'] = True
            session['utilisateur_id'] = utilisateur[0]
            session['email'] = email
            session['nom'] = utilisateur[1]
            session['poste'] = utilisateur[3]  # Poste de l'utilisateur
            flash('Connexion réussie.', 'success')
            return redirect(url_for('userDashboard'))

        else:
            flash('Email ou mot de passe incorrect.', 'danger')

    return render_template('connexion/userlogin.html')

@app.route('/userlogout')
def userLogout():
    if 'logged_in' in session:
        session.clear()  # Effacer toutes les informations de session
        # flash('Vous êtes déconnecté.', 'success')
    return redirect(url_for('userLogin'))

@app.route('/dashboard/vendeur')
def dashboard_vendeur():
    return render_template('membres/dashboard_vendeur.html')

@app.route('/dashboard/gestionnaire')
def dashboard_gestionnaire():
    return render_template('membres/dashboard_gestionnaire.html')

@app.route('/user/dashboard')
def userDashboard():
    if 'logged_in' in session:
        if 'poste' in session:
            if session['poste'] == 'vendeur':
                return redirect(url_for('dashboard_vendeur'))
            elif session['poste'] == 'gestionnaire':
                return redirect(url_for('dashboard_gestionnaire'))
        else:
            return redirect(url_for('accueil'))  # Redirection par défaut si le poste n'est pas spécifié
    else:
        return redirect(url_for('userLogin'))

  # Redirection vers la page de connexion si l'utilisateur n'est pas connecté


# @app.route('/index')
# def index():
#     # Rendre le template index.html
#     return render_template('index.html')

@app.route('/Produit/', methods=["post", "get"])
def Produit():
    if request.method == 'POST':
        nom = request.form['nom']
        categorie = request.form['categorie']
        designation = request.form['description']
        prix = request.form['prix']
        image = request.form['image']
        stock_min= request.form['nombre']
        stock=0

        curso = conn.cursor()
        curso.execute('INSERT INTO produit(nom_produit,categorie,prix,stock,stock_min,designation,image) VALUES (%s, %s, %s ,%s,%s, %s, %s)',
                      (nom,categorie,prix,stock,stock_min,designation,image))
        conn.commit()
        curso.close()
        flash('Produit ajouté avec succès', 'success')
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
        curso.execute('INSERT INTO client (nom_prenoms,telephone,email,adresse) VALUES (%s, %s, %s, %s)',
                      (nom,telephone,email,adresse))  # Correction de la requête SQL
        conn.commit()
        curso.close()
        flash('Client ajouté avec succès', 'success')
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
    curso = conn.cursor()
    curso.execute("SELECT * FROM administrateur")
    infos_admin = curso.fetchone()
    curso.close()

    return render_template('profil.html',infos_admin=infos_admin)

@app.route('/profil_vendeur/')
def profil_vendeur():
    # Rendre le template index.html
    return render_template('profil_vendeur.html')

@app.route('/profil_gestionnaire/')
def profil_gestionnaire():
    # Rendre le template index.html
    return render_template('profil_gestionnaire.html')


@app.route('/fournisseurs/', methods=["post", "get"])
def fournisseurs():
    if request.method == 'POST':
        nom = request.form['nom']
        telephone = request.form['tel']
        email = request.form['email']
        adresse = request.form['adresse']

        curso = conn.cursor()
        curso.execute('INSERT INTO fournisseur (nom_prenoms,telephone,email,adresse) VALUES (%s, %s, %s, %s)',
                      (nom,telephone,email,adresse))
        conn.commit()
        curso.close()
        flash('Fournisseur ajouté avec succès', 'success')
        return redirect(url_for("fournisseurs"))
    else:
        # Récupération des éléments de la table fournisseur
        curso = conn.cursor()
        curso.execute("SELECT * FROM fournisseur")
        resultat = curso.fetchall()
        curso.close()

        return render_template("fournisseurs.html", resultat=resultat)


@app.route('/ventes/', methods=["POST", "GET"])
def ventes():
    with conn.cursor() as cursor:
        cursor.execute("SELECT id_produit, nom_produit, categorie, prix FROM produit")
        produits = cursor.fetchall()

        cursor.execute("SELECT id_client, nom_prenoms FROM client")
        clients = cursor.fetchall()

    if request.method == 'POST':
        client_id = request.form.get("client")
        produit_id = request.form.get("produit")
        quantite = request.form.get("nombre")
        prix_vente = request.form.get("prix_vente")  # Récupérer le prix de vente du formulaire

        if not client_id:  # Si aucun client_id n'est fourni, créez un nouveau client
            nom = request.form.get("nom")
            tel = request.form.get("tel")
            email = request.form.get("email")
            adresse = request.form.get("adresse")
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO client (nom_prenoms, telephone, email, adresse) VALUES (%s, %s, %s, %s)',
                    (nom, tel, email, adresse))
                conn.commit()
                client_id = cursor.lastrowid

        if produit_id and quantite and prix_vente:
            quantite = int(quantite)  # Convertir en entier pour la manipulation
            prix_vente = int(prix_vente) 
            montant = prix_vente * quantite
            date_aujourdhui = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO vente (id_client, id_produit, quantite, montant, prix_vente, date_vente,statut) VALUES (%s, %s, %s, %s, %s, %s,%s)',
                    (client_id, produit_id, quantite, montant, prix_vente, date_aujourdhui,"Vendu"))
                conn.commit()
                cursor.execute(
                    'UPDATE produit SET stock = stock - %s WHERE id_produit = %s',
                    (quantite, produit_id))
                conn.commit()
                cursor.close()
                flash('Vente ajoutée avec succès', 'success')
        else:
            flash('Informations de vente manquantes ou incorrectes', 'danger')

    curso = conn.cursor()
    curso.execute(
        "select id_vente,date_vente,statut,client.nom_prenoms,produit.nom_produit from vente,client,produit where vente.id_client = client.id_client and vente.id_produit=produit.id_produit ")
    resultat = curso.fetchall()
    curso.close()
    return render_template("ventes.html", produits=produits, clients=clients,resultat=resultat)

@app.route('/status_vente/<entry_id>', methods=['POST'])
def status_vente(entry_id):
    if request.method == 'POST':
        # Récupérer le nouveau statut envoyé depuis le formulaire
        new_status = request.form.get('status')

        # Mettre à jour le statut dans la base de données
        cursor = conn.cursor()
        cursor.execute("UPDATE vente SET statut = %s WHERE id_vente = %s", (new_status, entry_id))
        conn.commit()
        cursor.close()

        # Rediriger vers la page d'achats après la mise à jour du statut
        return redirect(url_for('ventes'))
    else:
        # Si la méthode de la requête n'est pas POST, retourner une erreur 405 (Méthode non autorisée)
        return jsonify({'error': 'Method Not Allowed'}), 405

@app.route('/submit_vente', methods=['POST'])
def submit_vente():
    # Récupérer les données de la commande à partir du corps de la requête
    order_data = request.get_json()

    # Valider les données de la commande (vérifier les valeurs manquantes ou invalides)

    # Traiter les données de la commande
    for item in order_data:
        product_id = item['produit_id']
        quantity = item['nombre']
        prix_vente = item['prix_vente']
        id_client = item['id_client']
        montant = item['montant']
        # Insérer l'élément de commande dans la base de données
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO vente (id_client, id_produit, Quantite, prix_vente, Montant, date_vente, statut) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (id_client, product_id, quantity, prix_vente, montant, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Vendu')
        )
        conn.commit()
        cursor.close()

        cursor = conn.cursor()
        cursor.execute(
            'UPDATE produit SET stock = stock - %s WHERE id_produit = %s',
            (quantity, product_id))
        conn.commit()
        cursor.close()

        # Calculer le prix total (si nécessaire)

    # Préparer la réponse
    response_data = {
    }

    return jsonify(response_data), 200

@app.route('/submit_vente_client', methods=['POST'])
def submit_vente_client():
    # Récupérer les données de la commande à partir du corps de la requête
    order_data = request.get_json()

    nom = request.form.get("nom")
    tel = request.form.get("tel")
    email = request.form.get("email")
    adresse = request.form.get("adresse")
    with conn.cursor() as cursor:
        cursor.execute(
            'INSERT INTO client (nom_prenoms, telephone, email, adresse) VALUES (%s, %s, %s, %s)',
            (nom, tel, email, adresse))
        conn.commit()
        client_id = cursor.lastrowid

    for item in order_data:
        product_id = item['produit_id']
        quantity = item['nombre']
        prix_vente = item['prix_vente']
        id_client = item['id_client']
        montant = item['montant']
        # Insérer l'élément de commande dans la base de données
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO vente (id_client, id_produit, Quantite, prix_vente, Montant, date_vente, statut) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (client_id, product_id, quantity, prix_vente, montant, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Vendu')
        )
        conn.commit()
        cursor.close()

        cursor = conn.cursor()
        cursor.execute(
            'UPDATE produit SET stock = stock - %s WHERE id_produit = %s',
            (quantity, product_id))
        conn.commit()
        cursor.close()

        # Calculer le prix total (si nécessaire)

    # Préparer la réponse
    response_data = {
        'message': 'Vente effectuée avec succès'
    }

    return jsonify(response_data), 200


@app.route('/submit_order', methods=['POST'])
def submit_order():
    # Récupérer les données de la commande à partir du corps de la requête
    order_data = request.get_json()

    # Valider les données de la commande (vérifier les valeurs manquantes ou invalides)

    # Traiter les données de la commande
    for item in order_data:
        product_id = item['produit_id']
        quantity = item['nombre']
        unit_price = item['prix_unitaire']
        fournisseur_id = item['fournisseur_id']
        # Insérer l'élément de commande dans la base de données
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO entree (ID_fournisseur, id_produit, Quantite, prix, date_entree, statut) VALUES (%s, %s, %s, %s, %s, %s)""",
            (fournisseur_id, product_id, quantity, unit_price,datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'En cours')  # Remplacer 1 par l'ID du fournisseur réel
        )
        conn.commit()
        cursor.close()

        # Calculer le prix total (si nécessaire)

    # Préparer la réponse
    response_data = {
        'message': 'Commande soumise avec succès'
    }

    return jsonify(response_data), 200

@app.route('/donnee_vente/<int:ligne_id>', methods=['GET'])
def donnee_vente(ligne_id):
    # Exécuter la requête SQL pour récupérer la date associée à l'ID de la ligne
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date_vente FROM vente WHERE id_vente = %s", (ligne_id,))
    date_vente = cursor.fetchone()[0]  # Récupérer la date de la première colonne

    # Ensuite, utilisez cette date pour récupérer les données associées
    cursor.execute(
        "SELECT produit.designation, vente.quantite, vente.prix_vente, vente.montant, vente.date_vente,id_vente FROM vente JOIN produit ON vente.id_produit = produit.id_produit WHERE vente.date_vente = %s", (date_vente,))
    resultat1 = cursor.fetchall()
    cursor.close()

    # Formater les données et les renvoyer en tant que réponse JSON
    data = [{'designation': row[0], 'quantite': row[1], 'prix_vente': row[2], 'montant': row[3], 'date_commande': row[5]} for row in resultat1]

    return jsonify(data)

@app.route('/achats/', methods=["POST", "GET"])
def achats():
    cursor = conn.cursor()
    cursor.execute("SELECT id_produit, nom_produit, categorie, prix FROM produit")
    produits = cursor.fetchall()
    cursor.close()

    cursor = conn.cursor()
    cursor.execute("SELECT id_fournisseur, nom_prenoms FROM fournisseur")
    fournisseurs = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        produit_id = request.form["produit"]
        quantite = int(request.form["nombre"])  # Convertir en entier pour la manipulation
        fournisseur_id = request.form["fournisseur"]

        montant = 0
        date_aujourdhui = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor = conn.cursor()
        # Enregistrement de l'achat dans la base de données avec la date d'aujourd'hui
        cursor.execute(
            'INSERT INTO entree (ID_fournisseur, id_produit, Quantite, prix, date_entree, statut) VALUES (%s, %s, %s, %s, %s, %s)',
            (fournisseur_id, produit_id, quantite, montant, date_aujourdhui, "En cours"))
        conn.commit()
        cursor.close()
        flash('Achat ajouté avec succès', 'success')
        return redirect(url_for('achats'))
    else:
        flash('Produit non trouvé', 'danger')

    cursor = conn.cursor()
    cursor.execute(
        'UPDATE entree JOIN produit ON entree.id_produit = produit.id_produit SET entree.prix = produit.prix * entree.quantite')
    conn.commit()
    cursor.close()

    curso = conn.cursor()
    curso.execute(
        "select id_entree,date_entree,statut,fournisseur.nom_prenoms,produit.nom_produit from entree,fournisseur,produit where entree.id_fournisseur = fournisseur.id_fournisseur and entree.id_produit=produit.id_produit ")
    resultat = curso.fetchall()
    curso.close()

    return render_template("achats.html", produits=produits, fournisseurs=fournisseurs,resultat=resultat)



@app.route('/get_row_data/<int:row_id>', methods=['GET'])
def get_row_data(row_id):
    # Exécuter la requête SQL pour récupérer la date associée à l'ID de la ligne
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date_entree FROM entree WHERE id_entree = %s", (row_id,))
    date_entree = cursor.fetchone()[0]  # Récupérer la date de la première colonne

    # Ensuite, utilisez cette date pour récupérer les données associées
    cursor.execute(
        "SELECT produit.designation, entree.quantite, produit.prix, entree.prix, entree.date_entree,id_entree FROM entree JOIN produit ON entree.id_produit = produit.id_produit WHERE entree.date_entree = %s", (date_entree,))
    resultat1 = cursor.fetchall()
    cursor.close()

    # Formater les données et les renvoyer en tant que réponse JSON
    data = [{'designation': row[5], 'quantite': row[0], 'prix_produit': row[1], 'prix_entree': row[2], 'date_entree': row[3]} for row in resultat1]

    return jsonify(data)

@app.route('/status_achat/<entry_id>', methods=['POST'])
def status_achat(entry_id):
    if request.method == 'POST':
        # Récupérer le nouveau statut envoyé depuis le formulaire
        new_status = request.form.get('status')

        # Mettre à jour le statut dans la base de données
        cursor = conn.cursor()
        cursor.execute("UPDATE entree SET statut = %s WHERE id_entree = %s", (new_status, entry_id))
        conn.commit()
        cursor.close()

        # Rediriger vers la page d'achats après la mise à jour du statut
        return redirect(url_for('achats'))
    else:
        # Si la méthode de la requête n'est pas POST, retourner une erreur 405 (Méthode non autorisée)
        return jsonify({'error': 'Method Not Allowed'}), 405

@app.route('/get_product_info/<int:produit_id>')
def get_product_info(produit_id):
    # Effectuez une requête à la base de données pour obtenir les informations du produit
    cursor = conn.cursor()
    cursor.execute("SELECT nom_produit, prix,designation FROM produit WHERE id_produit = %s", (produit_id,))
    produit_info = cursor.fetchone()
    cursor.close()

    # Vérifiez si le produit existe
    if produit_info:
        # Retournez les informations du produit sous forme de données JSON
        response = {
            'nom': produit_info[0],
            'prix': produit_info[1],
            'designation': produit_info[2]
        }
        return jsonify(response)
    else:
        # Si le produit n'est pas trouvé, retournez un message d'erreur
        return jsonify({'error': 'Produit non trouvé'}), 404

@app.route('/get_fournisseur/<int:fournisseur_id>')
def get_fournisseur(fournisseur_id):
    # Effectuez une requête à la base de données pour obtenir les informations du produit
    cursor = conn.cursor()
    cursor.execute("SELECT nom_prenoms FROM fournisseur WHERE id_fournisseur = %s", (fournisseur_id,))
    fournisseur_infos = cursor.fetchone()
    cursor.close()

    # Vérifiez si le produit existe
    if fournisseur_infos:
        # Retournez les informations du fournisseur sous forme de données JSON
        response = {
            'nom': fournisseur_infos[0],
        }
        return jsonify(response)
    else:
        # Si le produit n'est pas trouvé, retournez un message d'erreur
        return jsonify({'error': 'Fournisseur non trouvé'}), 404

@app.route('/get_client/<int:client_id>')
def get_client(client_id):
    # Effectuez une requête à la base de données pour obtenir les informations du produit
    cursor = conn.cursor()
    cursor.execute("SELECT nom_prenoms FROM client WHERE id_client = %s", (client_id,))
    client_infos = cursor.fetchone()
    cursor.close()

    # Vérifiez si le client existe
    if client_infos:
        # Retournez les informations du fournisseur sous forme de données JSON
        response = {
            'nom': client_infos[0],
        }
        return jsonify(response)
    else:
        # Si le produit n'est pas trouvé, retournez un message d'erreur
        return jsonify({'error': 'Client non trouvé'}), 404

@app.route('/stock/', methods=["POST", "GET"])
def stock():
    cursor = conn.cursor()
    cursor.execute("SELECT id_produit, nom_produit,categorie,prix FROM produit")
    produits = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        produit_id = request.form["produit"]
        quantite = int(request.form["nombre"])  # Convertir en entier pour la manipulation
        # Obtenir la date d'aujourd'hui
        date_aujourdhui = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor = conn.cursor()

        # Enregistrement de la vente dans la base de données avec la date d'aujourd'hui
        cursor.execute(
            'INSERT INTO stock (ID_Produit, Quantite, date) VALUES (%s, %s, %s)',
            (produit_id, quantite, date_aujourdhui))

        cursor.execute(
            'UPDATE produit SET stock = stock + %s WHERE id_produit = %s',
            (quantite, produit_id))
        conn.commit()
        cursor.close()

        flash('Stock ajouté avec succès', 'success')
        return redirect(url_for('stock'))
    else:
        flash('Produit non trouvé', 'danger')
    curso = conn.cursor()
    curso.execute("select produit.nom_produit,produit.categorie,quantite,date FROM stock,produit WHERE stock.id_produit = produit.id_produit")
    resultat = curso.fetchall()
    curso.close()

    curso = conn.cursor()
    curso.execute(
        "select nom_produit,categorie,stock,stock_min FROM produit")
    resultat1 = curso.fetchall()
    curso.close()

    return render_template("stock.html", produits=produits,resultat=resultat,resultat1=resultat1)

@app.route('/submit_stock', methods=['POST'])
def submit_stock():
    # Récupérer les données de la commande à partir du corps de la requête
    order_data = request.get_json()

    # Valider les données de la commande (vérifier les valeurs manquantes ou invalides)

    # Traiter les données de la commande
    for item in order_data:
        produit_id = item['produit_id']
        quantite = item['nombre']
        date_aujourdhui = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor = conn.cursor()

        # Enregistrement de la vente dans la base de données avec la date d'aujourd'hui
        cursor.execute(
            'INSERT INTO stock (ID_Produit, Quantite, date) VALUES (%s, %s, %s)',
            (produit_id, quantite, date_aujourdhui))

        cursor.execute(
            'UPDATE produit SET stock = stock + %s WHERE id_produit = %s',
            (quantite, produit_id))
        conn.commit()
        cursor.close()

    # Préparer la réponse
    response_data = {
    }

    return jsonify(response_data), 200

@app.route('/commandes/', methods=["POST", "GET"])
def commandes():
    cursor = conn.cursor()
    cursor.execute("SELECT id_produit, nom_produit, categorie, prix FROM produit")
    produits = cursor.fetchall()
    cursor.close()

    cursor = conn.cursor()
    cursor.execute("SELECT id_client, nom_prenoms FROM client")
    clients = cursor.fetchall()
    cursor.close()
    if request.method == 'POST':
        produit_id = request.form["produit"]
        quantite = int(request.form["nombre"])  # Convertir en entier pour la manipulation
        id_client = request.form["client"]
        prix_vente = int(request.form["prix"])

        montant = quantite*prix_vente
        date_aujourdhui = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor = conn.cursor()
        # Enregistrement de l'achat dans la base de données avec la date d'aujourd'hui
        cursor.execute(
            'INSERT INTO commande (id_client, id_produit, Quantite, prix_vente,Montant, date_commande, statut) VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (id_client, produit_id, quantite, prix_vente,montant, date_aujourdhui, "En cours"))
        conn.commit()
        cursor.close()
        flash('Achat ajouté avec succès', 'success')
        return redirect(url_for('commandes'))
    else:
        flash('Produit non trouvé', 'danger')

    curso = conn.cursor()
    curso.execute(
        "select id_commande,date_commande,statut,client.nom_prenoms,produit.nom_produit from commande,client,produit where commande.id_client = client.id_client and commande.id_produit=produit.id_produit ")
    resultat = curso.fetchall()
    curso.close()
    return render_template('commandes.html', produits=produits, clients=clients,resultat=resultat)

@app.route('/status_commande/<entry_id>', methods=['POST'])
def status_commande(entry_id):
    if request.method == 'POST':
        # Récupérer le nouveau statut envoyé depuis le formulaire
        new_status = request.form.get('status')

        # Mettre à jour le statut dans la base de données
        cursor = conn.cursor()
        cursor.execute("UPDATE commande SET statut = %s WHERE id_commande = %s", (new_status, entry_id))
        conn.commit()
        cursor.close()

        # Rediriger vers la page d'achats après la mise à jour du statut
        return redirect(url_for('commandes'))
    else:
        # Si la méthode de la requête n'est pas POST, retourner une erreur 405 (Méthode non autorisée)
        return jsonify({'error': 'Method Not Allowed'}), 405

@app.route('/submit_commande', methods=['POST'])
def submit_commande():
    # Récupérer les données de la commande à partir du corps de la requête
    order_data = request.get_json()

    # Valider les données de la commande (vérifier les valeurs manquantes ou invalides)

    # Traiter les données de la commande
    for item in order_data:
        product_id = item['produit_id']
        quantity = item['nombre']
        prix_vente = item['prix_vente']
        id_client = item['id_client']
        montant = item['montant']
        # Insérer l'élément de commande dans la base de données
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO commande (id_client, id_produit, Quantite, prix_vente,Montant, date_commande, statut) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (id_client, product_id, quantity, prix_vente,montant,datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'En cours')  # Remplacer 1 par l'ID du fournisseur réel
        )
        conn.commit()
        cursor.close()

        # Calculer le prix total (si nécessaire)

    # Préparer la réponse
    response_data = {
    }

    return jsonify(response_data), 200

@app.route('/donnee_commande/<int:ligne_id>', methods=['GET'])
def donnee_commande(ligne_id):
    # Exécuter la requête SQL pour récupérer la date associée à l'ID de la ligne
    cursor = conn.cursor()
    cursor.execute(
        "SELECT date_commande FROM commande WHERE id_commande = %s", (ligne_id,))
    date_commande = cursor.fetchone()[0]  # Récupérer la date de la première colonne

    # Ensuite, utilisez cette date pour récupérer les données associées
    cursor.execute(
        "SELECT produit.designation, commande.quantite, commande.prix_vente, commande.montant, commande.date_commande,id_commande FROM commande JOIN produit ON commande.id_produit = produit.id_produit WHERE commande.date_commande = %s", (date_commande,))
    resultat1 = cursor.fetchall()
    cursor.close()

    # Formater les données et les renvoyer en tant que réponse JSON
    data = [{'designation': row[0], 'quantite': row[1], 'prix_vente': row[2], 'montant': row[3], 'date_commande': row[5]} for row in resultat1]

    return jsonify(data)

@app.route('/modifier_client/', methods=["post", "get"])
def modifier_client():
    # Rendre le template index.html
    return render_template('client.html')

# Point d'entrée de l'application
if __name__ == '__main__':
    # Lancer l'application sur le serveur local
    app.run(debug=True)
