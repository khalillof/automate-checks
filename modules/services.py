#!/usr/bin/env python3
from _typeshed import Self
import os
import shutil
import socket
from dataclasses import dataclass
from socket import create_connection
from ssl import wrap_socket
from typing import List
from urllib import request
import psutil
from modules.Iservices import Store
from modules.utils import excpt_msg, get_os, sub_process


class PyChecks:
    """ accept dictionary of health checks settings"""

    def __init__(self, host_name, ip_address):
        self.syslog = None
        self.nginx_log = None
        self.__host_name = host_name
        self.__ip_address = ip_address

    def __str__(self):
        return "Health Chechs Class invoked"

    def __repr__(self):
        return "Health Chechs Class invoked"

    def __check(self, test, msg):
        if test:
            return msg
        else:
            return False

    def __check_disk_full(self, disk, min_gb, min_percent):
        """Return True if there isn't enough disk space , false otherwise """
        du = shutil.disk_usage(disk)
        percent_free = du.free / du.total * 100
        gigabytes_free = du.free / 2**30
        if gigabytes_free < min_gb or percent_free < min_percent:
            return True
        return False

    #######################################

    def check_reboot(self):
        """ Return True if the computer has a pending reboot."""
        return self.__check(os.path.exists("/run/reboot-required"), "check_reboot - msg: your server require reboot")

    def check_internet(self):
        """ will Return True if it fail to resolve google's URL, False otherwise """
        return self.__check(socket.gethostbyname(self.__host_name) != self.__ip_address, "check_internet - msg: no internet connection")

    def check_root_disk_full(self):
        """ Return True if the root partation is full."""
        return self.__check(self.__check_disk_full(disk="/", min_gb=2, min_percent=10), "check_root_disk_full - msg: Available disk space is less than 20%")

    def check_cpu_usage(self):
        """Verifies that there's enough unused CPU"""
        return self.__check(psutil.cpu_percent(1) > 75, "check_cpu_usage - msg: CPU usage is over 80% ")

    def check_momory(self):
        """ 500MB = 52428800.0 """
        return self.__check(psutil.virtual_memory().available <= 52428800.0, "check_momory - msg: Available memory is less than 500MB")

    def check_localhost(self):
        """ will return true if localhost not equal '127.0.0.1'  """
        return self.__check(socket.gethostbyname('localhost') != '127.0.0.1', "check_localhost - msg: localhost cannot be resolved to 127.0.0.1")

    def check_update_available(self):
        """ will return true if there are update in linux ubuntu distrubution"""
        apt_update_check = '/usr/lib/update-notifier/apt_check'
        if os.path.isfile(apt_update_check):
            result = sub_process(apt_update_check)
            return self.__check(int(result.split(';')[0]) > 0, "check_update_available - msg: system updates avaliable to download")

    def check_syslog(self):
        pass

    def check_nginx_log(self):
        pass

    ######################################

    def get_tasks(self):
        # in one line
        # method_list = [attribute for attribute in dir(self) if callable(getattr(self, attribute)) and attribute.startswith('__') is False]
        method_list = []

        # attribute is a string representing the attribute name
        for attribute in dir(self):
            # Get the attribute value
            attribute_value = getattr(self, attribute)
            # Check that it is callable
            if callable(attribute_value):
                # Filter all dunder (__ prefix) methods
                if attribute.startswith('__') == False and attribute.startswith('_PyChecks') == False:
                    # add method as method (attribute_value)
                    # if want to add method name as string instead use (attribute)
                    method_list.append(attribute_value)

        method_list.remove(self.get_tasks)

        # return list of the functions as function
        return method_list


"""
Socket: To connect with different servers on a certain socket by a particular port
SSL: Required for the wrapping of the socket connection
"""


@dataclass
class Os_Checks:
    __slots__ = ['host_name', 'ip_address']
    host_name: str
    ip_address: str

    def get_tasks(self) -> list:

        return PyChecks(self.host_name, self.ip_address).get_tasks()


