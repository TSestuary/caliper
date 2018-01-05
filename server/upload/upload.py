# -*- coding: utf-8 -*-

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import logging
import hashlib
import urllib2
import shutil
import os
import sys
import subprocess
from caliper.server.shared import caliper_path
from caliper.server.shared.caliper_path import folder_ope as Folder

def upload_result(dirpath,server_url, server_user, server_password):
    '''
    upload result to server
    :param target: target machine running test
    :return: None
    '''

    #dir path for score, for example: /home/fanxh/caliper_output/frontend/frontend/data_files/Normalised_Logs
    dir_score_path = Folder.yaml_dir

    target_name = caliper_path.platForm_name
    #score json file name , for example:hansanyang-OptiPlex-3020_score_post.json
    score_json_file_name = target_name + '_score_post.json'

    #for example, /home/fanxh/caliper_output/frontend/frontend/data_files/Normalised_Logs/hansanyang-OptiPlex-3020_score_post.json
    score_json_file_fullname = os.path.join(dir_score_path,score_json_file_name)

    upload_and_savedb(dirpath,score_json_file_fullname,server_url, server_user, server_password)


def upload_and_savedb(dirpath,json_path_source,server_url, server_user, server_password):
    # tar file
    bin_file = os.path.exists(os.path.join(dirpath,"binary"))
    if bin_file:
        shutil.rmtree(os.path.join(dirpath,"binary"))
    json_file = os.path.join(dirpath,"output", "results", "json")
    config_json = os.path.join(json_file, 'hardwareinfo.json')
    json_path=os.path.join(dirpath,os.path.basename(json_path_source))
    shutil.copyfile(json_path_source,json_path)
    output_file=dirpath+".zip"
    json_output_file = dirpath+"_json.zip"
    if not os.path.exists(config_json):
        logging.info('no config_output.json file, please run hardwareinfo benchmark and upload again.')
        sys.exit()


    # upload
    register_openers()
    login_upload = urllib2.Request('http://%s/data/cert?userName=%s&password=%s' % (server_url, server_user, server_password))
    response = urllib2.urlopen(login_upload).read()
    logging.info(response)
    if response != 'success':
        logging.info('UAMS fail,please check your username and password')
        sys.exit()

    encryption(json_file, json_output_file, server_password)
    # # remove json dir
    shutil.copytree(json_file, os.path.join('/tmp', 'json'))
    shutil.rmtree(json_file)
    encryption(dirpath, output_file, server_password)
    shutil.copytree(os.path.join('/tmp', 'json'), json_file)
    shutil.rmtree(os.path.join('/tmp', 'json'))
    hash_output = calcHash(output_file)
    hash_log = calcHash(json_output_file)
    json_data = open(json_path, 'r')
    json_data = json_data.read()
    params = [
        ("output", open(output_file, 'rb')),
        ("log", open(json_output_file, 'rb')),
        ("username", server_user),
        ("result", json_data),
        ("hash_output", hash_output),
        ("hash_log", hash_log),
    ]
    datagen, headers = multipart_encode(params)
    request = urllib2.Request('http://%s/data/upload' % server_url,datagen, headers)
    response = urllib2.urlopen(request).read()
    logging.info(response)

def calcHash(filepath):
    '''
    计算文件的hash 值
    :param filepath:
    :return:
    '''
    with open(filepath, 'rb') as f:
        sha1obj = hashlib.sha1()
        sha1obj.update(f.read())
        hash = sha1obj.hexdigest()
    return hash

def encryption(inputpath, outpath, password):
    subprocess.call("cd %s && zip -rP %s %s %s" % (inputpath, '123', outpath, '*'), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    shell=True)  # 加密包


# example
#dirpath = "C:\\Users\\yangtt\\Desktop\\fanxh-OptiPlex-3020_WS_17-08-07_11-03-46"
# dirpath = caliper_path.workspace;
#json_path_source="C:\\Users\\yangtt\\Desktop\\Normalised_Logs\\ts-OptiPlex-3020_score_post.json"
# json_path_source = caliper_path.HTML_DATA_DIR_OUTPUT
# upload_and_savedb(dirpath,json_path_source)
