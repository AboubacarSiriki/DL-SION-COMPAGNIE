from flask import Flask, render_template

# Créer une instance de l'application Flask
app = Flask(__name__)

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

@app.route('/Produit/')
def Produit():
    # Rendre le template index.html
    return render_template('Produit.html')

@app.route('/clients/')
def clients():
    # Rendre le template index.html
    return render_template('clients.html')

@app.route('/profil/')
def profil():
    # Rendre le template index.html
    return render_template('profil.html')

@app.route('/equipe/')
def equipe():
    # Rendre le template index.html
    return render_template('equipe.html')


@app.route('/fournisseurs/')
def fournisseurs():
    # Rendre le template index.html
    return render_template('fournisseurs.html')

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
