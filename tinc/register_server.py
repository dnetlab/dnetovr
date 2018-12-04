#! /usr/bin/python
#coding: utf-8

import json
import os
import platform
import signal
import subprocess
import sys
import threading
import time

python_version = platform.python_version().split('.')[0]
if python_version == '2':
    import httplib
    import thread
elif python_version == '3':
    import http.client
    import _thread


geoip_host = '52.25.79.82'
geoip_port = 10000

master_host = '220.168.30.10'
master_port = 7070

heartbeaturl = '/vppn/api/v1/proxy/heartBeat'
registerurl = '/vppn/api/v1/proxy/register'

interface = 'eth0'

if len(sys.argv) > 1:
    tinc_path = sys.argv[1] + '/'
else:
    tinc_path = '/root/tinc/'

register_info = {
	"proxyIp":"220.168.30.12",
	"countryName":"China",
	"countryCode":"CN",
	"area":"ChangeSha",
	"oS":"Centos",
	"serverType":"vppn1",
	"authType":"0",
	"sshPort":"2222",
	"region":"",
}

heart_beat_info = {
    "proxyIp":"1.2.3.4"
}

tinc_isalive = {
    'alive':False
}

main_exit = {
    'isexit': False
}


class myThread (threading.Thread):
    def __init__(self, name, delay):
        threading.Thread.__init__(self)
        self.name = name
        self.delay = delay
    def run(self):
        if self.name == 'beat':
            heart_beat(self.name, self.delay)
        elif self.name == 'guard':
            guard()


guard_thread = myThread('guard', 3)


def load_config():
    fname = tinc_path + 'register_config_json'
    if os.path.exists(fname):
        f = open(fname, 'r')
        so = json.load(f)

        register_info['oS'] = so['OS']
        register_info['serverType'] = so['ServerType']
        register_info['authType'] = so['AuthType']
        register_info['sshPort'] = so['SSHPort']
        if so.get('master_host', -1) != -1:
            global master_host
            master_host = so['master_host']
        if so.get('master_port', -1) != -1:
            global master_port
            master_port = so['master_port']
        if so.get('wan_interface', -1) != -1:
            global interface
            interface = so['wan_interface']
        f.close()
    else:
        print(fname, 'is not exist')
        main_exit['isexit'] = True
        sys.exit()

    

def get_region_info():
    if python_version == '2':
        conn = httplib.HTTPConnection(geoip_host, geoip_port)
    elif python_version == '3':
        conn = http.client.HTTPConnection(geoip_host, geoip_port)
    else:
        print('http version error')
        pass
    conn.request("GET",'/geoip_json.php')
    res = conn.getresponse()
    s = res.read()
    conn.close()
    print(s)
    if s == 'timeout':
        pass
    dataDict = json.loads(s.decode('utf-8'))
    heart_beat_info['proxyIp'] = dataDict['ipaddr']

    register_info['proxyIp'] = dataDict['ipaddr']
    register_info['countryCode'] = dataDict['country_code']
    register_info['countryName'] = dataDict['country_name']
    register_info['area'] = dataDict['city']


def get_local_device_info():
    if platform.system() == 'Linux':
        ss = os.popen('ifconfig ' + interface + ' | awk \'/HWaddr/{ print $5 }\'')
        mac = ss.read().replace(":","").replace('\n','')
    else:
        pass
    

def do_http_post(h, p, path, data):
    try:
        if python_version == '2':
            conn = httplib.HTTPConnection(h, p, timeout=30)
        else:
            conn = http.client.HTTPConnection(h, p, timeout=30)
        conn.request("POST", path, data)
        res = conn.getresponse()
        s = res.read()
        conn.close()
        #print(s)
        return s
    except Exception as e:
        print("%s:\n %s\n %s" % ('http error', time.ctime(time.time()), e.message))
        return 'timeout'


def heart_beat(threadName, delay):
    while True:
        if tinc_isalive['alive'] == True:
            do_heart_beat_report()
        time.sleep(delay)


def guard():
    while True:
        if main_exit['isexit'] == True:
            thread.exit()
        ss = subprocess.check_output(['ps', '-ef'])
        if ss.find('/root/tinc/tinc.pid') == -1:
            os.system(tinc_path + '/start')
            #print("%s: %s" % ('guard_true', time.ctime(time.time())))
            tinc_isalive['alive'] = False
        else:
            #print("%s: %s" % ('guard_false', time.ctime(time.time())))
            tinc_isalive['alive'] = True
        time.sleep(3)


def do_report_client_info():
    do_http_post(master_host, master_port, '/vpnservice/ReportClientInfo', json.dumps(report_info))


def do_register_server():
    #print('do_register_server :\n', register_info)
    replay = do_http_post(master_host, master_port, registerurl, json.dumps(register_info))
    if replay != 'timeout':
        try:
            d_replay = json.loads(replay)
            #{"Code":"200","PubKey":"","PrivKey":"","OtherInfo":""}
            if d_replay['code'] == 200:
                pass
        except Exception as e:
            print("%s:\n %s\n %s\n %s" % ('do_register_server ERROR', time.ctime(time.time()), e.message, replay))
       


def do_heart_beat_report():
    replay = do_http_post(master_host, master_port, heartbeaturl, json.dumps(heart_beat_info))
    if replay != 'timeout':
        try:
            d_replay = json.loads(replay)
            #{"Code":"201","OtherInfo":"unregistered"}
            if d_replay['code'] == 902:
                if d_replay.get('message', -1) != -1:
                    global master_host
                    master_host = d_replay['message']
            if d_replay['code'] == 903:
                do_register_server()
                
        except Exception as e:
            print("%s:\n %s\n %s\n %s" % ('do_heart_beat_report ERROR', time.ctime(time.time()), e.message, replay))


def quit(signum, frame):
    main_exit['isexit'] = True
    sys.exit()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, quit)                                  
    signal.signal(signal.SIGTERM, quit) 

    register_info.clear()
    heart_beat_info.clear()

    load_config()
    get_region_info()
    get_local_device_info()

    guard_thread.start()
    heart_beat('main', 20)
