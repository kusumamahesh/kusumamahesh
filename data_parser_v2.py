# -*- coding: utf-8 -*-

"""
Created on Wed May 12 09:22:17 2021

@author: Hemant Singh
"""
from kafka import KafkaProducer
import json
import pprint
import re
import json
import time
from datetime import datetime
import codecs
from pymongo import MongoClient 
import socket
import geopy
from geopy.geocoders import Nominatim
import datetime as dt
import requests
OpenCell_Api_Key ="pk.9424e363757e6cb9cffd2e19a38ebba6"
def Opencell(MMC,MNC,LAC,ID,API_KEY=OpenCell_Api_Key):
    url = "https://us1.unwiredlabs.com/v2/process.php"
    data = {
        "token": API_KEY,
        "radio": "gsm",
        "mcc": MMC,
        "mnc": MNC,
        "cells": [{
            "lac": LAC,
            "cid": ID
        }]
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        if response.json()[u'status']== 'error':
            print('Error: {}'.format(response.json()[u'message']))
            return None
        else:
            lat = response.json()[u'lat']
            long = response.json()[u'lon']
            d = {'LAT': lat, 'LONG': long}
            print('Located Cell: {}'.format(ID))
            return d
    else:
        print('Error: {}'.format(response.status_code))
        return None
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("18.218.150.152",3000))
producer = KafkaProducer(
    bootstrap_servers="52.12.160.175:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"))
while True:
    try: 
        try:
            now = datetime.now()
            ut=""
            speed_dec=""
            current_time = now.strftime("%H:%M:%S.%f%z")
            current_date=now.strftime("%Y-%m-%d")
            from_server = client.recv(4096)
            test_str=str(from_server)
            test_str = test_str.replace('\\x','<')
            for ss in list(set(re.findall(r'<\S\S',test_str))):
                test_str = test_str.replace(ss,ss.upper()+'>')
            for ss in list(set(re.findall(r'\\\S',test_str))):
                if ss == "\\t":
                    test_str = test_str.replace(ss,'<'+"\t".encode('utf-8').hex()+'>')
                if ss == "\\r":
                    test_str = test_str.replace(ss,'<'+"\r".encode('utf-8').hex()+'>')
                if ss == "\\n":
                    test_str = test_str.replace(ss,'<'+"\n".encode('utf-8').hex()+'>')
                if ss == "\\b":
                    test_str = test_str.replace(ss,'<'+"\b".encode('utf-8').hex()+'>')
        except Exception as e:
            print(e)
#         test_str="204|11|001156053077|NORMAL DATA |!<00><01><00>11308<00><03><00>C<00><04><00>09:10:18<00><05><00>07/02/21<00><0a><00>11<00><0B><00>1186426450602<00><0C><00>214<00>!<00>9151<00>&<00>0<00>'<00>1<00>2<00>40<00><F2><00>1<00><F3><00>1<00><F5><00>868923058946413<00><F6><00>1,0,0,351,-1,1<00><F7><00>863305<00><F8><00>0,300,0,0,0,0,51,0,43,9,42,0,0<00><FA><00>85<00>||292|11|001156053077|NORMAL DATA |<E4><00><01><00>11309<00><02><00>09:10:18<00><03><00>07/02/21<00><04><00>-1<00><06><00>0<00><0a><00>404<00><0B><00>49<00><0C><00>20275<00><0d><00>55311<00><0E><00>19<00><10><00>5,5,1,1,10.109.229.41,65535,0,99,99,255,255,255,255<00><11><00>0<00><13><00>99<00><14><00>9151<00><19><00>0<00>1<00>0<00>2<00>1<00>Y<00>754974721<00>[<00>46<00>\\\\<00>114<00><F2><00>1<00><F3><00>1<00><F5><00>868923058946413<00><F6><00>1,0,0,351,-1,1<00><F7><00>863305<00><F8><00>0,300,0,0,0,0,,,,,,0,0<00><FA><00>85<00>||"
        data1=test_str
        data1=data1.split("||")
        for data in data1:
            print(data)
            msg_type="sensor"
            cfg_file = open("pattern.json")
            pattern=json.load(cfg_file)
            case_list = {}
            for i in pattern:
                #print(str(pattern[i]))
                x = re.search(pattern[i], data)
                #print(x)
                if x:
                    #print("YES! We have a match!")
                    result = re.findall(pattern[i],data)
                    #print(i,":",result[0])
                    case = {i: result[0]}
                    case_list.update(case)

                else:
                    #print("No match")
