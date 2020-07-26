from flask import Flask, request, flash, url_for, redirect, render_template, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from hashlib import sha1
import datetime, time
import os

the_secret_key = 'zot'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1/album'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'linyier'
db = SQLAlchemy(app)


class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    passwd = db.Column(db.String(50))

    all_images = db.relationship('images', backref='the_user')


class images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(200), unique=True)


@app.route('/')
def index():
    if identify():
        return redirect(url_for('control'))
    else:
        return redirect(url_for('signin'))


@app.route('/control/')
def control():
    if identify():
        the_user = getuser()
        url = my_sha1(str(the_user.id)+the_secret_key)
        return render_template('control.html', the_user=the_user, images=the_user.all_images, user_url=url)
    else:
        return redirect(url_for('signin'))


@app.route('/uploader/', methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        if identify():
            the_user = getuser()
            the_id = str(the_user.id)
            f = request.files['file']
            t = f.filename.split('.')[-1]
            filename = my_sha1(the_id + str(time.time())) + '.' + t
            f.save('./static/images/' + my_sha1(the_id + the_secret_key) + '/' + filename)

            add_ = images(owner_id=the_user.id, name=filename)
            db.session.add(add_)
            db.session.commit()

            flash('上传成功')
            return render_template('control.html', the_user=the_user)
        else:
            return "未登录错误"


@app.route('/delete/<filename>')
def delete(filename):
    if identify():
        T = getuser()
        url = my_sha1(str(T.id)+the_secret_key)
        os.remove('./static/images/'+url+'/'+str(filename))
        delete_which = images.query.filter(images.name == filename).first()
        db.session.delete(delete_which)
        db.session.commit()
        return "删除成功"


@app.route('/download/<filename>')
def download(filename):
    if identify():
        T = getuser()
        url = my_sha1(str(T.id)+the_secret_key)
        path = './static/images/'+url+'/'+str(filename)
        return send_file(path, as_attachment=True)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form['username']
        passwd1 = request.form['password1']
        for i in users.query.all():
            if i.name == username:
                flash('用户名\'%s\'已被注册' % username)
                return redirect(url_for('register'))
        add_user = users(name=username, passwd=passwd1)
        db.session.add(add_user)
        db.session.commit()
        temp_user = users.query.filter(users.name == username).first()
        os.mkdir('./static/images/' + my_sha1(str(temp_user.id) + the_secret_key))
        flash('注册成功')
        return redirect(url_for('signin'))


@app.route('/signin/', methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('signin.html')
    else:
        username = request.form['username']
        password = request.form['password1']
        the_user = users.query.filter(users.name == username).first()
        if the_user is None:
            flash('用户名不存在')
            return render_template('signin.html')
        if the_user.passwd == password:
            the_id = str(the_user.id)
            the_time = str(datetime.datetime.now() + datetime.timedelta(days=1))
            _secret_key = my_sha1(the_id + password + the_time + the_secret_key)
            resp = make_response(redirect(url_for('control')))
            resp.set_cookie('data', the_id + '/' + the_time + '/' + _secret_key)
            return resp
        else:
            # 匹配失败
            flash('密码错误')
            return render_template('signin.html')




def identify():
    cookies = request.cookies.get('data')
    if not cookies:
        return False
    datas = cookies.split('/')
    if len(datas) != 3:  # 不是服务器设置的cookies
        return False
    time = datas[1]
    if str(datetime.datetime.now()) > time:
        return False
    id = int(datas[0])
    sh = datas[2]
    result = users.query.filter(users.id == id).first()
    if result:
        calc_key = my_sha1(datas[0] + result.passwd + time + the_secret_key)
        if sh == calc_key:
            return True
        else:
            return False
    else:
        return False


def my_sha1(string):
    a = sha1()
    a.update(string.encode('utf-8'))
    return a.hexdigest()


def getuser():
    return users.query.filter(users.id == int(request.cookies.get('data')[0])).first()


if __name__ == '__main__':
    app.run(debug=True)
