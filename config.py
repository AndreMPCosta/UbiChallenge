import os

DEBUG = True

SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{pw}@{host}:{port}/{db}'.format(
    user=os.environ.get('user'),
    pw=os.environ.get('pw'),
    host=os.environ.get('host'),
    port=os.environ.get('port'),
    db=os.environ.get('db')
)

SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPAGATE_EXCEPTIONS = True

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = [
    "access",
]  # allow blacklisting for access and refresh tokens
