from flask import Flask, request, flash, url_for, redirect, render_template, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from hashlib import sha1
import datetime
import time
import os
import json
import redis

the_secret_key = 'zot'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1/album'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'linyier'
db = SQLAlchemy(app)

r = redis.StrictRedis(host='localhost', port=6379, db=0)

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
        return redirect(url_for('signin', rel='local'))


@app.route('/control/')
def control():
    if identify():
        the_user = getuser()
        url = my_sha1(str(the_user.id) + the_secret_key)
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
            return redirect(url_for('control'))
        else:
            return "未登录错误"


@app.route('/delete/<filename>')
def delete(filename):
    if identify():
        T = getuser()
        url = my_sha1(str(T.id) + the_secret_key)
        os.remove('./static/images/' + url + '/' + str(filename))
        delete_which = images.query.filter(images.name == filename).first()
        db.session.delete(delete_which)
        db.session.commit()
        return "删除成功"


@app.route('/download/<filename>')
def download(filename):
    if identify():
        T = getuser()
        url = my_sha1(str(T.id) + the_secret_key)
        path = './static/images/' + url + '/' + str(filename)
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
        return redirect(url_for('signin', rel='local'))


@app.route('/signin/<rel>', methods=['GET', 'POST'])
def signin(rel, ags=None):
    if request.method == 'GET':
        ags = request.args.get('ags')
        return render_template('signin.html', jump=rel, ags=ags)
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
            if rel == 'local':
                resp = make_response(redirect(url_for('control')))
                resp.set_cookie('data', the_id + '/' + the_time + '/' + _secret_key)
                return resp
            else:
                print("abc", request.form['ags'])
                resp = make_response(redirect(url_for('authorize', arg=request.form['ags'])))
                resp.set_cookie('data', the_id + '/' + the_time + '/' + _secret_key)
                return resp
        else:
            # 匹配失败
            flash('密码错误')
            return render_template('signin.html')


"""提供oauth"""


@app.route('/authorize', methods=['GET', 'POST'])
def authorize(arg=None):
    if request.method == 'GET':
        client_id = request.args.get('client_id')
        redirect_uri = request.args.get('redirect_uri')
        ags = request.args.get('arg')
        if ags:
            arg = ags
        if arg is not None:
            temp = arg.split('_', 1)
            client_id = temp[0]
            redirect_uri = temp[1]
        if client_id is None or redirect_uri is None:
            return "API调用错误（错误的url）"
        if identify():
            return render_template('authorize.html', client_id=client_id, redirect_uri=redirect_uri)
        else:
            return redirect(url_for('signin', rel='auth', ags=client_id+'_'+redirect_uri))
    else:
        the_user = getuser()
        client_id = request.form['client_id']
        redirect_uri = request.form['redirect_uri']
        t = request.form['time']
        scope = request.form['scope']
        code = my_sha1(str(time.time()))
        r.hmset(code, {'client_id': client_id, 'redirect_uri': redirect_uri,
                       'time': t, 'scope': scope, 'id': the_user.id})
        r.expire(code, 100)
        return redirect(redirect_uri+"?code="+code)


@app.route('/token', methods=['GET', 'POST'])
def token():
    if request.method == 'POST':
        client_id = request.args.get('client_id')
        redirect_uri = request.args.get('redirect_uri')
        code = request.args.get('code')
        if not code or not client_id or not redirect_uri:
            return "错误调用"
        else:
            dic = r.hgetall(code)
            if not dic:
                return "授权码错误/失效"
            if dic[b'client_id'] == client_id.encode() and dic[b'redirect_uri'] == redirect_uri.encode():
                the_id = dic[b'id'].decode()
                the_scope = dic[b'scope'].decode()
                the_token = my_sha1(str(the_id)+str(time.time()))
                r.hmset(the_token, {'id': the_id, 'scope': the_scope})

                keep_time = int(dic[b'time'].decode())*86400
                r.expire(the_token, keep_time)

                # r.delete(code)
                response = {'access_token': the_token, 'expires_in': keep_time, 'scope': the_scope}

                return json.dumps(response)
    else:
        return "method error"


@app.route('/getinfo')
def getinfo():
    the_token = request.headers["access_token"]
    print("收到令牌", the_token)
    dic = r.hgetall(the_token)
    the_id = dic[b'id'].decode()
    the_user = users.query.filter(users.id == the_id).first()
    the_images = []
    for i in the_user.all_images:
        the_images.append(i.name)
    response = {'id': the_user.id, 'name': the_user.name, 'images': the_images}
    return json.dumps(response)


@app.route('/api/getimg/<filename>')
def getimg(filename):
    the_token = request.headers["access_token"]
    msg = r.hgetall(the_token)
    if msg is None:
        return "令牌错误/过期"
    else:
        the_id = str(msg[b'id'].decode())
        path = my_sha1(the_id+the_secret_key)
        with open('./static/images/'+path+'/'+filename, 'rb') as f:
            data = f.read()
        return data


@app.route('/api/upload/')
def ApiUpload():
    f = request.files['files']
    t = f.filename.split('.')[-1]

    print(f.filename)

    the_token = request.headers["access_token"]
    msg = r.hgetall(the_token)
    if msg is None:
        return "令牌错误/过期"
    else:
        the_id = str(msg[b'id'].decode())
        filename = my_sha1(the_id + str(time.time())) + '.' + t
        f.save('./static/images/' + my_sha1(the_id + the_secret_key) + '/' + filename)

        add_ = images(owner_id=int(the_id), name=filename)
        db.session.add(add_)
        db.session.commit()
    return 'success'


@app.route('/api/download/<filename>')
def ApiDownload(filename):
    the_token = request.headers["access_token"]
    msg = r.hgetall(the_token)
    if msg is None:
        return "令牌错误/过期"
    else:
        the_id = str(msg[b'id'].decode())
        url = my_sha1(the_id + the_secret_key)
        path = './static/images/' + url + '/' + str(filename)
        return send_file(path, as_attachment=True)


@app.route('/api/delete/<filename>')
def ApiDelete(filename):
    the_token = request.headers["access_token"]
    msg = r.hgetall(the_token)
    if msg is None:
        return "令牌错误/过期"
    else:
        the_id = str(msg[b'id'].decode())
        scope = str(msg[b'scope'].decode())
        if scope == 'r':
            return "权限不足"
        url = my_sha1(the_id + the_secret_key)
        path = './static/images/' + url + '/' + str(filename)
        os.remove(path)
        remove = images.query.filter(images.name == filename).first()
        db.session.delete(remove)
        db.session.commit()
        return 'success'


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
