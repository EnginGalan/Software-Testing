import unittest
from flask import render_template
from app import app

class FlaskAppTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        self.app = app.test_client()

    def test_index_route(self):
        # / rotasını test etme
        response = self.app.get('/')

        # Sayfa başarıyla yüklendi mi kontrol etme
        self.assertEqual(response.status_code, 200)

        # Beklenen içeriği kontrol etme
        self.assertIn(b'Freelancer Web Uygulamasina Hosgeldiniz.', response.data)
        self.assertIn(b'Login', response.data)
        self.assertIn(b'Isalan Kayit', response.data)
        self.assertIn(b'Isveren Kayit', response.data)

if __name__ == '__main__':
    unittest.main()
