import flask_s3
from views import app
flask_s3.create_all(app)
