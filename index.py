from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from PIL import Image
import qrcode
import os

app = Flask(__name__)

folder_upload = 'static/uploads/'
render_folder = 'static/render/'

try:
    os.makedirs("api/static/uploads/")
except FileExistsError:
    pass

try:
    os.makedirs("api/static/render/")
except FileExistsError:
    pass

app.secret_key = "secret key"
app.config['folder_upload'] = folder_upload
app.config['render_folder'] = render_folder

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def home_get():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def home_post():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    url = request.form.get('url')
    name = request.form.get('name')

    if file.filename == '':
        flash('No image selected for create the QR Code')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['folder_upload'], filename))

        logo = Image.open(f'static/uploads/{filename}')
        hsize = int((float(logo.size[1]) * float((75 / float(logo.size[0])))))
        logo = logo.resize((75, hsize), Image.Resampling.LANCZOS)
        qr_big = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr_big.add_data(url)
        qr_big.make()
        img_qr_big = qr_big.make_image(fill_color='black', back_color='white').convert('RGB')
        pos = ((img_qr_big.size[0] - logo.size[0]) // 2, (img_qr_big.size[1] - logo.size[1]) // 2)
        img_qr_big.paste(logo, pos)
        full_filename = os.path.join(app.config['render_folder'], name)

        img_qr_big.save(f'static/render/{name}.png')
        os.remove(f'static/uploads/{filename}')
        flash('QR Code created successfully and shown below. \n right click on the image to save')
        return render_template('index.html', filename=full_filename)

    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/<filename>.png', methods=['GET'])
def home_filename_get(filename):
    return redirect(url_for('static', filename='render/' + filename + '.png'), code=301)


@app.route('/about', methods=['GET'])
def about_get():
    return render_template('about.html')


if __name__ == "__main__":
    app.run(debug=True)
