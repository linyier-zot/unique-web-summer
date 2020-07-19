import mysql.connector

BuiltAttr = ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__',
             '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__',
             '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__',
             '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '__tablename__']

"""only mysql"""


class DB(object):
    def __init__(self, user, password, database):
        self.session = None
        self.user = user
        self.password = password
        self.database = database
        # self.Connect()

    def Connect(self):
        self.session = mysql.connector.connect(
            user=self.user,
            password=self.password,
            database=self.database
        )

    def CreateTable(self, obj):
        tableName = getTableName(obj)
        columns = []
        for i in dir(obj):
            if i not in BuiltAttr:
                columns.append("`%s` %s" % (i, getattr(obj, i)))

        sql = "CREATE TABLE IF NOT EXISTS `%s` (%s) CHARSET=utf8 " % (tableName, ','.join(columns))
        self.Execute(sql)

    def Create(self, obj):
        columns, values = getInfo(obj)
        sql = "INSERT INTO %s (%s) values (%s) " % (getTableName(obj), ','.join(columns), ','.join(values))
        print(sql)
        self.Execute(sql)

    def Update(self, obj, whereExpression):
        columns, values = getInfo(obj)
        kv = []
        for i, j in columns, values:
            if j != '':
                kv.append("%s='%s'" % (i, j))
        sql = "UPDATE %s SET %s WHERE %s" % (getTableName(obj), ','.join(kv), whereExpression)
        self.Execute(sql)

    def Find(self, whereExpression, obj):
        sql = "SELECT * FROM %s WHERE %s" % (getTableName(obj), whereExpression)
        cursor = self.session.cursor()
        cursor.execute(sql)
        r = cursor.fetchall()
        cursor.close()

        final_result = []
        for i in r:
            final_result.append(getObj(obj, i))

        """result转换成对象"""
        return final_result

    def Commit(self):
        self.session.commit()

    def Rollback(self):
        self.session.rollback()

    def Close(self):
        self.session.close()

    def Execute(self, string):
        cursor = self.session.cursor()
        cursor.execute(string)
        # cursor.rowcount
        cursor.close()


class Model:
    def __init__(self, **kwargs):
        for i in dir(self):
            if i not in BuiltAttr:
                setattr(self, i, None)
        for i, j in kwargs.items():
            if i in dir(self):
                setattr(self, i, j)
            else:
                print("type error")


"""工具函数"""


# 驼峰命名转蛇形命名
def TransformName(string):
    output = ''
    for i in string:
        if 'A' <= i <= 'Z':
            output += '_'
        output += i
    if output[0] == '_':
        return output[1:]
    else:
        return output


# 获取表名
def getTableName(obj):
    if hasattr(obj, '__name__'):
        tableName = obj.__name__
    else:
        tableName = obj.__class__.__name__
    if hasattr(obj, '__tablename__'):
        tableName = getattr(obj, '__tablename__')
    return TransformName(tableName)


# 记录转实例
def getObj(obj, value):
    dic = {}
    column = []
    value = list(value)
    for i in dir(obj):
        if i not in BuiltAttr:
            column.append(i)
    print(column, value)
    for i, j in zip(column, value):
        dic[i] = j
    return obj(**dic)


# 实例转记录
def getInfo(obj):
    columns, values = [], []
    for i in dir(obj):
        if i not in BuiltAttr:
            v = getattr(obj, i)
            if v:
                columns.append(i)
                values.append('"'+v+'"')
    print(columns, values)
    return columns, values


# 默认表名为类名映射
class UsersInfo(Model):
    # __tablename__ = 'Users_Info'
    id = 'INT UNSIGNED AUTO_INCREMENT PRIMARY KEY'
    name = 'VARCHAR(40) NOT NULL'
    date = 'DATE'


db = DB('root', '123456', 'for_orm')
db.Connect()
# db.CreateTable(UsersInfo)
# db.Create(UsersInfo())
# db.Close()
# a = UsersInfo(name='job')
# db.Create(a)
result = db.Find('id>1 AND id<10', UsersInfo)
print(result)
# db.Commit()
db.Close()

