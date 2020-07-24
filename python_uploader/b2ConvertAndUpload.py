import os
import requests
from urllib.parse import quote
import base64
import json
import subprocess ##pip3 install subprocess32
import re
import sys
import io
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

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


def addMovieToStreama(moviename,movieyear,movieurl):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://app.fireflix.stream/login/auth")
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
    username = driver.find_element_by_xpath("//input[@placeholder='Username']")
    password = driver.find_element_by_xpath("//input[@placeholder='Password']")
    loginbutton = driver.find_element_by_xpath("//button[@class='btn btn-primary pull-right ng-binding']")
    username.send_keys("gijs")
    password.send_keys("896912666")
    loginbutton.click()
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Manage Content')]")))
    time.sleep(5)
    managerbutton = driver.find_element_by_xpath("//a[contains(text(),'Manage Content')]")
    managerbutton.click()
    time.sleep(1)
    managerbutton.click()
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//div[@class='nav']//a[contains(text(),'Movies')]")))
    time.sleep(1)
    moviebutton = driver.find_element_by_xpath("//div[@class='nav']//a[contains(text(),'Movies')]")
    moviebutton.click()
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search Movie from collection or TheMovieDB...']")))
    searchmoviefield = driver.find_element_by_xpath("//input[@placeholder='Search Movie from collection or TheMovieDB...']")
    searchmoviefield.send_keys(moviename)
    time.sleep(5)
    foundmoviereleasedate = driver.find_element_by_xpath("//div[@class='media-list similar-media']//div[1]//div[3]")
    if movieyear in foundmoviereleasedate.text:
        print("Movie year matches: " + movieyear)
        addmovieandopenbutton = driver.find_element_by_xpath("//div[@class='media-list similar-media']//div[1]//div[1]//div[1]//button[1]")
        addmovieandopenbutton.click()
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//i[@class='ion-ios-settings icon-xl dropdown-toggle']")))
        movieadddropdown = driver.find_element_by_xpath("//i[@class='ion-ios-settings icon-xl dropdown-toggle']")
        movieadddropdown.click()
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Manage Files')]")))
        managefilesbutton = driver.find_element_by_xpath("//a[contains(text(),'Manage Files')]")
        managefilesbutton.click()
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'External URL')]")))
        externalurlbutton = driver.find_element_by_xpath("//a[contains(text(),'External URL')]")
        externalurlbutton.click()
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='External URL']")))
        urltextfield = driver.find_element_by_xpath("//input[@placeholder='External URL']")
        urltextfield.send_keys(movieurl)
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//button[@class='btn btn-success btn-sm']")))
        addurlbutton = driver.find_element_by_xpath("//button[@class='btn btn-success btn-sm']")
        addurlbutton.click()
        time.sleep(5)
        driver.quit()
    else:
        print("The movie: " + moviename + ", release year: " + movieyear + " could not be found!")
        print("Please add this movie manually.")
        input("Press Enter to continue when this is done...")

def addSerieToStreama(showname, seasonnumber, episodenumber, episodeurl):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://app.fireflix.stream/login/auth")
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
    username = driver.find_element_by_xpath("//input[@placeholder='Username']")
    password = driver.find_element_by_xpath("//input[@placeholder='Password']")
    loginbutton = driver.find_element_by_xpath("//button[@class='btn btn-primary pull-right ng-binding']")
    username.send_keys("gijs")
    password.send_keys("896912666")
    loginbutton.click()
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Manage Content')]")))
    time.sleep(5)
    managerbutton = driver.find_element_by_xpath("//a[contains(text(),'Manage Content')]")
    managerbutton.click()
    time.sleep(1)
    managerbutton.click()
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search Show from collection or TheMovieDB...']")))
    searchmoviefield = driver.find_element_by_xpath("//input[@placeholder='Search Show from collection or TheMovieDB...']")
    searchmoviefield.send_keys(showname)
    time.sleep(5)
    addmovieandopenbutton = driver.find_element_by_xpath("//div[@class='media-list similar-media']//div[1]//div[1]//div[1]//button[1]")
    addmovieandopenbutton.click()
    time.sleep(2)
    fetchepisodes = driver.find_element_by_xpath("//button[@class='btn btn-primary ng-scope']")
    fetchepisodes.click()
    time.sleep(2)
    seasonnumberfield = driver.find_element_by_xpath("//input[@id='alertify-text']")
    seasonnumberfield.send_keys(seasonnumber)
    time.sleep(2)
    fetchepisodesokbutton = driver.find_element_by_xpath("//button[@id='alertify-ok']")
    fetchepisodesokbutton.click()
    time.sleep(10)
    mediacontainer = driver.find_element_by_xpath("//span[contains(text(),'"+seasonnumber+"e"+episodenumber+"')]")
    parentElement = mediacontainer.find_element_by_xpath("..")
    fullmediacontainer = parentElement.find_element_by_xpath("..")
    editbutton = fullmediacontainer.find_element_by_xpath(".//button[contains(text(),'Manage Files')]")
    editbutton.click()
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'External URL')]")))
    externalurlbutton = driver.find_element_by_xpath("//a[contains(text(),'External URL')]")
    externalurlbutton.click()
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='External URL']")))
    urltextfield = driver.find_element_by_xpath("//input[@placeholder='External URL']")
    urltextfield.send_keys(episodeurl)
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//button[@class='btn btn-success btn-sm']")))
    addurlbutton = driver.find_element_by_xpath("//button[@class='btn btn-success btn-sm']")
    addurlbutton.click()
    time.sleep(5)
    driver.quit()
    

