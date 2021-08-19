from flask import Flask, render_template, request, redirect, sessions
from flask.helpers import flash, make_response, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import session
from werkzeug.wrappers import response

db_user = "root"
db_pass = ""
db_name = "my_notes"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://{}:{}@localhost/{}".format(db_user, db_pass, db_name)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class Users(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    username=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(256))
    name=db.Column(db.String(100))

    def __init__(self,username,password,name):
        self.username=username
        self.password=password
        self.name=name

    @staticmethod
    def exists(username)->bool:
         # "select * from users where username=? limit 1;"
         user=Users.get_user_by_username(username)
         return user!=None

    @staticmethod
    def get_user_by_username(username):
        return Users.query.filter_by(username=username).first()


    def __str__(self) -> str:
        return f"{self.username}"
        
@app.route




@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template("login.html")
    
    if request.method=='POST':
        form=request.form
        username=form.get('username',None)
        password=form.get('password',None)
        if(Users.exists(username=username)):
            user=Users.get_user_by_username(username)
            if(check_password_hash(user.password,password)):
                session['user']=user.id
                flash("You are logged in","success")
                response=make_response(url_for('index'))
                if(form.get('remember_me',None)):
                    token=Token.create_token(user.id)
                    response.set_cookie('token',token,max_age=60*30)
                return response
            else:
                flash("Incorrect password","info")
                return redirect(url_for('login'))
        else:
            flash("Incorrect user credentials","info")
            return redirect(url_for('login'))


        
@app.route("/logout")
@login_required
def logout():
    response=make_response(redirect(url_for('login')))
    if 'user' in session:
        user_id=sessioon.pop('user')
        response.set_cookie('token','',max_age=-)
        db.session.execute("delete from token where user_id=:user_id",{"user_id":user_id})
        db.session.commit()
    flash("Logged Out Successfully","success")
    return response


@app.route("/")
@login_required
def index():
    notes_sql = "Select * from notes where deleted_at is null"
    notes = db.session.execute(notes_sql)
    # print(type(notes))
    # for note in notes:
    #     print(note)
    return render_template('index.html', notes=notes)


@app.route("/create", methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        folders_sql = "Select * from folder"
        folders = db.session.execute(folders_sql)
        return render_template('create.html', folders=folders)
    elif request.method == 'POST':

        form = request.form
        params = {
            "title": form['title'],
            "content": form.get('content', ''),
            "folder_id": form.get('folder_id', ''),
        }
        if not params['folder_id']:
            params['folder_id'] = None

        sql = f"insert into notes (`title`, `content`, `folder_id`) values(:title, :content, :folder_id)"

        db.session.execute(sql, params)
        db.session.commit()
        return redirect(url_for('index'))


@app.route("/update/<int:id>", methods=['GET', 'POST'])
@login_required
def update(id):

    if request.method == 'GET':

        folders_sql = "Select * from folder"
        folders = db.session.execute(folders_sql)
        note_sql = "Select * from notes where id= :id and deleted_at is null"
        note = db.session.execute(note_sql, {"id": id}).fetchone()

        if not note:
           return redirect(url_for('error', code = 404))

        return render_template('update.html', folders=folders, note=note)
    elif request.method == 'POST':

        form = request.form
        params = {
            "title": form['title'],
            "content": form.get('content', ''),
            "folder_id": form.get('folder_id', ''),
            "id": id,
        }
        if not params['folder_id']:
            params['folder_id'] = None

        sql = f"update notes set title=:title, content=:content, folder_id=:folder_id where id=:id"

        res = db.session.execute(sql, params)
        db.session.commit()
        return redirect(url_for('index'))


@app.route("/delete",methods=['POST'])
@login_required
def delete():

    if request.method=='POST':
        try:
            id=request.form.get('id',None)
            if not id:
                return redirect('error',code=404)
            sql = f"update notes set deleted_at =now() where id=:id"
            db.session.execute(sql, {"id": id})
            db.session.commit()
        except (Exception):
            return redirect(url_for('error',code=404))
        return render_template(url_for('index')) 


@app.route("/thrash")
def thrash():
    pass


@app.route("/error/<code>")
def error(code):
    codes = {
        "404": "404 Not Found"
    }
    return render_template("error.html", message = codes.get(code, "Invalid request"))


if __name__ == "__main__":
    app.run(debug=True)
