import unittest
from flask import session
from app import app

class FlaskAppTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        self.app = app.test_client()

    def test_logout(self):
        # Oturum başlatma işlemi
        with self.app as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 123

        # /logout rotasını test etme
        with app.test_request_context('/logout'):
            response = self.app.get('/logout', follow_redirects=True)

        # Oturumun doğru bir şekilde sonlandırılıp sonlandırılmadığı kontrolü
        with self.app as client:
            with client.session_transaction() as sess:
                self.assertNotIn('user_id', sess)

        # Ana sayfaya başarılı bir şekilde yönlendirildiği kontrolü
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Ana Sayfa', response.data)

if __name__ == '__main__':
    unittest.main()
