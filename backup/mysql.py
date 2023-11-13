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

mysql = MySQLdb.connect(
        host="mysql-152093-0.cloudclusters.net",
        user="admin",
        port=19876,
        password="hXtRVj9v",
        db="redchatbot"
    )

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