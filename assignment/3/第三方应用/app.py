from flask import Flask, request, render_template, make_response, redirect, url_for, send_file
import socket
import json, os
import requests

# 客户端信息
client_id = "f9e1e112f14b401fb8cc"
redirect_url = "http://localhost:8080/callback/login"
# 授权码接口
origin_host = "http://localhost:5000"
api = "http://localhost:5000/authorize?client_id=" + client_id + "&redirect_uri=" + redirect_url
# 令牌的接口
gettoken = "/token?client_id=" + client_id + "&redirect_uri=" + redirect_url + "&code="

app = Flask(__name__)


@app.route('/')
def index():
    cookies = request.cookies.get('data')
    if cookies is None:
        return '<a href="%s">sign in by my app</a>' % api
    else:
        T = cookies.split('|')
        name = T[0]
        access_token = T[1]
        result = getuserinfo(access_token)
        images = result['images']
        return render_template('index.html', name=name, images=images)


@app.route('/callback/login')
def test():
    code = request.args.get('code')
    result, access_token = getinfo(code)
    print(result)
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('data', result['name'] + '|' + access_token)  # 这里应该用redis存储name-token
    return resp


@app.route('/third/upload/', methods=['GET', 'POST'])
def upload():
    url = "http://localhost:5000/api/upload"
    f = request.files['file']
    filename = f.filename
    f.save(filename)
    path = './'+filename
    headers = {"access_token": GetTokenFromCookie()}
    files = {"files": (filename, open(path, 'rb'))}
    reply = requests.get(url, data=None, headers=headers, files=files)
    return reply.content


@app.route('/third/get/<filename>')
def get(filename):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 5000))
    string = 'GET /api/getimg/%s HTTP/1.1\r\nHost: localhost:5000\r\naccess_token: %s\r\n\r\n' % (filename, GetTokenFromCookie())
    s.send(string.encode())
    data = []
    while True:
        a = s.recv(1024)
        if a:
            data.append(a)
        else:
            break
    data = b''.join(data)
    data = data.split(b'\r\n\r\n')[1]
    s.close()
    return data


@app.route('/third/delete/<filename>')
def delete(filename):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 5000))
    string = 'GET /api/delete/%s HTTP/1.1\r\nHost: localhost:5000\r\naccess_token: %s\r\n\r\n' % (filename, GetTokenFromCookie())
    s.send(string.encode())
    data = []
    while True:
        a = s.recv(1024)
        if a:
            data.append(a)
        else:
            break
    data = b''.join(data)
    data = data.split(b'\r\n\r\n')[1].decode()
    s.close()
    print(data)
    return '%s' % data


@app.route('/third/download/<filename>')
def download(filename):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 5000))
    string = 'GET /api/download/%s HTTP/1.1\r\nHost: localhost:5000\r\naccess_token: %s\r\n\r\n' % (filename, GetTokenFromCookie())
    s.send(string.encode())
    data = []
    while True:
        a = s.recv(1024)
        if a:
            data.append(a)
        else:
            break
    data = b''.join(data)
    data = data.split(b'\r\n\r\n')[1]
    s.close()
    with open(filename, 'wb') as f:
        f.write(data)
    return send_file(filename, as_attachment=True)



def GetTokenFromCookie():
    return request.cookies.get('data').split('|')[1]


def getinfo(code):
    access_token = getusertoken(code)
    result = getuserinfo(access_token)
    return result, access_token


def getusertoken(code):
    """获取令牌"""
    url = gettoken + code
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 5000))
    string = 'POST %s HTTP/1.1\r\nHost: localhost:5000\r\naccept: application/json\r\nConnection: close\r\n\r\n' % url
    s.send(string.encode())
    data = []
    while True:
        a = s.recv(1024)
        if a:
            data.append(a)
        else:
            break
    s.close()
    data = b''.join(data)
    data = data.split(b'\r\n\r\n')[1].decode()
    result = json.loads(data)
    access_token = result['access_token']
    return access_token


def getuserinfo(access_token):
    """获取用户信息"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 5000))
    string = 'GET /getinfo HTTP/1.1\r\nHost: localhost:5000\r\naccept: application/json\r\n' \
             'Connection: close\r\naccess_token: %s\r\n\r\n' % access_token
    print(string)
    s.send(string.encode())
    data = []
    while True:
        a = s.recv(1024)
        if a:
            data.append(a)
        else:
            break
    print("获取用户信息部分", data)
    data = b''.join(data)
    data = data.split(b'\r\n\r\n')[1]
    s.close()
    result = json.loads(data.decode())
    return result


if __name__ == '__main__':
    app.run(debug=True, port=8080)
