#!/usr/bin/env python3

import os
import shelve
from dataclasses import asdict, dataclass
from os import path
from typing import List

import yaml

from modules.services import Os_Checks, Server, TestServer
from modules.plugins import EmailSet,ToPdf
from modules.utils import loader, Log, Runners

class Store:
    def __init__(self, filename='pychecks/data/db/obj.shelve', flag='c', writeback=True):
        name = path.join(os.getcwd(),filename)
        self.shelve = shelve.open(name, flag=flag, writeback=writeback)

        """ check if settings data is already on db"""

        if len(self.shelve.keys()) > 2:
             #print([k for k in self.shelve.keys()])
             pass
        else:
            settings = Settings.load()
            self.add_item('settings',settings)
            self.add_items(settings.asdic())
            #print([ k for k in self.shelve.keys()])
        # redirect standard outputs,errors
        #(self.oldStdErr, self.oldStdOut) = (sys.stderr, sys.stdout)
        #(sys.stderr, sys.stdout) = (self, self)

    def get_item(self, id) -> object:
        return self.shelve.get(id)

    def all_items(self) -> object:
        return self.shelve.items()

    def add_item(self, key, obj):
        self.shelve.setdefault(key, obj)
        self.shelve.sync()
        # self.close()

    def update(self, dic):
        self.add_items(dic)

    def add_items(self, dic_data):
        self.shelve.update(dic_data)
        self.shelve.sync()
        # self.close()

    def keys(self):
        self.shelve.keys()
        self.shelve.close()

    def values(self):
        self.shelve.values()
        self.shelve.close()

    def remove(self, key):
        self.shelve.pop(key)
        self.shelve.close()

    def pop_item(self):
        self.shelve.popitem()
        self.shelve.close()

    def clear(self):
        self.shelve.clear()
        self.close()

    def end(self):
        self.shelve.close()
        #(sys.stderr, sys.stdout) = (self.oldStdErr, self.oldStdOut)

    def close(self):
        self.end()


@dataclass
class Settings:
    __slots__ = ['docs_name', 'obj_db', 'sql_db',
                 'log', 'os_checks', 'emailset', 'servers']
    docs_name: str
    obj_db: str
    sql_db: str
    log: str
    os_checks: Os_Checks
    emailset: EmailSet
    servers: List[Server]

    def asdic(self):
        return asdict(self)

    @staticmethod
    def load():

        docs = loader('pychecks/config/settings.yaml', yaml.full_load)

        dcs = docs['docs_name']
        obj = docs['obj_db']
        sql = docs['sql_db']
        log = docs['log']
        os_check = Os_Checks(**docs['os_checks'])
        email = EmailSet(**docs['emailset'])
        svs = []
        for sts in docs['servers']:
            for k, v in sts.items():
                svs.append(Server(k, *v.values()))

        return Settings(docs_name=dcs, obj_db=obj, sql_db=sql, log=log, os_checks=os_check, emailset=email, servers=svs)

""" servives """
class ISvc:
    def __init__(self, osChecks:bool=True, connections:bool=True):
        """ load settings"""
        __db = Store()
        __sts=__db.get_item("settings")

        self.logger = Log.Defualt
        self.send_email = __sts.emailset.send_email
        self.gen_report = ToPdf(__sts.docs_name).generate_pdf

        tasks = []

        if osChecks:
            tasks += __sts.os_checks.get_tasks()

        if connections:
            tasks += TestServer(__db).runtTasks

        if len(tasks) > 0:
            self.run = Runners(tasks)
        
        __db.close()
