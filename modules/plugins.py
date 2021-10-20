#!/usr/bin/env python3
import ssl
from dataclasses import asdict, dataclass
from email import encoders, policy
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, formatdate
from os import path
from smtplib import SMTP, SMTP_SSL, SMTPException
from typing import List

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer,
                                Table)

from modules.html_template import html_template
from modules.utils import Log, compin_strs, mimeFile, get_date
from modules.templates import EmailHtmlParser


@dataclass
class EmailSet:
    __slots__ = ['host', 'port', 'sslport', 'method', 'user_name', 'email_pass', 'default_sender',
                 'default_sender_name', 'default_recipient', 'default_recipient_name', 'html']
    host: str
    port: int
    sslport: int
    method: str
    user_name: str
    email_pass: str
    default_sender: str
    default_sender_name: str
    default_recipient: str
    default_recipient_name: str
    html: bool

    def asdic(self):
        return asdict(self)

    def __createAddress(self, name, email_address) -> str:
        return formataddr((name, email_address), 'utf-8')

    def sender_address(self):
        return self.__createAddress(self.default_sender_name, self.default_sender)

    def recipient_address(self):
        return self.__createAddress(self.default_recipient_name, self.default_recipient)

    def send_email(self, subject: str, body: str, recipient: str = None, attachment_names: any = None, Cc: List[str] = None, BCC: List[str] = None):
        return Emails(self).send_email(subject=subject, body=body, recipient=recipient, attachment_names=attachment_names, Cc=Cc, BCC=BCC)


""" Emails class"""


class Emails(Log):
    """ accept dictionary of email settings"""

    def __init__(self, emailset: EmailSet):
        super().__init__('email')

        if not emailset.email_pass or not emailset.user_name:
            raise('email setting missing important settings')
        # email settings
        self._sets = emailset
        # Create a  MIMEMultipart object
        self._msgRoot = MIMEMultipart()
        # Set the multipart email preamble attribute value. Please refer https://docs.python.org/3/library/email.message.html to learn more.
        self._msgRoot.preamble = '====================================================================='
        self._msgRoot.policy = policy.SMTP
        # Create a MIMEMultipart Alternative and related.
        self._msgAlternative = MIMEMultipart('alternative')
        self._msgRelated = MIMEMultipart('related')

        # attech messages in order
        self._msgRelated.attach(self._msgAlternative)
        self._msgRoot.attach(self._msgRelated)

    def __str__(self):
        return "Emails Class invoked"

    def __repr__(self):
        return "Emails Class was invoked"

    def __get_ssl_context(self):
        return ssl.create_default_context()

    def __sortout_body(self, body):
        if body and isinstance(body, list):
            if self._sets.html:
                return compin_strs(body, '<br>')
            else:
                return compin_strs(body, '\n')
        else:
            return body

    def __get_smtp(self):
        if self._sets.method == 'default':
            return SMTP(self._sets.host, self._sets.port)
        elif self._sets.method == 'ssl':
            return SMTP_SSL(self._sets.host, self._sets.port, context=self.__get_ssl_context())
        elif self._sets.method == 'local':
            return SMTP('localhost')

    def __get_server(self):
        """Sends the message to the configured SMTP server."""
        try:
            with self.__get_smtp() as _server:
                if self._sets.method == 'default':
                    _server.starttls(context=self.__get_ssl_context())

                # login
                if self._sets.method in 'default ssl':
                    login_rst = _server.login(
                        self._sets.user_name, self._sets.email_pass)
                    # this the feedback for login tuple (235, b'2.7.0 Accepted')
                    print(login_rst)

                # send msg and receive feedback empty {}
                _server.sendmail(self._msgRoot["From"], self._msgRoot["To"], self._msgRoot.as_string())

                # log data
                log_msg = f"email was sent today from: {self._msgRoot['From']} to: {self._msgRoot['To']} - Subject: {self._msgRoot['Subject']} - Status :{login_rst}"

                self.logger.info(log_msg)
                _server.quit()
        except SMTPException or Exception as ex:
            print("Error: unable to send email : \n %s" % str(ex))

    def __htmlTemplate(self, subject:str, body:str):
        prsr = EmailHtmlParser(templateName='simple_email.html')       
        prsr.render_template(kwards={"{title}": subject,"{date}": get_date(),"{message_body}": body})
        _html =mimeFile(prsr.temFileName)
        
        # Add attachment html to alternative message
        self._msgAlternative.attach(_html.Obj)

        for item in prsr.mimeObj_list:
            self._msgRelated.attach(item.Obj)
            
        prsr.close()
    

    def __attachment_file(self, file_path):
        # Add attachment to message
        self._msgRoot.attach(mimeFile(file_path).Obj)

    def send_email(self, subject: str, body: str, recipient: str = None, attachment_names: any = None, Cc: List[str] = None, BCC: List[str] = None):
        body = self.__sortout_body(body)
        self._msgRoot['From'] = self._sets.sender_address()
        self._msgRoot['To'] = recipient if recipient else self._sets.recipient_address()
        self._msgRoot['Subject'] = Header(subject).encode()
        self._msgRoot['Date'] = formatdate(localtime=True)
        self._msgRoot['Replay-To'] = 'Reciption  <tuban@profdrivers.co.uk>'
        if Cc:
            self._msgRoot["Cc"] = ','.join(Cc)
        if BCC:
            self._msgRoot["BCC"] = ','.join(BCC)

        _text_body = mimeFile.mime_core('text','plain', body)
        # Basic Email formatting
        if self._sets.html:
            # attach plain msg
            self._msgAlternative.attach(_text_body)
            # attach html template
            self.__htmlTemplate(subject, body)
        else:
            self._msgRoot.attach(_text_body)

        """ Process the attachment to the email  option eith list of string"""
        if attachment_names and isinstance(attachment_names, list):
            for _filename in attachment_names:
                self.__attachment_file(_filename)

        elif attachment_names and isinstance(attachment_names, str):
            self.__attachment_file(attachment_names)

        # pass message to server
        return self.__get_server()


