import socket
import sys
import time
import pytesseract
import pymysql
import datetime
import os
import matplotlib.pyplot as plt
import threading
from _thread import *
import serial

'2023-03-20'
today_day_ = datetime.datetime.now().strftime('%Y-%m-%d')
day = datetime.datetime.now().strftime('%Y-%m-%d')
img_car_numer = None
user_in_car_count = 0

LOCELPATH = 'C:\\Users\\202-1575\\PycharmProjects\\pythonProject2\\lastproject\\picture\\'


class DB:  # 데이터 베이스와 연결
    def __init__(self):
        self.con = pymysql.connect(host='localhost', user='root', password='0000', charset='utf8',
                                   sql_mode='NO_ENGINE_SUBSTITUTION')  # 데이터베이스 생성전 SQL과 Python을 연결하는 코드
        self.cur = self.con.cursor()

    def make_db(self):  # 존재 유무에 따라 만들려고 하였으나 계속 오류가 나서 try를 사용하여 데이터베이스를 만들었으며 마지막에 finally로 SQL에 생성한 데이터베이스로 Python을 연결
        try:
            with self.con:
                with self.con.cursor() as self.cur:
                    self.cur.execute("CREATE DATABASE project_car")
                    self.con.commit()
                    self.make_car_info()
                    self.make_use_data()
                    self.make_remember_park()
                    # self.make_customer_info()

        except Exception as e:
            print('존재하는 데이터베이스입니다.')

        finally:
            self.con = pymysql.connect(host='localhost', user='root', password='0000', db='project_car',charset='utf8', sql_mode='NO_ENGINE_SUBSTITUTION')
            self.cur = self.con.cursor()
            self.make_car_info()
            self.make_use_data()
            self.make_remember_park()

    def make_car_info(self):  # 입차하는 차량의 정보를 저장하는 Table을 만드는 함수
        try:
            a = "CREATE TABLE if not exists car_info (car_id varchar(100) , number int(10), in_time varchar(40),img varchar(100));"
            self.cur.execute(a)
            self.con.commit()

        except Exception as e:
            print("DB macke", e)

    def make_use_data(self):  # 이용 차량 수와 이용시간 정보를 저장하는 Table을 만드는 함수
        try:
            a = "CREATE TABLE if not exists use_data (year varchar(5), Mon varchar(4), week int(10), day varchar(10) ,in_car int(100), use_time varchar(1000),pay int(255));"
            self.cur.execute(a)
            self.con.commit()

        except Exception as e:
            print("use_table 에러", e)

    def make_remember_park(self):
        try:
            a = "CREATE TABLE if not exists remember_park (park_key int(10));"
            self.cur.execute(a)
            self.con.commit()

        except Exception as e:
            print("customer_info 에러",e)

    def insert_cer_info(self, car_id, number, in_time, img):  # 입차하는 차량의 정보를 입차할때마다 저장하는 함수
        try:
            a = "insert into project_car.car_info(car_id,number,in_time,img) values (%s,%s,%s,%s);"
            arr = (car_id, number, in_time, img)

            self.cur.execute(a, arr)
            self.con.commit()
        except Exception as e:
            print("자동차 데이터 베이스 오류", e)

    def insert_use_data(self, year, Mon, week, day, in_car, use_time, pay):  # 출차할 때마다 이용 차량 수와 이용 시간을 저장하는 함수
        try:
            a = "insert into project_car.use_data(year,Mon,week,day,in_car,use_time,pay) values (%s,%s,%s,%s,%s,%s,%s);"
            arr = (str(year), str(Mon), str(week), str(day), str(in_car), str(use_time), str(pay))

            self.cur.execute(a, arr)
            self.con.commit()
        except Exception as e:
            print("자동차 데이터 베이스 오류2222222222", e)

    def insert_remember_park(self,key):
        try:
            a = "insert into project_car.remember_park(park_key) values (%s);"
            arr = (key)

            self.cur.execute(a,arr)
            self.con.commit()
        except Exception as e:
            print("insert customer_info 오류",e)

    def check_car_info(self, car_id):  # 입차된 차량이 있는지 체크하는 함수
        try:
            pp = f"select * from project_car.car_info;"
            self.cur.execute(pp)
            result = self.cur.fetchall()
            print(result, '<--resurt 데이터베이스 찾은 값들')

            for i in result:
                for j in i:
                    if j == car_id:
                        return 1
                    else:
                        pass
            return 0
        except Exception as e:
            print("차량 번호 찾기 오류", e)

    def find_car_info(self, car_id):  # 차량의 정보를 입력 하였을 때 차량의 정보를 출력하는 함수
        a = f"select * from project_car.car_info Where car_id = {car_id}"
        self.cur.execute(a)
        result = self.cur.fetchall()
        return result

    def find_car_park_number(self, parking_number):
        a = f"select * from project_car.car_info Where number = {parking_number}"
        print(parking_number)
        self.cur.execute(a)
        result = self.cur.fetchall()
        if result != "":
            return result
        else:
            return 0

    def find_car_time_number(self, time_):
        a = f"select * from project_car.car_info Where in_time = {time_}"
        self.cur.execute(a)
        result = self.cur.fetchall()
        return result

    def find_remember_park(self):
        a =f"select * from project_car.remember_park"

        self.cur.execute(a)
        result = self.cur.fetchall()
        return result

    def find_use_data(self, day, week, car_in, user_time,pay):  # 이용차량수와 이용시간을 일,주,월별로 출력할수 있도록한 함수
        try:
            day = day.split('-')# day는 리스트 연,월,일

            pp = f"SELECT * FROM project_car.use_data WHERE day = {day[2]};"
            self.cur.execute(pp)
            result = self.cur.fetchall()

            if result == ():
                self.insert_use_data(day[0], day[1], week, day[2],car_in, user_time, pay)
            elif result != ():
                one_list = []
                for i in result:
                    if i != "":
                        for j in i:
                            one_list.append(j)

                one_list[4] += car_in

                one_list[6] = int(one_list[6])
                one_list[6] += int(pay)

                # time__ = datetime.datetime.strptime(one_list[5], "%Y-%m-%d %H:%M:%S")
                result_time = int(one_list[5]) + int(user_time)
                result_time = str(result_time)
                self._update_(str(one_list[4]), result_time,str(one_list[6]))

        except Exception as e:
            print(" dddd오류", e)

    def Delete_car_info(self, car_id):  # 차량이 출차하였을 때 저장된 입차 정보를 지우는 함수
        try:
            send_db = f"DELETE FROM project_car.car_info WHERE number = '{car_id}';"
            self.cur.execute(send_db)
            self.con.commit()

        except Exception as e:
            print("데이터 삭제 함수 오류", e)

    def find_car_info_full(self):
        try:
            pp = "SELECT * FROM project_car.use_data;"
            a = self.cur.execute(pp)
            return a

        except Exception as e:
            print("그래프용 데이터 찾기 오류", e)

    def _update_(self, in_car_count, in_car_time,pay):  # 이용차량수와 이용시간을 업데이트하는 함수
        # UPDATE use_data SET in_car = 값, use_time = 값 WHERE 조건식
        try:
            print(in_car_time[11:])
            sql = f"UPDATE project_car.use_data SET in_car = {int(in_car_count)}, use_time = {in_car_count} WHERE pay = {pay}"
            self.cur.execute(sql)
            self.con.commit()

        except Exception as e:
            print("수정 오류", e)

    def park_update_(self, key):
        try:
            sql = f"UPDATE project_car.remember_park SET park_key = {key}"
            self.cur.execute(sql)
            self.con.commit()

        except Exception as e:
            print("주차 번호 업데이트 오류", e)

    def show_use_graph(self):  # 그래프에 정보를 띄우기 위해 출격하는 함수
        pp = f"SELECT * FROM project_car.use_data;"
        self.cur.execute(pp)
        result = self.cur.fetchall()
        print(result)
        return result


