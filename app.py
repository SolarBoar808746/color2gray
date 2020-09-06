import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory,flash
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

UPLOAD_FOLDER ='static/uploads/'
DOWNLOAD_FOLDER = 'static/downloads/'
ALLOWED_EXTENSIONS = {'mkv', 'avi','mp4','wav'}
app = Flask(__name__,  static_url_path="/static")


# APP CONFIGURATIONS
#app.config['SECRET_KEY'] = 'opencv'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# limit upload size upto 6mb
#app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file found')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            process_file(os.path.join(UPLOAD_FOLDER, filename), filename)
            e_mail = request.form['e_mail']
            name = request.form['name']
            data='static/downloads/video.mkv'
            send_mail(e_mail,data,name)
            return render_template("index.html")
    return render_template('index.html')


def process_file(path, filename):
    detect_object(path, filename)


def detect_object(path, filename):
	cap = cv2.VideoCapture(path)

	ret, frame = cap.read()
	print('ret =', ret, 'W =', frame.shape[1], 'H =', frame.shape[0], 'channel =', frame.shape[2])


	FPS= 10.0
	FrameSize=(frame.shape[1], frame.shape[0])
	fourcc = cv2.VideoWriter_fourcc(*'MPEG')

	out = cv2.VideoWriter('static/downloads/video.mkv', fourcc, FPS, FrameSize, 0)

	while(cap.isOpened()):
		ret, frame = cap.read()

		# check for successfulness of cap.read()
		if not ret: break

		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		frame = gray

		# Save the video
		out.write(frame)

		#cv2.imshow('frame',frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
		 break

	cap.release()
	out.release()
	cv2.destroyAllWindows()
def send_mail(e_ma,fname,name):

    email_user = 'pasija2709@gmail.com'
    email_password = 'noobmaster123'
    email_send = e_ma

    subject = 'RGB to Grayscale Video'

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject

    body = 'Hi '+ name +' there, sending email of Video form Parshant Asija'
    msg.attach(MIMEText(body,'plain'))

    filename= fname
    attachment  =open(filename,'rb')

    part = MIMEBase('application','octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment; filename= "+filename)

    msg.attach(part)
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(email_user,email_password)
    server.sendmail(email_user,email_send,text)


# download
# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run()
