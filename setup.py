#!/usr/bin/env python3
from modules.utils import sub_process, get_home_dir, get_user_name
"""
Developer's Quick Start:

            $ mkdir project
            $ cd project
            $ python -m virtualenv .
            $ . bin/activate
            $ pip install reportlab

"""

if __name__ == "__main__":
    home=get_home_dir()
    query=f"cd {home}/pychecks && pip install virtualenv && sleep 2 && python3 -m virtualenv . && sleep 2 && . bin/activate && sleep 2 && pip install -r ./requirements.txt && cd {home} && sudo chmod +x ./pychecks/main.py"
    try:
        result = sub_process(query)
        msg="================================================================ \nJust finshed installing all necessary pacKages --- now run the following command :\nsudo ./pychecks/main.py"
        if result:        
            print(result)
            print(msg)
        else:
            print(msg)
    except:
        print(f"Please make sure the file is executable and run this script with root privilage or \nsudo -u {get_user_name()} {home}/pychecks/setup.py")
