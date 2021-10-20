#!/usr/bin/env python3
import datetime
import logging
import logging.config
import mimetypes
import pickle
import platform
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from multiprocessing import Pool
from os import mkdir, path, rename, system
from tempfile import NamedTemporaryFile
from typing import List


def restart():
    osName = get_os()
    if  osName == 'window':
        system('shutdown /r /t 1')
    elif osName == 'linux':
        system('sudo reboot')
    else:
        print("I can't do that" )

def shutdown():
    osName = get_os()
    if  osName == 'window':
        system('shutdown /s /t 1')
    elif osName == 'linux':
        system('sudo shutdown now')
    else:
        print("I can't do that" )

def logout():
    osName = get_os()
    if  osName == 'window':
        system('shutdown -1')
    elif osName == 'linux':
        system('logout')
    else:
        print("I can't do that" )

class Log:
    def __init__(self, name):
        # logging.basicConfig(filename='example.log',format='%(asctime)s - %(levelname)s- %(message)s',datefmt='%m/%d/%Y %I:%M:%S %p', encoding='utf-8', level=logging.DEBUG)
        _path = path.abspath('pychecks/config/logs.conf')
        logging.config.fileConfig(fname=_path)
        # create logger
        self.logger = logging.getLogger(name)

    @staticmethod
    def instance(name):
        return Log(name).logger

    @staticmethod
    def Defualt():
        return Log('pychecks').logger

class mimeFile:
    def __init__(self, filepath: str, contentId: str = None, content_disposition=False, charset='utf-8') -> None:
        _types=mimeType(filepath)
        self.charset = charset
        self.mType = _types[0] 
        self.mSubtype =_types[1]

        self.baseName = path.basename(filepath)
        self.filepath = filepath
        self.contentId = contentId
        self.supportedTypes = 'application,image,text,audio'
        # mimie object
        self.Obj = self.__get()

        # Add 'Content-ID' header value to the above MIMEImage object to make it refer to the image source (src="cid:image1") in the Html content.
        if contentId:
            self.add_content_id()

        if content_disposition or self.mType == 'application':
            self.add_content_disposition()

        if self.mType not in self.supportedTypes:
            self.add_content_disposition()

    def add_content_disposition(self):
        self.Obj.add_header("Content-Disposition",f"attachment; filename={self.baseName}")

    def add_content_id(self):
        self.Obj.add_header('Content-ID', self.contentId)

    def __get(self):        
        mode = 'r' if self.mType == 'text' else 'rb'
        return self.mime_core(self.mType, self.mSubtype, readFile(self.filepath, mode=mode))

    @staticmethod
    def mime_core(mType: str, subType:str, content: any):
        if mType in 'text':
            return MIMEText(content, subType, 'utf-8')
        elif mType == 'application':
            return MIMEApplication(content, subType)
        elif mType == 'image':
            return MIMEImage(content, subType)
        elif mType == 'audio':
            return MIMEAudio(content, subType)
        else:
            _base = MIMEBase('application', 'octet-stream')
            _base.set_payload(content)
            encoders.encode_base64(_base)
            return _base

def mimeType(filename:str):
    return mimetypes.guess_type(filename)[0].split('/')

def if_else(else_obj,if_obj=None):
    return if_obj if if_obj else else_obj

def COMMASPACE(texts:List[str]) -> str:
        return ','.join(texts)  
        
# get or make dir base on mime type
def getDir_OrMakeOne(name:str, parent='/home/tuban/pychecks/docs/') -> str :
    dir = path.join(parent,name)

    if  not path.isdir(parent):
        return None

    if not path.isdir(dir): 
        mkdir(dir)      
    return dir

def temfile_extention(extention) -> str:
    with  NamedTemporaryFile(delete=False) as tem:
        newName = "%s%s" % (tem.name,extention)
        rename(tem.name, newName)
        return newName

def touch(pathName:str) -> str:
    open(pathName, 'a').close()
    return pathName

def staticFile(dirName,fName,ext) -> str:
    Dirname = getDir_OrMakeOne(dirName)
    newName = "%s/%s%s" % (Dirname,fName,ext)
    return touch(newName)     

# get content of file as bytes
def readFile(filepath, mode='rb'):
    with open(filepath,mode) as f:
        _file = f.read()
        #f.close()
        return _file

# Make a local copy of what we are going to send.
def writeFile(msg, filename:str, mode='wb'):
    with open(filename, mode=mode) as f:
        f.write(msg)
        f.close()

def loader(filename, callback, mode='r') -> any:
    try:
        result = callback(readFile(path.abspath(filename), mode))
        return result
    except Exception as ex:
        Log.Defualt().error(excpt_msg(ex, callback.__name__))
        raise ex

