#!/usr/bin/env python3
import sys

from modules.Iservices import ISvc
from modules.utils import compin_strs


def main():
    svc = ISvc()

    """ run as normal"""
    #result = svc.run.default()

    """ run concurrent execution """
    #result= svc.run.concurrent()

    """ run multiprocessing"""
    result = svc.run.multiprocessing()

    _summary = ["Security scan report", 'The summary:']
    if result and isinstance(result, list):
        _summary += result
    else:
        _summary.append("All security checks passed, every thing is OK")

    html_body = compin_strs(_summary, ' <br/> ')
    # string_body=compin_strs(_summary,'/n')

    report_path = svc.gen_report(_summary[0], html_body)
    # send email
    svc.send_email(subject=_summary[0],
                   body=_summary, attachment_names=report_path)

    # log
    svc.logger().info(compin_strs(_summary, ','))

    sys.exit(0)


if __name__ == "__main__":
    main()
