#! /usr/bin/env python
# coding=utf-8

import json
import os
import requests
import shutil
import sys
import urllib2
import zipfile

omahaproxy = "https://omahaproxy.appspot.com/deps.json?version="
chromium_directory = "chromium_apk"

def getChromiumReversion(chromium_tag):
  omahaproxy_search_url = omahaproxy + chromium_tag
  req = urllib2.Request(omahaproxy_search_url)
  handler = urllib2.urlopen(req)
  if handler.getcode() == requests.codes.ok:
    text = handler.read()
    d_text = json.loads(text)
    for k,v in d_text.items():
      if k == "chromium_base_position":
        getChromiumDownloadUrl(v)
        return
  else :
    print "获取chromium reversion失败"

def getChromiumDownloadUrl(chromium_reversion):
  media_url_server = "https://www.googleapis.com/storage/v1/b/chromium-browser-snapshots/o?delimiter=/&prefix=Android/"+str(chromium_reversion)+"/&fields=items(kind,mediaLink,metadata,name,size,updated),kind,prefixes,nextPageToken"
  req = urllib2.Request(media_url_server)
  handler = urllib2.urlopen(req)
  if handler.getcode() == requests.codes.ok:
    text = handler.read()
    d_text = json.loads(text)
    for k,v in d_text.items():
      if k == "items":
        downloadChromiumApk(v[1]["mediaLink"])
        return
  else:
    print "获取下载链接失败"

def downloadChromiumApk(download_url):
  req = urllib2.urlopen(download_url)
  chromium_zipfile_name = chromium_directory + ".zip"
  file_handle = open(chromium_zipfile_name, 'wb')
  if not file_handle:
    print "打开文件失败"

  content_meta = req.info()
  file_size = int(content_meta.getheaders("Content-Length")[0])
  print "Downloading: %s Bytes: %s " % (chromium_zipfile_name, file_size)

  file_size_dl = 0
  block_sz = 8192
  while True:
    buffer_ = req.read(block_sz)
    if not buffer_:
      break
    file_size_dl += len(buffer_)
    file_handle.write(buffer_)
    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
    status = status + chr(8)*(len(status)+1) 
    sys.stdout.write(status)
  file_handle.close()
  if file_size_dl == file_size:
    zip_ref = zipfile.ZipFile(chromium_zipfile_name, 'r')
    os.mkdir(chromium_directory)
    zip_ref.extractall(chromium_directory)
    zip_ref.close()
    os.remove(chromium_zipfile_name)
    print "下载完成 已解压至 %s" % chromium_directory
  else:
    print "下载失败"

def main():

  suffix = 1 
  global chromium_directory
  if len(sys.argv) <= 1:
    chromium_directory = raw_input("请输入要下载的版本号:")
  else:
    chromium_directory = sys.argv[1]
  while os.path.isfile(chromium_directory) or os.path.exists(chromium_directory):
    info = r"是否删除已存在的目录 %s Y:yes N:no " % chromium_directory 
    delete = raw_input(info)
    if delete == 'Y' or delete == 'y':
      if os.path.isfile(chromium_directory):
        os.remove(chromium_directory)
      else:
        shutil.rmtree(chromium_directory)
    else:
      chromium_directory = chromium_directory + "-" + str(suffix) 
      suffix += 1;
  getChromiumReversion(chromium_directory)
  return 0

if __name__ == '__main__':
  sys.exit(main())

    
