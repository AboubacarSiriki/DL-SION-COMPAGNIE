from flask import Flask, render_template, request, redirect, url_for,flash
import pymysql

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

# Définir une route et la fonction associée
@app.route('/')
def login():
    # Rendre le template index.html
    return render_template('connexion/login.html')

@app.route('/base', methods=["post","get"])
def base():
    # Rendre le template index.html
    return render_template('index.html')

@app.route('/index')
def index():
    # Rendre le template index.html
    return render_template('index.html')

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
        curso.execute('INSERT INTO fournisseur (nom, adresse, telephone, email) VALUES (%s, %s, %s, %s)',
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



# Point d'entrée de l'application
if __name__ == '__main__':
    # Lancer l'application sur le serveur local
    app.run(debug=True)
