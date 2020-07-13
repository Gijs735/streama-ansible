import os
import requests
import base64
import json
import subprocess ##pip3 install subprocess32
import re
import sys
import io
import time

def Run(command):
    proc = subprocess.Popen(command,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        universal_newlines=True)
    return proc


def Trace(proc):
    while proc.poll() is None:
        line = proc.stdout.readline()
        if line:
            print(line)
            proc.stdout.flush()


def createFileList(location, filepath):
    print("Creating file list for remote: " + location)
    if not os.path.exists("data"):
        os.makedirs("data")
    
    process = subprocess.Popen(["rclone", "lsf", "--config", "rclone.conf", "-R", "--csv", "--files-only", 
    "--filter-from", "filter_file.txt", "--fast-list", "--no-traverse", location], shell=False, 
    stdout=subprocess.PIPE, cwd=os.path.dirname(os.path.realpath(__file__)))
    data = process.communicate()[0]
    string = data.decode('utf-8')
    
    f = open(filepath, "w")
    f.write(string.replace('"', ""))
    f.close()


def dedupeFileLists(file1, file2, outputfile):
    print("Deduping...")
    lower_filter_lines = list()
    with open(file2,'r+') as source:
        filter_lines = source.readlines()

    with open(file1,'r') as f:
        lines = f.readlines()
    
    for lowerline in filter_lines:
        lowerline = os.path.splitext(lowerline)[0]
        lower_filter_lines.append(lowerline.lower())

    with open(outputfile, 'w') as target:
        for line in lines:
            if os.path.splitext(line.lower())[0] not in lower_filter_lines:
                target.write(line)
    print("Created deduped file: " + outputfile + " containing content from: " + file1 + " minus the content from: " + file2)


def downloadFileToTemp(remotefilepath):
    if not os.path.exists("/tmp/download"):
        os.makedirs("/tmp/download")
    if not os.path.exists("/tmp/output"):
        os.makedirs("/tmp/output")
    print("Downloading: " + remotefilepath)
    process = subprocess.Popen(["rclone copy -P --fast-list --config rclone.conf " + remotefilepath + " /tmp/download/"], shell=True, 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.path.dirname(os.path.realpath(__file__)))
    print(process.stdout.read().decode('utf-8') + "\nDownload complete!")


def uploadToBackBlaze(convertedFile, b2path):
    print("Uploading to backblaze: " + convertedFile)
    process = subprocess.Popen(["rclone move -P --fast-list --config rclone.conf " + convertedFile + " " + b2path], shell=True, 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.path.dirname(os.path.realpath(__file__)))
    print(process.stdout.read().decode('utf-8') + "\nUpload complete!")


def mainMovie():
    # createFileList("sftp_hetzner:/G:/films", "data/src_movielist.txt")
    # createFileList("b2:devbucket735/Movies", "data/dest_movielist.txt")
    dedupeFileLists("data/src_movielist.txt", "data/dest_movielist.txt", "data/parsedMovielist.txt")
    with open("data/parsedMovielist.txt",'r') as f:
        lines = f.readlines()
        for line in lines:
            fullpath=line.rstrip()
            oldfilepath=(line.rstrip()).split('/', 1)[-1]
            oldfilefolder=(line.rstrip()).split('/', 1)[0]
            
            filepathmp4=os.path.splitext(oldfilepath)[0]+".mp4"
            fullfilepathmp4="\'"+"/tmp/output/"+filepathmp4+"\'"
            b2mp4path="devbucket735/Movies/"+oldfilefolder
            print(b2mp4path)

            # downloadFileToTemp("sftp_hetzner:" + "\'" + "/G:/films/" + fullpath + "\'")
            # proc = Run(["HandBrakeCLI","--preset-import-file","streama_handbrake.json","-Z","Streama","-i","/tmp/download/"+oldfilepath,"-o","/tmp/output/"+filepathmp4])
            # Trace(proc)
            # uploadToBackBlaze(fullfilepathmp4,"b2:" + "\'" + b2mp4path + "\'")
            # os.remove("/tmp/download/"+oldfilepath)


def mainSerie():
    # createFileList("sftp_hetzner:/G:/amerikaanse series", "data/src_serielist.txt")
    # createFileList("b2:devbucket735/TV", "data/dest_serielist.txt")
    dedupeFileLists("data/src_serielist.txt", "data/dest_serielist.txt", "data/parsedSerielist.txt")
    with open("data/parsedSerielist.txt",'r') as f:
        lines = f.readlines()
        for line in lines:
            fullpath=line.rstrip()
            oldfilepath=(line.rstrip()).split('/', 2)[-1]
            oldfilefolder=(line.rstrip()).rsplit('/', 1)[0]
            
            filepathmp4=os.path.splitext(oldfilepath)[0]+".mp4"
            fullfilepathmp4="\'"+"/tmp/output/"+filepathmp4+"\'"
            b2mp4path="devbucket735/TV/"+oldfilefolder

            downloadFileToTemp("sftp_hetzner:" + "\'" + "/G:/amerikaanse series/" + fullpath + "\'")
            proc = Run(["HandBrakeCLI","--preset-import-file","streama_handbrake.json","-Z","Streama","-i","/tmp/download/"+oldfilepath,"-o","/tmp/output/"+filepathmp4])
            Trace(proc)
            uploadToBackBlaze(fullfilepathmp4,"b2:" + "\'" + b2mp4path + "\'")
            os.remove("/tmp/download/"+oldfilepath)

mainMovie()

