import pymysql as pms

db = pms.connect(host = '***REMOVED***', user = '***REMOVED***',passwd = '***REMOVED***', db = '***REMOVED***', autocommit = True)
cur = db.cursor()
sql = "SELECT 'Password' FROM `flexiblelogin_users` WHERE 'Username'='NIGGER'"
cur.execute(sql)
print(cur.fetchall())