""" ToPdaf"""


class ToPdf():
    def __init__(self, docs_path=None) -> None:
        self.filename = "%s/pychecks_report.pdf" % docs_path

    def generate_pdf(self, title, additional_info, table_data=None, filename=None) -> str:
        styles = getSampleStyleSheet()
        report = SimpleDocTemplate(filename if filename else self.filename)
        report_title = Paragraph(title, styles["h1"])
        report_info = Paragraph(additional_info, styles["BodyText"])
        empty_line = Spacer(1, 20)

        """if there is table data build here"""
        if table_data:
            # check if table_date is dic and not list of list then convert to list of list
            if isinstance(table_data, dict):
                table_data = self.dict_to_table(table_data)

            table_style = [('GRID', (0, 0), (-1, -1), 1, colors.black), ('FONTNAME', (0, 0), (-1, 0),
                                                                         'Helvetica-Bold'), ('ALIGN', (0, 0), (-1, -1), 'CENTER')]
            report_table = Table(
                data=table_data, style=table_style, hAlign="LEFT")
            # Build the report
            report.build([report_title, empty_line,
                         report_info, empty_line, report_table])
        else:
            report.build([report_title, empty_line, report_info, empty_line])

        print('report generated successfully title :' + title)
        return self.filename

    def dict_to_table(self, table_dic):
        """Turns the data in thei dictionary into a list of lists."""

        _keys = []
        _values = []

        # recusive function for inner dictionaries
        def is_dic(_item):
            if isinstance(_item, dict):
                for k, v in _item.items():
                    _keys.append(k)
                    is_dic(v)
            else:
                _values.append(_item)

        # iterate through main dic
        for item_key, item_value in table_dic.items():
            _keys.append(item_key)
            is_dic(item_value)

        return [_keys, _values]
