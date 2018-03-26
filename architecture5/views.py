#-*- coding utf-8 -*-
from flask import Flask, session
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import jsonify
from flask import send_from_directory
from os.path import join, dirname, realpath

from werkzeug import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from flask_s3 import FlaskS3
import boto
from boto.s3.key import Key

import pymysql
import os

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

AWS_ACCESS_KEY_ID='<YOUR_ACCESS_KEY>'
AWS_SECRET_ACCESS_KEY='<YOUR_SECRET_ACCESS_KEY>'
REGION='<YOUR_REGION>'
app.config['FLASKS3_BUCKET_NAME'] = 'uisaws'
app.config['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY_ID
app.config['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_ACCESS_KEY
app.config['FLASKS3_REGION']=REGION
app.config['FLASKS3_CDN_DOMAIN'] = 'https://s3.'+app.config['FLASKS3_REGION']+'.amazonaws.com'
app.config['FLASKS3_BUCKET_DOMAIN'] = app.config['FLASKS3_CDN_DOMAIN']+'/'+app.config['FLASKS3_BUCKET_NAME']
app.config['FLASKS3_FORCE_MIMETYPE'] = True
s3 = FlaskS3(app)

app.config['STATIC_ROOT'] = app.config['FLASKS3_BUCKET_DOMAIN']+"/static"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'HELLO_UIS'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

DB_HOST="<YOUR_RDS_ENDPOINT>"
DB_USER="root"
DB_PASSWORD="uisaws123"
DB_NAME="earthquake"

@app.route('/',methods=['GET'])
def index():

    connection = pymysql.connect(host=DB_HOST,
                             user=DB_USER,
                             password=DB_PASSWORD,
                             db=DB_NAME,
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    sql = "SELECT * FROM `posts` \
            LEFT JOIN `users`ON `posts`.`user_id` = `users`.`id` \
            WHERE 1 ORDER BY `posts`.`id` DESC"
    cursor.execute(sql)
    posts = cursor.fetchall()

    connection.close()
    userName = request.args.get('name')

    return render_template('index.html',posts=posts,userName=userName)


@app.route('/signup',methods=['POST'])
def signup():
    userName = request.form['username']
    email = request.form['email']
    password = request.form['password']

    connection = pymysql.connect(host=DB_HOST,
                             user=DB_USER,
                             password=DB_PASSWORD,
                             db=DB_NAME,
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    try :
        if len(userName) == 0 or len(email) == 0 or len(password) == 0 :
            result = False
        else :
            sql = "INSERT INTO `users` (`id`, `user_name`, `user_email`, `user_password`) \
            VALUES (NULL, \'"+str(userName)+"\', \'"+str(email)+"\', \'"+str(generate_password_hash(password))+"\');"
            print sql
            cursor.execute(sql)
            connection.commit()
            print cursor.lastrowid
            result = True
    except Exception as e :
        print e
        result = False

    connection.close()

    return render_template('signup.html',result=result)



@app.route('/signin',methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['password']

    connection = pymysql.connect(host=DB_HOST,
                             user=DB_USER,
                             password=DB_PASSWORD,
                             db=DB_NAME,
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    try :
        if len(email) == 0 or len(password) == 0 :
            result = False
        else :
            sql = "SELECT * FROM `users` \
            WHERE `user_email` = \'"+str(email)+"\' LIMIT 1"
            cursor.execute(sql)
            user = cursor.fetchone()
            if user :
                if check_password_hash(user['user_password'], password) :
                    session['user_name'] = user['user_name']
                    session['user_id'] = user['id']
                    session.permanant = True
                    result = True
                else :
                    result = False
            else :
                result = False
    except Exception as e :
        print e
        result = False

    connection.close()

    return render_template('signin.html',result=result)

@app.route('/signout')
def signout():
    session.clear()
    return redirect('/')





@app.route('/posting',methods=['POST'])
def posting():
    title = request.form['title']
    picture_url = request.form['picture_url']
    content = request.form['content']
    user_id = session['user_id']
    connection = pymysql.connect(host=DB_HOST,
                             user=DB_USER,
                             password=DB_PASSWORD,
                             db=DB_NAME,
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()


    try :
        if len(title) == 0 or len(content) == 0 :
            result = False
        else :
            sql = "INSERT INTO `posts` (`id`, `title`, `content`,`user_id`,`picture_url`) \
            VALUES (NULL, \'"+str(title)+"\', \'"+str(content)+"\',\'"+str(user_id)+"\',\'"+str(picture_url)+"\');"
            print sql
            cursor.execute(sql)
            connection.commit()
            print cursor.lastrowid
            result = True
    except Exception as e :
        print e
        result = False

    connection.close()

    return jsonify(result=result)


@app.route('/file_upload', methods=['POST'])
def file_upload():
    result = {}
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            s3 = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, host='s3-'+app.config['FLASKS3_REGION']+'.amazonaws.com')
            bucket_name = app.config['FLASKS3_BUCKET_NAME']
            bucket = s3.get_bucket(bucket_name)
            k = Key(bucket)
            file_contents = file.read()
            file_path = '/static/uploadedimages/'+filename
            k.key = file_path
            k.set_contents_from_string(file_contents,policy='public-read')

            result["success"]=True
            result["url"]="/uploadedimages/"+filename
            result["path"]=app.config['STATIC_ROOT']+"/uploadedimages/"+filename


    return jsonify(result = result)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS




if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8000,debug = True)
