import mysql.connector
import datetime

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
        indexs = []
        foreign = []
        for i in dir(obj):
            if i[0] != '_':
                filed = getattr(obj, i)
                assert isinstance(filed, Field)
                temp = filed.name
                if filed.autoIncrease:
                    temp += ' AUTO_INCREMENT'
                if filed.primary:
                    temp += ' PRIMARY KEY'
                if filed.unique:
                    temp += ' UNIQUE'
                if filed.NotNull:
                    temp += ' NOT NULL'
                if filed.Index:
                    indexs.append(i)
                if filed.foreignkey:
                    foreign.append('FOREIGN KEY(%s) REFERENCES %s(%s)' %
                                   (i, getTableName(filed.reference[0]), filed.reference[1]))
                columns.append("`%s` %s" % (i, temp))
        if indexs:
            columns.append('INDEX(%s)' % ','.join(indexs))
        for i in foreign:
            columns.append(i)

        sql = "CREATE TABLE IF NOT EXISTS `%s` (%s) CHARSET=utf8 " % (tableName, ','.join(columns))

        print(sql)

        self.Execute(sql)

    def Create(self, obj):
        columns, values = getInfo(obj)
        sql = "INSERT INTO %s (%s) values (%s) " % (getTableName(obj), ','.join(columns), ','.join(values))
        self.Execute(sql)

    def Update(self, obj, whereExpression):
        columns, values = getInfo(obj)
        kv = []
        for i, j in zip(columns, values):
            if j != '':
                kv.append("%s='%s'" % (i, j))
        sql = "UPDATE %s SET %s WHERE %s" % (getTableName(obj), ','.join(kv), whereExpression)
        self.Execute(sql)

    def Find(self, whereExpression, obj, sort=None):
        tablename = getTableName(obj)

        cursor = self.session.cursor()
        sql = "SELECT * FROM %s WHERE %s" % (tablename, whereExpression)
        columns = self.GetColumnName(tablename)

        if sort is not None:
            sql += ' ORDER BY %s' % sort

        cursor.execute(sql)
        r = cursor.fetchall()
        cursor.close()

        final_result = []
        for i in r:
            final_result.append(getObj(obj, columns, i))

        return final_result

    def FindAll(self, obj, sort=None):
        tablename = getTableName(obj)

        cursor = self.session.cursor()
        sql = "SELECT * FROM %s" % tablename
        columns = self.GetColumnName(tablename)

        if sort is not None:
            sql += ' ORDER BY %s' % sort

        cursor.execute(sql)
        r = cursor.fetchall()
        cursor.close()

        final_result = []
        for i in r:
            final_result.append(getObj(obj, columns, i))

        return final_result

    def Delete(self, obj, whereExpression=None):
        if whereExpression is None:
            columns, values = getInfo(obj)
            kv = []
            for i, j in zip(columns, values):
                if j != '':
                    kv.append("%s=%s" % (i, j))
            sql = "DELETE FROM %s WHERE %s" % (getTableName(obj), ' AND '.join(kv))
            self.Execute(sql)
        else:
            self.Execute("DELETE FROM %s WHERE %s" % (getTableName(obj), whereExpression))

    def DeleteAll(self, obj):
        sql = "DELETE FROM %s" % getTableName(obj)
        self.Execute(sql)

    def DropTable(self, obj):
        sql = "DROP TABLE %s" % getTableName(obj)
        self.Execute(sql)

    def Commit(self):
        self.session.commit()

    def Rollback(self):
        self.session.rollback()

    def Close(self):
        self.session.close()

    def Execute(self, string):
        cursor = self.session.cursor()
        cursor.execute(string)
        cursor.close()

    def GetColumnName(self, tablename):
        cursor = self.session.cursor()
        cursor.execute("DESC %s" % tablename)
        define = cursor.fetchall()
        columns = []
        for i in define:
            columns.append(i[0])
        cursor.close()
        return columns


class Model:
    def __init__(self, **kwargs):
        for i in dir(self):
            if i[0] != '_':
                setattr(self, i, None)
        for i, j in kwargs.items():
            if i in dir(self):
                setattr(self, i, j)
            else:
                raise TypeError("没有该属性 %s" % i)


class Field:
    def __init__(self, name, primary=False, autoIncrease=False, NotNull=False, unique=False,
                 Index=False, foreignkey=False, reference=None):
        self.name = name
        self.primary = primary
        self.autoIncrease = autoIncrease
        self.NotNull = NotNull
        self.unique = unique
        self.Index = Index
        self.foreignkey = foreignkey
        self.reference = reference


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
    if hasattr(obj, '__tablename__'):
        tableName = getattr(obj, '__tablename__')
        return tableName
    if hasattr(obj, '__name__'):
        tableName = obj.__name__
    else:
        tableName = obj.__class__.__name__
    if '_' in tableName:
        return tableName
    else:
        return TransformName(tableName)


# 记录转实例
def getObj(obj, columns, value):
    dic = {}
    value = list(value)
    for i, j in zip(columns, value):
        dic[i] = j
    return obj(**dic)


# 实例转记录
def getInfo(obj):
    columns, values = [], []
    for i in dir(obj):
        if i[0] != '_':
            v = getattr(obj, i)
            if v:
                columns.append(i)
                values.append('"' + str(v) + '"')
    return columns, values


# 默认表名为类名映射
class AuthorInfo(Model):
    id = Field('INT UNSIGNED', autoIncrease=True, primary=True)
    name = Field('VARCHAR(20)', Index=True)


class Book(Model):
    id = Field('INT UNSIGNED', autoIncrease=True, primary=True)
    name = Field('VARCHAR(20)', unique=True)
    datetime = Field('DATETIME')
    author_id = Field('INT UNSIGNED', foreignkey=True, reference=(AuthorInfo, 'id'))


db = DB('root', '123456', 'for_orm')
db.Connect()
author1 = AuthorInfo(name="job")
book1 = Book(name="kkk", datetime=datetime.datetime.now(), author_id=1)
book2 = Book(name="job", datetime=datetime.datetime.now(), author_id=1)
book3 = Book(name="ppp", datetime=datetime.datetime.now(), author_id=1)

db.CreateTable(AuthorInfo)
db.CreateTable(Book)
db.Create(author1)
db.Create(book1)
db.Create(book2)
db.Create(book3)

result = db.FindAll(Book, sort='name')
for i in result:
    print(i.id, i.name, i.datetime, i.author_id)
db.Commit()
db.Close()
