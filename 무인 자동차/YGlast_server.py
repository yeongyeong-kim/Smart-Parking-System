import socket
import datetime
from _thread import *
import YGlast_modul
from PIL import Image  # Pillow
import cv2 as cv  # OpenCV
import numpy as np
import threading
import time
from datetime import datetime
from queue import Queue
import asyncio
from urllib.request import urlopen
from collections import Counter
import pytesseract
import pyzbar.pyzbar as pyzbar


data1 = 0
data2 = 0
data3 = 0
gijuncheck = 0
bacode_number = 1
threadtimer = 0
maxkey = 0


after_time = 0

client_sockets = []
HOST, PORT = '192.168.0.66', 9999


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
LOCELPATH = 'C:\\Users\\202-1575\\PycharmProjects\\pythonProject2\\lastproject\\picture\\'
# C:\\Users\\202-1575\\PycharmProjects\\pythonProject2\\lastproject\\
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\Tesseract.exe'
day = datetime.now().strftime('%Y-%m-%d')


def message():
    global data1
    global data2
    global data3
    global gijuncheck

    buffer = b''
    url = "http://192.168.4.1"  # Your url
    stream = urlopen(url)

    while True:
        buffer += stream.read(2560)
        head = buffer.find(b'\xff\xd8')
        end = buffer.find(b'\xff\xd9')
        if head > -1 and end > -1:
            jpg = buffer[head:end + 2] # 바이너리에서 jpg파일 빼기
            buffer = buffer[end + 2:]  # 버퍼초기화
            data = np.frombuffer(jpg, dtype='uint8')
            # 리시브로 온 바이너리데이터를 가지고 np.frombuffer 속성을 통해 nparray 타입으로 변경함.
            beforerl = cv.imdecode(data, 1) # 위 nparray타입의 데이터를 cv.imdecode를 통해 디코딩을 하여 이미지 데이터로 만듬.
            data1 = beforerl
            if gijuncheck == 0:
                # print('data2에 들어감.')
                data2 = beforerl
            # ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()
            # data2 == 0로 해놓을시 비교기준 사진 할당할 때 2번째 반복때 부터 에러가 발생함. 키값을 다른곳에 넣고 변경
            else:
                # print("데이터2에 안들어감.")
                pass
            if gijuncheck == 0:
                # print('data3에 들어감.')
                data3 = beforerl
                gijuncheck += 1
            else:
                # print("데이터3에 안들어감.")
                pass

        # frame = cv.cvtColor(beforerl, cv.COLOR_BGR2RGB)
        # data1 = np.fliplr(frame)

thread_ing = threading.Thread(target=message)
thread_ing.daemon = True
thread_ing.start()

def savetime():
    global threadtimer
    while True:
        time.sleep(1)
        threadtimer+=1
        globals()[f'savetime{threadtimer}'] = []
        if threadtimer > 10:
            # print('del', f"{threadtimer-10}초의 프래임들 삭제")
            del globals()[f'savetime{threadtimer-10}']
        # print(threadtimer, '<-------threadtimer')

globaltimer = threading.Thread(target=savetime)
globaltimer.daemon = True
globaltimer.start()

def countdown():
    global data2
    global gijuncheck

    if True:
        time.sleep(3)
        data2 = data1
        # print("data2들어갔다!")

countdown()

