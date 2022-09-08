import tkinter as tk
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import warnings
import random
import datetime
import json
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import csv
import requests



HOST = "localhost"
USERNAME = "nud-11"
PASSWORD = "iot1234"

filename = "./iot-data.csv"

fields = ["day","humidity","stationname"]



def on_connect(self,client,userdata,rc):
    print("MQTT Connected")

def on_disconnect(client,userdata,rc=0):
    print("MQTT Disconnected")
    client.loop_stop()

#LED
"""
def on_message(client,userdata,msg):
    print(msg.topic)
    print(msg.payload.decode('utf-8','strict'))
    LED = msg.payload.decode('utf-8','strict')
    if LED == "0":
        GPIO.output(8,GPIO.HIGH)
        GPIO.output(10,GPIO.HIGH)
        GPIO.output(12,GPIO.HIGH)
    elif LED == "2":
        GPIO.output(8,GPIO.HIGH)
        GPIO.output(10,GPIO.LOW)
        GPIO.output(12,GPIO.HIGH)
    else:
        GPIO.output(8,GPIO.LOW)
        GPIO.output(10,GPIO.LOW)
        GPIO.output(12,GPIO.HIGH)
"""

#Classsifier
global classifier
classifier = KNeighborsClassifier(n_neighbors = 1)
warnings.simplefilter(action='ignore',category=UserWarning)

def predict(day,threedays,humidity):
    pred=classifier.predict([[day,threedays,humidity]])
    print(pred[0])
    return pred[0]

#line_notify
def linenotify(stationname,Token):
    url = 'https://notify-api.line.me/api/notify'
#    token = 'FfobZhNnTYC565NAZVVYqYdww65wlPdEQ9x84aI29g9'
    #token = '0ngKxQJNPDAXMFpyaSB7ytKpk1PaPqy3yAMlm23HpCv'
    token = Token
    headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+token}
    msg = 'สถานี '+stationname+' มีโอกาสเกิดดินถล่มสูง'
    r = requests.post(url, headers=headers, data = {'message':msg})
    print(r.text)


#message from topic

def on_message(client,userdata,msg):
    now = datetime.datetime.now()
    print(msg.topic)
    Data = json.loads(msg.payload.decode('utf-8','strict'))
    csvfile = open(filename,'a')
    csvwriter = csv.writer(csvfile)    
    csvwriter.writerow([Data["day"],
        getLast2days()+Data["day"],
        Data["humidity"],
        Data["stationname"],
        now.strftime("%Y-%m-%d %H:%M:%S")])
    print("day =",Data["day"])
    print("humidity =",Data["humidity"])
    print("stationname =",Data["stationname"])
    csvfile.close()
    predictbutton(Data["stationname"])

def getLast2days():
    f = open(filename,'r')
    df2 = pd.read_csv("./iot-data.csv")
    dimension_y = len(df2)
    print(df2)
    sum = df2['day'][dimension_y-2]+df2['day'][dimension_y-1]
    f.close()
    return sum
    
#systemInit
def systemInit():
    df=pd.read_csv("./Data_stationA.csv")
    level = df[['level']]
    le = preprocessing.LabelEncoder()
    level_encoded=le.fit_transform(level)
    level_encoded
    x = df.iloc[:,:3]
    y = level_encoded
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.20)
    classifier.fit(x_train, y_train)
    y_pred = classifier.predict(x_test)
    result = accuracy_score(y_test,y_pred)
    print(y_test)
    print(y_pred)
    print("Accuracy",result)
    print("System was started")
def accuracy():
    df=pd.read_csv("./Data_stationA.csv")
    level = df[['level']]
    le = preprocessing.LabelEncoder()
    level_encoded=le.fit_transform(level)
    level_encoded
    x = df.iloc[:,:3]
    y = level_encoded
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.20)
    classifier.fit(x_train, y_train)
    y_pred = classifier.predict(x_test)
    result = accuracy_score(y_test,y_pred)
    result2 = round(result, 4)
    return result2

print("%.4f" % accuracy())

