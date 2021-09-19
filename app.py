from flask import render_template, request, flash, jsonify, Flask, redirect, url_for, Blueprint, session
import numpy as np
import pickle
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os
# import speech_recognition as sr
# import librosa
import io
import soundfile as sf
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
onehot_encoder = OneHotEncoder()
from sklearn.preprocessing import OrdinalEncoder
ordinal_encoder = OrdinalEncoder()
from datetime import datetime

###########################################################################################

def create_database(app):
    if not os.path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

db = SQLAlchemy()
DB_NAME = "database.db"

cwd = os.getcwd()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    patient_name = db.Column(db.String(150))
    patient_age = db.Column(db.Integer)
    patient_gender = db.Column(db.String(150))
    tests = db.relationship('Test')

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.String(100))
    result = db.Column(db.String(250))
    result = db.Column(db.Float)
    display = db.Column(db.String(1000))

    hc1 = db.Column(db.Float)
    pd1 = db.Column(db.Float)
    pro1 = db.Column(db.Float)

    hc2 = db.Column(db.Float)
    pd2 = db.Column(db.Float)
    pro2 = db.Column(db.Float)

    hc3 = db.Column(db.Float)
    pd3 = db.Column(db.Float)
    pro3 = db.Column(db.Float)

    hc4 = db.Column(db.Float)
    pd4 = db.Column(db.Float)
    pro4 = db.Column(db.Float)

    hc5 = db.Column(db.Float)
    pd5 = db.Column(db.Float)
    pro5 = db.Column(db.Float)
      

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hjsh782kjshkjdhjs'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
db.init_app(app)
create_database(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

########################################################################################

#auth = Blueprint('auth', __name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                #flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('index'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("2_login.html", user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('patName')
        age = request.form.get('patAge')
        try:
            gender = request.form['patGen']
        except:
            gender = 'Not specified'
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, patient_name=name, patient_age=age, patient_gender=gender, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('index'))

    return render_template("2_signup.html", user=current_user)

###########################################################################################

pickle_files = {}
directory = 'pickles'

for root, dirs, files in os.walk(directory):
    for filename in files:
        if filename[-4:]=='.pkl':   
            data = filename[-9:-4]
            if data not in pickle_files.keys():
                pickle_files[data] = []    
            # pickle_files[data].append(os.path.join(root,filename))
            pickle_files[data].append(root+"\\"+filename)


@app.route('/')
# @login_required
def index():
    return render_template('1_home.html',user=current_user)

@app.route('/my-tests')
@login_required
def my_tests():
    t = Test.query.filter_by(user_id=current_user.id).first()
    if t==None:
        n=0
    else:
        n=1
    return render_template('3_mytests.html', user=current_user, n=n)


####################################################################################################


# FOR MULTIPLE GROUPS
def predict_all(hc, pd, pro):
    prob_lst = [sum(hc)/len(hc), sum(pd)/len(pd), sum(pro)/len(pro)]

    output_prob = max(prob_lst)
    prediction = prob_lst.index(output_prob)
    output_prob = round(output_prob,4)
    
    return prediction, output_prob


# FOR MULTIPLE GROUPS
def predict_single(X,models):
    HC_prob = []
    PD_prob = []
    Prodroma_prob = []
    for model_name in models:
        
        model = pickle.load(open(model_name, 'rb'))
        pred = model.predict(X)
        
        pred_prob = model.predict_proba(X)
        HC_prob.append(pred_prob[0][0])
        PD_prob.append(pred_prob[0][1])
        Prodroma_prob.append(pred_prob[0][2])

    HC_result = sum(HC_prob)/len(HC_prob)
    PD_result = sum(PD_prob)/len(PD_prob)
    Prodroma_result = sum(Prodroma_prob)/len(Prodroma_prob)

    prob_lst = [HC_result, PD_result, Prodroma_result]
    return prob_lst

    
