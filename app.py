from flask import Flask, render_template

# Créer une instance de l'application Flask
app = Flask(__name__)

# Définir une route et la fonction associée
@app.route('/')
def index():
    # Rendre le template index.html
    return render_template('index.html')

# Point d'entrée de l'application
if __name__ == '__main__':
    # Lancer l'application sur le serveur local
    app.run(debug=True)
