import pymysql as pms

host = '***REMOVED***'
db = pms.connect(host=host, user='***REMOVED***', passwd='***REMOVED***', db='***REMOVED***',
                              autocommit=True)
cursor = db.cursor()
cursor.execute("SELECT vote_db.username FROM vote_db JOIN flexiblelogin_users ON "
                                        "vote_db.username = flexiblelogin_users.Username")
votes = cursor.fetchall()
print(votes)