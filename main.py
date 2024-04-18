import config
from boot import connection 
import urequests as requests



url = f"http://{config.SERVER}:{config.PORT}{config.ENDPOINT}"

<<<<<<< HEAD
=======
def tijdbereken(currentwachtrij, bussen):  # fuctie appart gezet voor als hij door andere moet worden aangesproken
    wachttijd_var = 12 if bussen != 3 or currentwachtrij < 70 else 8
    if currentwachtrij % 70 != 0:
        wachttijd = (currentwachtrij // 70) * wachttijd_var
    else:
        wachttijd = (currentwachtrij // 70 + 1) * wachttijd_var
    return wachttijd


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
>>>>>>> 34c2fe6a78b48cd794da985502df504e31d2e0b5

while connection.isconnected():
    params = {'bussen': 3}  
    response = requests.get(url, params=params)

    if response.status_code == 200:
        response_data = response.json() 
        print('Server response:', response_data)
    else:
        print('Error:', response.status_code)


<<<<<<< HEAD
=======
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


# @app.route('/controll', methods=['POST'])  # sample voor buspanel mischien nog
# def .route('/panel')  # HIER BUSPANNEL
# form = busform()  # niet aangemaakt
# if form.validate_on_submit():
#     global bus_var
#     data = form.bus.data
#     if data:
#         bus = data
#     else:
#         bus = 1
#     bus_var = bus


#     return render_template('buscontroller.html')

@app.route('/update')
def current():
    current = count.value
    return f"Huidig aantal mensen in de wachtrij: {str(current)} <br> Aantal bussen: {bussen} <br> Wachttijd = {tijdbereken(count.value, bussen)}

@app.route('/total')
def total():
    return render_template('index.html')


@app.route('/update/<num>')
def update(num):
    count.value += int(num)
    return "Done"


@app.route('/wachttijden')  # wachtrij view
def current_wachtijd():
    wachtijd_var = count.value
    bus_var = ""  # bussen moet uit de website panel komen
    return tijdbereken(wachtijd_var, bus_var)


print(tijdbereken(140, 3))


@app.route('/espget')
def espget():
    return str(count.value)


if __name__ == '__main__':
    app.run()

>>>>>>> 34c2fe6a78b48cd794da985502df504e31d2e0b5