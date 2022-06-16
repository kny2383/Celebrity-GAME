from selenium import webdriver
import os
import urllib.request
from selenium.webdriver.chrome.options import Options
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import cv2
import numpy as np
import time
from collections import OrderedDict

chrome_options = Options()
chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9150")

# haarcascade 불러오기
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

header_n = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

# 사진 이름 인덱스용 전역변수
global imgNum
imgNum = 0

WikiList = []

## 네이버 뉴스 연예 기사 크롤링함수
def newsCrawling():
    url = 'https://entertain.naver.com/home'
    r = requests.get(url)
    html = r.content
    soup = BeautifulSoup(html, 'html.parser')
    title_area = soup.select('.title_area > a')
    txt_area = soup.select('.txt_area > a')

    # news.txt에 기사 제목 저장
    f = open("news.txt", 'w', encoding='UTF-8')
    for i in range(len(title_area)): #'.title_area > a'
        f.write(title_area[i].text)
    for j in range(len(txt_area)): #'.txt_area > a'
         f.write(txt_area[j].text)
    f.close()

## 위키백과 연예인 목록 크롤링함수
def wikiListCrawling():

    # 위키백과 연예인 목록 주소(크롤링 할 주소)
    urlArray = [
                ## 남자 배우
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EB%82%A8%EC%9E%90_%EB%B0%B0%EC%9A%B0&pagefrom=%EA%B9%80%EC%83%81%ED%98%B8+%28%EB%B0%B0%EC%9A%B0%29#mw-pages",
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EB%82%A8%EC%9E%90_%EB%B0%B0%EC%9A%B0&pagefrom=%EB%8F%99%EC%9C%A4%EC%84%9D#mw-pages",
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EB%82%A8%EC%9E%90_%EB%B0%B0%EC%9A%B0&pagefrom=%EC%84%9C%EC%98%81%EC%A3%BC#mw-pages",
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EB%82%A8%EC%9E%90_%EB%B0%B0%EC%9A%B0&pagefrom=%EC%98%A4%EC%84%B1%EC%97%B4#mw-pages",
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EB%82%A8%EC%9E%90_%EB%B0%B0%EC%9A%B0&pagefrom=%EC%9D%B4%EC%8A%B9%EC%9D%BC+%28%EB%B0%B0%EC%9A%B0%29#mw-pages",
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EB%82%A8%EC%9E%90_%EB%B0%B0%EC%9A%B0&pagefrom=%EC%A0%84%EB%B3%91%EC%9A%B1+%28%EB%B0%B0%EC%9A%B0%29#mw-pages",
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EB%82%A8%EC%9E%90_%EB%B0%B0%EC%9A%B0&pagefrom=%EC%B5%9C%EA%B1%B4%EC%9A%B0#mw-pages",
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EB%82%A8%EC%9E%90_%EB%B0%B0%EC%9A%B0&pagefrom=%ED%99%A9%EB%A7%8C%EC%9D%B5#mw-pages",
                ## 여자 배우
                "https://ko.wikipedia.org/wiki/%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EC%97%AC%EC%9E%90_%EB%B0%B0%EC%9A%B0",
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EC%97%AC%EC%9E%90_%EB%B0%B0%EC%9A%B0&pagefrom=%EA%B9%80%EC%9D%B4%EC%A7%80#mw-pages",
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EC%97%AC%EC%9E%90_%EB%B0%B0%EC%9A%B0&pagefrom=%EB%B0%95%ED%95%9C%EB%B3%84#mw-pages",
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EC%97%AC%EC%9E%90_%EB%B0%B0%EC%9A%B0&pagefrom=%EC%96%91%ED%98%84%EC%98%81#mw-pages",
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EC%97%AC%EC%9E%90_%EB%B0%B0%EC%9A%B0&pagefrom=%EC%9D%B4%EC%8B%9C%EC%9A%B0+%281997%EB%85%84%29#mw-pages",
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EC%97%AC%EC%9E%90_%EB%B0%B0%EC%9A%B0&pagefrom=%EC%A0%95%EC%88%98%EC%A7%80#mw-pages",
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EC%97%AC%EC%9E%90_%EB%B0%B0%EC%9A%B0&pagefrom=%ED%95%9C%EB%8B%A4%EC%9D%80#mw-pages",
                ## 아이돌
                "https://ko.wikipedia.org/wiki/%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EC%95%84%EC%9D%B4%EB%8F%8C",
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EC%95%84%EC%9D%B4%EB%8F%8C&pagefrom=%EC%84%B1%EB%AF%BC+%281986%EB%85%84%29#mw-pages",
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EC%95%84%EC%9D%B4%EB%8F%8C&pagefrom=%EC%A1%B0%EC%8B%9C%EC%9C%A4#mw-pages",
                ## 남자 희극인
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EB%82%A8%EC%9E%90_%ED%9D%AC%EA%B7%B9%EC%9D%B8&pageuntil=%EC%9D%B4%ED%98%81%EC%9E%AC#mw-pages",
                "https://ko.wikipedia.org/w/index.php?title=%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EB%82%A8%EC%9E%90_%ED%9D%AC%EA%B7%B9%EC%9D%B8&pagefrom=%EC%9D%B4%ED%98%81%EC%9E%AC#mw-pages",
                ## 여자 희극인
                "https://ko.wikipedia.org/wiki/%EB%B6%84%EB%A5%98:%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD%EC%9D%98_%EC%97%AC%EC%9E%90_%ED%9D%AC%EA%B7%B9%EC%9D%B8"
    ]

    for t in range(0,20):
        html = urlopen(f"{urlArray[t]}")
        bsObject = BeautifulSoup(html, "html.parser")  # html 정보 가져오기
        li_code = bsObject.select('div.mw-category-group>ul>li')

        for c in range(0, len(li_code) - 1):
            WikiList.append(li_code[c].get_text())
        Artist = ',\n'.join(WikiList)

        # Artist.txt에 위키백과 크롤링 한 것 저장
        f = open("Artist.txt", 'w', encoding='UTF-8')
        f.write(Artist)
        f.close()

