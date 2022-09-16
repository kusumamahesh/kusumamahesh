#import datetime 
#import time
from pykafka import KafkaClient
from kafka import KafkaConsumer
# Import sys module
from json import loads
from pymongo import MongoClient
# Import json module to serialize data
import json
from datetime import datetime
import requests
#from datetime import datetime
#import datetime 
#client = KafkaClient("52.12.160.175:9092")
#topic = client.topics["device_data-SCMXpert"]
#producer = topic.get_producer()
consumer=KafkaConsumer(bootstrap_servers='52.12.160.175:9092',
                                 auto_offset_reset='earliest',
                                 value_deserializer=lambda m: json.loads(m.decode('utf-8')))
consumer.subscribe(['device_data-SCMXPERT_raw'])
client = MongoClient('localhost:27017')
collection = client.SCM.DeviceDataStream
try:
    for message in consumer:
        message=message.value
        data=message
        try:
            for i in data:
                if i=='<':
                    data=data.replace('<','3c')
                elif i=='>':
                    data=data.replace('>','3e')
                elif i=='|':
                    data=data.replace('|','7c')
                elif i=='=':
                    data=data.replace('=','3d')
                elif i=='[':
                    data=data.replace('[','5b')
                elif i==']':
                    data=data.replace(']','5d')
                elif i==')':
                    data=data.replace(')','29')
                elif i=='(':
                    data=data.replace('(','28')
                elif i=='{':
                    data=data.replace('{','7b')
                elif i=='}':
                    data=data.replace('}','7d')
                elif i=='*':
                    data=data.replace('*','2a')
                elif i=='#':
                    data=data.replace('#','23')
                elif i=='@':
                    data=data.replace('@','40')
                elif i=='/':
                    data=data.replace('/','2f')
                elif i=='%':
                    data=data.replace('%','25')
                elif i=='?':
                    data=data.replace('?','3f')
                elif i==':':
                    data=data.replace(':','3a')
                elif i==';':
                    data=data.replace(';','3b')
                elif i=="'":
                    data=data.replace("'",'27')
                elif i=="$":
                    data=data.replace("$",'24')
                elif i=="5c5c":
                    data=data.replace("5c5c",'5c')
        except Exception as e:
            print(e)
        #print (message)
        print(len(data))
        now = datetime.now()                
        #st = now.strftime("%Y-%m-%d %H:%M:%S")
        f = open("./device_data12.txt", "a")
        f.write(str(data)+" at "+str(now)+"\n")
        #print(len(data))
        try:
            if len(data)==182:
            
                a = data[14:22]
                time = int(a, 16)
                Epoc = datetime.fromtimestamp(time)
                SensorUTC = Epoc.strftime('%Y-%m-%d'+'T'+'%H:%M:%S'+'.00Z')
                ct = now.strftime("%H:%M:%S.%f%z")
                cd = now.strftime("%Y-%m-%d")
                ld=Epoc.strftime('%m/%d/'+'21')
                lt=Epoc.strftime('%H:%M:%S')
                #Latitude
                d = data[24:32]
                #print(d)
                lat = (int(d, 16)/1800000)
                #print(lat)
                #longitude
                e=data[32:40]
                #print(e)
                long1="".join(e)
                def twos_comp(val, bits):                                      
                    if (val & (1 << (bits - 1))) != 0:
                        val = val - (1 << bits)    
                    return val
                long2 = twos_comp(int(long1,16), 32)
                long=long2/1800000
                #print(long)
                payload = {'format':"json",'lat': lat, 'lon':long,"accept-language":"en"}
                data1=requests.get(url="https://nominatim.openstreetmap.org/reverse.php",params=payload)
                add=data1.json()
                add=add.get("display_name")
                #Getting battery percentage
                c=data[114:118]
                bat1="".join(c)
                bat2=round((int(bat1, 16))/1000,2)
                #print(bat2)
                #Getting temp value
                b = data[150:154]
                temp = (int(b, 16))/256
                temp1 = round((temp),2)
                #MCC
                f = data[54:58]
                MCC = int(f,16)
                #print(MCC)
                #MNC
                g=data[58:62]
                MNC = int(g,16)
                #print(MNC)
                #LAC
                h = data[62:66]
                LAC = int(h,16)
                #print(LAC)
                #CID
                i = data[66:74]
                CID = int(i,16)
                #print(CID)
                #STATUS
                j = data[110:114]
                STATUS = int(j,16)
                #print(STATUS)
                #Probe
                k = data[174:178]
                stemp="".join(k)
                stemp1 = round((int(k, 16))/16,2)
                #print(stemp1)
                dic = {
                        "Battery_Level" : str(bat2),
                        "Device_Id" : "085287",
                        "locationType" : "",
                        "reportPeriod" : "",
                        "maxHumidityThreshold" : "",
                        "reporting_zone" : "UTC",
                        "iccid" : "",
                        "Modem_IMEI" : "",
                        "shakeThreshold" : "",
                        "minTempThreshold" : "",
                        "sensorPhySampleCycle" : "",
                        "Current_Terminal_Zone" : "",
                        "humdity_2" : "",
                        "mileage" : "",
                        "airpressure" : "",
                        "sensorReportCycle" : "",
                        "humidity_1" : "",
                        "active" : "",
                        "device_slno" : "",
                        "Message_Type" : "sensor",
                        "Address" : add,
                        "Longitude" : long,
                        "tiltAngle" : "",
                        "Internal_temperature" : str(temp1) +" " + "C",
                        "reporting_Time" : ct,
                        "minHumidityThreshold" : "",
                        "Speed" : "",
                        "current_terminal_time" : lt,
                        "maxTempThreshold" : "",
                        "Latitude" : lat,
                        "device_oem" : "EELINK",
                        "current_terminal_date" : ld,
                        "Reporting_Date" : cd,
                        "SensorUTC" : SensorUTC,
                        "Out_of_coverage_duration" : "",
                        "Unit_serial_number" : "",
                        "New_Modem_IP" : "",
                        "External_power_voltage" : "",
                        "Message_no" : "",
                        "Course" : "",
                        "Eight_Sensor_temperature" : "",
                        "Third_Sensor_ID" : "",
                        "Current_cellular_operator" : "",
                        "Unit_Type" : "",
                        "Fifth_Sensor_ID" : "",
                        "First_Sensor_ID" : "",
                        "fW_version" : "",
                        "Eight_Sensor_ID" : "",
                        "linkquality" : "",
                        "Fifth_Sensor_temperature" : "",
                        "Seventh_Sensor_ID" : "",
                        "Third_Sensor_temperature" : "",
                        "Fourth_Sensor_temperature" : "",
                        "Integrated_total_distance" : "",
                        "Login_Time" : "",
                        "Fourth_Sensor_ID" : "",
                        "Sixth_Sensor_temperature" : "",
                        "Emg_Alaram_type" : "",
                        "Report_Status" : "",
                        "Low_Battery_Level" : "",
                        "external_high_precision_temp" : "",
                        "External_power_state" : "",
                        "gPS_Total_Distance" : "",
                        "Solar_pannel_charging_voltage" : "",
                        "Solar_panels_charging_current" : "",
                        "Seventh_Sensor_temperature" : "",
                        "First_Sensor_temperature" : str(temp1) +" " + "C",
                        "Second_Sensor_temperature" : "",
                        "gPRS_Registration_state" : "",
                        "Sixth_Sensor_ID" : "",
                        "Second_Sensor_ID" : "",
                        "sensorid" : "",
                        "Alrm_link_state" : "",
                        "Login_date" : "",
                        "Emergency_status" : "",
                        "Altitude" : "",
                        "_class" : "com.scmxpert.model.DeviceDataStream"
                        }

                print(dic)
                try:
                    collection.insert_one(dic)
                    print('{} added to {}'.format(dic, collection))
                except:
                    print("Error with Dump")
        except Exception as e:
            print(e)

except Exception as e:
    print(e)
    f.close()