class changimg():

    used_codes = []
    data_list = []
    raw_data = {"seachtime": [], "X-Ypoint": [], "vidio": [], "size":[]}
    savecount = 0
    timerque = Queue(20)

    def default(self):
        global data1
        global data2
        global data3
        global after_time
        frame2 = data2
        frame3 = data3
        frame = data1
        draw = frame

        a = cv.cvtColor(frame2, cv.COLOR_BGR2GRAY)  # 비교기준 1
        b = cv.cvtColor(frame3, cv.COLOR_BGR2GRAY) # 비교기준 2
        c = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)  # 상시 영상


        changedimg = cv.absdiff(a, c) # 정적 배경 차분 방법 배경영상과 다른 부분을 찾아내는 함수
        changedimg2 = cv.absdiff(b, c) # frame2,3는 처음에 받은 초기 정적 화면임. 따라서 비교를 하더라도 같은값이 나올확률이 높음.
        # 같은 값은 0으로 처리 다른 값은 그대로 넣는다. (0,0,0) => 0

        ret, thresh1 = cv.threshold(changedimg, 50, 255, cv.THRESH_BINARY)  # RGB 수치 값 차이가 50이상이면 255(흰색), 차이가 50보다 작으면 0(검정색)
        ret, thresh2 = cv.threshold(changedimg2, 50, 255, cv.THRESH_BINARY)  # cv2.threshold 임계점 처리 함수 : 색의 이진화를 하는 함수.
        # print(thresh1)
        # 기준이 되는 임계값을 정해놓고, 그기준에 따라 임계값보다 크면 백, 작으면 흑색으로 변경
        # 이진화, 기준과 다른 픽셀에 대해서 흑과 백으로 나누어 나타내는 함수.
        # 배경이 바다인데, 배가 하나 지나간다면 기준과 같은 바다는 흑색, 기준과 다른 배 사진은 백색으로 만듬.

        diff = cv.bitwise_and(thresh1, thresh2)
        # 두가지 그림중 비트 연산을 하여 두개의 값이 같으면 True, 다르면 False를 반환하여 각 픽샐값으로 넣는다.
        # 255와 0으로 구분되어 있던 값들이 1과 0으로 변환됨.
        # print(diff)


        k = cv.getStructuringElement(cv.MORPH_CROSS, (3, 3))
        diff = cv.morphologyEx(diff, cv.MORPH_OPEN, k)

        # 모폴로지는 영상을 이진화 하였을 때 남아있는 노이즈 제거에 사용되는 함수.
        # Erosion 침식: 바이너리 이미지에서 흰색 dbj의 외각 픽셀을 검은색으로 만듭니다.
        # Dilation 팽창: Erosion와 반대로 작동 외각 픽셀을 하얀색으로 만듭니다.
        # opening : 침식 팽창 한번씩 수행
        # Erosion 연산 다음에 Dilation 연산을 적용 이미지상의 노이즈(작은흰색물체)를 제거하는데 사용합니다. (피사체 뿐 아니라 배경노이즈 지우는데 좋음.)
        # 노이즈(작은흰색오브젝트)를 없애기 위해 사용한 Erosion에 의해서 작아졌던 오브젝트에 Dilation를 적용하면 오브젝트가 원래 크기로 돌아옴
        # 참조 https://webnautes.tistory.com/1257
        # print(type(diff))
        # print(diff)



        diff_cnt = cv.countNonZero(diff)
        # diff 안에 0이 아닌 개수 : 숫자형태로 반환됨.
        if diff_cnt > 10:
            nzero = np.nonzero(diff)
            # 위cv countNonZero 와 달리 np모듈의 nonzero는 array형태로 값이 0이 아닌 인덱스들을 array에 담아 반환한다.
            cv.rectangle(draw, (min(nzero[1]), min(nzero[0])),(max(nzero[1]), max(nzero[0])), (0, 255, 0), 2)
            # rectangle(img, 시작점좌표, 끝점좌표, 색(BGR), 선두께, 라인종류, 시프트)
            # cv.putText(draw, "Motion detected!!", (10, 30),cv.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 255))
            # 이미지에 텍스트 넣는 함수 cv2.putText(img, 넣을텍스트, 텍스트좌표, 폰트, 폰트크기, 폰트색상)

            if self.timerque.full() == False:
                self.timerque.put(cv.cvtColor(draw, cv.COLOR_BGR2RGB))
            if self.timerque.full():
                # print("큐2 가득참")
                asyncio.run(self.pandasinput())
                # RuntimeWarning: Enable tracemalloc to get the object allocation traceback
                # 비동기 함수는 정상적인 함수의 방법으로는 구동이 불가능하다.
                # asyncio.run(self.savevideos()) 와 같은 방법으로 쓰레드를 돌리듯 run을 따로 선언해줘야 한다.
                while True:
                    self.timerque.get()
                    if self.timerque.empty() == True:
                        # print("와일문은 들어온당")
                        break

                time = datetime.now().strftime('%H:%M:%S')
                time = datetime.now().strftime('%H:%M:%S')
                if time not in self.raw_data["seachtime"]:
                    self.raw_data["seachtime"].append(time)
                    self.raw_data["X-Ypoint"].append(f'{min(nzero[1])} : {min(nzero[0])} X {max(nzero[1])} : {max(nzero[0])}')
                    self.raw_data["vidio"].append(f'{threadtimer}.mp4')
                    self.raw_data["size"].append("640x480")



                    #######################################################
            # print(time)
            # print(f'{min(nzero[0])} : {max(nzero[0])} X {min(nzero[1])} : {max(nzero[1])}')
            # print(self.raw_data)
            # print(draw)
        # globals()[f'savetime{threadtimer}'].append(cv.cvtColor(draw, cv.COLOR_BGR2RGB))


    async def savevideos(self):
        global LOCELPATH
        # print('비동기 들어옴')
        fourcc = cv.VideoWriter_fourcc(*'DIVX')
        out = cv.VideoWriter(f'{LOCELPATH}{threadtimer}.mp4', fourcc, 12.0, (640, 480))
        for i in range(7, -1, -1):
            for j in globals()[f'savetime{threadtimer - i}']:
                out.write(j)
        # print('비동기 끝!')

    def start(self):
        while True:
            self.default()
            time.sleep(0.05)

    async def pandasinput(self):
        global bacode_number
        global LOCELPATH
        self.savecount = 0
        # df = pd.DataFrame(a.raw_data)
        # df.to_csv("test.csv")
        # cv.imwrite(f'C:\\Users\\202-1576\\PycharmProjects\\GYpythonProject1\\pasdasstudy\\{threadtimer}.png', data1)
        for i in range(33):
            self.savecount += 1
            cv.IMREAD_UNCHANGED
            cv.imwrite(f'{LOCELPATH}{self.savecount}.jpg', data1)
            time.sleep(0.03)
        ##################################################################
        # while True:
        #     out.write(a.que.get())
        #     if a.que.empty() == True:
        #         break
        ##################################################################
        # print("저장됬다!!")
        self.OTCcheck()
        # if bacode_number == 0:
        #     self.OTCcheck()
        # else:
        #     self.barcode()

    def OTCcheck(self):
        global maxkey
        checked = []
        # print(111111)
        for i in range(self.savecount):
            result = recogtest.ExtractNumber(i+1)
            checked.append(result)
            # print(result, '<--글자 인식!!!!!!!')
        word_item = Counter(checked)

        # for key, value in word_item.items():
        #     # if key.isdigit():
        #     #     pass
        #     # else:
        #     print("{}: {}개".format(key, value))
        # print(word_item)
        # print(max(word_item, key=word_item.get), "<--------맥스키")
        if 0 in word_item:
            # print('0지움')
            del word_item[0]
        if '' in word_item:
            # print('띄어쓰기지움')
            del word_item['']
        if len(word_item) == 0:
            # print("딕셔너리가 비어있어 retrun")
            return

        maxkey = max(word_item, key=word_item.get)
        # print(type(maxkey), '<-- 맥스키 타입')
        maxkey = str(maxkey).replace("\n", "").replace(" ", "")
        # print(11111111,maxkey, '<--리플레이스 한 맥스키')
        a = YGlast_modul.in_user()
        a.in_car(client_socket,maxkey)

        # if max(word_item, key=word_item.get).isdigit() == True:
        #     maxkey = max(word_item, key=word_item.get)
        #     print(maxkey, "<-- 마지막if")
        # else:
        #     maxkey = max(word_item, key=word_item.get).replace("\n", "")
        #     print(maxkey, "<-- 마지막else")