def mainMovie():
    createFileList("sftp_hetzner:/G:/films", "data/src_movielist.txt")
    createFileList("b2:devbucket735/Movies", "data/dest_movielist.txt")
    dedupeFileLists("data/src_movielist.txt", "data/dest_movielist.txt", "data/parsedMovielist.txt")
    with open("data/parsedMovielist.txt",'r') as f:
        lines = f.readlines()
        for line in lines:
            fullpath=line.rstrip()
            oldfilepath=(line.rstrip()).split('/', 1)[-1]
            oldfilefolder=(line.rstrip()).split('/', 1)[0]
            
            filepathmp4=os.path.splitext(oldfilefolder)[0]+".mp4"
            fullfilepathmp4="\'"+"/tmp/output/"+filepathmp4+"\'"
            b2mp4path="devbucket735/Movies/"+oldfilefolder
            movieurl = "https://" + quote("cdn.fireflix.stream/file/"  + "devbucket735/Movies/"+oldfilefolder+"/"+oldfilefolder + ".mp4")

            downloadFileToTemp("sftp_hetzner:" + "\'" + "/G:/films/" + fullpath + "\'")
            proc = Run(["HandBrakeCLI","--preset-import-file","streama_handbrake.json","-Z","Streama","-i","/tmp/download/"+oldfilepath,"-o","/tmp/output/"+filepathmp4])
            Trace(proc)
            uploadToBackBlaze(fullfilepathmp4,"b2:" + "\'" + b2mp4path + "\'")
            os.remove("/tmp/download/"+oldfilepath)
            print(oldfilefolder[:-6] + oldfilefolder[-5:-1] + movieurl)
            addMovieToStreama(oldfilefolder[:-6], oldfilefolder[-5:-1], movieurl)


def mainSerie():
    createFileList("sftp_hetzner:/G:/amerikaanse series", "data/src_serielist.txt")
    createFileList("b2:devbucket735/TV", "data/dest_serielist.txt")
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

            episodeurl = "https://" + quote("cdn.fireflix.stream/file/"  + "devbucket735/TV/"+oldfilefolder+"/" + filepathmp4)
            showname = oldfilefolder.split("/", 1)[0]
            seasonnumber = ""
            if "Specials" in oldfilefolder.split("/", 1)[1]: 
                seasonnumber = "0" 
            else: 
                seasonnumber = oldfilefolder.split("/", 1)[1].split(" ", 1)[1]
            episodenumber = re.findall(r"E[0-9]+",oldfilepath)
            showname = showname.replace('(2019)', '') # fix another life show
            showname = showname.replace('(2020)', '') # fix amazing stories show

            downloadFileToTemp("sftp_hetzner:" + "\'" + "/G:/amerikaanse series/" + fullpath + "\'")
            proc = Run(["HandBrakeCLI","--preset-import-file","streama_handbrake.json","-Z","Streama","-i","/tmp/download/"+oldfilepath,"-o","/tmp/output/"+filepathmp4])
            Trace(proc)
            uploadToBackBlaze(fullfilepathmp4,"b2:" + "\'" + b2mp4path + "\'")
            os.remove("/tmp/download/"+oldfilepath)

            if len(episodenumber) > 1:
                for epnum in range(int(episodenumber[0].split("E",1)[1]), int(episodenumber[1].split("E",1)[1]) + 1):
                    addSerieToStreama(showname, seasonnumber, str(epnum), episodeurl)
            else:
                addSerieToStreama(showname, seasonnumber, episodenumber[0].split("E",1)[1], episodeurl)

mainSerie()