class Server:
    """
    Name: name of a server
    Port: the port number to which we want to connect
    Connection: tells the connection type, e.g., SSL or ping
    Priority:  tell us the server priority, e.g., you can set alerts if you set priority
    History:  to keep server history list
    Alert:to send alerts to your email
    Msg: used to display a message if connection established or failed which is initially empty
    Success: used to tell if the connection is successful or not
    """

    def __init__(self, name, port, html, connection, priority):
        self.name = name
        self.port = port
        self.connection = connection.lower()
        self.priority = priority.lower()
        self.history = []
        self.alert = False
        self.html = html
        self.msg = ""
        self.success = False
        self.status_code = 0
        if html:
            self.name = self.__html_url(self.name)

    def __html_url(self, url):
        _url = url.lower()
        _http = "http://"
        _https = "https://"
        if _http in _url or _https in _url:
            return _url
        elif self.connection == "ssl":
            return _https.__add__(_url)
        else:
            return _http.__add__(_url)

    def __set_msg(self, err=None):
        _name = "The website" if self.html else "The server"
        code = f"and status code is : ({self.status_code})" if self.html else ""
        # ...............................................

        err_msg = f"Error occured while try to connect to the {_name} - error message: {err}" 

        msg = f"{_name} {'is up and running' if self.success else 'is down or could not fulfill the request'}- {code} "

        mmgs = f"{_name} tested was ({self.name}) on port ({self.port}) with connection ({self.connection}). Msg: {msg if err is None else err_msg}"
        self.msg = mmgs

    def connect(self):
        try:
            if self.connection == "plain" and self.html or self.connection == "ssl" and self.html:
                """ check website """
                self.success = self.__check_website()
            elif  not self.html:
                if self.connection == "ssl" :
                    """ check server connection """
                    with wrap_socket(create_connection((self.name, self.port), timeout=10)) as sev:
                        self.success = True
                        sev.close()
                else:
                    with create_connection((self.name, self.port), timeout=10) as sev:
                        self.success = True
                        sev.close()
            else:
                self.success = self.__ping()
        except Exception as ex:
            self.status_code = 0
            self.success = False
            self.alert = True
            """ set message important """
            self.__set_msg(err=excpt_msg(ex, 'connect'))
        else:
            """ set message important """
            self.__set_msg()
            """ create history """
            self.__create_history()

            """ check for email alert """
            if not self.success or self.alert:
                    self.__email_aler()

        """ return result"""
        return self.get_stats()

    def __check_website(self) -> bool:
        self.status_code = request.urlopen(self.name).getcode()
        return self.status_code > 0

    def get_stats(self):
        # print the history of each server and how much that particular server has uptime.
        server_up = 0
        history_len = len(self.history)
        if history_len > 0:
            for point in self.history:
                if point[1]:
                    server_up += 1

        server_up = (server_up / history_len * 100)
        return "%s server up time - %s Total history :%s" % (self.msg, server_up, history_len)

    def __create_history(self):
        # the attributes with maximum limit defined, and if the history limit exceeds, it will delete the older one
        history_max = 100
        self.history.append((self.msg, self.success))
        while len(self.history) > history_max:
            self.history.pop(0)

    def __ping(self):
        # ping() function will ping the server or computer. If the ping is successful, it will output True, and if the connection failed, it will return False
        try:
            opt = 'n'if get_os() == "window" else 'c'
            output = sub_process("ping -%s 1 %s" % (opt, self.name))
            if 'unreachable' in output:
                return False
            else:
                return True
        except Exception:
            return False

    def __email_aler(self):
        try:
            from modules.Iservices import ISvc
            ISvc(False, False).send_email(
                "email alert from servers connections", self.msg)
            print("email alert from servers connections: %s" % self.msg)
        except:
            raise

class TestServer:

    def __init__(self, obj_db:Store) -> None:
        self.__db =  obj_db
        _hist = self.__db.get_item('servers_history')
        self.history:dict = _hist if _hist else  {}
        self.servers:List[Server] = self.__db.get_item('servers')

    def runtTasks(self):
        return self.get_stats()


    def close(self):
        # update db
        self.__db.update({'servers_history':self.history})
        self.__db.update({'servers':self.servers})
        self.__db.close()

    def create_history(self, name, success, msg) -> None:
        if name in self.history:
            if success:
                self.history[name]['up']+=1
                self.history[name]['msg']=msg
            else:
                self.history[name]['down']+=1
                self.history[name]['msg']=msg
        else:
            if success:
                self.history[name]={'up':1,'down':0, 'msg':msg}
            else:
                self.history[name]={'up':0,'down':1, 'msg':msg}
        
    def get_stats(self) -> list:
        for s in self.servers:
            s.connect()
            self.create_history(s.name,s.success, s.msg)

        result = []
        for items in self.history.values():
            server_up = items['up']
            history_len = server_up + items['down']
            server_up = (server_up / history_len * 100)
            result.append("%s server up time - %s Total history :%s" % (items['msg'], server_up, history_len))
        self.close()
        return result

    def add_server(self):
        print("adding new server ??")

        __server_name = input("inter your server name")
        __port = int(input("enter a port number as integer"))
        __connection_type = input("enter type ping/plain/ssl")
        __priority = input("enter priority high/low")
        __html = bool(input("enter is it a website ?  True/False"))
        __new_server = Server(name=__server_name, port=__port, html=__html,connection=__connection_type, priority=__priority)

        self.servers.append(__new_server)
        self.__db.update({'servers': self.servers})


