import requests
import execjs
from jscode import jscode
from bs4 import BeautifulSoup
import json
import sys
from datetime import datetime
session=requests.session()
zju_username=input("请输入统一身份认证用户名：")
zju_password=input("请输入统一身份认证用户名密码：")
user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58'
zjuam_login_url="http://zjuam.zju.edu.cn/cas/login?service=http%3A%2F%2Fbooking.lib.zju.edu.cn%2Fapi%2Fcas%2Fcas"
zjuam_login_resp=session.get(zjuam_login_url)
zjuam_pubkey_url='https://zjuam.zju.edu.cn/cas/v2/getPubKey'
zjuam_pubkey_resp=session.get(zjuam_pubkey_url)
zjuam_login_headers={
    'User-Agent': user_agent,
}
zjuam_login_data={
    'username': zju_username,
    'password': execjs.compile(jscode).call('encrypt',zjuam_pubkey_resp.json()["modulus"],zjuam_pubkey_resp.json()["exponent"],zju_password),
    '_eventId': 'submit',
    'execution': BeautifulSoup(zjuam_login_resp.text,"html.parser").find("input",attrs={'name':'execution'})['value'],
    'authcode': '',
}
zjuam_login_resp=session.post(zjuam_login_url,headers=zjuam_login_headers,data=zjuam_login_data)
if "用户名或密码错误" in zjuam_login_resp.text:
    print("统一身份认证用户名或密码错误")
    sys.exit(1)
booking_user_url='http://booking.lib.zju.edu.cn/api/cas/user'
booking_user_headers={
    'User-Agent': user_agent,
}
booking_user_data={
    'cas': zjuam_login_resp.url[zjuam_login_resp.url.find('cas=') + 4:]
}
booking_user_resp=session.post(booking_user_url,headers=booking_user_headers,data=booking_user_data)
booking_user_data=json.loads(booking_user_resp.text)
booking_user_authorization='bearer'+booking_user_data['member']['token']
booking_select_time_url='http://booking.lib.zju.edu.cn/reserve/index/quickSelect'
booking_select_time_headers={
    'User-Agent': user_agent,
}
booking_select_time_data={
    'id': '1',
    'authorization': booking_user_authorization,
}
booking_select_time_resp=session.post(booking_select_time_url,headers=booking_select_time_headers,data=booking_select_time_data)
booking_select_time_data=json.loads(booking_select_time_resp.text)
# for i in booking_select_time_data['data']['date']:
#     print(i)
# user_select_time=input("请输入想要预约的时间：")
# flag=0
# for i in booking_select_time_data['data']['date']:
#     if user_select_time == i:
#         flag=1
# if flag == 0:
#     print("输入不正确")
#     sys.exit(1)
user_select_time=booking_select_time_data['data']['date'][0]
booking_select_premises_url='http://booking.lib.zju.edu.cn/reserve/index/quickSelect'
booking_select_premises_headers={
    'User-Agent': user_agent,
}
booking_select_premises_data={
    'id': '1',
    'date': user_select_time,
    'authorization': booking_user_authorization,
}
booking_select_premises_resp=session.post(booking_select_premises_url,headers=booking_select_premises_headers,data=booking_select_premises_data)
booking_select_premises_data=json.loads(booking_select_premises_resp.text)
for i in booking_select_premises_data['data']['premises']:
    print('ID:'+i['id']+' 名称:'+i['name']+' 余量:'+str(i['free_num'])+'/'+str(i['total_num']))
user_select_premises=input("请输入想要预约的场馆ID：")
flag=0
for i in booking_select_premises_data['data']['premises']:
    if user_select_premises == i['id']:
        flag=1
if flag == 0:
    print("输入不正确")
    sys.exit(1)
for i in booking_select_premises_data['data']['storey']:
    if user_select_premises == i['topId']:
        print('ID:'+i['id']+' 名称:'+i['name']+' 余量:'+str(i['free_num'])+'/'+str(i['total_num']))
user_select_storey=input("请输入想要预约的楼层ID：")
flag=0
for i in booking_select_premises_data['data']['storey']:
    if user_select_storey == i['id']:
        flag=1
if flag == 0:
    print("输入不正确")
    sys.exit(1)
for i in booking_select_premises_data['data']['area']:
    if user_select_storey == i['parentId']:
        print('ID:'+i['id']+' 名称:'+i['name']+' 余量:'+str(i['free_num'])+'/'+str(i['total_num']))
user_select_area=input("请输入想要预约的区域ID：")
flag=0
for i in booking_select_premises_data['data']['area']:
    if user_select_area == i['id']:
        flag=1
if flag == 0:
    print("输入不正确")
    sys.exit(1)
booking_date_url='http://booking.lib.zju.edu.cn/api/Seat/date'
booking_date_headers={
    'User-Agent': user_agent,
}
booking_date_data={
    'build_id': '59',
    'authorization': booking_user_authorization,
}
booking_date_resp=session.post(booking_date_url,headers=booking_date_headers,data=booking_date_data)
booking_date_=json.loads(booking_date_resp.text)
booking_seat_url='http://booking.lib.zju.edu.cn/api/Seat/seat'
booking_seat_headers={
    'User-Agent': user_agent,
}
booking_seat_data={
    'area': user_select_area,
    'segment': booking_date_['data'][0]['times'][0]['id'],
    'day': booking_date_['data'][0]['day'],
    'startTime': booking_date_['data'][0]['times'][0]['start'],
    'endTime': booking_date_['data'][0]['times'][0]['end'],
    'authorization': booking_user_authorization,
}
booking_seat_resp=session.post(booking_seat_url,headers=booking_seat_headers,data=booking_seat_data)
booking_seat=json.loads(booking_seat_resp.text)
free_num=0
using_num=0
for i in booking_seat['data']:
    if i['status'] == '6':
        using_num+=1
    if i['status'] == '1':
        free_num+=1
    if i['status'] == '7':
        using_num+=1
if free_num == 0:
    print("当前区域座位已满")
    sys.exit(1)
print("当前空闲座位：")
for i in booking_seat['data']:
    if i['status'] == '1':
        print('ID:'+i['id']+' 名称:'+i['name'])
print('当前区域共'+str(free_num)+'个空闲座位')
user_select_seat=input("请输入想要预约的座位ID：")
flag=0
for i in booking_seat['data']:
    if user_select_seat == i['id']:
        flag=1
if flag == 0:
    print("输入不正确")
    sys.exit(1)
date=datetime.now().strftime("%Y%m%d")
booking_confirm_url='http://booking.lib.zju.edu.cn/api/Seat/confirm'
booking_confirm_headers={
    'User-Agent': user_agent,
    'authorization': booking_user_authorization,
}
encrypt='''
const CryptoJS = require('./crypto-js');
function encrypt(seat_id,segment,date){
    c = '{"seat_id":"'+seat_id+'","segment":"'+segment+'"}';
    v = date;
    y = "ZZWBKJ_ZHIHUAWEI";
    // return v;
    var v = CryptoJS.enc.Utf8.parse(v);
    var y = CryptoJS.enc.Utf8.parse(y);
    var b = CryptoJS.AES.encrypt(c, v, {
        iv: y,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
});
    return b.toString();
}
'''
booking_confirm_data={
    'aesjson': execjs.compile(encrypt).call("encrypt",user_select_seat,booking_date_['data'][0]['times'][0]['id'],date+date[::-1]),
    'authorization': booking_user_authorization,
}
booking_confirm_resp=session.post(booking_confirm_url,headers=booking_confirm_headers,data=booking_confirm_data)
print("预约结果：")
print(json.loads(booking_confirm_resp.text)['msg'])