# DO NOT MODIFY    
def predict_pq_mt_forpq3only(X,models):
    HC_prob = []
    PD_prob = []
    Prodroma_prob = []
    for model_name in models:
        model = pickle.load(open(model_name, 'rb'))
        pred = model.predict(X)
        
        pred_prob = model.predict_proba(X)
        HC_prob.append(pred_prob[0][0])
        PD_prob.append(pred_prob[0][1])
        Prodroma_prob.append(pred_prob[0][2])

    HC_result = sum(HC_prob)/len(HC_prob)
    PD_result = sum(PD_prob)/len(PD_prob)
    Prodroma_result = sum(Prodroma_prob)/len(Prodroma_prob)

    prob_lst = [HC_result, PD_result, Prodroma_result]
        
    output_prob = max(prob_lst)
    prediction = prob_lst.index(output_prob)
    output_prob = round(output_prob,4)
    return prediction, output_prob


#  ---------------------------------------------------------------------------------------
@app.route('/predict-pq2',methods=['POST','GET'])
@login_required
def predict_pq2():
    if request.method=='POST':

        models = pickle_files['PQ_G2']
        
        if len(request.form)!=20: 
            flash('Please answer all questions', category='error')
            return redirect(url_for('render_pq2'))
            
        X = np.array([[int(x) for x in request.form.values()]])
        # X = np.array(features)

        prob_lst = predict_single(X, models)

        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        new_test = Test(type="Questionnaire", hc2=prob_lst[0], pd2=prob_lst[1], pro2=prob_lst[2], date=date, user_id = current_user.id)
        db.session.add(new_test)
        db.session.commit()
    
    return redirect(url_for('render_pq3'))


@app.route('/pq2',methods=['POST','GET'])
@login_required
def render_pq2():
    return render_template("3_pq2.html",user=current_user)



@app.route('/predict-pq3',methods=['POST','GET'])
@login_required
def predict_pq3():
    if request.method=='POST':

        models = pickle_files['PQ_G3']

        if len(request.form)!=21: 
            flash('Please answer all questions', category='error')
            return redirect(url_for('render_pq3'))
            
        X = np.array([[int(x) for x in request.form.values()]])

        prob_lst = predict_single(X, models)

        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        t = Test.query.order_by(Test.id.desc()).first()
        
        t.hc3=prob_lst[0]
        t.pd3=prob_lst[1]
        t.pro3=prob_lst[2]
        t.date=date
        db.session.commit()
    
    return redirect(url_for('render_pq4'))


@app.route('/pq3',methods=['POST','GET'])
@login_required
def render_pq3():
    return render_template("3_pq3.html",user=current_user)



@app.route('/predict-pq4',methods=['POST','GET'])
@login_required
def predict_pq4():
    if request.method=='POST':

        models = pickle_files['PQ_G4']

        if len(request.form)!=1: 
            flash('Please answer all questions', category='error')
            return redirect(url_for('render_pq4'))
            
        X = np.array([[int(x) for x in request.form.values()]])

        prob_lst = predict_single(X, models)

        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        t = Test.query.filter(Test.user_id==current_user.id).order_by(Test.id.desc()).first()
        
        t.hc4=prob_lst[0]
        t.pd4=prob_lst[1]
        t.pro4=prob_lst[2]
        t.date=date
        db.session.commit()

        HC = [t.hc2, t.hc3, t.hc4]
        PD = [t.pd2, t.pd3, t.pd4]
        PRODROMA = [t.pro2, t.pro3, t.pro4]

        prediction, output_prob = predict_all(HC, PD, PRODROMA)

        t.result = prediction
        t.prob = output_prob
        db.session.commit()

        # ADD RESULTS PAGE HERE
        if prediction==0:
            # if output_prob>75:
            #     return render_template("4_result.html", prediction_text="you are at very low risk of being affected by Parkinson's Disease.", user=current_user)
            # else:
                # return render_template("4_result.html", prediction_text="you are at low risk ({}%) of being affected by Parkinson's Disease.".format(100-output_prob), user=current_user)
                t.display = "Healthy"
                db.session.commit()
                return render_template("4_result.html", prediction_text="you are at low risk of being affected by Parkinson's Disease.", user=current_user)
        elif prediction==1:
            t.display = str(output_prob*100)+"% risk of Parkinson's Disease"
            db.session.commit()
            return render_template("4_result.html", prediction_text="you are at {}% risk of being affected with Parkinson's Disease.".format(output_prob*100), user=current_user)    
        elif prediction==2:
            t.display = str(output_prob*100)+"% risk of being in the early stages of Parkinson's Disease"
            db.session.commit()
            return render_template("4_result.html", prediction_text="your are at {}% risk of being in the early stages of Parkinson's Disease.".format(output_prob*100), user=current_user)
    
    return redirect(url_for('render_pq4'))


