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

def getAudioLanguage(file):
    cmnd = ['ffprobe', file, '-show_entries', 'stream=index:stream_tags=language', '-select_streams', 'a', '-v', '0', '-of', 'compact=p=0:nk=1']
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out =  p.communicate()[0]
    out = (out.decode('utf-8'))
    return out

def AutoSelectSubNeeded(file):
    file="\""+file+"\""
    if not "eng" in getAudioLanguage(file) or ("jpn" in getAudioLanguage(file) and "eng" in getAudioLanguage(file)):
        print("English audio not detected in: " + file)
        print("Enter 'y/Y' if the video is in english, enter 'n/N' if it is in another language or is dual language:")
        userinput = input()
        if userinput == "y" or userinput == "Y":
            return False
        elif userinput == "n" or userinput == "N":
            return True
        else:
            return AutoSelectSubNeeded(file)
    else:
        return False

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


def dedupeFileLists(file1, file2, outputfile, movie = False):
    print("Deduping...")
    lower_filter_lines = list()
    with open(file2,'r+') as source:
        filter_lines = source.readlines()

    with open(file1,'r') as f:
        lines = f.readlines()
    
    for lowerline in filter_lines:
        lowerline = os.path.splitext(lowerline)[0]
        if movie == True:
            lowerline = lowerline.split("/", 1)[0]
        lower_filter_lines.append(lowerline.lower())
    if movie == False:
        with open(outputfile, 'w') as target:
            for line in lines:
                if os.path.splitext(line.lower())[0] not in lower_filter_lines:
                    target.write(line)
    else:
        with open(outputfile, 'w') as target:
            for line in lines:
                lineinlowercase = os.path.splitext(line.lower())[0]
                if lineinlowercase.split("/", 1)[0] not in lower_filter_lines:
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
    chrome_options.add_argument("--no-sandbox")
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
        time.sleep(5)
        addmovieandopenbutton.click()
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//i[@class='ion-ios-settings icon-xl dropdown-toggle']")))
        time.sleep(5)
        movieadddropdown = driver.find_element_by_xpath("//i[@class='ion-ios-settings icon-xl dropdown-toggle']")
        movieadddropdown.click()
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Manage Files')]")))
        time.sleep(5)
        managefilesbutton = driver.find_element_by_xpath("//a[contains(text(),'Manage Files')]")
        managefilesbutton.click()
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'External URL')]")))
        time.sleep(5)
        externalurlbutton = driver.find_element_by_xpath("//a[contains(text(),'External URL')]")
        externalurlbutton.click()
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='External URL']")))
        time.sleep(5)
        urltextfield = driver.find_element_by_xpath("//input[@placeholder='External URL']")
        urltextfield.send_keys(movieurl)
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//button[@class='btn btn-success btn-sm']")))
        time.sleep(5)
        addurlbutton = driver.find_element_by_xpath("//button[@class='btn btn-success btn-sm']")
        addurlbutton.click()
        time.sleep(5)
        driver.quit()
    else:
        print("The movie: " + moviename + ", release year: " + movieyear + " could not be found!")
        print("Please add this movie manually.")
        print("URL: " + movieurl)
        input("Press Enter to continue when this is done...")
        driver.quit()

def addSerieToStreama(showname, seasonnumber, episodenumber, episodeurl):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
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
    time.sleep(2)
    managerbutton.click()
    time.sleep(1)
    managerbutton.click()
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search Show from collection or TheMovieDB...']")))
    searchmoviefield = driver.find_element_by_xpath("//input[@placeholder='Search Show from collection or TheMovieDB...']")
    time.sleep(2)
    searchmoviefield.send_keys(showname)
    time.sleep(5)
    addmovieandopenbutton = driver.find_element_by_xpath("//div[@class='media-list similar-media']//div[1]//div[1]//div[1]//button[1]")
    addmovieandopenbutton.click()
    time.sleep(2)
    fetchepisodes = driver.find_element_by_xpath("//button[@class='btn btn-primary ng-scope']")
    time.sleep(2)
    fetchepisodes.click()
    time.sleep(2)
    seasonnumberfield = driver.find_element_by_xpath("//input[@id='alertify-text']")
    seasonnumberfield.send_keys(seasonnumber)
    time.sleep(2)
    fetchepisodesokbutton = driver.find_element_by_xpath("//button[@id='alertify-ok']")
    time.sleep(2)
    fetchepisodesokbutton.click()
    time.sleep(10)
    mediacontainer = driver.find_element_by_xpath("//span[contains(text(),'"+seasonnumber+"e"+episodenumber+"')]")
    time.sleep(2)
    parentElement = mediacontainer.find_element_by_xpath("..")
    fullmediacontainer = parentElement.find_element_by_xpath("..")
    editbutton = fullmediacontainer.find_element_by_xpath(".//button[contains(text(),'Manage Files')]")
    time.sleep(2)
    editbutton.click()
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'External URL')]")))
    time.sleep(5)
    externalurlbutton = driver.find_element_by_xpath("//a[contains(text(),'External URL')]")
    time.sleep(2)
    externalurlbutton.click()
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='External URL']")))
    time.sleep(5)
    urltextfield = driver.find_element_by_xpath("//input[@placeholder='External URL']")
    urltextfield.send_keys(episodeurl)
    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//button[@class='btn btn-success btn-sm']")))
    time.sleep(5)
    addurlbutton = driver.find_element_by_xpath("//button[@class='btn btn-success btn-sm']")
    time.sleep(2)
    addurlbutton.click()
    time.sleep(5)
    driver.quit()
    