barcode = 0


class in_user():
    count = 1

    def in_car(self, client_socket, car):  # 입차하였을 떄 입차한 차량의 사진과 번호를 Client에게 보내는 함수
        global LOCELPATH
        global img_car_numer
        global barcode
        global packing_number
        noting = 0
        if packing_number == []:
            noting = 1
        elif packing_number != []:
            noting = 0
        print(car, "<_---------- maxkey 들어옴")
        if len(str(car)) == 4 and car != 0 and car.isdecimal() == True:
            if noting == 0:
                old_file = f"{LOCELPATH}20.jpg"
                print(old_file, "<-- old_file")
                new_file = f"{LOCELPATH}{str(car) + str(self.count)}.jpg"
                print(new_file, '<--new_file')
                while os.path.isfile(new_file) == True:
                    # if os.path.isfile(new_file):
                    #     print('if++++',self.count)
                    #     self.count += 1
                    #     continue
                    # else:
                    #     print("else++++")
                    #     img_car_numer = str(car)+str(self.count)
                    #     print(img_car_numer, '<--img_car_numer')
                    #     break
                    self.count += 1
                    new_file = f"{LOCELPATH}{str(car) + str(self.count)}.jpg"

                os.rename(old_file, new_file)
                img_car_numer = str(car) + str(self.count)
                self.count = 1

                info_ = f"입차,{car}"
                aduino.serialout(car + '\n')

                client_socket.send(info_.encode())
                # print(info_)
                send_img = new_file

                data_transferred = 0
                with open(send_img, 'rb') as f:
                    data_ = f.read(65536)
                    # time.sleep(3)
                    print(2, '입차 사진')
                    data_transferred += client_socket.send('a'.encode() + data_)
                    print("데이터 송신 완료")
                    print(f"파일명 : {car}.jpg  전송량{data_transferred}")
                    data_ = f.read(65536)

                # elif noting == 1:
                #     a = f"입차,빈 주차 공간이 없어 주차가 불가능합니다."
                #     client_socket.send(a.encode())


            else:
                info_ = f"입차,주차 공간이 없습니다.0"
                client_socket.send(info_.encode())

        elif len(car) >= 4 and car != 0 and car.isalnum() == True:
            print(car, "<-------바코드 if문 들어옴")
            barcode = int(car[0:len(car) - 1])
            print('type:', type(barcode), '값', barcode)

            print('modul', car)


packing_number = [1, 2, 3, 4, 5, 6]
remember_pack = 1
before_day = "2023-03-22"
D_day = 0


