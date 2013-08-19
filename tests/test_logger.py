#!/usr/bin/env python
from nose.tools import assert_almost_equal, assert_equal, assert_true
from os.path import isdir,isfile
from os import listdir
import os
import sys
from testfixtures import LogCapture
import logging
from genologics.epp import EppLogger

file_path = os.path.realpath(__file__)
test_dir_path = os.path.dirname(file_path)
tmp_dir_path = test_dir_path + 'test_data/nose_tmp_output'

CWD = os.getcwd()

class TestCMD(object):
    def test_stderr(self):
        txt = "Text to check for"
        tmp_file = 'dummy'
        with EppLogger(tmp_file,level=logging.DEBUG):
            sys.stderr.write(txt)
        log = open(tmp_file,'r').read()
        # Search for red color
        assert_true(log.find('#F62217')>=0)
        
