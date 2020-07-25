from flask import Flask, request
import socket
import ssl
import json

# 客户端信息
client_id = "f9e1e112f14b401fb8cc"
client_secret = "dd0cf56837aabf1361c99b3d47fc342f4c729bae"
redirect_url = "http://localhost:5000/callback/login"
# 授权码接口
api = "https://github.com/login/oauth/authorize?client_id=" + client_id + "&redirect_uri=" + redirect_url
# 令牌的接口
token = "/login/oauth/access_token?client_id=" + client_id + "&client_secret=" + client_secret + "&code="

app = Flask(__name__)


@app.route('/')
def index():
    return '<a href="%s">sign in by github</a>' % api


@app.route('/callback/login')
def test():
    code = request.args.get('code')
    result = getinfo(code)
    print(result)
    return "success sign in as %s" % result['login']


def getinfo(code):
    """获取令牌"""
    url = token + code
    s = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    s.connect(('github.com', 443))
    string = 'POST %s HTTP/1.1\r\nHost: github.com\r\naccept: application/json\r\nConnection: close\r\n\r\n' % url
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
    data = data.split(b'\r\n\r\n')[1]
    data = data.split(b'\r\n')[1].decode()
    result = json.loads(data)
    access_token = result['access_token']

    """获取用户信息"""
    s = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    s.connect(('api.github.com', 443))
    string = 'GET /user HTTP/1.1\r\nHost: api.github.com\r\naccept: application/json\r\n' \
             'Connection: close\r\nUser-Agent: Mozilla/5.0\r\nAuthorization: token %s\r\n\r\n' % access_token
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
    result = json.loads(data.decode())
    return result


if __name__ == '__main__':
    app.run(debug=True)
