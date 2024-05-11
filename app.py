from flask import Flask, session, send_file, render_template, request, flash, url_for, redirect
from flask_session import Session
from werkzeug.utils import secure_filename
import cv2
from PIL import Image
from rembg import remove
import base64
import io

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'photo-file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['photo-file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        print("File name is: ", file.filename)
        inputImg = Image.open(file)
        outputImg = remove(inputImg)
        
        img_io = io.BytesIO()  # Create a bytes buffer for the image
        outputImg.save(img_io, 'PNG')  # Save the image as a PNG to the bytes buffer
        img_io.seek(0)  # Go to the beginning of the bytes buffer
        session['img_data'] = base64.b64encode(img_io.getvalue()).decode('ascii')  # Encode the bytes buffer to Base64

        return render_template('index.html', img_data=session['img_data'])
        

    return render_template('index.html', img_data=None)


@app.route('/download')
def download():
    if 'img_data' in session:
        img_data = session['img_data']
        img_bytes = base64.b64decode(img_data)
        img_io = io.BytesIO(img_bytes)
        img_io.seek(0)
        session.clear()
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='processed_image.png')
    else:
        flash('No image to download')
        return redirect(url_for('upload'))