## 구글 자동 검색화 + 크롤링 + 얼굴 인식 -> 사진 가공 과정
def photo_processing(keywords):

    options = webdriver.ChromeOptions() # 옵션 생성
    options.add_argument("headless") # 창 숨기는 옵션 추가

    ### 구글 자동 검색
    path = "https://www.google.com/search?q=" + keywords + "&newwindow=1&rlz=1C1CAFC_enKR908KR909&sxsrf=ALeKk01k_BlEDFe_0Pv51JmAEBgk0mT4SA:1600412339309&source=lnms&tbm=isch&sa=X&ved=2ahUKEwj07OnHkPLrAhUiyosBHZvSBIUQ_AUoAXoECA4QAw&biw=1536&bih=754"
    driver = webdriver.Chrome('./chromedriver',options=options)
    driver.get(path)

    global imgNum
    counter = 0
    succounter = 0

    # data 디렉토리 없으면 만들기
    if not os.path.exists('MainData'):
        os.mkdir('MainData')

    ### 이미지 크롤링
    for x in driver.find_elements_by_class_name('rg_i.Q4LuWd'):
        counter += 1
        # 이미지 url
        img = x.get_attribute("data-src")
        if img is None:
            img = x.get_attribute("src")
        # 이미지 확장자
        imgtype = 'jpg'

        # 구글 이미지를 읽고 저장한다.
        raw_img = urllib.request.urlopen(img).read()
        File = open(os.path.join('MainData/', keywords + "_" + str(counter) + "." + imgtype), "wb")
        File.write(raw_img)
        File.close()

        ### 얼굴인식 코드 시작 ### -> 배기원님 파트
        # path = 'MainData/' + keywords + "_" + str(counter) + "." + imgtype
        #
        # img_array = np.fromfile(path, np.uint8)  # 컴퓨터가 읽을수 있게 넘파이로 변환
        # decode_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  # 이미지를 읽어옴
        #
        # # 얼굴인식 후 튜플로 저장
        # faces = face_cascade.detectMultiScale(decode_img, 1.3, 5)
        # if len(faces) == 1:  # 성공적 인식
        #     for (x, y, w, h) in faces:
        #         cropped_img = decode_img[y - int(h / 4):y + h + int(h / 1),
        #                       x - int(w / 4):x + w + int(w / 4)]  # 상:하, 좌:우
        #
        #         # 자른 이미지 크기 조정: (400, 500)
        #         try:
        #             resized_img = cv2.resize(cropped_img, dsize=(400, 500), interpolation=cv2.INTER_CUBIC)
        #             # 위 사이즈 코드에서 예외 발생시 except로 이동
        #             succounter = succounter + 1
        #             imgNum = imgNum + 1
        #
        #         except:
        #             print("!resize error!\n")  # 오류 확인용 문구 출력
        #             break
        #
        #         extension = os.path.splitext(str(imgNum) + "." + imgtype)[1]
        #
        #         # 자른 사진 저장
        #         result, encoded_img = cv2.imencode(extension, resized_img)
        #
        #         if result:
        #             with open('MainData/' + str(imgNum) + "." + imgtype, mode='w+b') as f:
        #                 encoded_img.tofile(f)
        #
        #     os.remove('MainData/' + keywords + "_" + str(counter) + "." + imgtype)  # 사용한 사진은 삭제
        #     break
        #
        # else:  # 다중인식
        #     # print("얼굴 다중인식\n")
        #
        #     if counter == 3:  # 만약 해당 연예인의 마지막 사진이 다중인식 처리될 경우
        #
        #         # 자르지 않고 원본 그대로 저장
        #         imgNum = imgNum + 1
        #         succounter = succounter + 1
        #         print(imgNum, "번: 원본 저장됨")  # 확인문구 출력
        #
        #         try:
        #             resized_img = cv2.resize(decode_img, dsize=(400, 500), interpolation=cv2.INTER_CUBIC)
        #             # 위 사이즈 코드에서 예외 발생시 except로 이동
        #
        #             extension = os.path.splitext(str(imgNum) + "." + imgtype)[1]
        #
        #             # 자른 사진 저장
        #             result, encoded_img = cv2.imencode(extension, resized_img)
        #
        #             if result:
        #                 with open('MainData/' + str(imgNum) + "." + imgtype, mode='w+b') as f:
        #                     encoded_img.tofile(f)
        #
        #             os.remove('MainData/' + keywords + "_" + str(counter) + "." + imgtype)  # 사용한 사진은 삭제
        #
        #         except:
        #             print("!resize error:강제진행!\n")  # 오류 확인용 문구 출력
        #
        #             extension = os.path.splitext(str(imgNum) + "." + imgtype)[1]
        #             result, encoded_img = cv2.imencode(extension, decode_img)
        #
        #             if result:
        #                 with open('MainData/' + str(imgNum) + "." + imgtype, mode='w+b') as f:
        #                     encoded_img.tofile(f)
        #
        #             os.remove('MainData/' + keywords + "_" + str(counter) + "." + imgtype)
        #
        #     else:
        #         os.remove('MainData/' + keywords + "_" + str(counter) + "." + imgtype)  # 사용한 사진은 삭제

        if counter == 3:
            break

    print(succounter, "succesfully downloaded")
    driver.close()


## 트렌드를 반영한 연예인 이름 불러오기
def check_string():
    BefoList = [0] * (len(WikiList)-1) # 중복 제거 전 연예인 리스트
    fw = open('befoList.txt', 'w', encoding='UTF-8')
    with open('news.txt',encoding='UTF-8') as temp_f:
        datafile = temp_f.readlines()
    for line in datafile:
        for i in range(0,len(WikiList)-1):
            if WikiList[i] in line:
                BefoList[i] = WikiList[i]
                fw.write(BefoList[i])
                fw.write('\n')
                global finalList  # befoList에서 중복 이름을 제거 후 리스트
                finalList = []
                finalList = list(OrderedDict.fromkeys(BefoList)) # 중복 제거
                with open('finalList.txt', 'w', encoding='UTF-8') as f:
                    f.write('시작\n')
                    for name in finalList[1:]:
                        f.write(name + '\n')

## 사진 가공 실행 함수
def crawling() :
    with open("finalList.txt", 'r', encoding='UTF-8') as f:
        lines = f.read().splitlines()
    for i in range(1,15):
        photo_processing(f"{lines[i]}")  # finalList에 있는 이름들을 읽어와서 crawling