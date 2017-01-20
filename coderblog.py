from flask import Flask, render_template, flash, redirect, session, g
from flask_login import login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS
import os
from flask_login import LoginManager
from flask_openid import OpenID
from hashlib import md5
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length
from flask import request, url_for

class CommentForm(FlaskForm):
    body = TextAreaField('body', validators=[Length(min=0, max=400)])


class PostForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    body = TextAreaField('body', validators=[Length(min=0, max=100000)])
    category = SelectField(u'Programming Language', choices=[('Technology', 'Technology'), ('Social', 'Social'), ('Random thoughts', 'Random thoughts')])

class EditForm(FlaskForm):
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=2000)])

    def __init__(self, original_nickname, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user != None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True

app = Flask(__name__,static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = "billwangwork"
app.config['WTF_CSRF_ENABLED'] = True
# mail server settings
MAIL_SERVER = '108.177.96.108'
MAIL_PORT = 465
MAIL_USERNAME = 'yunchuwang5@gmail.com'
MAIL_PASSWORD = 'nininini'
# administrator list
ADMINS = ['yunchuwang5@gmail.com']
basedir = os.path.abspath(os.path.dirname(__file__))
CORS(app)
lm = LoginManager()
lm.init_app(app)
oid = OpenID(app, os.path.join(basedir, 'tmp'))
lm.login_view = 'login'
db = SQLAlchemy(app)
# pagination
POSTS_PER_PAGE = 4

class LoginForm(FlaskForm):
    openid = StringField('openid', validators=[DataRequired()],render_kw={"placeholder": "openid.aol.com/aolemailnamebefore@"})
    remember_me = BooleanField('remember_me', default=False)

class Category(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   name = db.Column(db.String(60),index=True, unique=True)

   def __init__(self, name):
       self.name = name

   def __repr__(self):
       return '<Category %r>' % self.name

class Blog(db.Model):
   blog_id = db.Column( db.Integer, primary_key = True)
   title = db.Column(db.String(80))
   body = db.Column(db.Text)
   category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
   category = db.relationship('Category', backref=db.backref('blogs', lazy='dynamic'))
   user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   author = db.relationship('User', backref=db.backref('blogs', lazy='dynamic'))
   pub_date = db.Column(db.DateTime)

   def __init__(self, author, title, category, body, pub_date=None):
       self.author = author
       self.title = title
       self.category = category
       self.body = body
       if pub_date is None:
           pub_date = datetime.utcnow()
       self.pub_date = pub_date

   def __repr__(self):
       return '<Blog %r>' % self.title

class User(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   nickname = db.Column(db.String(64), index=True, unique=True)
   email = db.Column(db.String(120), index=True, unique=True)
   about_me = db.Column(db.Text)

   @staticmethod
   def make_unique_nickname(nickname):
       if User.query.filter_by(nickname=nickname).first() is None:
           return nickname
       version = 2
       while True:
           new_nickname = nickname + str(version)
           if User.query.filter_by(nickname=new_nickname).first() is None:
               break
           version += 1
       return new_nickname

   def __init__(self, nickname, email):
       self.nickname = nickname
       self.email = email

   @property
   def is_authenticated(self):
       return True

   @property
   def is_active(self):
       return True

   @property
   def is_anonymous(self):
       return False

   def avatar(self, size):
       return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

   def getbgurl(self):
       pass

   def get_id(self):
       try:
           return unicode(self.id)
       except NameError:
           return str(self.id)

   def __repr__(self):
       return '%r' % (self.nickname)

class Comments(db.Model):
   comment_id = db.Column( db.Integer, primary_key = True)
   author = db.Column(db.String(60))
   body = db.Column(db.Text)
   blog_id = db.Column(db.Integer, db.ForeignKey('blog.blog_id'))
   blog = db.relationship('Blog', backref=db.backref('comments', lazy='dynamic'))
   user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   author = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))
   pub_date = db.Column(db.DateTime)


   def __init__(self, author, body, blog, pub_date=None):
       self.author = author
       self.body = body
       if pub_date is None:
           pub_date = datetime.utcnow()
       self.blog = blog
       self.pub_date = pub_date

if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'microblog failure',
                                  credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
# db.drop_all()
# db.create_all()
# admin = User.query.filter_by(nickname='Bill Wang').first()
# py = Category('Technology')
# py2 = Category('Social')
# py3 = Category('Random thoughts')
# db.session.add(py)
# db.session.add(py2)
# db.session.add(py3)
# p = Blog(admin, 'Python is pretty cool', py, "Hello World", None)
# p2 = Blog(admin, 'Python is pretty awesome', py, "Hello World2", None)
# p3 = Blog(admin, 'Python is pretty great', py, "Hello World3", None)
# p4 = Blog(admin, 'Python is pretty nice', py, "Hello World4", None)
# db.session.add(admin)
# db.session.add(py)
# db.session.add(p)
# db.session.add(p2)
# db.session.add(p3)
# db.session.add(p4)
# db.session.commit()
# print (admin.blogs.all())
# print (p.category)

@app.before_request
def before_request():
    g.user = current_user

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
# @login_required
def index():
    return render_template('base.html',title='index')

@app.route('/blog')
@app.route('/blog/<int:page>', methods=['GET', 'POST'])
@login_required
def blog(page=1):
    blogs = Blog.query.order_by(Blog.pub_date.desc()).paginate(page, POSTS_PER_PAGE, False)
    return render_template('blog.html',title=None,posts=blogs)

@app.route('/contact')
def contact():
    return render_template('contact.html',title='index')

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html',
                           title='Sign In',
                           form=form)
@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>/<string:scrollplace>')
@login_required
def user(nickname,scrollplace,page=1):
    form = EditForm(g.user.nickname)
    form.nickname.data = g.user.nickname
    form.about_me.data = g.user.about_me
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    posts = user.blogs.order_by(Blog.pub_date.desc()).paginate(page, POSTS_PER_PAGE, False)
    # print posts.items
    print scrollplace
    return render_template('user.html',
                           user=user,
                           posts=posts, form=form, scroll=scrollplace)

@app.route('/detailview/<int:bid>')
@login_required
def detailview(bid):
    blog = Blog.query.filter_by(blog_id=bid).first()
    form = CommentForm()
    if blog == None:
        flash('blog %s not found.' % bid)
        return redirect(url_for('index'))
    comments = blog.comments.all()
    return render_template('blogdetailview.html', blog=blog, comments= comments, form=form)

@app.route('/comment/<int:bid>', methods=['POST'])
@login_required
def comment(bid):
    form = CommentForm()
    if form.validate_on_submit():
        blog = Blog.query.filter_by(blog_id=bid).first()
        comment = Comments(g.user, form.body.data, blog)
        db.session.add(comment)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('detailview', bid=bid))
# @app.route('/comment/<int:cid>', methods=['GET', 'POST'])
# @login_required
# def comment(cid):
#     form = CommentForm()
#     if request.method == 'GET':
#
#     else:

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/home')
def home():
    return render_template('home.html',title='index')

@app.route('/about')
def about():
    return render_template('about.html',title='index')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/edit', methods=['POST','GET'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', nickname=g.user.nickname))

@app.route('/compose', methods=['POST','GET'])
@login_required
def compose():
    form = PostForm()
    if not form.validate_on_submit():
        return render_template('compose.html', title='index', form=form)
    else:
        print form.category.data
        category1 = Category.query.filter_by(name=form.category.data).first()
        post = Blog(author=g.user,title=form.title.data, category=category1, body= form.body.data, pub_date = None)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index', title='index'))

if __name__ == '__main__':
    app.run(port=5555)