def mainMovie():
    createFileList("sftp_hetzner:/G:/films", "data/src_movielist.txt")
    createFileList("b2:devbucket735/Movies", "data/dest_movielist.txt")
    dedupeFileLists("data/src_movielist.txt", "data/dest_movielist.txt", "data/parsedMovielist.txt", True)
    with open("data/parsedMovielist.txt",'r') as f:
        lines = reversed(f.readlines())
        for line in lines:
            fullpath=line.rstrip()
            oldfilepath=(line.rstrip()).split('/', 1)[-1]
            oldfilefolder=(line.rstrip()).split('/', 1)[0]
            
            filepathmp4=os.path.splitext(oldfilefolder)[0]+".mp4"
            fullfilepathmp4="\""+"/tmp/output/"+filepathmp4+"\""
            b2mp4path="devbucket735/Movies/"+oldfilefolder
            movieurl = "https://" + quote("cdn.fireflix.stream/file/"  + "devbucket735/Movies/"+oldfilefolder+"/"+oldfilefolder + ".mp4")
            fullpath=fullpath.replace("$", "\\$") #fix dollar sign bug
            oldfilepath=oldfilepath.replace("$", "\\$") #fix dollar sign bug

            downloadFileToTemp("sftp_hetzner:" + "\"" + "/G:/films/" + fullpath + "\"")
            if AutoSelectSubNeeded("/tmp/download/"+oldfilepath) == False:
                proc = Run(["flatpak","run","--filesystem=/tmp","--filesystem=/root","--command=HandBrakeCLI","fr.handbrake.ghb","--preset-import-file","streama_handbrake.json","-Z","Streama","-i","/tmp/download/"+oldfilepath,"-o","/tmp/output/"+filepathmp4])
            else:
                proc = Run(["flatpak","run","--filesystem=/tmp","--filesystem=/root","--command=HandBrakeCLI","fr.handbrake.ghb","--preset-import-file","streama_subs.json","-Z","Streama_subs","-i","/tmp/download/"+oldfilepath,"-o","/tmp/output/"+filepathmp4])
            Trace(proc)
            uploadToBackBlaze(fullfilepathmp4,"b2:" + "\"" + b2mp4path + "\"")
            os.remove("/tmp/download/"+oldfilepath)
            addMovieToStreama(oldfilefolder[:-6], oldfilefolder[-5:-1], movieurl)


def mainSerie():
    createFileList("sftp_hetzner:/G:/amerikaanse series", "data/src_serielist.txt")
    createFileList("b2:devbucket735/TV", "data/dest_serielist.txt")
    dedupeFileLists("data/src_serielist.txt", "data/dest_serielist.txt", "data/parsedSerielist.txt")
    with open("data/parsedSerielist.txt",'r') as f:
        lines = reversed(f.readlines())
        for line in lines:
            fullpath=line.rstrip()
            oldfilepath=(line.rstrip()).split('/', 2)[-1]
            oldfilefolder=(line.rstrip()).rsplit('/', 1)[0]
            fullpath=fullpath.replace("$", "\\$") #fix dollar sign bug
            oldfilepath=oldfilepath.replace("$", "\\$") #fix dollar sign bug
            
            filepathmp4=os.path.splitext(oldfilepath)[0]+".mp4"
            fullfilepathmp4="\""+"/tmp/output/"+filepathmp4+"\""
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

            downloadFileToTemp("sftp_hetzner:" + "\"" + "/G:/amerikaanse series/" + fullpath + "\"")
            if AutoSelectSubNeeded("/tmp/download/"+oldfilepath) == False:
                proc = Run(["flatpak","run","--filesystem=/tmp","--filesystem=/root","--command=HandBrakeCLI","fr.handbrake.ghb","--preset-import-file","streama_handbrake.json","-Z","Streama","-i","\"/tmp/download/"+oldfilepath+"\"","-o","\"/tmp/output/"+filepathmp4+"\""])
            else:
                proc = Run(["flatpak","run","--filesystem=/tmp","--filesystem=/root","--command=HandBrakeCLI","fr.handbrake.ghb","--preset-import-file","streama_subs.json","-Z","Streama_subs","-i","\"/tmp/download/"+oldfilepath+"\"","-o","\"/tmp/output/"+filepathmp4+"\""])
            Trace(proc)
            uploadToBackBlaze(fullfilepathmp4,"b2:" + "\"" + b2mp4path + "\"")
            os.remove("\"/tmp/download/"+oldfilepath+"\"")

            if len(episodenumber) > 1:
                for epnum in range(int(episodenumber[0].split("E",1)[1]), int(episodenumber[1].split("E",1)[1]) + 1):
                    addSerieToStreama(showname, seasonnumber, str(epnum), episodeurl)
            else:
                addSerieToStreama(showname, seasonnumber, episodenumber[0].split("E",1)[1], episodeurl)

mainSerie()


## pip3 install selenium
## pip3 install subprocess32
## pip3 install --upgrade setuptools

## sudo add-apt-repository ppa:alexlarsson/flatpak
## sudo apt install policykit-1
## sudo apt update
## sudo apt install flatpak
## flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
## flatpak --user install https://flathub.org/repo/appstream/fr.handbrake.ghb.flatpakref

## curl https://rclone.org/install.sh | sudo bash
## https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/
## sudo apt install ffmpeg (ffprobe)
## Firewall IP
