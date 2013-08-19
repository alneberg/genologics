import logging
import sys
import os
from shutil import copy
from html import HTML

def attach_file(src,resource):
    """Attach file at src to given resource

    Copies the file to the current directory, EPP node will upload this file
    automatically if the process output is properly set up"""
    original_name = os.path.basename(src)
    new_name = resource.id + '_' + original_name
    dir = os.getcwd()
    location = os.path.join(dir,new_name)
    print "Moving {0} to {1}".format(src,location)
    copy(src,location)

def unique_check(l,msg):
    "Check that l is of length 1, otherwise raise error, with msg appended"
    if len(l)==0:
        raise Exception("No item found for {0}".format(msg))
    elif len(l)!=1:
        raise Exception("Multiple items found for {0}".format(msg))



    
class EppLogger(object):
    """Logger class that collect stdout, stderr and info. Output is in html."""

    def __enter__(self):
        pass

    def __exit__(self,exc_type,exc_val,exc_tb):
        if self.html:
            log = self.htmlify(exc_tb)
        elif exc_tb:
            pass
        else:
            log = open(self.tmp_log_file,'r').read()

        # append new log to log file
        open(self.log_file,'a').write(log)
        return False

    def __init__(self, log_file,level=logging.INFO,html=True):
        self.log_file = log_file
        self.tmp_log_file = 'tmp_' + log_file
        self.level = level
        self.html = html

        # Basic Configurations
        logging.basicConfig(
            level=self.level,
            format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
            filename=self.tmp_log_file,
            filemode='w'
            )

        # This part was copied together with the StreamToLogger class below
        stdout_logger = logging.getLogger('STDOUT')
        self.out_logger = self.StreamToLogger(stdout_logger, logging.INFO)
        sys.stdout = self.out_logger

        stderr_logger = logging.getLogger('STDERR')
        self.error_logger = self.StreamToLogger(stderr_logger, logging.ERROR)
        sys.stderr = self.error_logger

    def htmlify(self,exec_tb):
        """Turn log file into html with colour coding"""
        head_pre_style = """pre {
                      white-space: pre-wrap; /* css-3 */
                      white-space: -moz-pre-wrap !important; /* Mozilla, since 1999 */
                      white-space: -pre-wrap; /* Opera 4-6 */
                      white-space: -o-pre-wrap; /* Opera 7 */
                      word-wrap: break-word; /* Internet Explorer 5.5+ */
                      border: 1px double #cccccc;
                      background-color: #f0f8ff;
                      padding: 5px;
                   }"""
        colors= {'green':'#28DD31', 'red':'#F62217'}
        log = open(self.tmp_log_file,'r').read()
        if len(log)>0 and exec_tb:
            color = colors['red']
        else:
            color = colors['green']
        pre_style = "background-color: {0}".format(color)
        print dir(exec_tb)
        doc = HTML()
        h = doc.html
        he = h.head
        he.title("EPP script Log")
        he.style(head_pre_style,type="text/css")
        b = h.body
        b.pre(log,style=pre_style)
        return str(h)


    class StreamToLogger(object):
        """Fake file-like stream object that redirects writes to a logger instance.
        
        source: 
        http://www.electricmonk.nl/log/2011/08/14/
        redirect-stdout-and-stderr-to-a-logger-in-python/
        """
        def __init__(self, logger, log_level=logging.INFO):
            self.logger = logger
            self.log_level = log_level
            self.linebuf = ''
            
        def write(self, buf):
            for line in buf.rstrip().splitlines():
                self.logger.log(self.log_level, line.rstrip())
                
