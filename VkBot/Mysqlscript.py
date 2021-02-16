import pymysql as pms

db = pms.connect(host = '***REMOVED***', user = '***REMOVED***',passwd = '***REMOVED***', db = '***REMOVED***', autocommit = True)
cur = db.cursor()
sql = "UPDATE `flexiblelogin_users` SET `Username` = 'sword2001' WHERE `flexiblelogin_users`.`UserID` = 10;"
cur.execute(sql)
cur.fetchall()
sql = "INSERT INTO `flexiblelogin_users` (UUID,Username,Password,email) VALUES ('0x72a605ca5dbe350dab46a090bbe1dc1f', 'nik', 'dsadasd', 'sa')"