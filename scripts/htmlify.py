#!/usr/bin/env python
from genologics.epp import EppLogger
import sys

def main():
    tmp_file = 'dummy'
    with EppLogger(tmp_file):
        sys.stderr.write('Hej!')
        raise Exception

if __name__=='__main__':
    main()
