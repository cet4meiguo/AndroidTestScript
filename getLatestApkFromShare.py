# !/usr/bin/env python -u
# coding=utf-8

import os
import shutil
import sys
import time

UNITY_COMMAND="/Applications/Unity/Unity.app/Contents/MacOS/Unity"
SHARE_SERVER_IP = "192.168.1.3"
PRODUCT_OUTPUT_PATH = os.path.join(os.path.expanduser("~"), "livedemo")

def _fix_cmd(cmd):
    '''
    fix the command for windows platform
    '''
    mswindows = (sys.platform == 'win32')

    if not mswindows:
        cmd = '{ ' + cmd + '; }'
    return cmd + " 2>&1"

def _exec_cmd(cmd):
    print("exec:"+cmd)
    fixed_cmd = _fix_cmd(cmd)
    pipe = os.popen(fixed_cmd)
    text = pipe.read()
    stat = pipe.close()
    if stat is not None:
        print (text)
        raise Exception( "execute <" + cmd + "> failed. errorCode: " + str(stat) )
    return text

def _get_project_path():
    return os.path.dirname(os.path.realpath(__file__))

def _delete_file_or_folder(fpath):
    '''
    删除指定的文件或者文件夹
    '''
    if os.path.exists(fpath):
        if os.path.isfile(fpath):
            os.remove(fpath)
        elif os.path.isdir(fpath):
            shutil.rmtree(fpath)

def _make_if_not_exists(fpath):
    if not os.path.exists(fpath):
        os.makedirs(fpath)

def get_latest_folder(src_local_path, folder_type):
    '''
        @param src_local_path: mount in local avroom sdk path
        @folder_type: the value is one of in ('android', 'ios')
    '''
    folders = os.listdir(src_local_path)
    latest_date = 0
    latest_time = 0
    found_folder_name = ""
    for folder_name in folders:
        sdk_path = os.path.join(src_local_path, folder_name, folder_type)
        # 检查文件夹下是否存在指定的 folder_type 目录
        if not os.path.exists(sdk_path): continue

        try:
            date, time = [int(item) for item in folder_name.split("_")[ : 2]]
            if date > latest_date:
                latest_date = date
                latest_time = time
                found_folder_name = folder_name
            elif date == latest_date:
                if time > latest_time:
                    latest_time = time
                    found_folder_name = folder_name
            else: pass
        except:
            pass

    return found_folder_name

def _unzip_android_libs(libs_folder, target_folder):
    libs_zip_file = None
    for fname in os.listdir(libs_folder):
        if fname.startswith("zegokit_libs_unity_"):
            libs_zip_file = os.path.join(libs_folder, fname)
            break

    if libs_zip_file is None:
        raise Exception("not found android libs")

    _delete_file_or_folder(target_folder)

    unzip_cmd = "unzip -d {0} {1}".format(target_folder, libs_zip_file)
    _exec_cmd(unzip_cmd)


def mount_share_folder(remote_folder_name):
    def _mount(remote_folder_name, local_path):
        mount_cmd = "mount -t smbfs //share:share%40zego@{0}/share/{1} {2}".format(SHARE_SERVER_IP, remote_folder_name, local_path)
        _exec_cmd(mount_cmd)

    def _umount(local_path):
        _umount_cmd = "umount -f {0}".format(local_path)
        try:
            _exec_cmd(_umount_cmd)
        except Exception, e:
            pass

    print ("mount remote //{0}/share/{1} folder".format(SHARE_SERVER_IP, remote_folder_name))
    _folder_local_name = "_tmp_mount_share_" + remote_folder_name
    share_local_path = os.path.join(_get_project_path(), _folder_local_name)
    if os.path.exists(share_local_path):
        _umount(share_local_path)
        _delete_file_or_folder(share_local_path)

    _make_if_not_exists(share_local_path)
    _mount(remote_folder_name, share_local_path)

    return share_local_path

def umount_share_folder(local_path):
    print ("unmount folder: " + local_path)
    _umount_cmd = "umount -f {0}".format(local_path)
    _exec_cmd(_umount_cmd)
    _delete_file_or_folder(local_path)

def _exception_if_not_exists(fpath):
    '''
    检查文件或者文件夹是否存在
    '''
    if not os.path.exists(fpath):
        raise Exception(fpath + " not exists")

def _copy_some_to_folder(src_list, target_folder):
    _make_if_not_exists(target_folder)
    print(src_list)

    for p in src_list:
        _exception_if_not_exists(p)

        target = os.path.join(target_folder, os.path.basename(p))
        if os.path.isdir(p):
            print ("copy {0} to {1}".format(p, target))
            shutil.copytree(p, target)
        elif os.path.isfile(p):
            print ("copy {0} to {1}".format(p, target))
            shutil.copyfile(p, target)
        else:
            print ("{0} isn't file or directory. ignore ...".format(p))

def get_latest_apk_from_share():
    folder_type="android"
    local_folder_path=mount_share_folder("zego_demo")
    # print("local_folder_path="+local_folder_path)
    latest_folder_name=get_latest_folder(os.path.join(local_folder_path,"livedemo5_master"),folder_type)
    # print("latest_folder_name="+latest_folder_name)

    latest_folder_path = os.path.join(local_folder_path,"livedemo5_master",latest_folder_name, folder_type)
    # print("latest_folder_path="+latest_folder_path)

    copyFile=os.path.join(latest_folder_path,"LiveDemo5-udp.apk")
    # print("cpoyFile="+copyFile)
    shutil.copy(copyFile,".")
    
    umount_share_folder(local_folder_path)


if __name__=="__main__":
	print("getLatestApkFromShare")
	get_latest_apk_from_share()

