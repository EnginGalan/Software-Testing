import unittest
from app import app, db, IsVeren

class FlaskAppTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'
        self.app = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_dashboard_isVeren_authenticated(self):
        # Kullanıcı ekleyin
        new_user = IsVeren(username='test_user', password='test_password')
        with app.app_context():
            db.session.add(new_user)
            db.session.commit()

        # Kullanıcının ID'sini alın
        user_id = new_user.id

        # Session'da kullanıcı oturumu başlatın
        with self.app as client:
            with client.session_transaction() as sess:
                sess['user_id'] = user_id

        # Dashboard_isVeren sayfasına istek yapın
        response = self.app.get('/dashboard_isVeren')

        # Beklenen davranışı kontrol edin
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hosgeldiniz, test_user', response.data)
        self.assertIn(b'Is Olusturma', response.data)
        self.assertIn(b'Cikis Yap', response.data)
        self.assertIn(b'Ilanlarim', response.data)

    def test_dashboard_isVeren_unauthenticated(self):
        # Dashboard_isVeren sayfasına istek yapın (oturum açılmamış kullanıcı)
        response = self.app.get('/dashboard_isVeren')

        # Kullanıcının login sayfasına yönlendirilip yönlendirilmediğini kontrol edin
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'http://localhost/index')

if __name__ == '__main__':
    unittest.main()
