#!/usr/bin/env python -u
#coding:utf-8


import sys, os

def fixCmd(cmd):
    '''
    fix the command for windows platform
    '''
    mswindows = (sys.platform == 'win32')

    if not mswindows:
        cmd = '{ ' + cmd + '; }'
    return cmd + " 2>&1"

def asyncExec(cmd, stop):
    '''
    execute a command that take long time
    '''
    print ("exec cmd: %s" % (cmd))

    cmd = fixCmd(cmd)
    pipe = os.popen(cmd, 'r')
    while not stop():
        line = pipe.readline()
        if line.endswith('\n'): line = line[ : -1]
        if line.endswith('\r'): line = line[ : -1]
        yield line
    print ("end yield, finish asyncExec")

def getstatusoutput(cmd, showLog = True):
    """Return (status, output) of executing cmd in a shell.
    @ref https://mail.python.org/pipermail/python-win32/2008-January/006606.html
    """
    if showLog:
        print ("exec cmd: %s" % (cmd))

    cmd = fixCmd(cmd)
    pipe = os.popen(cmd, 'r')
    text = pipe.read()
    sts = pipe.close()
    if sts is None: sts = 0
    if text[-1:] == '\n': text = text[:-1]
    return sts, text

if __name__ == "__main__":
    print __file__
