from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'mysecretkey'
client = MongoClient('mongodb://localhost:27017/')
db = client['user_database']
collection = db['users']
# Liste des formulaires
forms = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Enregistrement de l'utilisateur dans la base de données
        user = {'username': username, 'password': password}
        collection.insert_one(user)
        return redirect('/login')
    return render_template('signup.html')

# Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = collection.find_one({'username': username, 'password': password})
        if user:
            session['user_id'] = str(user['_id'])
            return redirect('/profile')
        else:
            return render_template('login.html', error='Identifiant ou mot de passe incorrect')
    else:
        return render_template('login.html')

# Page de profil de l'utilisateur connecté
@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    user = collection.find_one({'_id': ObjectId(user_id)})
    if user:
        return render_template('profile.html', user=user)
    else:
        return redirect('/login')
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/delete', methods=['POST'])
def delete():
    user_id = session.get('user_id')
    collection.delete_one({'_id': ObjectId(user_id)})
    session.clear()
    return redirect('/')
    
# Page de création d'un formulaire
@app.route('/create', methods=['GET', 'POST'])
def create_form():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session.get('user_id')
        forms.append({'title': title, 'content': content, 'user_id': user_id})
        return redirect('/forms')
    else:
        return render_template('create_form.html')

# Page des formulaires de l'utilisateur connecté
@app.route('/forms')
def user_forms():
    user_id = session.get('user_id')
    user_forms = [form for form in forms if form['user_id'] == user_id]
    return render_template('user_forms.html', forms=user_forms)

if __name__ == '__main__':
    app.run(debug=True)