cam = changimg()
espcam_thread = threading.Thread(target=cam.start)
espcam_thread.daemon = True
espcam_thread.start()


class Recognition:

    def ExtractNumber(self, savecounts):
        global LOCELPATH
        try:
            Number = f'{LOCELPATH}{savecounts}.jpg'
            # print(Number)
            # 해당 폴더에 있는 이미지파일을 Number 객체에 할당.
            img = cv.imread(Number, cv.IMREAD_COLOR)
            # img변수에 위 Number객체(파일이름객체) BGR이미지 데이터로 읽어서 선언

            copy_img = img.copy()
            img2 = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            qr_codes = pyzbar.decode(img2)
            if qr_codes:
                qr_code_data = qr_codes[0].data.decode('utf-8')
                print('QR code data:', qr_code_data)
                return qr_code_data
            else:
                pass
            # img 이미지 객체를 BGR에서 흑백으로 변경하고 img2에 할당
            cv.imwrite('gray.jpg', img2)
            # img2를 첫번째 매개변수로 저장

            equal = cv.equalizeHist(img2)

            blur = cv.GaussianBlur(equal, (3, 3), 5)
            # 가우시안 블러 처리 # 사진을 흐릿하게 만들어냄.
            # cv.GaussianBlur(src, ksize, sigmaX, dst=None, sigmaY=None, borderType=None) -> dst
            # src : 입력영상, 각 채널별로 처리됨.
            # dst : 출력영상 src와 같은 크기, 같은 타입
            # ksize: 가우시안 커널 크기, (0,0)을 지정하면 sigma값에 의해 자동 결정됨.
            # sigmaX : x방향 sigma
            # sigmaY : y방향 sigma , 0이면 Xsigma 와 같게 설정
            # borderType : 가장자리 픽셀 확장방식
            cv.imwrite('blur.jpg', blur)
            # 블러처리한 사진 저장
            canny = cv.Canny(blur, 100, 200)
            # 캐니 외각선 추출 처리
            # cv.Canny(image, threshold1, threshold2, edges=None, apertureSize=None, L2gradient=None) -> edges
            # image : 입력이미지
            # threshold1 : 하단 임계값
            # threshold2 : 상단 임계값
            # edges : 엣지 사진
            # apertureSize: 소벨 연산을 위한 커널 크기. 기본값은 3
            # L2gradient: True이면 L2 norm 사용, False이면 L1 norm 사용. 기본값은 False.
            cv.imwrite('canny.jpg', canny)
            # 캐니 영상 저장
            contours, hierarchy = cv.findContours(canny, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            # 파인드컨튜얼 외각선 정보 검출 함수
            # cv.findContours(image, mode, method, contours=None, hierarchy=None, offset=None) -> contours, hierarchy
            # image: 입력 영상. non-zero 픽셀을 객체로 간주함.
            # mode: 외곽선 검출 모드. cv.RETR_로 시작하는 상수.
            # method: 외곽선 근사화 방법. cv.CHAIN_APPROX_로 시작하는 상수.
            # contours: 검출된 외곽선 좌표. numpy.ndarray로 구성된 리스트. len(ccontoursontours)=전체 외곽선 개수(N). contours[i].shape=(K, 1, 2). contours[i].dtype=numpy.int32.
            # hierarchy: 외곽선 계층 정보. numpy.ndarray. shape=(1, N, 4). dtype=numpy.int32. hierarchy[0, i, 0] ~ hierarchy[0, i, 3]이 순서대로 next, prev, child, parent 외곽선 인덱스를 가리킴. 해당 외곽선이 없으면 -1.
            # offset: 좌표 값 이동 옵셋. 기본값은 (0, 0).
            # 리턴을 image, contours , hierachy 로 한다.? 고 되어 있으나
            # contours : 등고선
            # hierarchy : 계층?

            # cv.RETR_TREE : mode 부분에서 -> 계층 구조를 만듭니다.
            # cv.CHAIN_APPROX_SIMPLE : method 부분에서 ->  contours line을 그릴 수 있는 point 만 저장. (ex; 사각형이면 4개 point)

            box1 = []
            f_count = 0
            select = 0
            plate_width = 0

            for i in range(len(contours)):
                cnt = contours[i]
                area = cv.contourArea(cnt)
                # cv.contourArea : 외곽선이 감싸는 영역의 면적을 반환합니다.
                # cv.contourArea(contour, oriented=None) -> retval
                # contour: 외곽선 좌표. numpy.ndarray. shape=(K, 1, 2)
                # oriented: True이면 외곽선 진행 방향에 따라 부호 있는 면적을 반환. 기본값은 False.
                # retval: 외곽선으로 구성된 영역의 면적 리턴값

                x, y, w, h = cv.boundingRect(cnt)
                # cv.boundingRect : 주어진 점을 감싸는 최소 크기 사각형(바운딩 박스)를 반환합니다.
                # cv.boundingRect(array) -> retval
                # array: 외곽선 좌표. numpy.ndarray. shape=(K, 1, 2)
                # retval: 사각형 정보. (x, y, w, h) 튜플. 리턴값

                rect_area = w * h  # area size
                aspect_ratio = float(w) / h  # ratio = width/height

                if (aspect_ratio >= 0.1) and (aspect_ratio <= 0.7) and (rect_area >= 100) and (rect_area <= 1800):
                    cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
                    # rectangle(img, 시작점좌표, 끝점좌표, 색(BGR), 선두께, 라인종류, 시프트)
                    # img 에 사각형 그리기
                    box1.append(cv.boundingRect(cnt))

            for i in range(len(box1)):  # Buble Sort on python
                for j in range(len(box1) - (i + 1)):
                    if box1[j][0] > box1[j + 1][0]:
                        temp = box1[j]
                        box1[j] = box1[j + 1]
                        box1[j + 1] = temp

            # to find number plate measureing length between rectangles
            for m in range(len(box1)):
                count = 0
                for n in range(m + 1, (len(box1) - 1)):
                    delta_x = abs(box1[n + 1][0] - box1[m][0])
                    # 절대값 함수 abs
                    if delta_x > 150:
                        break
                    delta_y = abs(box1[n + 1][1] - box1[m][1])
                    if delta_x == 0:
                        delta_x = 1
                    if delta_y == 0:
                        delta_y = 1
                    gradient = float(delta_y) / float(delta_x)
                    if gradient < 0.25:
                        count = count + 1
                # measure number plate size
                if count > f_count:
                    select = m
                    f_count = count
                    plate_width = delta_x
            cv.imwrite('snake.jpg', img)
            # 이미지 저장

            number_plate = copy_img[box1[select][1] - 10:box1[select][3] + box1[select][1] + 20, box1[select][0] - 10:110 + box1[select][0]]
            resize_plate = cv.resize(number_plate, None, fx=1.8, fy=1.8, interpolation=cv.INTER_CUBIC + cv.INTER_LINEAR)
            # 사이즈 변경 함수 cv.resize
            plate_gray = cv.cvtColor(resize_plate, cv.COLOR_BGR2GRAY)
            # BGR 이미지 흑백으로 변경
            ret, th_plate = cv.threshold(plate_gray, 80, 255, cv.THRESH_BINARY)
            # 이미지 임계처리 이진화 : 픽셀 RGB값의 절대값이 thresh(임계값)을 넘어가면 maxval로 변경됨.
            # cv.threshold(src, thresh, maxval, type) → retval, dst

            cv.imwrite('plate_th.jpg', th_plate)
            kernel = np.ones((3, 3), np.uint8)
            # 3:3 np 테이블을 1로 채운 후에 kernel 변수에 할당.
            er_plate = cv.erode(th_plate, kernel, iterations=1)
            # 모폴로지 침식 연산함수 cv.erode
            # cv.erode(src, kernel, dst=None, anchor=None, iterations=None, borderType=None, borderValue=None) -> dst
            # src: 입력 영상
            # kernel: 구조 요소. getStructuringElement() 함수에 의해 생성 가능. 만약 None을 지정하면 3x3 사각형 구성 요소를 사용.
            # dst: 출력 영상. src와 동일한 크기와 타입
            # anchor: 고정점 위치. 기본값 (-1, -1)을 사용하면 중앙점을 사용.
            # iterations: 반복 횟수. 기본값은 1
            # borderType: 가장자리 픽셀 확장 방식. 기본값은 cv.BORDER_CONSTANT.
            # borderValue: cv.BORDER_CONSTANT인 경우, 확장된 가장자리 픽셀을 채울 값.

            er_invplate = er_plate
            cv.imwrite('er_plate.jpg', er_invplate)
            custom_config = r'--psm 6 -c tessedit_char_whitelist=0123456789 --tessdata-dir "C:\Program Files\Tesseract-OCR\tessdata"'
            result = pytesseract.image_to_string(Image.open('er_plate.jpg'), config=custom_config)# , config='digits',config='digits'
            # Tesseract OCR 처리에서 수정되지 않은 출력을 문자열로 반환합니다.
            # 매개변수 이미지, lang = 언어
            return (result.replace(" ", ""))
        except Exception as ee:
            # print(f"ExtractNumber 에러 : {ee}")
            return 0

recogtest = Recognition()





def start_server(client_socket, addr):
    print('>> Connected by :', addr[0], ':', addr[1])

    # 클라이언트가 접속을 끊을 때 까지 반복합니다.
    while True:

        try:

            # 데이터가 수신되면 클라이언트에 다시 전송합니다.(에코)
            data = client_socket.recv(1024).decode()

            YGlast_modul.client_connect().data_Analyiss(data, client_socket,day)

            if not data:
                print('>> Disconnected by ' + addr[0], ':', addr[1])
                break


            # 서버에 접속한 클라이언트들에게 채팅 보내기
            # 메세지를 보낸 본인을 제외한 서버에 접속한 클라이언트에게 메세지 보내기
            # for client in client_sockets:
            #     if client != client_socket:
            #         client.send(data)

        except ConnectionResetError as e:
            print('>> Disconnected by ' + addr[0], ':', addr[1])
            break

    if client_socket in client_sockets:
        client_sockets.remove(client_socket)
        print('remove client list : ', len(client_sockets))

    client_socket.close()


try:
    while True:
        print('>> Wait')

        client_socket, addr = server_socket.accept()
        client_sockets.append(client_socket)
        start_new_thread(start_server, (client_socket, addr))
        print("참가자 수 : ", len(client_sockets))

        db = YGlast_modul.DB()
        db.make_db()

        day = '2023-03-01'
        # day = datetime.datetime.today()
        print('DB 완료')

except Exception as e:
    print('에러는? : ', e)

finally:
    server_socket.close()