#                     f = open("./test.txt", "a")  
#                     st = now.strftime("%Y-%m-%d %H:%M:%S")
#                     f.write(str(test_str)+" at "+str(st)+"\n")
                    #f.close()
                    cfg_file.close()
            try:
                result = re.findall(r"\d+", data)
                bat_pattern=re.compile("<00><F6><00>(.*?)<00>")
                bat=bat_pattern.findall(data)
                battery=bat[0]
                identity={"message_no":result[0],"Device_Id":result[2]}
                case_list.update(identity)
                bet={"Battery_Level":int(battery[6:9])/100}
                case_list.update(bet)
                del case_list["bAT"]
            except Exception as e:
                print(e)
            try:
                check_temp1 = "First_Sensor_temperature" in case_list.keys()
                if check_temp1==True:
                    if int(case_list['First_Sensor_temperature'])<2000:
                        if case_list['temp_Measurment']=='F':
                            temp=round((round(int(case_list["First_Sensor_temperature"])/10,2) - 32) * 5/9,2)
                        else:
                            temp=round(int(case_list["First_Sensor_temperature"])/10,2)
                        case_list["First_Sensor_temperature"]=str(temp)+" "+"C"
                    else:
                        tem1={"First_Sensor_temperature":""}
                        case_list.update(tem1)
                else:
                    tem1={"First_Sensor_temperature":""}
                    case_list.update(tem1)
            except:
                tem1={"First_Sensor_temperature":""}
                case_list.update(tem1)

            check_temp = "internal_temperature" in case_list.keys()
            if check_temp==True:
                case_list["internal_temperature"]=round(int(case_list["internal_temperature"]),2)
            else:
                tem={"internal_temperature":""}
                case_list.update(tem)
            check_gps = "application_type" in case_list.keys()
            check_distance="gPS_Total_Distance" in case_list.keys()
            if check_distance==False:
                tem_dist={"gPS_Total_Distance":""}
                case_list.update(tem_dist)
            add=""
            try:
                str1=str(case_list["current_terminal_date"])
                str1=str1.replace("/","-")
                str2=str(case_list["current_terminal_time"])
                str3=str1+"T"+str2+".00Z"
                str3= datetime.strptime(str3, '%m-%d-%yT%H:%M:%S.00Z')
                ut=dt.datetime.strftime(str3, '%Y-%m-%dT%H:%M:%S.00Z')
            except:
                now = datetime.now()
                ut = now.strftime('%Y-%m-%d'+'T'+'%H:%M:%S'+'.00Z')
            if check_gps==True:
                try:
                    now = datetime.now()
                    ut = now.strftime('%Y-%m-%d'+'T'+'%H:%M:%S'+'.00Z')
                    test_str=case_list["application_type"]
                    test_str11=test_str
                    print(test_str11)
                    if test_str11[-1]!='<':
                        test_str11+=str('<')
                    pattern1=re.compile("<(.*?)>")
                    pattern2=re.compile(">(.*?)<")


                    value1=pattern1.findall(test_str11)
                    value2=pattern2.findall(test_str11)
                    lis=[]
                    for i in value2:
                        my=str.encode(i)
                        t=codecs.encode(my,"hex")
                        b=t.decode('utf-8')
                        lis+=[b]
                        #b.append(i)
                    lol=re.split('>',test_str11)
                    result = [None]*(len(value1)+len(lis))
                    result[::2] = value1
                    result[1::2] = lis
                    Not_none_values = filter(''.__ne__, result)
                    list_of_values = list(Not_none_values)
                    list_of_values.pop()
                    print(list_of_values)
                    lat=''
                    long=''
                    speed=''
                    time1=''
                    time3=''
                    def twos_comp(val, bits):
                        """compute the 2's complement of int value val"""
                        if (val & (1 << (bits - 1))) != 0:
                            val = val - (1 << bits)     
                        return val
                    print(len(list_of_values[1]))
                    if len(list_of_values[1])==2:
                        for k in range(4): 
                            test1=str(list_of_values[k])
                            lat += test1
                        for l in range(4,8):
                            test2=str(list_of_values[l])
                            long +=test2
                    elif len(list_of_values[1])==4:
                        for k in range(3): 
                            test1=str(list_of_values[k])
                            lat += test1
                        for l in range(3,7):
                            test2=str(list_of_values[l])
                            long +=test2
                    elif len(list_of_values[1])==6:
                        for k in range(2): 
                            test1=str(list_of_values[k])
                            lat += test1
                        for l in range(2,6):
                            test2=str(list_of_values[l])
                            long +=test2
                    print(lat)
                    print(long)
                    lat_dec=round(int(lat,16)/600000,4)
                    if lat_dec>90:
                        lat_dec=round(lat_dec/100,4)*-1
                    print(lat_dec)
                    out = twos_comp(int(long,16), 32)
                    long_dec=round(int(out)/600000,4)
                    if long_dec>180:
                        long_dec=round(long_dec/100,4)*-1
                    print(long_dec)
                    for m in range(8,10):
                        test2=str(list_of_values[m])
                        speed +=test2
                    speed_dec=int(speed,16)
                    print(speed_dec)
                    case_list['current_terminal_date']=""
