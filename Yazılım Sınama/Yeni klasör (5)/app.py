
from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import praw
from flask import flash

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class IsAlan(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    job_listings = db.relationship('JobListing', backref='isAlan', lazy=True)
    applications = db.relationship('JobApplication', backref='isAlan', lazy=True, foreign_keys="[JobApplication.is_Veren_id]", primaryjoin="IsAlan.id == foreign(JobApplication.is_Veren_id)")
    money = db.Column(db.Float, default=0.0)
    isTransaction = db.Column(db.Boolean, default=False)

class IsVeren(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    applications = db.relationship('JobApplication', backref='is_Veren', lazy=True, foreign_keys="[JobApplication.is_Veren_id]")

class JobListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    isAlan_id = db.Column(db.Integer, db.ForeignKey('is_alan.id'), nullable=False)
    status = db.Column(db.String(100), nullable=False, default= 'Kabul Edilmedi')
    applications = db.relationship('JobApplication', backref='job_listing', lazy=True)

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cover_letter = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Accepted, Rejected
    is_Veren_id = db.Column(db.Integer, db.ForeignKey('is_veren.id'), nullable=False)
    job_listing_id = db.Column(db.Integer, db.ForeignKey('job_listing.id'), nullable=False)
    
@app.route('/')
def index():
    return render_template('index.html')

#İşAlan Login işlemini yapar.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        isAlan = IsAlan.query.filter_by(username=username).first()

        if isAlan and check_password_hash(isAlan.password, password):
            session['user_id'] = isAlan.id
            return redirect(url_for('dashboard_isAlan'))
        else:
            error = 'Kullanıcı adı veya şifre yanlış.'
            return render_template('login.html', error=error)

    return render_template('login.html')
#İşVeren Login işlemini yapar.
@app.route('/login_isVeren', methods=['GET', 'POST'])
def login_isVeren():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_Veren = IsVeren.query.filter_by(username=username).first()

        if is_Veren and check_password_hash(is_Veren.password, password):
            session['user_id'] = is_Veren.id
            return redirect(url_for('dashboard_isVeren'))
        else:
            error_veren = 'Kullanıcı adı veya şifre yanlış.'
            return render_template('login.html', error_veren=error_veren)

    return render_template('login_isVeren.html')

#İşAlan Kayıt işlemini yapar.
@app.route('/register_isAlan', methods=['GET', 'POST'])
def register_isAlan():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Kullanıcı adının benzersiz olup olmadığını kontrol et
        existing_user = IsAlan.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register_isAlan.html', error='Bu kullanıcı adı zaten kullanılıyor.')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_isAlan = IsAlan(username=username, password=hashed_password)

        db.session.add(new_isAlan)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register_isAlan.html')
#İşVeren Kayıt işlemini yapar.
@app.route('/register_isVeren', methods=['GET', 'POST'])
def register_isVeren():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Kullanıcı adının benzersiz olup olmadığını kontrol et
        existing_user = IsVeren.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register_isVeren.html', error='Bu kullanıcı adı zaten kullanılıyor.')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_isVeren = IsVeren(username=username, password=hashed_password)

        db.session.add(new_isVeren)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register_isVeren.html')

#İşAlan Dashboard'una gidiş işlemini yapar.
@app.route('/dashboard_isAlan')
def dashboard_isAlan():
    if 'user_id' in session:
        user_id = session['user_id']
        user = IsAlan.query.filter_by(id=user_id).first()
        return render_template('dashboard_isAlan.html', user=user)
    else:
        return redirect(url_for('login'))
#İşVeren Dashboard'una gidiş işlemini yapar.
@app.route('/dashboard_isVeren')
def dashboard_isVeren():
    if 'user_id' in session:
        user_id = session['user_id']
        user = IsVeren.query.filter_by(id=user_id).first()
        return render_template('dashboard_isVeren.html', user=user)
    else:
        return redirect(url_for('login'))
#İşVerenin iş oluşturmasını sağlar.
@app.route('/create_job_listing', methods=['GET', 'POST'])
def create_job_listing():
    if 'user_id' in session and request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = float(request.form['price'])

        isAlan_id = session['user_id']
        new_job_listing = JobListing(title=title, description=description, price=price, isAlan_id=isAlan_id)

        db.session.add(new_job_listing)
        db.session.commit()
        return redirect(url_for('dashboard_isVeren'))

    return render_template('create_job_listing.html')
    
#İşleri listeleme    
@app.route('/job_listings')
def job_listings():
    job_listings = JobListing.query.all()
    return render_template('job_listings.html', job_listings=job_listings)
    
#İlan Kabul.
@app.route('/accept_job_listing/<int:job_listing_id>', methods=['GET', 'POST'])
def accept_job_listing(job_listing_id):
    if 'user_id' in session:
        isAlan_id = session['user_id']
        job_listing = JobListing.query.get_or_404(job_listing_id)

        if request.method == 'POST':
            # İlanın durumunu "Kabul Edildi" olarak güncelleyin
            job_listing.status = 'Accepted'

            # İş başvurusunu kabul eden işverenin ilanları arasına ekleyin
            isAlan = IsAlan.query.get_or_404(isAlan_id)
            job_application = JobApplication(
                cover_letter="Kabul Edildi",  # Bu kısmı istediğiniz bir metinle doldurabilirsiniz
                is_Veren_id=job_listing.isAlan_id,
                job_listing_id=job_listing.id
            )
            isAlan.applications.append(job_application)

            # İş alanın hesabına para ekleyin
            isAlan.money += job_listing.price

            db.session.commit()

            return redirect(url_for('dashboard_isAlan'))

        return render_template('accept_job_listing.html', job_listing=job_listing)
    else:
        return redirect(url_for('login'))

#Çıkış İşlemi.
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/accepted_job_listings')
def accepted_job_listings():
    if 'user_id' in session:
        user_id = session['user_id']
        user = IsAlan.query.filter_by(id=user_id).first()

        accepted_job_listings = JobListing.query.filter_by(isAlan_id=user_id, status='Accepted').all()

        return render_template('accepted_job_listings.html', user=user, accepted_job_listings=accepted_job_listings)
    else:
        return redirect(url_for('login'))

#İşVerenin ilanlarını listeleme
@app.route('/my_job_listings')
def my_job_listings():
    if 'user_id' in session:

        user_id = session['user_id']
        user = get_user_by_id(user_id)
        job_listings = JobListing.query.filter_by(status='Kabul Edilmedi').all()
        return render_template('my_job_listings.html', user=user, job_listings=job_listings)
    else:
        return redirect(url_for('login'))


def get_user_by_id(user_id):
    return IsAlan.query.filter_by(id=user_id).first()

#İlan Silme
@app.route('/delete_job_listing', methods=['POST'])
def delete_job_listing():
    if 'user_id' in session and request.method == 'POST':
        # Formdan gelen iş ilanı ID'sini al
        job_listing_id = request.form['job_listing_id']
        
        # Kullanıcı giriş yapmışsa ve iş ilanı ID'si mevcutsa, ilanı sil
        user_id = session['user_id']
        job_listing = JobListing.query.get(job_listing_id)

        if job_listing and job_listing.isAlan_id == user_id:
            db.session.delete(job_listing)
            db.session.commit()

    return redirect(url_for('my_job_listings'))

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SECRET_KEY'] = 'your_secret_key'
    db.init_app(app)

    return app
#Reddit Transaction İşlemi.            
@app.route('/check_comments', methods=['POST'])
def check_comments():
    user_id = session.get('user_id')  # session.get kullanımı
    if user_id is None:
        flash("User not authenticated", "error")
        return redirect(url_for("login"))  # Örnek olarak login sayfasına yönlendirme

    isAlan = get_user_by_id(user_id)
    
    redditUserName = request.form.get('reddit_username')  # request.form.get kullanımı
    
    print(redditUserName)
        
    reddit = praw.Reddit(
        client_id='sGlaUWH86Na_0PAbFe7h9A',
        client_secret='Mj-fkpiHVbNd9BA6iJzeYL2wvG7cHQ',
        user_agent='proje'
    )
    url = f"https://www.reddit.com/user/hakancabbarr/comments/18yj6jf/yazilim_sinama_proje/"
    
    submission = reddit.submission(url=url)
    
    for comment in submission.comments.list():
        if comment.author.name == redditUserName:
            if not isAlan.isTransaction:
                isAlan.money += 200
                isAlan.isTransaction = True 
                db.session.commit()
                flash("200TL bakiyenize eklendi.", "success")
                print(f"200TL bakiyenize eklendi. New balance: {isAlan.money}")
                return redirect(url_for("dashboard_isAlan"))  # Örnek olarak dashboard sayfasına yönlendirme
            else:
                flash("Zaten Alınmış.", "info")
                print("Already collected.")
                return redirect(url_for("dashboard_isAlan"))  # Örnek olarak dashboard sayfasına yönlendirme

    flash("Kullanıcı Adı Bulunamadı.", "warning")
    print("Kullanıcı Adı Bulunamadı.")
    return redirect(url_for("dashboard_isAlan"))  # Örnek olarak dashboard sayfasına yönlendirme    


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)