#predict button command
x = 0
y = 0
z = 0
def predictbutton(stationname):
    now = datetime.datetime.now()
    f = open(filename,'r')
    df = pd.read_csv("./iot-data.csv")
    size = len(df)
    x = 4.83 * df['day'][size-1]
    y = 4.83 * df['threeday'][size-1]
    z = 1024 -df['humidity'][size-1] 
    
    predict_value=predict(x,y,z)
    level_msg = "" 
    if predict_value == 0:
        print("The chance is HIGH\n","Day =",x,"3day =",y,"Soil Moisture  =",z)
        level_msg = "HIGH"
        
    elif predict_value == 1:
        print("The chance is LOW\n","Day =",x,"3day =",y,"Soil Moisture  =",z)
        level_msg = "LOW"
    else:
        print("The chance is MEDIUM\n","Day =",x,"3day =",y,"Soil Moisture =",z)
        level_msg = "MEDIUM"
        
    if df["stationname"][size-1] == "A":
        stationADayStringLabel.set(x)
        stationAThreedaysStringLabel.set(y)
        stationAHumidityStringLabel.set(z)
        stationALatestUpdateStringLabel.set(now.strftime("%Y-%m-%d %H:%M:%S"))
        stationAStringLabel.set(level_msg)
        stationAAccuracyStringLabel.set(accuracy())
        if level_msg == "HIGH":
            linenotify("A",'0ngKxQJNPDAXMFpyaSB7ytKpk1PaPqy3yAMlm23HpCv')
        
        
    elif df["stationname"][size-1] == "B":
        stationBDayStringLabel.set(x)
        stationBThreedaysStringLabel.set(y)
        stationBHumidityStringLabel.set(z)
        stationBLatestUpdateStringLabel.set(now.strftime("%Y-%m-%d %H:%M:%S"))
        stationBStringLabel.set(level_msg)
        stationBAccuracyStringLabel.set(accuracy())
        if level_msg == "HIGH":
            linenotify("B",'FmVyJT1tsbaysiGICjHR6zlgfN4yUQOjqZ3WWyZBDdm')
        
    
    elif df["stationname"][size-1] == "C":
        stationCDayStringLabel.set(x)
        stationCThreedaysStringLabel.set(y)
        stationCHumidityStringLabel.set(z)
        stationCLatestUpdateStringLabel.set(now.strftime("%Y-%m-%d %H:%M:%S"))
        stationCStringLabel.set(level_msg)
        stationCAccuracyStringLabel.set(accuracy())
        if level_msg == "HIGH":
            linenotify("c",'NTUlOZnNNfY8801Gf7GV0sF5TkfqeZMGS0vPsO6IBmH')
        
#call graph
def graph1(stationname):
    df1 = pd.read_csv("./iot-data.csv")
    temp = df1[(df1.stationname == stationname)]
    df1 = temp
    size = len(df1)
    print("graph1 was called")
    data = temp[:-2:-1]
    data_day       = data['day']
    data_threedays = data['threeday']
    data_humidity  = data['humidity']
    kmeans = KMeans(n_clusters=3, random_state=0)
    df=pd.read_csv("./Data_stationA.csv")
    df['cluster'] = kmeans.fit_predict(df[['day', 'humidity']])
    # get centroids
    centroids = kmeans.cluster_centers_
    cen_x = [i[0] for i in centroids] 
    cen_y = [i[1] for i in centroids]
    df['cen_x'] = df.cluster.map({0:cen_x[0], 1:cen_x[1], 2:cen_x[2]})
    df['cen_y'] = df.cluster.map({0:cen_y[0], 1:cen_y[1], 2:cen_y[2]})
    # define and map colors
    colors = ['#DF2020', '#81DF20', '#2095DF']
    df['c'] = df.cluster.map({0:colors[0], 1:colors[1], 2:colors[2]})
    #####PLOT#####
    from matplotlib.lines import Line2D
    fig, ax = plt.subplots(1, figsize=(7,7))
    # plot data
    plt.scatter(df.day, df.humidity, c=df.c, alpha = 0.6, s=10)
    # create a list of legend elemntes
    ## markers / records
    legend_elements = [Line2D([0], [0], marker='s', color='w', label='class {}'.format(i), 
               markerfacecolor=mcolor, markersize=5) for i, mcolor in enumerate(colors)]
    # plot legend
    plt.legend(handles=legend_elements, loc='upper right')
    # title and labels
    plt.title("Station_" + stationname,loc='center',fontsize=22)
    plt.xlabel('Day',fontsize = 18)
    plt.ylabel('Soil Moisture',fontsize= 18)
    plt.scatter(cen_x, cen_y, marker='^', c=colors, s=70)
    plt.scatter(data_day,data_humidity ,marker= 'x', color='black')
    plt.show()
