import shutil
import time

import cv2
import glob
import os
import imutils as imutils
import pytesseract
import requests
import win32gui
from PIL import Image, ImageOps
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt
from pywinauto.application import Application
import pyautogui




# app = Application(backend="uia").connect(process=21476)
# win = app.window(title='理財寶籌碼k線1.20.0901.2(正式版)')
# win.child_window(title="2108", control_type="Edit")
# print(win.window(control_type="Edit").print_control_identifiers())
# # print(app.window(title='理財寶籌碼k線1.20.0901.2(正式版)').print_control_identifiers())


# ========================================================================================

# hwnd_title = dict()
#
#
# def get_all_hwnd(hwnd, mouse):
#     if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
#         hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})
#
#
# win32gui.EnumWindows(get_all_hwnd, 0)
#
# for h, t in hwnd_title.items():
#     if t is not "":
#         print(h, t)

# ========================================================================================

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#
# headers = {
#     'Host': 'bsr.twse.com.tw',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
# }
#
# cookies = {}

# session = requests.Session()
#
# resp = session.get('https://bsr.twse.com.tw/bshtm/bsMenu.aspx', headers=headers)
#
# for key, value in resp.cookies.items():
#     cookies[key] = value
#
# soup = BeautifulSoup(resp.text, 'html.parser')
# captcha = soup.select('img')[1]['src'].split('=')[1]
# __VIEWSTATE = soup.find('input', id='__VIEWSTATE')['value']
# __VIEWSTATEGENERATOR = soup.find('input', id='__VIEWSTATEGENERATOR')['value']
# __EVENTVALIDATION = soup.find('input', id='__EVENTVALIDATION')['value']
#
# img = session.get(f'https://bsr.twse.com.tw/bshtm/CaptchaImage.aspx?guid={captcha}', headers=headers, cookies=cookies,
#                   stream=True)
#
# img.raw.decode_content = True
#
# with open('captcha.png', 'wb') as f:
#     shutil.copyfileobj(img.raw, f)
#
# f.close()


# img = cv2.imread(r"D:\free\captcha.PNG")
# kerenl = np.ones((4, 4), np.uint8)
# canny = cv2.Canny(
#     cv2.GaussianBlur(
#         cv2.erode(img, kerenl, iterations=1), (5, 5), 0
#     ),
#     30,
#     150
# )
#
# dilate = cv2.dilate(canny, kerenl, iterations=1)
#
# contours, hierarchy = cv2.findContours(dilate.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# cnts = sorted([(c, cv2.boundingRect(c)[0]) for c in contours], key=lambda x: x[1])
#
# ary = []
# for (c, _) in cnts:
#     (x, y, w, h) = cv2.boundingRect(c)
#     if w > 15 and h > 15:
#         ary.append((x, y, w, h))
#
# for id, (x, y, w, h) in enumerate(ary):
#     roi = dilate[y:y + h, x:x + w]
#     cv2.imwrite(f"D:\\free\\tt\\captcha_{id}.png", cv2.resize(roi.copy(), (50, 50)))
#
#
# def mse(m1, m2):
#     err = np.sum((m1.astype('float') - m2.astype('float')) ** 2)
#     err /= float(m1.shape[0] * m1.shape[1])
#     return err
#
#
# texts = {}
#
# for path in glob.glob(f"D:\\free\\te\\*.png"):
#     texts[os.path.basename(path).split('.')[0]] = cv2.imread(path)
#
#
# def get(t):
#     m = 9999999999
#     text = None
#     for name, img in texts.items():
#         if mse(img, t) < m:
#             m = mse(t, img)
#             text = name
#     return text, m
#
#
# t1 = cv2.imread('captcha_0.png')
# t2 = cv2.imread('captcha_1.png')
# t3 = cv2.imread('captcha_2.png')
# t4 = cv2.imread('captcha_3.png')
# t5 = cv2.imread('captcha_4.png')
#
#
# pytesseract.image_to_string(Image.open('captcha_0.png'))
#
# print(get(t1))
# print(get(t2))
# print(get(t3))
# print(get(t4))
# print(get(t5))

pass
