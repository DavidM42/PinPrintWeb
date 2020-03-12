#!/usr/bin/env python
import os
from flask import Flask, render_template, Response, request
import picamera
import cups
import datetime
from tinydb import TinyDB, Query

try:
    print("Trying picamera camera module")
    # testing if picam available else raise exception
    with picamera.PiCamera() as camera:
        picamera.mmal_check(camera.capture('tempTestPiCam.jpg', 'jpeg'))

    # if got until here initialize picam
    from pythonCam.camera_pi import Camera
except:
    print("Creating opencv fallback cam")
    from pythonCam.camera_opencv import Camera

RUN_PATH = os.path.dirname(os.path.realpath(__file__))

# probably not change
# is linked in many places
BASE_PATH = RUN_PATH + 'static/pictures/'

#arbitrary filename as fallback for files
FILENAME = "web.jpg"

# set this printer short (non human) name in cups web ui
PRINTER_NAME = "HP"

# init mock db
db = TinyDB(RUN_PATH + '/users.json')

app = Flask(__name__)

def gen(cam):
    """Video streaming generator function."""
    while True:
        frame = cam.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


## real routes to use
@app.route('/')
def indexName():
    """Index start page."""
    return render_template('index.html')

@app.route('/print/index', methods=["POST"])
def printIndex():
    """Print Index home page."""
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    accept = request.form["accept"]

    if firstname is None or lastname is None or accept is None or accept != "on":
        return "invalid", 400

    return render_template('print_index.html', firstname=firstname, lastname=lastname)


@app.route('/print/frame', methods=["POST"])
def printFrame():
    cam = Camera()
    json = request.get_json()

    print(json)

    if json is None:
        return "invalid", 400
    else:
        firstname = json["firstname"]
        lastname = json["lastname"]

        if firstname is None or lastname is None:
            # TODO error page
            return "invalid", 400

    # save file to ms since epoch
    now = datetime.datetime.now()
    msSinceEpoch = str(now.timestamp() * 1000000)
    filename = msSinceEpoch + '.jpg'
    path = BASE_PATH + filename

    #capture current frame #maybe better if frame comes from web whatever
    with open(path, 'wb') as f:
        f.write(cam.get_frame())

    #write into db
    db.insert({'firstname': firstname, 'lastname': lastname, 'date': now.strftime("%Y-%m-%d %H:%M:%S"), 'filename': filename})

    # Set up CUPS
    conn = cups.Connection()

    # code only for testing without really printing to not waste
    # return 'success'

    cups.setUser('pi')
    # Send the picture to the printer
    # give custom media size in pin size with into it
    # CHANGE CM VALUES HERE IF BIGGER OR SMALLER PRINT SIZE
    print_id = conn.printFile(PRINTER_NAME, path, "Projekt Webcam Print", {"media": "Custom.8.5x8.5cm"})


    return "sucess"
    # wait for job
    # from time import sleep
    # while conn.getJobs().get(print_id, None):
    #     sleep(1)


@app.route('/users/list')
def listUsers():
    return render_template('list_users.html', users=db.all())

@app.route('/users/purge')
def purgeUsers():
    # delete file 
    dir_name = BASE_PATH
    picture_dir = os.listdir(dir_name)

    for item in picture_dir:
        if item.endswith(".jpg"):
            os.remove(os.path.join(dir_name, item))
    
    # clear database
    db.purge()
    return "success"

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