graph1("")


def readDataStation():
    df=pd.read_csv("./Data_stationA.csv")
    print(df)

def set_label():
    currenttime = datetime.datetime.now()
    label["text"] = currenttime
    mainWindow.after(set_label)

#Result
#label = tk.Label(mainWindow,text ="Result",font=('Arial',25))
#label.pack()
#set_label()

#mainWindow
mainWindow = tk.Tk()
mainWindow.geometry("1024x600")
mainWindow.title("Super prediction for the future")

mainWindow.attributes('-fullscreen',True)
stationASchoolLabel = tk.Label(
    text = "โรงเรียนมัธยมสาธิตมหาวิทยาลัยนเรศวร",
    font = ("Arial",25)
)
stationASchoolLabel.place(x=225 , y=10)

#station A
stationAFrame = tk.LabelFrame(
    text = "Station A",
    height=480,
    width=335
)

stationAFrame.place (x=5 ,y= 100)

stationAStringLabel = tk.StringVar()
stationAStringLabel.set("Status A")

stationAStatusLabel = tk.Label(
    stationAFrame,
    textvariable = stationAStringLabel,
    font = ("Arial",25),
    fg = "Green",
    justify = "center",
    width=16
)
stationAStatusLabel.place(y = 38)


stationAaccuracyStringLabel = tk.StringVar()
stationAaccuracyStringLabel.set("Accuracy :")

stationAaccuracyLabel = tk.Label(
    stationAFrame,
    textvariable = stationAaccuracyStringLabel,
    font =("Arial",10),
    justify = "center",
    width=40
)
stationAaccuracyLabel.place(y = 78)

stationADayLabel = tk.Label(
    stationAFrame,
    text = "ปริมาณน้ำฝนใน 1 วัน    :",
    font = ("Arial",12),
)
stationADayLabel.place(x = 20, y = 180)

stationAThreedaysLabel = tk.Label(
    stationAFrame,
    text = "ปริมาณน้ำฝนใน 3 วัน    :",
    font = ("Arial",12),
)
stationAThreedaysLabel.place(x = 20, y = 230)

stationAHumidityLabel = tk.Label(
    stationAFrame,
    text = "ความชื้นสัมพัทธ์ในดิน  :",
    font = ("Arial",12),
)
stationAHumidityLabel.place(x = 20, y = 280)

stationALatestUpdateLabel = tk.Label(
    stationAFrame,
    text = "อัปเดตล่าสุด   :",
    font = ("Arial",12),
)
stationALatestUpdateLabel.place(x = 20,y = 330)

stationAAccuracyStringLabel = tk.StringVar()
stationAAccuracyStringLabel.set("-")
stationAAccuracyValueLabel = tk.Label(stationAFrame,textvariable = stationAAccuracyStringLabel)
stationAAccuracyValueLabel.place(x = 175, y = 78)

stationADayStringLabel = tk.StringVar()
stationADayStringLabel.set("-")
stationADayValueLabel = tk.Label(stationAFrame,textvariable = stationADayStringLabel)
stationADayValueLabel.place(x = 190, y = 180)

stationAThreedaysStringLabel = tk.StringVar()
stationAThreedaysStringLabel.set("-")
stationAThreedaysValueLabel = tk.Label(stationAFrame,textvariable = stationAThreedaysStringLabel)
stationAThreedaysValueLabel.place(x = 190, y = 230)

stationAHumidityStringLabel = tk.StringVar()
stationAHumidityStringLabel.set("-")
stationAHumidityValueLabel = tk.Label(stationAFrame,textvariable = stationAHumidityStringLabel)
stationAHumidityValueLabel.place(x = 190, y = 280)

stationALatestUpdateStringLabel = tk.StringVar()
stationALatestUpdateStringLabel.set("-")
stationALatestUpdateValueLabel = tk.Label(stationAFrame,textvariable = stationALatestUpdateStringLabel)
stationALatestUpdateValueLabel.place(x = 130, y = 330)