class client_connect:  # Client와 연결하는 함수
    def __init__(self):
        # 주차타워 주차공간에 대한 자리 번호

        self.save_info = []  # 입차하는 차의 차량번호, 입차시간, 주차되는 추파공간에 대한 정보를 리스트로 저장
        self.DB = DB()
        self.connect = None  # Client에 send를 편하게 하기 위하여 self로 박아둠
        self.week_number = 1

        self.checking_parking_number()
        self.checking_day()
        self.checking_remember()

    def checking_parking_number(self):
        global packing_number
        remove = []
        if packing_number != None:
            for i in packing_number:
                checking = self.DB.find_car_park_number(str(i))
                # print(checking,"<------checking")
                if checking != ():
                    remove.append(i)
                else:
                    pass
            for i in remove:
                packing_number.remove(i)
        # print(remove,'<-------remove')
        # print(packing_number,'<--------packing_number')
        else:
            packing_number = [1, 2, 3, 4, 5, 6]
            for i in packing_number:
                checking = self.DB.find_car_park_number(str(i))
                # print(checking,"<------checking")
                if checking != ():
                    remove.append(i)
                else:
                    pass
            for i in remove:
                packing_number.remove(i)
            pass

    def checking_day(self):
        global packing_number
        global before_day
        global user_in_car_count
        today = str(datetime.datetime.today())[0:10]
        if today == before_day:
            if user_in_car_count == 0:
                user_in_car_count = 6 - len(packing_number)
            else:
                pass
        else:
            user_in_car_count = 0
            before_day = today

    def checking_remember(self):
        remember = self.DB.find_remember_park()
        if remember == ():
            self.DB.insert_remember_park(1)
        else:
            remember_pack = remember
        print(remember, "<---------remember")

    def data_Analyiss(self, data, client_socket, day_):  # Client에서 받은 데이텨를 적절한 곳으로 보내는 데이터 분석 함수
        global D_day
        global remember_pack
        global packing_number
        global user_in_car_count
        global barcode
        global LOCELPATH

        self.connect = client_socket
        print(data)
        if data[
           1:3] == '조회':  # 차량의 번호 입력 후 조회를 누르면 보내지는 데이터  / DB에서 존재 여부를 찾고 리턴되는 데이터의 type을 보고 Ture,False를 Client에 전달
            data = data[4:8]  # -1?? 아니면 없이/???
            # print(data, '<--데이터베이스 체그 번호')
            a = self.DB.check_car_info(data)
            # print(a, '<--a는 데이터베이스 찾은다음 출력')

            if a == 1:  # DB에 번호가 존재하는지 찾는 조건문 필요 /
                a = self.DB.find_car_info(data)

                send_result = "출차,조회,True"
                two_list = []
                for i in a:
                    one_list = []
                    for j in i:
                        one_list.append(j)
                    two_list.append(one_list)
                    send_result += f'={one_list}'

                print(send_result, "<--send_result")
                # print(5,'변경')
                self.send_massege(send_result)

                for i in range(len(two_list)):
                    print(i, "<---------for 문 i")
                    print(two_list, "<------- two_list")
                    print(str(two_list[i][3]), "<-------str(i[3])")

                    data_transferred = 0
                    if i == 0:
                        send_img = f'{LOCELPATH}{str(two_list[i][3])}.jpg'
                        print(send_img, "<------send_img")
                        data_transferred = 0
                        print('0번')
                        with open(send_img, 'rb') as f:
                            data_ = f.read(65536)

                            # time.sleep(3)
                            print(3, '조회 - T')
                            data_transferred += client_socket.send('f'.encode() + data_)
                            print('f'.encode() + data_, "<--------0번데이타")
                            print("데이터 송신 완료")
                            print(f"파일명 : {str(two_list[i][3])}.jpg  전송량{data_transferred}")
                            data_ = f.read(65536)
                        time.sleep(0.5)

                    elif i == 1:
                        send_img = f'{LOCELPATH}{str(two_list[i][3])}.jpg'
                        print(send_img, "<------send_img")
                        data_transferred = 0
                        print('1번')

                        with open(send_img, 'rb') as f:
                            data_ = f.read(65536)
                            # time.sleep(3)
                            print(2, '조회 - T')
                            data_transferred += client_socket.send('g'.encode() + data_)
                            print('g'.encode() + data_, "<-------1번데이타")
                            print("데이터 송신 완료")
                            print(f"파일명 : {str(two_list[i][3])}.jpg  전송량{data_transferred}")
                            data_ = f.read(65536)
                        time.sleep(0.5)

                    elif i == 2:
                        send_img = f'{LOCELPATH}{str(two_list[i][3])}.jpg'
                        print(send_img, "<------send_img")
                        data_transferred = 0
                        print('2번')
                        with open(send_img, 'rb') as f:
                            data_ = f.read(65536)
                            # time.sleep(3)
                            print(2, '조회 - T')
                            data_transferred += client_socket.send('h'.encode() + data_)
                            print('h'.encode() + data_, "<-------2번데이타")
                            print("데이터 송신 완료")
                            print(f"파일명 : {str(two_list[i][3])}.jpg  전송량{data_transferred}")
                            data_ = f.read(65536)
                        time.sleep(0.5)


                    elif i == 3:
                        send_img = f'{LOCELPATH}{str(two_list[i][3])}.jpg'
                        data_transferred = 0

                        with open(send_img, 'rb') as f:
                            data_ = f.read(65536)
                            print(3, '조회 - T')
                            data_transferred += client_socket.send('i'.encode() + data_)
                            print("데이터 송신 완료")
                            print(f"파일명 : {str(two_list[i][3])}.jpg  전송량{data_transferred}")
                            data_ = f.read(65536)
                        time.sleep(0.5)


            elif a == 0:
                send = "출차,조회,False"
                print(4, "F")
                self.send_massege(send)

            else:
                print('출차 번호 검증 오류')

        elif data[
             2:4] == "출차":  # 출차를 완료했을 시 보내지는 함수 / DB에서 차량 정보를 조회하여 주차된 칸의 정보를 얻어 차량을 꺼낸 뒤 DB에서 그 차량에 대한 정보를 지움 (출차,1234)
            car_number = data[15:19]
            print(car_number, '<--car_number')
            out_time = data[56:len(data) - 1]
            print(out_time, '<--out_time')
            in_time = data[28:47]
            print(in_time, '<--in_time')
            in_user_info = self.DB.find_car_info(car_number)  # 차량번호에 대한 정보를 가지고 오는 함수
            print(in_user_info, '<--in_user_info')
            in_time_ = datetime.datetime.strptime(in_time, "%Y-%m-%d %H:%M:%S")  # 입차된 시간
            print(in_time_, '<--in_time_')
            out_time_ = datetime.datetime.strptime(out_time, "%Y-%m-%d %H:%M:%S")  # 출차된 시간
            print(out_time_, '<--out_time_')

            user_time = out_time_ - in_time_  # 이용시간 구하는 함수
            user_min = 0
            if 'day' in str(user_time):
                user_time = str(user_time).split(',')
                user_time[1] = str(user_time[1]).split(":")
                user_time[0] = str(user_time[0][0:len(user_time[0]) - 5])
                user_min = (int(user_time[0]) * 24 * 60) + int(user_time[1][0]) * 60 + int(user_time[1][1])
            else:
                user_time = str(user_time).split(":")
                user_min = int(user_time[0]) * 60 + int(user_time[1])
            pay = user_min * 100
            save_pay = pay

            a = '출차,True'
            self.send_massege(a + "," + str(pay))
            print(pay, "원", '<-- 출차 완료보낸 메세지')

            while pay != 0:
                print(pay, "<--------pqy")
                print(barcode, "<---------barcode")
                if barcode != 0:
                    pay = pay - barcode
                    barcode = 0
                    if pay < 0:
                        pay = 0
                    print(pay, "<-------- 계산된 값")
                    self.send_massege(a + "," + str(pay))
                    print('변경 된 값 보냈다!!')
                else:
                    continue

            # ----------------------------------------------------------------------------
            one_list = []
            for i in in_user_info:
                for j in i:
                    if j == in_time:
                        for k in i:
                            one_list.append(k)
                    else:
                        pass

            before_remember = remember_pack

            remember_pack = one_list[1]  # 출차된 주차칸의 정보를 전달
            self.DB.park_update_(remember_pack)
            packing_number.append(remember_pack)  # 출차된 주차칸의 번호를 다시 packing_number에 넣는 함수
            packing_number = packing_number.sort()  # 크기 정렬

            after_remember = remember_pack

            if before_remember > after_remember:
                if before_remember == 1 or before_remember == 2:
                    self.send_massege('출차,결제,86')
                elif before_remember == 3 or before_remember == 4:
                    self.send_massege('출차,결제,115')
                elif before_remember == 5 or before_remember == 6:
                    self.send_massege('출차,결제,145')
            elif before_remember < after_remember:
                if after_remember == 1 or after_remember == 2:
                    self.send_massege('출차,결제,86')
                elif after_remember == 3 or after_remember == 4:
                    self.send_massege('출차,결제,115')
                elif after_remember == 5 or after_remember == 6:
                    self.send_massege('출차,결제,145')
            elif before_remember == after_remember:
                if after_remember == 1 or after_remember == 2:
                    self.send_massege('출차,결제,86')
                elif after_remember == 3 or after_remember == 4:
                    self.send_massege('출차,결제,115')
                elif after_remember == 5 or after_remember == 6:
                    self.send_massege('출차,결제,145')

            # 기존에 있던 파렛트 넣는 부분
            if before_remember == 1:
                aduino.serialout('z\n')
            elif before_remember == 2:
                aduino.serialout('x\n')
            elif before_remember == 3:
                aduino.serialout('a\n')
            elif before_remember == 4:
                aduino.serialout('s\n')
            elif before_remember == 5:
                aduino.serialout('q\n')
            elif before_remember == 6:
                aduino.serialout('w\n')

            # 파렛트 출차함
            if after_remember == 1:
                aduino.serialout('c\n')
            elif after_remember == 2:
                aduino.serialout('v\n')
            elif after_remember == 3:
                aduino.serialout('d\n')
            elif after_remember == 4:
                aduino.serialout('f\n')
            elif after_remember == 5:
                aduino.serialout('e\n')
            elif after_remember == 6:
                aduino.serialout('r\n')

            path = f'{LOCELPATH}'
            os.remove(path + one_list[3] + '.jpg')  # 출차된 차량의 사진을 지우는 함수
            self.DB.Delete_car_info(remember_pack)  # 데이터베이스에서 차량 정보 지움

            day = out_time  # 출차된 시간의 날짜를 구하는 함수
            day = day[:10]

            week__ = self.get_week(day_)  # 매개 변수에 들어간 함수의 날짜에 대한 주를 구하는 함수
            # ------------------------------------------------------------------------- 주 구분 및 데이터 찾고 추가 또는 업데이트 하는 코드
            if week__ == "5":
                self.DB.find_use_data(day, self.week_number, 1, user_min, save_pay)
                if self.week_number != 4:
                    self.week_number += 1
                elif self.week_number == 4:  # 다음 달로 넘기는 함수
                    self.week_number = 1
            else:
                self.DB.find_use_data(day, self.week_number, user_in_car_count, user_min, save_pay)

            # ------------------------------------------------------------------------------


        elif data[
             2:4] == "입차":  # 입차 완료 버튼을 눌렀을 떄 발동 되는 함수로 남아 있는 parking_number에서 제일 작은 수에 보내며 입차한 차량번호, 입차시간, 입차된 주차공간번호(사용된 번호는 삭제)를 DB에 저장
            # Arduino에 데이터 전송
            # len 에서 넌타입 에러 발생함 수정 요함
            global img_car_numer
            aduino.serialout('y\n')  # 아두이노 서보모터 닫는 키
            # 서보모터 아직 시간이 지나면 자동적으로 내려오는 코드 없음.
            try:
                print(data)

                if len(packing_number) == 6:  # 입차시 주차 칸으로 들어가는 함수

                    number = 1
                    remember_pack = 1
                else:
                    print(remember_pack, "<-------remember_pack")
                    print(self.pull_car_plate(remember_pack), "<--------self.pull_car_plate(remember_pack)")
                    remember_pack = self.pull_car_plate(remember_pack)
                    self.DB.park_update_(remember_pack)
                print(remember_pack, '<--remember_pack')

                car_number = data[15:19]
                in_time = data[27:len(data) - 1]
                in_time = in_time

                self.save_info.append(car_number)
                self.save_info.append(remember_pack)
                self.save_info.append(in_time)
                if car_number == img_car_numer[0:4]:
                    print(img_car_numer, "<--------img_car_numer")
                    print(car_number, "<--------car_numer")
                    self.save_info.append(img_car_numer)
                    print(111111)

                elif car_number != img_car_numer[0:4]:
                    print(img_car_numer, "<--------img_car_numer")
                    print(car_number, "<--------car_numer")
                    count = 1
                    path_old = f"{LOCELPATH}{img_car_numer}.jpg"
                    path = f"{LOCELPATH}{str(car_number)}{str(count)}.jpg"
                    name = f"{car_number}{str(count)}"
                    while os.path.isfile(path) == True:
                        count += 1
                        path = f"{LOCELPATH}{car_number}{str(count)}.jpg"

                        name = f"{car_number}{str(count)}"

                    os.rename(path_old, path)
                    self.save_info.append(name)
                    car_number = 0

                if remember_pack == 1:
                    aduino.serialout('z\n')
                elif remember_pack == 2:
                    aduino.serialout('x\n')
                elif remember_pack == 3:
                    aduino.serialout('a\n')
                elif remember_pack == 4:
                    aduino.serialout('s\n')
                elif remember_pack == 5:
                    aduino.serialout('q\n')
                elif remember_pack == 6:
                    aduino.serialout('w\n')

                packing_number.remove(remember_pack)

                remember_pack = self.pull_car_plate(remember_pack)
                if remember_pack == 1:
                    aduino.serialout('c\n')
                elif remember_pack == 2:
                    aduino.serialout('v\n')
                elif remember_pack == 3:
                    aduino.serialout('d\n')
                elif remember_pack == 4:
                    aduino.serialout('f\n')
                elif remember_pack == 5:
                    aduino.serialout('e\n')
                elif remember_pack == 6:
                    aduino.serialout('r\n')

                print(self.save_info, "<---------self.save_info")
                self.DB.insert_cer_info(self.save_info[0], self.save_info[1], self.save_info[2], self.save_info[3])
                user_in_car_count += 1
                # self.pull_car_plate(remember_pack)
                self.save_info.clear()
                self.send_massege('incarTrue')  # 클라이언트로 메세지 보냄
                # if remember_pack == '6':
                #     Serial.print('w')
                # else if remember_pack == '5':
                #     Serial.print('q')


            except Exception as e:
                print("차량 정보 추자 오류", e)

        # elif data[0:4] == "변경완료":
        #     a = self.DB.find_car_park_number(data[25:26])
        #     str_info = None
        #
        #     for i in a:
        #         if i !="":
        #             str_info = i
        #     one_list = []
        #     for i in str_info:
        #         one_list.append(i)
        #
        #     send_str = f"변경,True,{one_list[0]},{one_list[2]}"
        #     print(send_str,"<-------send_str변경완료")
        #
        #     self.send_massege(send_str)
        #     print("메세지 전송완료")
        #
        #     send_img = f'{LOCELPATH}{one_list[3]}.jpg'
        #
        #     data_transferred = 0
        #     with open(send_img, 'rb') as f:
        #         data_ = f.read(65536)
        #         # time.sleep(3)
        #         # print(7,"변경 완료")
        #         data_transferred += client_socket.send("g".encode()+data_)
        #         print("데이터 송신 완료")
        #         print(f"파일명 : {one_list[3]}.jpg  전송량{data_transferred}")
        #         data_ = f.read(65536)

        elif data[2:9] == '관리자 로그인' or data[
                                       1:7] == '관리자 조회':  # 관리자 창에서 비밀번호를 눌렀을 때 발동되는 함수로 passward와 같은 번호를 입력해야지만이 Client에 Ture가 전달
            passward = '0000'

            if data[2:9] == '관리자 로그인':
                data = data[11:len(data) - 1]

                if passward == data:
                    self.send_massege("관리자,True")


                elif passward != data:
                    self.send_massege("관리자,False")

            if data[1:7] == '관리자 조회':
                print(data)
                if data[8:9] == '일':
                    self.pay_day(data[8:9])

                elif data[8:9] == '주':

                    self.pay_week(data[8:9])

                elif data[8:9] == '월':

                    self.pay_MON(data[8:9])

                elif data[8:9] == "원":

                    self.manger_check_count(today_day_)


                elif data[8:10] == "점검":
                    a = f'관리자,점검,안전 점검까지 {D_day}일'
                    print(a, "<---------점검 까지 남은 수")
                    # print(a)
                    # print(len(a))

                    self.send_massege(a)


                elif data[8:10] == '매출':
                    a = self.find_today_pay_count(data[8:10])
                    self.send_massege(a)

                elif data[8:11] == "입차수":
                    a = self.find_today_pay_count(data[8:11])

                    self.send_massege(a)

        elif data[1:5] == '모니터링':
            self.manger_monitary()

        else:
            print(data)
            print('++++++++')

            pass

    def find_today_pay_count(self, data):
        global user_in_car_count
        self.checking_day()
        today_data = self.DB.show_use_graph()
        print(today_data)

        data_list = []
        for i in today_data:
            if i != "":
                one_list = []
                for j in i:
                    one_list.append(j)

                data_list.append(one_list)
        print(2, data_list)

        use_count = "0"
        today_pay = "0"
        today = datetime.datetime.today().day
        # print(today)

        for i in data_list:
            if int(i[3]) == today:
                # j = i[6][9:len((i[6]))].split(":")
                # today_pay = j[0]*60 +j[1]
                today_pay = i[6]  # 시간을 분 형식으로 변환

        # print(3,use_count)
        # print(4,today_pay)

        if data == "매출":
            a = '관리자,매출,' + str(today_pay)
            return a
        elif data == "입차수":
            b = '관리자,입차수,' + str(user_in_car_count)
            return b

    def pull_car_plate(self, data):  # 입차 후 car_plate를 가지올 때 최적의 동선으로 가지고 오는 알고리즘
        global packing_number
        if data % 2 != 0:
            # 홀수
            if data + 1 not in packing_number:
                min = sys.maxsize
                for i in packing_number:
                    gap = abs(data - i)
                    if gap < min:
                        near = i
                        min = gap
            else:
                near = data + 1
                min = near - data

        else:
            min = sys.maxsize
            for i in packing_number:
                gap = abs(data - i)
                if gap < min:
                    near = i
                    min = gap
        print(packing_number)
        print(f"""입력 {data} 근사값 {near} 차이 {min}""")
        return near
        #     if data + 1 in packing_number:
        #         pass
        #     else:
        #         for i in range(data-1,0,-1):
        #             if i in packing_number:
        #                 pass
        # elif data % 2 == 0:
        #     if data -1  in packing_number:
        #         pass
        #     else:
        #         for i in range(data-2,0,-1):
        #             if i in packing_number:
        #                 pass

    def get_week(self, day):  # 무슨 요일인지 구하는 함수
        day = datetime.datetime.strptime(day, '%Y-%m-%d')
        day = day.weekday()
        return day

    def pay_graph(self, x, y, day):
        # 데이터 생성
        pp = None
        if day == '일':
            pp = "day"
        elif day == '주':
            pp = "week"
        elif day == '월':
            pp = "mon"
        fig, ax1 = plt.subplots()

        s_x = x
        s_y = y
        s_x.sort()
        s_y.sort()

        ax1.plot(x, y, '-s', color='black', markersize=7, linewidth=5, alpha=0.7, label='Price')
        ax1.set_ylim(0, s_y[len(s_y) - 1] + 3000)
        ax1.set_xlabel(f"{pp}")
        ax1.set_ylabel("won")
        ax1.tick_params(axis='both', direction='in')

        # # 그래프 출력
        # plt.show()

        plt.savefig(f"save_graph_{day}.png", dpi=150)

        send_img = f'C:\\Users\\202-1575\\PycharmProjects\\pythonProject2\\lastproject\\save_graph_{day}.png'

        data_transferred = 0
        with open(send_img, 'rb') as f:
            data_ = f.read(65536)
            while data_:
                time.sleep(0.2)
                if day == '일':
                    data_transferred += self.connect.send('b'.encode() + data_)
                elif day == '주':
                    data_transferred += self.connect.send('c'.encode() + data_)
                elif day == '월':
                    data_transferred += self.connect.send('d'.encode() + data_)
                print("데이터 송신 완료")
                print(f"파일명 : ave_graph_{day}.png  전송량{data_transferred}")
                data_ = f.read(65536)

    def pay_day(self, d):
        data = self.DB.show_use_graph()
        MON = datetime.datetime.now()
        MON = MON.month

        data_list = []
        for i in data:
            if i != "":
                one_list = []
                for j in i:
                    one_list.append(j)

                data_list.append(one_list)

        day = []
        pay = {}

        for i in data_list:

            if int(i[1]) == MON:
                if i[3] in day:
                    pay[i[3]] = pay[i[3]] + i[6]

                else:
                    day.append(i[3])
                    pay[i[3]] = i[6]

        list_pay = []

        for i in pay.values():
            list_pay.append(i)

        self.pay_graph(day, list_pay, d)

    def pay_week(self, d):
        data = self.DB.show_use_graph()
        MON = datetime.datetime.now()
        MON = MON.month

        data_list = []
        for i in data:
            if i != "":
                one_list = []
                for j in i:
                    one_list.append(j)

                data_list.append(one_list)

        week = []
        pay = {1: 0, 2: 0, 3: 0, 4: 0}
        for i in data_list:
            if int(i[1]) == MON:
                print(i[1])
                pay[i[2]] = pay[i[2]] + i[6]

        list_pay = []

        for i in pay.values():
            list_pay.append(i)
        for i in pay.keys():
            week.append(i)

        print(week)
        print(list_pay, "<---------count")

        self.pay_graph(week, list_pay, d)

    def pay_MON(self, d):
        data = self.DB.show_use_graph()

        data_list = []
        for i in data:
            if i != "":
                one_list = []
                for j in i:
                    one_list.append(j)

                data_list.append(one_list)

        print(data_list, "<-------data_list")
        mon = []
        pay = {}
        timer = {}
        for i in data_list:
            print(i, "<----------i")

            if i[1] in mon:
                print(i[1])
                pay[i[1]] = pay[i[1]] + i[6]
                # timer[i[3]] = timer[i[3]] + i[5]
            else:
                mon.append(i[1])
                pay[i[1]] = i[6]
                # timer[i[3]] = i[5]
        list_pay = []
        list_time = []
        for i in pay.values():
            list_pay.append(i)
        # for i in timer.values():
        #     list_time.append(i)

        print(mon)
        print(list_pay, "<---------count")

        self.pay_graph(mon, list_pay, d)

    def draw_circle(self, remaining, past):
        global LOCELPATH
        plt.rcParams['font.size'] = 13

        slang_usage = ['remaining days', 'past days ']
        values = [remaining, past]
        lable_color = ["gold", "gainsboro"]
        wed = {"edgecolor": "w", "linewidth": 3, "width": 0.4}  # wedgeprops=wed

        fig = plt.figure(figsize=(12, 12))
        fig.set_facecolor("white")
        ax = fig.add_subplot()

        ax.pie(values, labels=slang_usage, colors=lable_color, wedgeprops=wed, counterclock=False)

        plt.savefig('save_graph_circle_.png', dpi=150)

        send_img = f'C:\\Users\\202-1575\\PycharmProjects\\pythonProject2\\lastproject\\save_graph_circle_.png'

        data_transferred = 0
        with open(send_img, 'rb') as f:
            data_ = f.read(65536)
            while data_:
                time.sleep(0.2)
                data_transferred += self.connect.send('e'.encode() + data_)
                print("데이터 송신 완료")
                print(f"파일명 : ave_graph_{day}.png  전송량 {'save_graph_circle_.png'}")
                # print(data_)
                data_ = f.read(65536)

        # shadow : 기본 값이 False로 True로 바꾸면 그림자가 생김
        # autopct = 그래프 안에 퍼센트 표시("%.1f%" = 소수 첫째짜리까지 표시, "%.2f" = 소수 둘째짜리까지 표시, "%.1f%%" = 퍼센트까지 포함)

    def manger_check_count(self, day):  # '2023-03-20'
        global D_day
        # 정기 검진은 설치 후 최소 3년 후 2년 마다 정기 안점 검사를 실시 해야 함.
        day_a = datetime.datetime.today()
        print(day_a, '<-- day_a')
        D_day_ = 730
        day = datetime.datetime.strptime(day, "%Y-%m-%d")
        print(day, '<-- day')
        if datetime.datetime.now().hour >= 10:
            d_day = str(day_a - day)[0:2]  # 오전에 시연할때 애러가 생김
        else:
            d_day = str(day_a - day)[0:1]  # 오전에 시연할때 애러가 생김
        print(d_day, '<-- d_day')

        D_day = D_day_ - int(d_day)  # while error invalid literal for int() with base 10: '9:'
        D_day_p = D_day_ - D_day
        print(D_day_p, '<-- D_day_p')
        print(D_day, '<-- D_day')
        self.draw_circle(D_day_, D_day_p)
        time.sleep(0.3)

        # if D_day == 0:
        #     self.send_massege("오늘은 안점 점검 날입니다. 점검을 실시 해주세요.")
        #     D_day = 730
        # else:
        #     pass

    def manger_monitary(self):
        global packing_number
        current_time = datetime.datetime.now()
        # 사용중인 주차칸과 사용중이 아닌 주차칸에 대한 정보를 보내는 함수
        list_parking = [1, 2, 3, 4, 5, 6]
        use_parking = '모니터링'
        parking = []
        send_ = ""
        print(packing_number)

        for i in list_parking:
            if i not in packing_number:
                parking.append(i)

            else:
                pass

        print(11111, parking)

        one_list = []
        for i in parking:
            a = self.DB.find_car_park_number(i)
            print(a)

            for k in a:
                if k != "":
                    print(k)
                    two = []
                    for j in k:
                        two.append(j)
                    one_list.append(two)

                else:
                    pass
        print(one_list, "<------one_list")

        result_pay = 0
        current_useing_time = ""

        for i in range(len(one_list)):
            useing_time = datetime.datetime.strptime(one_list[i][2], "%Y-%m-%d %H:%M:%S")
            current_useing_time = current_time - useing_time
            print(current_useing_time, '<--current_useing_time')
            if "day" in str(current_useing_time):
                current_useing_time = str(current_useing_time).split(",")
                current_useing_time[0] = current_useing_time[0].replace("day", "일")
                current_useing_time_ = current_useing_time[0] + str(current_useing_time[1][0:8])
                print(current_useing_time_ < "<-------current_useing_time_")
                print(current_useing_time, "<_--------current_useing_time")
                useing_pay = current_useing_time[1][0:7].split(":")
                day_use = current_useing_time[0][0:len(current_useing_time[0]) - 5]
                print(len(current_useing_time[0]))
                print(day_use, "<------day_use")
                print(useing_pay, "<---------useing_pay")

                result_pay = ((int(day_use) * 24 * 60) + (int(useing_pay[0]) * 60) + int(useing_pay[1])) * 100
                print(result_pay, "<-------result_pay")
                # str(current_useing_time[1][0:len(current_useing_time[1])-7])

                b = '=' + str(parking[i]) + "," + one_list[i][0] + ',' + one_list[i][
                    2] + ',' + current_useing_time_ + "," + str(result_pay) + "원"
                # b = ""
                print(b, "<----------- 보내는 메세지")
                use_parking += b
            elif "days" in str(current_useing_time):
                current_useing_time = str(current_useing_time).split(",")
                current_useing_time[0] = current_useing_time[0].replace("days", "일")
                current_useing_time_ = current_useing_time[0] + str(current_useing_time[1][0:8])
                print(current_useing_time_ < "<-------current_useing_time_")
                print(current_useing_time, "<_--------current_useing_time")
                useing_pay = current_useing_time[1][0:7].split(":")
                day_use = current_useing_time[0][0:len(current_useing_time[0]) - 5]
                print(len(current_useing_time[0]))
                print(day_use, "<------day_use")
                print(useing_pay, "<---------useing_pay")

                result_pay = ((int(day_use) * 24 * 60) + (int(useing_pay[0]) * 60) + int(useing_pay[1])) * 100
                print(result_pay, "<-------result_pay")
                # str(current_useing_time[1][0:len(current_useing_time[1])-7])

                b = '=' + str(parking[i]) + "," + one_list[i][0] + ',' + one_list[i][
                    2] + ',' + current_useing_time_ + "," + str(result_pay) + "원"
                # b = ""
                print(b, "<----------- 보내는 메세지")
                use_parking += b

            else:
                useing_pay = str(current_useing_time)[0:7].split(":")
                print(useing_pay, "<---------useing_pay")
                result_pay = ((int(useing_pay[0]) * 60) + int(useing_pay[1])) * 100
                print(result_pay, "<-------result_pay")

                b = '=' + str(parking[i]) + "," + one_list[i][0] + ',' + one_list[i][2] + ',' + str(
                    current_useing_time)[0:7] + "," + str(result_pay) + "원"
                print(b, "<----------- 보내는 메세지")
                use_parking += b

        print(88888, use_parking)

        self.send_massege(use_parking)

    def send_massege(self, data):  # Client로 데이터를 송신하는함수
        data = data.encode()
        print(data)
        self.connect.send(data)


py_serial = serial.Serial('COM7', 9600)
aduinorecv = None


class aduinoSerial:
    global aduinorecv
    adurespons = None

    def serialin(self):
        while True:
            if py_serial.readable():
                adurespons = py_serial.readline()
                adurespons = adurespons.decode()
                adurespons = adurespons.replace('\r', '')
                adurespons = adurespons.replace('\n', '')
                print(adurespons, "<-- adurespons 값")
                aduinorecv = adurespons
                # print(aduinorecv, "<-- aduinorecv전역변수")
                if aduinorecv == 'carposition':
                    aduino.serialout('t\n')
                    aduinorecv = None
                # if adurespons == '1in' or adurespons == '2in' or adurespons == '3in' or adurespons == '4in' or adurespons == '5in' or adurespons == '6in':

    def serialout(self, sdata):
        # commend = input("아두이노 전달사항 : ")
        commend = sdata  # 't'
        py_serial.write(commend.encode())
        print(sdata, '<-- sdata아두이노메세지')
        time.sleep(1)


aduino = aduinoSerial()

aduinput = threading.Thread(target=aduino.serialin)
aduinput.daemon = True
aduinput.start()