def load_pickle(file_path, callback):
    """ The try statement will load the objs from pickle file if it already exists. If it does not exist, a fresh objs from to_invock.   """
    file_path = path.abspath(file_path)
    try:
        objs = []
        if path.exists(file_path):
            objs = pickle.load(open(file_path, "rb"))
            print(
                "====================================LOADED OBJS FROM PICKLE===============================================")
        else:
            objs = pickle.dump(callback(), open(file_path, "wb"))
            print(
                "====================================LOADED FRESH OBJS===============================================")
        return objs
    except Exception as ex:
        Log.Defualt().error(excpt_msg(ex, 'load_objs'))
        raise ex

def excpt_msg(ex, method_name) -> str:
    return f"Exception was thrown on method - ({method_name}) - :  Error type : {type(ex).__name__} - message : {str(ex)} "


def invoker(callback, msg=None, throw=False):
    try:
        result = callback()
        return result
    except Exception as ex:
        if msg:
            return msg
        elif throw:
            raise ex
        else:
            ex_msg = excpt_msg(ex, callback.__name__)

            Log.Defualt().error(ex_msg)

        return ex_msg


def lister(items) -> list:
    return[msg for msg in items if msg]


def get_timestamp() -> str:
    return datetime.datetime.utcnow().isoformat()


def get_date(msg=None, str_format="%B %d, %Y, %H:%M:%S") -> str:
    date = datetime.datetime.utcnow().strftime(str_format)
    if msg:
        return "%s\n%s" % (msg, date)
    else:
        return date

# compine list of strings to string rows


def compin_strs(_list, new_line) -> str:
    compined_string = "" 
    for line in _list:
        compined_string += line + new_line
    return compined_string


def get_os() -> str:
    return platform.system().lower()

def get_home_dir() -> str:
    return path.expanduser('~')
    
def get_user_name() -> str:
    if get_os() == 'windows':
        return get_home_dir().split('\\')[2]       
    return get_home_dir().split('/')[2]

"""subprocess expect either command as list or string """


def sub_process(_commands):
    result = subprocess.getoutput(_commands)
    return result


def find_char(_char, text) -> bool:
    if _char in text:
        return True
    else:
        return False


""" check text if contain some chars """


def get_chars(_chars, _text:str) -> list:
    chars = []
    for _char in _chars:
        if _char in _text:
            chars.append(_char)
    return chars


""" get text between two symboles or chars recusive """


def get_txt_between_two_symboles(left_symbole, right_symbole, _text:str):

    if left_symbole and right_symbole in _text:
        start = _text.find(left_symbole)
        end = _text.find(right_symbole)
        _cut = _text[start:end+1]
        return _cut


""" replace text between two symboles or chars recusive """


def replace_txt_between_two_symboles_recusive(left_symbole, right_symbole, _text:str):

    _cut = get_txt_between_two_symboles(
        left_symbole, right_symbole, _text)
    if _cut:
        _text = _text.replace(_cut, '')
        return replace_txt_between_two_symboles_recusive(left_symbole, right_symbole, _text)
    else:
        return _text.strip()


""" clean text from some chars """


def clean_text(chars, text:str):
    for c in [chr for chr in chars if chr in text]:
        text = text.replace(c, '')
    return text.strip()

#################################################################


class Writer:
    def __init__(self, filename='e:\\log.txt'):
        self.outfile = open(filename, 'a')
        self.write(
            "======================== LOG START =============================\n")
        # redirect standard outputs,errors
        (self.oldStdErr, self.oldStdOut) = (sys.stderr, sys.stdout)
        (sys.stderr, sys.stdout) = (self, self)

    def write(self, text):
        self.outfile.write(text)

    def writelines(self, lines):
        self.outfile.writelines("%s\n" % l for l in lines)
        self.close()

    def write_err(self, text):
        self.outfile.write("Error"+text)

    def end(self):
        self.outfile.close()
        (sys.stderr, sys.stdout) = (self.oldStdErr, self.oldStdOut)

    def close(self):
        self.write(
            "======================== LOG END =============================\n")
        self.end()

    def log_bash(string_body, file_path):
        try:
            # log query
            query = "echo '%s' >> %s" % (string_body, file_path)
            sub_process(query)
        except Exception as ex:
            Log.Defualt().error(excpt_msg(ex, 'log_bash'))


class Runners:

    def __init__(self, tasks):
        self.Tasks = tasks
        self.tasks_len = len(tasks)
        # processing choice:

    def default(self):
        rst = lister([invoker(_fun) for _fun in self.Tasks])
        return rst

    def concurrent(self):
        with ThreadPoolExecutor(max_workers=self.tasks_len) as executor:
            result = lister(executor.map(
                invoker, self.Tasks, timeout=60))
        return result

    def multiprocessing(self):
        with Pool(self.tasks_len) as pol:
            result = lister(pol.map(invoker, self.Tasks))
        return result
