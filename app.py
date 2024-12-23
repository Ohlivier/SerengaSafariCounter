from flask import Flask, request, render_template, jsonify
from multiprocessing import Process, Value
from ultralytics import YOLO
from ultralytics.solutions import object_counter
import cv2
import logging
import os
import json

# Configuring logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

Fillip = "¬Cool"
model = YOLO("yolov3-tinyu.pt")
classes_to_count = [0, 2]  # person and car classes for count
count = Value('i', 0)
bussen = 2
delta_wachttijd = 0

# Laad count.value vanuit file als het bestaat 
count_file = "count.json"
if os.path.exists(count_file):
    with open(count_file, 'r') as f:
        count.value = json.load(f).get('count', 0)


def save_count():
    with open(count_file, 'w') as f:
        json.dump({'count': count.value}, f)


def tijdbereken(currentwachtrij, bussen):  # fuctie appart gezet voor als hij door andere moet worden aangesproken
    global delta_wachttijd
    wachttijd_var = 12 if bussen != 3 or currentwachtrij < 70 else 8
    if currentwachtrij < 70:
        wachttijd = 0
    elif currentwachtrij % 70 != 0:
        wachttijd = (currentwachtrij // 70) * wachttijd_var
    else:
        wachttijd = (currentwachtrij // 70 + 1) * wachttijd_var
    return wachttijd + delta_wachttijd


def run_object_detection(ip, count):
    cap = cv2.VideoCapture(f"http://{ip}:81/stream")
    assert cap.isOpened(), "Error reading video file"
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    line_points = [(w * 3 / 4, h), (w * 3 / 4, 0)]
    # Video writer
    video_writer = cv2.VideoWriter("object_counting_output.avi",
                                   cv2.VideoWriter_fourcc(*'mp4v'),
                                   fps,
                                   (w, h))

    # Init Object Counter
    counter = object_counter.ObjectCounter()
    counter.set_args(view_img=True,
                     reg_pts=line_points,
                     classes_names=model.names,
                     draw_tracks=True,
                     line_thickness=2)

    while cap.isOpened():
        success, im0 = cap.read()
        if not success:
            print("Video frame is empty or video processing has been successfully completed.")
            break
        tracks = model.track(im0, persist=True, show=False,
                             classes=classes_to_count)

        im0 = counter.start_counting(im0, tracks)
        video_writer.write(im0)
        if 'perso' in counter.class_wise_count:
            if counter.class_wise_count['perso']['in'] >= 1 or counter.class_wise_count['perso']['out'] >= 1:
                count.value += counter.class_wise_count['perso']['in']
                count.value -= counter.class_wise_count['perso']['out']
                counter.class_wise_count['perso']['in'] = 0
                counter.class_wise_count['perso']['out'] = 0

        save_count()  # Het slaat aantal mensen op, dit waren we vergeten.

    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()


@app.route('/', methods=['POST'])
def run_object_detection_on_request():
    data = request.get_json()
    ip_address = data.get('ip')
    print(ip_address)
    # Run object detection in a separate process
    p = Process(target=run_object_detection, args=(ip_address, count))
    p.start()
    print("Object detection process started")
    return 'Object detection process started.'


@app.route('/debug')
def currentdebug():
    return f"Huidig aantal mensen in de wachtrij: {str(count.value)} <br> Aantal bussen: {bussen} <br> Wachttijd = {tijdbereken(count.value, bussen)} minuten"


@app.route('/update')
def current():
    wachttijd = tijdbereken(count.value, bussen)
    aantal_personen = count.value
    return render_template('scherm.html', wachttijd=wachttijd, bussen=bussen, aantal_personen=aantal_personen)


@app.route('/api/wachttijd')
def api_wachttijd():
    wachttijd = tijdbereken(count.value, bussen)
    return jsonify({'wachttijd': wachttijd})


@app.route('/total')
def total():
    return render_template('index.html')


@app.route('/update/<num>')
# Deze functie/view voegt mensen toe aan de count
def update(num):
    count.value += int(num)
    save_count()  # De aantal moet ook gesaved worden
    logging.debug(f"Aantal mensen geüpdate by {num}. nieuwe waarde: {count.value}")  # test
    return "Done"


@app.route('/wachttijden')  # wachtrij view
def current_wachtijd():
    wachtijd_var = count.value
    bus_var = ""  # bussen moet uit de website panel komen
    return tijdbereken(wachtijd_var, bus_var)


@app.route('/espget')
def espget():
    return str(count.value)


@app.route('/aantal_bussen', methods=['POST'])
def aantal_bussen():
    global bussen
    data = request.json
    print(data)
    bussen = data.get("bussen")
    logging.debug(f"Bussen geüpdate naar: {bussen}")
    response = {'message': 'Aantal bussen succesvol bijgewerk', 'bussen': bussen}
    return jsonify(response)


@app.route('/wachttijd_update', methods=['POST'])
def wachttijd_update():
    global delta_wachttijd
    data = request.json
    update_tijd = data.get("wachttijd")
    delta_wachttijd += update_tijd
    wachttijd_nu = tijdbereken(count.value, bussen)
    if wachttijd_nu > 0:
        logging.debug(f"Wachttijd delta is nu {delta_wachttijd}")
        response = {'message': 'Wachttijd bijgewerkt', 'wachttijd_delta': delta_wachttijd}
    else:
        print("Wachttijd kan niet negatief zijn")
        response = {'message': 'Wachttijd mag niet negatief zijn'}
        delta_wachttijd += 5
    return jsonify(response)


@app.route('/bus/<num>')
def bus(num):
    global bussen
    bussen = int(num)
    logging.debug(f"Bussen geüpdate via bus route naar: {bussen}")
    return "Done"


if __name__ == '__main__':
    app.run(debug=True)
