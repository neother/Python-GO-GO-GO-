# virtual enviroment path C:\Users\moochergaga\Envs\Pyflask\Scripts\
# activate the envi first
from flask import Flask
from flask import make_response
from flask import redirect
from flask import abort
from flask_script import Manager
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from flask_mail import Mail
# print(os.path.dirname(__file__))
# print(os.path.abspath(__file__))
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)


app.config['SECRET_KEY'] = 'hardtoguess'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMYCOMMITONTEARDOWN'] = True

app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
#app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = '401316161@qq.com'
app.config['MAIL_PASSWORD'] = ''

mail = Mail(app)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
#manager = Manager(app)


class Role(db.Model):
    __tablename__ = 'roles'

    #id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), primary_key=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):

        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    #id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', name=session.get('name'),
                           form=form, current_time=datetime.utcnow(), known=session.get('known', False))


@app.route('/user/<id>')
def get_user(id):

    return render_template('user.html', name=id)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(port=8000, debug=True)
