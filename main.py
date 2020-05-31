from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from datetime import datetime
import random
import string

app=Flask(__name__)
app.config['MONGO_URI']='mongodb://localhost:27017/flasktest'
mongo = PyMongo(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/img-detection')
def img_detection():
    return render_template('img-detection.html')

@app.route('/testimg', methods=['POST'])
def testimg():
    if 'profile' in request.files:
        print('yes')
        profile = request.files['profile']
        profile.filename=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))+'.jpg'
        mongo.save_file(profile.filename, profile)
        mongo.db.users.insert({'username' : request.form.get('username') , 'image_name': profile.filename , 'result' : request.form.get('result'), 'upload_time' :  datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    else:
        print('no')
    return redirect(url_for('img_detection'))
    
@app.route('/mongodata')
def mongodata():
    data_list = mongo.db.users.find().sort('upload_time', -1)
    return render_template('mongodata.html', data_list = data_list)

@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)

@app.route('/deletdata', methods=['POST'])
def deletdata():
    if 'delete' in request.form:
        mongo.db.users.delete_one({'image_name' : request.form['delete']})
        result = mongo.db.fs.files.find_one({'filename' : request.form['delete']})
        mongo.db.fs.files.remove({'_id': result['_id']})
        mongo.db.fs.chunks.remove({'files_id': result['_id']})
        return redirect(url_for('mongodata'))
    else:
        return "no"