stationAButton = tk.Button(stationAFrame,text = "Graph",command = lambda: graph1("A"),height = 3, width = 30)
stationAButton.place(x = 20, y = 380)
def close():
    #mainWindow.quit()
    exit(0)
exit_button = tk.Button(mainWindow, text= "EXIT", command = close )
exit_button.place(x=899,y=50)

stationADividerLine = tk.Label(stationAFrame,text = "_________________________________________")
stationADividerLine.place(x = 20, y = 120)



#station B
stationBFrame = tk.LabelFrame(
    text = "Station B",
    height=480,
    width=335
)

stationBFrame.place (x = 345,y = 100)

stationBStringLabel = tk.StringVar()
stationBStringLabel.set("Status B")

stationBStatusLabel = tk.Label(
    stationBFrame,
    textvariable = stationBStringLabel,
    font = ("Arial",25),
    fg = "Blue",
    justify = "center",
    width=16 
)
stationBStatusLabel.place(y = 38)

stationBaccuracyStringLabel = tk.StringVar()
stationBaccuracyStringLabel.set("Accuracy :")

stationBaccuracyLabel = tk.Label(
    stationBFrame,
    textvariable = stationBaccuracyStringLabel,
    font =("Arial",10),
    justify = "center",
    width=40
)
stationBaccuracyLabel.place(y = 78)

stationBDayLabel = tk.Label(
    stationBFrame,
    text = "ปริมาณน้ำฝนใน 1 วัน    :",
    font = ("Arial",12),
)
stationBDayLabel.place(x = 20, y = 180)

stationBThreedaysLabel = tk.Label(
    stationBFrame,
    text = "ปริมาณน้ำฝนใน 3 วัน    :",
    font = ("Arial",12),
)
stationBThreedaysLabel.place(x = 20, y = 230)

stationBHumidityLabel = tk.Label(
    stationBFrame,
    text = "ความชื้นสัมพัทธ์ในดิน  :",
    font = ("Arial",12),
)
stationBHumidityLabel.place(x = 20, y = 280)

stationBLatestUpdateLabel = tk.Label(
    stationBFrame,
    text = "อัปเดตล่าสุด   :",
    font = ("Arial",12),
)
stationBLatestUpdateLabel.place(x = 20,y = 330)

stationBAccuracyStringLabel = tk.StringVar()
stationBAccuracyStringLabel.set("-")
stationBAccuracyValueLabel = tk.Label(stationBFrame,textvariable = stationBAccuracyStringLabel)
stationBAccuracyValueLabel.place(x = 175, y = 78)

stationBDayStringLabel = tk.StringVar()
stationBDayStringLabel.set("-")
stationBDayValueLabel = tk.Label(stationBFrame,textvariable = stationBDayStringLabel)
stationBDayValueLabel.place(x = 190, y = 180)

stationBThreedaysStringLabel = tk.StringVar()
stationBThreedaysStringLabel.set("-")
stationBThreedaysValueLabel = tk.Label(stationBFrame,textvariable = stationBThreedaysStringLabel)
stationBThreedaysValueLabel.place(x = 190, y = 230)

stationBHumidityStringLabel = tk.StringVar()
stationBHumidityStringLabel.set("-")
stationBHumidityValueLabel = tk.Label(stationBFrame,textvariable = stationBHumidityStringLabel)
stationBHumidityValueLabel.place(x = 190, y = 280)

stationBLatestUpdateStringLabel = tk.StringVar()
stationBLatestUpdateStringLabel.set("-")
stationBLatestUpdateValueLabel = tk.Label(stationBFrame,textvariable = stationBLatestUpdateStringLabel)
stationBLatestUpdateValueLabel.place(x = 130, y = 330)

stationBButton = tk.Button(stationBFrame,text = "Graph",command = lambda: graph1("B"),height = 3, width = 30)
stationBButton.place(x = 20, y = 380)

stationBDividerLine = tk.Label(stationBFrame,text = "_________________________________________")
stationBDividerLine.place(x = 20, y = 120)

#station C
stationCFrame = tk.LabelFrame(
    text = "Station C",
    height=480,
    width=335
)

stationCFrame.place (x = 685,y = 100)

stationCStringLabel = tk.StringVar()
stationCStringLabel.set("Status C")

