app.config['MYSQL_HOST'] = 'mysql-152093-0.cloudclusters.net'
app.config['MYSQL_PORT'] = 19876
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'redchatbot'   
app.config['MYSQL_DB'] = 'redcms'

app.config['MYSQL_HOST'] = "mysql-152093-0.cloudclusters.net"
app.config['MYSQL_USER'] = "admin"
app.config['MYSQL_PORT'] = 19876
app.config['MYSQL_PASSWORD'] = "hXtRVj9v"
app.config['MYSQL_DB'] = "redchatbot"
app.config['MYSQL_DATABASE_URI'] = 'mysql://admin:hXtRVj9v@mysql-152093-0.cloudclusters.net:19876/redchatbot?init_command=SET time_zone=+08:00'

app.config['MYSQL_HOST'] = "bteoc1hjrvxi0jsf8u2d-mysql.services.clever-cloud.com"
app.config['MYSQL_USER'] = "u4ii1cazgwjra6qw"
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_PASSWORD'] = "M8iNilfIRKii1a2n4tL5"
app.config['MYSQL_DB'] = "bteoc1hjrvxi0jsf8u2d"



mysql = MySQLdb.connect(
        host="mysql-152093-0.cloudclusters.net",
        user="admin",
        port=19876,
        password="hXtRVj9v",
        db="redchatbot"
    )

mysql = MySQLdb.connect(
        host="bteoc1hjrvxi0jsf8u2d-mysql.services.clever-cloud.com",
        user="u4ii1cazgwjra6qw",
        port=3306,
        password="M8iNilfIRKii1a2n4tL5",
        db="bteoc1hjrvxi0jsf8u2d"
    )

try:
    mysql = MySQLdb.connect(
        host="localhost",
        user="root",
        password="",
        db="redcms"
    )
    print("Database connected successfully!")
    mysql.close()
except MySQLdb.Error as e:
    print(f"Error: {e}")


MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PORT = int(os.getenv('MYSQL_PORT'))  # Convert to integer
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DB = os.getenv('MYSQL_DB')

mysql = MySQLdb.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    port=MYSQL_PORT,
    password=MYSQL_PASSWORD,
    db=MYSQL_DB
)

print(f"MYSQL_HOST: {MYSQL_HOST}")
print(f"MYSQL_USER: {MYSQL_USER}")
print(f"MYSQL_PORT: {MYSQL_PORT}")
print(f"MYSQL_PASSWORD: {MYSQL_PASSWORD}")
print(f"MYSQL_DB: {MYSQL_DB}")