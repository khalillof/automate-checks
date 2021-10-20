#!/usr/bin/env python3
from html.parser import HTMLParser
from os import path
#from html.entities import name2codepoint
from typing import List
from urllib.parse import urlsplit
from urllib.request import urlopen
from modules.utils import temfile_extention, mimeFile, staticFile, readFile, writeFile
from modules.generator import get_random_string
# Import HTML from a URL
def fetchUrl(url:str="https://khaliltuban.co.uk"):
    url = urlopen(url)
    html = url.read().decode()
    url.close()
    return html

class ReWrite:
    def __init__(self, fname:str=None, mode='w') -> None:
        self.fname = fname
        self.ouFile = None
        self.lines : List[str] = []
        self.mode =mode

        if fname:
            self.ouFile = open(self.fname, mode=self.mode,encoding='utf-8')

        self.write = self.ouFile.write if self.fname else self.lines.append
        
    def as_string(self):
        sss = ""
        for item in self.lines:
            sss += item
        return sss

    def render(self,**kwards):
        sss = self.as_string()        
        if kwards:
            for k,v in kwards.items():
                sss = sss.replace(k,v)               
        return sss
    
    def get_Filename(self):
        self.close()
        return self.fname

    def close(self):
        if self.ouFile:
            self.ouFile.close()
        if self.lines:
            self.lines.clear()


class EmailHtmlParser(HTMLParser):
    def __init__(self, templateName:str=None, convert_charrefs: bool = ...) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.reset()

        self.temFileName :str = None
        #self.Writer = ReWrite(fname=self.temFileName)
        self.Writer = ReWrite()
        self.mimeObj_list: List[mimeFile] =[]
        # sortout template
        if templateName:
            temf=path.join('/home/tuban/pychecks/docs/html/', templateName)
            self.templateName =  temf if path.exists(temf) else None
            if self.templateName:
                self.feed(readFile(self.templateName,'r'))
   
    def __getFileName(self) -> str:
        return staticFile('html/emails',get_random_string(8),'.html')

    def img(self,tag,attrs):
        """ process images"""
        if tag == 'img':
            # attrs is a list of tuples, (attribute, value)
            srcindex = -1
            for i in range(len(attrs)):
                if attrs[i][0] == 'src':
                    srcindex =  i

            if srcindex < 0:
                return   # img with no src tag? skip it
            src = attrs[srcindex][1]
            # Make relative URLs absolute
            src = self.make_absolute(src)
            # create mimi
            id =get_random_string(8)
            self.mimeObj_list.append(mimeFile(src, contentId=id))
            cid = "cid:%s" % id
            attrs[srcindex] = (attrs[srcindex][0], cid)
    
    def anchor(self,tag,attrs):
        # process 'anchor' tag a
        if tag == "a":
            for name, link in attrs:
                #if name == "href" and link.startswith("http"):
                if name == "href":
                    print(link)
   
    def starTag(self,tag,attrs):
        #print("start tag  :", tag)
        self.Writer.write('<' + tag)
        for attr in attrs:
            self.Writer.write(' ' + attr[0])
            if len(attr) > 1 and isinstance(attr[1], str):
                # make sure attr[1] doesn't have any embedded double-quotes
                val = attr[1].replace('"', '\"')
                self.Writer.write('="' + val + '"')
        self.Writer.write('>')
    
    def endTag(self,tag):
        #print("End tag  :", tag)
        if tag not in 'br img hr':
            self.Writer.write('</' + tag + '>\n')

    def UriUrl(self,_url):
        _data = None
        if urlsplit(_url).netloc:            
            _data=fetchUrl(_url)
        else:
            _data=readFile(_url,'r')
        self.feed(_data)
    
    def render_template(self,kwards:dict):
        if self.templateName:
            temData = self.Writer.render(**kwards)
            self.temFileName = self.__getFileName()
            writeFile(temData,self.temFileName ,'w')
            #print('html file is :',self.temFileName)
 
        else:
            print(dir + ': this template does not exits')

    def make_url(self,src):      
        return "https://khaliltuban.co.uk%s" % src

    def make_absolute(self,src:str):
        #return "............%s" % src
        return src

    def handle_starttag(self, tag, attrs):
        """ # process 'anchor' tag a
        self.__anchor(tag,attrs)
        """

        """ process images"""
        self.img(tag,attrs)

        """ default start Tag"""
        self.starTag(tag,attrs)

    def handle_endtag(self, tag):
        """ default endTag"""
        self.endTag(tag)      

    def handle_data(self, data):
        #pass
        self.Writer.write(data)

    def handle_comment(self, data):
        
        self.Writer.write('<!--'+ data + '-->')

    def handle_entityref(self, name):
        self.Writer.write(name)
        """
        c = chr(name2codepoint[name])
        print("Named ent:", c)
        """
    
    def handle_charref(self, name):
        self.Writer.write(name)
        """
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))

        print("Num ent  :", c)
        """

    def handle_decl(self, data:str):
        #self.outFile.write('<!DOCTYPE html>')
        self.Writer.write('<!'+data.replace('doctype', 'DOCTYPE')+'>')
    
    def handle_startendtag(self,tag, attrs):
        # print("handle_startendtag :", tag) 
        self.img(tag,attrs)
        self.starTag(tag,attrs)
    
    def unknown_decl(self,data):
        self.Writer.write('<!'+data+'>')

    def close(self):
        self.Writer.close()
        super().close()
    

        