stationCStatusLabel = tk.Label(
    stationCFrame,
    textvariable = stationCStringLabel,
    font = ("Arial",25),
    fg = "Red",
    justify = "center",
    width=16
)
stationCStatusLabel.place(y = 40)

stationCaccuracyStringLabel = tk.StringVar()
stationCaccuracyStringLabel.set("Accuracy :")

stationCaccuracyLabel = tk.Label(
    stationCFrame,
    textvariable = stationCaccuracyStringLabel,
    font =("Arial",10),
    justify = "center",
    width=40
)
stationCaccuracyLabel.place(y = 78)

stationCDayLabel = tk.Label(
    stationCFrame,
    text = "ปริมาณน้ำฝนใน 1 วัน    :",
    font = ("Arial",12),
)
stationCDayLabel.place(x = 20, y = 180)

stationCThreedaysLabel = tk.Label(
    stationCFrame,
    text = "ปริมาณน้ำฝนใน 3 วัน    :",
    font = ("Arial",12),
)
stationCThreedaysLabel.place(x = 20, y = 230)

stationCHumidityLabel = tk.Label(
    stationCFrame,
    text = "ความชื้นสัมพัทธ์ในดิน  :",
    font = ("Arial",12),
)
stationCHumidityLabel.place(x = 20, y = 280)

stationCLatestUpdateLabel = tk.Label(
    stationCFrame,
    text = "อัปเดตล่าสุด   :",
    font = ("Arial",12),
)
stationCLatestUpdateLabel.place(x = 20,y = 330)

stationCAccuracyStringLabel = tk.StringVar()
stationCAccuracyStringLabel.set("-")
stationCAccuracyValueLabel = tk.Label(stationCFrame,textvariable = stationCAccuracyStringLabel)
stationCAccuracyValueLabel.place(x = 175, y = 78)

stationCDayStringLabel = tk.StringVar()
stationCDayStringLabel.set("-")
stationCDayValueLabel = tk.Label(stationCFrame,textvariable = stationCDayStringLabel)
stationCDayValueLabel.place(x = 190, y = 180)

stationCThreedaysStringLabel = tk.StringVar()
stationCThreedaysStringLabel.set("-")
stationCThreedaysValueLabel = tk.Label(stationCFrame,textvariable = stationCThreedaysStringLabel)
stationCThreedaysValueLabel.place(x = 190, y = 230)

stationCHumidityStringLabel = tk.StringVar()
stationCHumidityStringLabel.set("-")
stationCHumidityValueLabel = tk.Label(stationCFrame,textvariable = stationCHumidityStringLabel)
stationCHumidityValueLabel.place(x = 190, y = 280)

stationCLatestUpdateStringLabel = tk.StringVar()
stationCLatestUpdateStringLabel.set("-")
stationCLatestUpdateValueLabel = tk.Label(stationCFrame,textvariable = stationCLatestUpdateStringLabel)
stationCLatestUpdateValueLabel.place(x = 130, y = 330)

stationCButton = tk.Button(stationCFrame,text = "Graph",command = lambda: graph1("C"),height = 3, width = 30)
stationCButton.place(x = 20, y = 380)

stationCDividerLine = tk.Label(stationCFrame,text = "_________________________________________")
stationCDividerLine.place(x = 20, y = 120)

#photo1 = tk.PhotoImage(file='สไลด์1.PNG')

#GPIO.SET
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10,GPIO.OUT)
GPIO.setup(8,GPIO.OUT)
GPIO.setup(12,GPIO.OUT)

#client
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.username_pw_set(username=USERNAME,password=PASSWORD)
client.connect(HOST)
client.subscribe("rainy")
client.loop_start()

mainWindow.mainloop()






#ตัวอย่างรับค่าแล้วคำนวน
"""
a = []
b = []
while len(a) < 3:
    x = int(input())
    a.append(x)
    print("days =",a)
if len(a) == 3:
    y = sum(a)
    print(y)
    k = a.pop()
    b.append(y)
    b.append(k)
    a.clear()
    print(a)
    print("threedays&day =",b)


a1 = []
while len(a1) < 3:
    x = input()
    a1.append(x)
    print("humidity =",a1)
if len(a1) == 3:
    k1 = a1.pop()
    a1.clear()
    print(a1)
    print("humidity =",k1)
    
print("day =",b[1],"threedays =",b[0])
print("humidity =",k1)
"""
