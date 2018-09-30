
# constants
HOST = 'apttoyou-postgresql.czqsvjcidxtf.eu-central-1.rds.amazonaws.com'
PORT = 5432
DBNAME = 'apttoyou_db'
USER = 'apttoyou'
PASSWORD = 'F7e-QhV-Mfm-ybD'
URI = 'postgresql://{}:{}@{}:{}/{}'

# edit the URI below to add your RDS password and your AWS URL
# The other elements are the same as used in the tutorial
# format: (user):(password)@(db_identifier).amazonaws.com:3306/(db_name)

SQLALCHEMY_DATABASE_URI = URI.format(USER, PASSWORD, HOST, PORT, DBNAME)

# Uncomment the line below if you want to work with a local DB
#SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

SQLALCHEMY_POOL_RECYCLE = 3600

WTF_CSRF_ENABLED = True
SECRET_KEY = 'dsaf0897sfdg45sfdgfdsaqzdf98sdf0a'
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
