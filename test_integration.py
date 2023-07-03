import pytest
from flask import Flask
from flask_testing import TestCase
from app import app

# Classe de test héritant de TestCase de flask_testing
class AppTestCase(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Désactive la protection CSRF pour les tests
        return app

    def setUp(self):
        self.client = self.app.test_client()
        # Créer un utilisateur pour le test
        self.create_test_user()

    def create_test_user(self):
        # Ajouter un utilisateur de test dans la base de données (MongoDB) pour les tests
        test_user = {'username': 'testuser', 'password': 'testpassword'}
        self.app.config['collection'].insert_one(test_user)

    def tearDown(self):
        # Supprimer l'utilisateur de test de la base de données après chaque test
        self.app.config['collection'].delete_one({'username': 'testuser'})

    # Test : connexion réussie
    def test_login_success(self):
        response = self.client.post('/login', data={'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)  # Vérifie si la redirection a eu lieu
        self.assertEqual(response.location, 'http://localhost/profile')  # Vérifie si la redirection vers le profil a eu lieu

    # Test : connexion avec des identifiants invalides
    def test_login_invalid_credentials(self):
        response = self.client.post('/login', data={'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)  # La page doit rester sur /login
        self.assertIn('Identifiant ou mot de passe incorrect', response.get_data(as_text=True))

    # Test : accès à la page de profil sans être connecté (redirection vers /login)
    def test_profile_access_without_login(self):
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 302)  # Vérifie si la redirection a eu lieu
        self.assertEqual(response.location, 'http://localhost/login')  # Vérifie si la redirection vers la page de connexion a eu lieu

    # Test : accès à la page de profil en étant connecté (statut 200 OK)
    def test_profile_access_with_login(self):
        with self.client:
            self.client.post('/login', data={'username': 'testuser', 'password': 'testpassword'})  # Se connecter avant d'accéder à la page de profil
            response = self.client.get('/profile')
            self.assertEqual(response.status_code, 200)  # La page de profil doit être accessible

if __name__ == '__main__':
    pytest.main()