@app.route('/pq4',methods=['POST','GET'])
@login_required
def render_pq4():
    return render_template("3_pq4.html",user=current_user)

#  ---------------------------------------------------------------------------------------

####################################################################################################

voice_model = pickle.load(open('voice_model.pkl','rb'))

@app.route('/voice',methods=['POST','GET'])
@login_required
def render_voice():
    return render_template("3_voice.html", user=current_user)


@app.route("/voice-result", methods=["POST","GET"])
@login_required
def voice_result():
    voice_prediction = session['voice_prediction']
    idx = voice_prediction[0]
    output_prob = voice_prediction[1]

    if idx==0:
        return render_template("4_result.html", prediction_text="you are at low risk of being affected by Parkinson's Disease.", user=current_user)
    elif idx==1:
        return render_template("4_result.html", prediction_text="you are at {}% risk of being affected with Parkinson's Disease.".format(output_prob), user=current_user)

    return redirect(url_for('voice_result'))


@app.route("/predict-voice", methods=["POST","GET"])
@login_required
def predict_voice():

    if request.method=='POST': 

        audio_bytes = request.files['audio_data'].read()
        y, sr = sf.read(io.BytesIO(audio_bytes))

        # EXTRACT VOICE FEATURES
        duration = librosa.get_duration(y=y,sr=sr)
        rmse = librosa.feature.rms(y=y)
        chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
        spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)
        spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        zcr = librosa.feature.zero_crossing_rate(y)
        mfcc = librosa.feature.mfcc(y=y, sr=sr)
        to_append = f'{duration} {np.mean(chroma_stft)} {np.mean(rmse)} {np.mean(spec_cent)} {np.mean(spec_bw)} {np.mean(rolloff)} {np.mean(zcr)}' 
        for e in mfcc:
            to_append += f' {np.mean(e)}'
        
        # VOICE FEATURES LIST
        voice_data = np.array(to_append.split(),dtype='float').reshape(1, -1)
        
        # PREDICT VOICE
        try:
            prob = voice_model.predict_proba(voice_data)
            output_prob = round(max(prob[0])*100,2)
            idx = prob[0].tolist().index(max(prob[0]))
            pred = voice_model.predict(voice_data)[0]
            
            hc = round(prob[0][0],4)*100
            pd = round(prob[0][1],4)*100

            session['voice_prediction'] = [idx,output_prob]

            date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            if idx==0:
                new_test = Test(type="Voice", result=0, display="Healthy", hc1=hc, pd1=pd, date=date, user_id = current_user.id)
                db.session.add(new_test)
                db.session.commit()
                
            elif idx==1:
                new_test = Test(type="Voice", result=1, display=str(output_prob)+"% risk", hc1=hc, pd1=pd, date=date, user_id = current_user.id)
                db.session.add(new_test)
                db.session.commit()

            return redirect(url_for('voice_result'))

        except:
            print('Exception')

    return redirect(url_for('render_voice'))

#################################################################################################

if __name__ == "__main__":
    app.run(debug=True)