#                     ut=datetime.utcnow().isoformat()[:-3]+'Z'
#                     line=str(list_of_values[11])
#                     n = 2
#                     line=[line[i:i+n] for i in range(0, len(line), n)]
#                     print(len(line))
#                     time1=str(list_of_values[10])+str(line[0])
#                     print(time1)
#                     if len(line)==3:  
#                         time2=str(line[1])
#                         print(time2)
#                         time3=str(line[2])
#                         print(time3)
#                     elif len(line)==2:
#                         time2=str(line[1])
#                         print(time2)
#                         time3=str(list_of_values[12])
#                         print(time3)
#                     elif len(line)==1:
#                         time2=list_of_values[12]
#                         time3=list_of_values[13]
#                         print(time2,time3)

# #                     time1_dec=int(time1,16)
#                     day=int(time1_dec/2048)
#                     day=str(day).zfill(2)
#                     minute=int(time1_dec%2048)
#                     time_mid1=int(minute/60)
#                     time_mid1=str(time_mid1).zfill(2)
#                     time_mid2=int(minute%60)
#                     time_mid2=str(time_mid2).zfill(2)
#                     time_mid=str(time_mid1)+':'+str(time_mid2)
#                     year=2021
#                     time2_dec=int(time2,16)
#                     month=int(time2_dec%16)
#                     month=str(month).zfill(2)
#                     time3_dec=int(time3,16)
#                     time3_dec=str(time3_dec).zfill(2)
#                     print(time1_dec,time2_dec,time3_dec)
#                     print(len(list_of_values))
                    #ut=str(2021)+'-'+str(month)+'-'+str(day)+'T'+str(time_mid)+':'+str(time3_dec)+'.000Z'
                    now = datetime.now()
                    ut = now.strftime('%Y-%m-%d'+'T'+'%H:%M:%S'+'.00Z')
                    print(ut) 
                    case_list["current_terminal_date"]=now.strftime('%m/%d/'+'21')
                    case_list["current_terminal_time"]=now.strftime('%H:%M:%S')
                    msg_type="GPS MESSAGE"
                    gps_data={"Latitude":lat_dec,"Longitude":long_dec}
                    try:
                        payload = {'format':"json",'lat': lat_dec, 'lon':long_dec,"accept-language":"en"}
                        data=requests.get(url="https://nominatim.openstreetmap.org/reverse.php",params=payload)
                        add=data.json()
                        add=add.get("display_name")
                    except:
                        add=''
                    del case_list["application_type"]
                    case_list.update(gps_data)
                except Exception as e:
                    print(e)
            else:
                gps_data={"Latitude":"","Longitude":""}
                case_list.update(gps_data)

            static={"speed":speed_dec,"sensor_id" : "","reporting_Time":current_time,"no_of_tags":10,"reporting_Date":current_date,
                    "report_type" : "1","signal" : "","course":"","tag_Life_Time":"","distance" : "","altitude" : "",
                    "Message_Type" : msg_type,"SensorUTC":ut, "locationType" : "","reportPeriod" : "",
                    "maxHumidityThreshold" : "",    "reporting_zone" : "UTC",    "iccid" : "","shakeThreshold" : "","minTempThreshold" : "",
                    "sensorPhySampleCycle" : "", "Current_Terminal_Zone" : "","external_high_precision_temp":"","humdity_2" : "",    "mileage" : "", "airpressure" : "", 
                    "sensorReportCycle" : "",
                    "humidity_1" : "",    "active" : "",    "device_slno" : "","tiltAngle" : "",
                    "minHumidityThreshold" : "","maxTempThreshold" : "",
                    "device_oem" : "WLI",    "out_of_coverage_duration" : "",
                    "n ew_Modem_IP" : "",    "external_power_voltage" : "",  "eight_Sensor_temperature" : "", "third_Sensor_ID" : "",
                    "current_cellular_operator" : "", "unit_Type" : "Piccolo plus with internal battery",    "fifth_Sensor_ID" : "",
                    "fW_version" : "",    "eight_Sensor_ID" : "",    "linkquality" : "",    "fifth_Sensor_temperature" : "",
                    "seventh_Sensor_ID" : "",    "third_Sensor_temperature" : "",    "fourth_Sensor_temperature" : "",
                    "integrated_total_distance" : "", "login_Time" : "",    "fourth_Sensor_ID" : "",    "sixth_Sensor_temperature" : "",
                    "emg_Alaram_type" : "","low_Battery_Level" : "",  
                    "external_power_state" : "unit_is_runnig_from_internal_battery_only","solar_pannel_charging_voltage" : "", "solar_panels_charging_current" : "",
                    "seventh_Sensor_temperature" : "",    "second_Sensor_temperature" : "",
                    "gPRS_Registration_state" : "","sixth_Sensor_ID" : "",    "second_Sensor_ID" : "",       "alrm_link_state" : "",
                    "login_date" : "","emergency_status" : "","Address":add,"_class" : "com.scmxpert.model.DeviceDataStream"}
            case_list.update(static)

            #case_list["Battery_Level"]=round(int(case_list["Battery_Level"])/10,2)
            #print(case_list)
            data_type = case_list["data_type"]
            data_type=str(data_type)
            #print(data_type)
            punc = '''|'''
            for ele in data_type: 
                if ele in punc: 
                    data_type = data_type.replace(ele, "")
                    print(data_type)
            if str(data_type)=='<C9>' or str(data_type)=='!':
                del case_list["data_type"]
                try:
                    metrics = producer.metrics()
                    #pprint.pprint(metrics)
                    producer.send("device_data-SCMXpert", value=case_list)
                    print(case_list)
                    print("published")
                except:
                    print("error got during access to Kafka Broker")
            elif str(data_type)=='<E4>':
                del case_list["data_type"]
                try:
                    str1_pattern=re.compile("<03><00>(.*?)<00>")
                    str1=str(str1_pattern.findall(data)[0])
                    current_date_e4={"current_terminal_date":str1}
                    case_list.update(current_date_e4)
                    str1=str1.replace("/","-")
                    str2_pattern=re.compile("<02><00>(.*?)<00>")
                    str2=str(str2_pattern.findall(data)[0])
                    str3=str1+"T"+str2+".00Z"
                    str3= datetime.strptime(str3, '%m-%d-%yT%H:%M:%S.00Z')
                    ut=dt.datetime.strftime(str3, '%Y-%m-%dT%H:%M:%S.00Z')
                    case_list["current_terminal_time"]=str2
                    case_list["response_on_Message"]="E4"
                    case_list["temp_Measurment"]=""
                    case_list["Message_Type"]="GPS MESSAGE"
                except:
                    now = datetime.now()
                    ut = now.strftime('%Y-%m-%d'+'T'+'%H:%M:%S'+'.00Z')
                case_list["SensorUTC"]=ut
                try:
                    mcc_pattern=re.compile("<0A><00>(.*?)<00>")
                    mcc_pattern1=re.compile("<0a><00>(.*?)<00>")
                    mcc=mcc_pattern.findall(data)
                    if not mcc:
                        mcc=mcc_pattern1.findall(data)
                        print("done")
                    mnc_pattern=re.compile("<0B><00>(.*?)<00>")
                    mnc_pattern1=re.compile("<0b><00>(.*?)<00>")
                    mnc=mnc_pattern.findall(data)
                    if not mnc:
                        mnc=mnc_pattern1.findall(data)
                        print("done")
                    lac_pattern=re.compile("<0C><00>(.*?)<00>")
                    lac_pattern1=re.compile("<0c><00>(.*?)<00>")
                    lac=lac_pattern.findall(data)
                    if not lac:
                        lac=lac_pattern1.findall(data)
                        print("done")
                    id_pattern=re.compile("<0D><00>(.*?)<00>")
                    id_pattern1=re.compile("<0d><00>(.*?)<00>")
                    cell_id=id_pattern.findall(data)
                    if not cell_id:
                        cell_id=id_pattern1.findall(data)
                    value=Opencell(mcc[0],mnc[0],lac[0],cell_id[0])
                    print(value)
                    lati=value.get('LAT')
                    longi=value.get('LONG')
                    case_list["Latitude"]=lati
                    case_list["Longitude"]=longi
                    try:
                        payload = {'format':"json",'lat': lati, 'lon':longi,"accept-language":"en"}
                        data=requests.get(url="https://nominatim.openstreetmap.org/reverse.php",params=payload)
                        add=data.json()
                        add=add.get("display_name")
                    except:
                        add=''
                    case_list["Address"]=add
                    metrics = producer.metrics()
                    #pprint.pprint(metrics)
                    producer.send("device_data-SCMXpert", value=case_list)
                    print(case_list)
                    print("published")
                except:
                    print("error got during access to Kafka Broker")
            else:
                print("Incorrect device response")
        
    except Exception as e:
        print(e)
    #print(case_list)
client.close()