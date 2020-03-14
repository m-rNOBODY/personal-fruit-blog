from flask import Flask, render_template, url_for, request, redirect,flash
from forms import registrationform, loginform
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY']= '2aa8079ef7d91c429a6ec829948bb53b'
db = SQLAlchemy(app)
bcrypt= Bcrypt(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))

class user(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(20), unique= True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts= db.relationship('add', backref = 'author', lazy=True)

    def __repr__(self):
        return f"user('{self.username}','{self.email}')"

class add(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable= False)

    def __repr__(self):
       return f"add('{self.name}','{self.date_created}')"


@app.route('/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('Post'))
    form = registrationform()
    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = user(username=form.username.data, email= form.email.data, password= hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('Post'))


    return render_template('register.html', title='register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('Post'))
    form = loginform()
    if form.validate_on_submit():
        user_login= user.query.filter_by(email=form.email.data).first()
        if user_login and bcrypt.check_password_hash(user_login.password, form.password.data):
            login_user(user_login)
            return redirect(url_for('Post'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html', title ='login', form =form)

@app.route('/Post', methods=['GET','POST'])
def Post():

    if request.method == 'POST':
        name_of_fruit = request.form['fruit_name']
        fruit_content = request.form['content']
        new_fruit = add(name=name_of_fruit, content=fruit_content, author= current_user)
        try:
            db.session.add(new_fruit)
            db.session.commit()
            return redirect('/Post')
        except:
            return "There was an an error."
    else:
        fruits = add.query.order_by(add.date_created).all()
        return render_template('Post.html', variable=fruits)

@app.route('/delete/<int:id>')
def delete(id):
    fruit_to_delete = add.query.get_or_404(id)

    try:
        db.session.delete(fruit_to_delete)
        db.session.commit()
        return redirect('/Post')
    except:
        return "There was an error"

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('register'))

if __name__ == "__main__":
    app.run(debug=True)