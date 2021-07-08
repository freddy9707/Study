#-*- coding: utf-8 -*-
import time
import win32api
import win32con
import win32gui
from ctypes import windll
import threading
import numpy as np
import cv2
import keyboard
from PIL import ImageGrab
import PIL.Image as pilimg

# Win32 API : http://docs.activestate.com/activepython/2.4/pywin32/win32api.html
# Virtual-Key Codes : https://docs.microsoft.com/ko-kr/windows/desktop/inputdev/virtual-key-codes

virtual_key = [['a',0x41],
               ['b',0x42],
               ['c',0x43],
               ['d',0x44],
               ['e',0x45],
               ['f',0x46],
               ['g',0x47],
               ['h',0x48],
               ['i',0x49],
               ['j',0x4A],
               ['k',0x4B],
               ['l',0x4C],
               ['m',0x4D],
               ['n',0x4E],
               ['o',0x4F],
               ['p',0x50],
               ['q',0x51],
               ['r',0x52],
               ['s',0x53],
               ['t',0x54],
               ['u',0x55],
               ['v',0x56],
               ['w',0x57],
               ['x',0x58],
               ['y',0x59],
               ['z',0x5A],
               ['0',0x30],
               ['1',0x31],
               ['2',0x32],
               ['3',0x33],
               ['4',0x34],
               ['5',0x35],
               ['6',0x36],
               ['7',0x37],
               ['8',0x38],
               ['9',0x39],
               ['enter',0x0D],
               ['space',0x20],
               ['shift',0x10],
               ['ctrl',0x11],
               ['alt',0x12],
               ['tab',0x09],
               ['capslock',0x14],
               ['esc',0x1B],
               ['windows',0x5B],
               ['left',0x25],
               ['up',0x26],
               ['right',0x27],
               ['down',0x28],
               [';',0xBA],
               ['=',0xBB],
               [',',0xBC],
               ['-',0xBD],
               ['.',0xBE],
               ['/',0xBF],
               ['`',0xC0],
               ['[',0xDB],
               ['\\',0xDC],
               [']',0xDD],
               ['\'',0xDE],
               ['f1',0x70],
               ['f2',0x71],
               ['f3',0x72],
               ['f4',0x73],
               ['f5',0x74],
               ['f6',0x75],
               ['f7',0x76],
               ['f8',0x77],
               ['f9',0x78],
               ['f10',0x79],
               ['f11',0x7A],
               ['f12',0x7B],
               ['backspace',0x08],
               ['ins',0x2D],
               ['del',0x2E],
               ['pgup',0x21],
               ['pgdown',0x22],
               ['end',0x23],
               ['home',0x24],
               ['numlock',0x90],
               ['scrolllock',0x91],
               ['printscreen',0x2C],
               ['hanguel',0x15],
               ['hanja',0x19]
               ]

def get_realtime_mouse_pos(): # 실시간 마우스 좌표 출력 함수
	prev = win32api.GetCursorPos()
	while True:
		mouse_p = win32api.GetCursorPos()
		if prev != mouse_p:
			print(mouse_p)
		prev = mouse_p

def get_mouse_pos(): # 현재 마우스 좌표 반환 함수
	return win32api.GetCursorPos()

def set_mouse_pos(x, y): # 설정한 좌표로 마우스 이동시키는 함수
	win32api.SetCursorPos((x, y))

def move_mouse(x, y): # 설정한 좌표로 마우스 이동시키는 함수
	scrWidth = win32api.GetSystemMetrics(win32con.SM_CXSCREEN) # 절대 좌표에서 화면 좌측 상단은 (0,0), 우측 하단은 (65535,65535)
	scrHeight = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
	win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE, int(x * 65535 / scrWidth), int(y * 65535 / scrHeight), 0, 0) # 절대좌표로 변환 후 이동

def move_mouse_game(x, y): # 설정한 좌표로 마우스 이동시키는 함수(게임 내에서도 동작)
	windll.user32.mouse_event(0x0001, x, y, 0, 0)

def click_mouse_left(x, y): # 마우스 좌클릭 함수
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0) # (0,0) 좌표로 입력 시 현재 마우스 좌표 좌클릭
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
	# windll.user32.mouse_event(0x0002, x, y, 0, 0) # 0x8000 절대좌표
	# windll.user32.mouse_event(0x0004, x, y, 0, 0)

def click_mouse_down_left(): # 마우스 좌클릭 상태를 유지하는 함수
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

def click_mouse_up_left(): # 마우스 좌클릭 상태를 해제하는 함수
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def click_mouse_right(x, y): # 마우스 우클릭 함수
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
	# windll.user32.mouse_event(0x0008, x, y, 0, 0)
	# windll.user32.mouse_event(0x0010, x, y, 0, 0)

def click_mouse_down_right(): # 마우스 우클릭 상태를 유지하는 함수
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)

def click_mouse_up_right(): # 마우스 우클릭 상태를 해제하는 함수
	win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

def click_mouse_wheel(): # 마우스 휠클릭 함수
	windll.user32.mouse_event(0x0020, 0, 0, 0, 0)
	windll.user32.mouse_ent(0x0040, 0, 0, 0, 0)

def click_mouse_down_wheel(): # 마우스 휠클릭 상태를 유지하는 함수
	windll.user32.mouse_event(0x0020, 0, 0, 0, 0)

def click_mouse_up_wheel(): # 마우스 휠클릭 상태를 해제하는 함수
	windll.user32.mouse_event(0x0040, 0, 0, 0, 0)

def drag_mouse(x, y): # 설정한 좌표로 마우스 드래그하는 함수
	scrWidth = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
	scrHeight = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE, x * 65535 / scrWidth, y * 65535 / scrHeight, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def detect_mouse_left_state(): # 마우스 좌클릭 감지 함수
	th = threading.Thread(target=detect_mouse_left_state_thread, args=()) # 스레드 설정
	th.start() # 스레드 생성
	th.join() # 스레드가 종료될 때까지 대기
	return True # 마우스 좌클릭이 감지됐을 경우의 반환

def detect_mouse_left_state_thread(): # 마우스 좌클릭 감지 스레드
	mouse_state = win32api.GetKeyState(0x01) # 초기 마우스 좌클릭 상태
	while True:
		cur_mouse_state = win32api.GetKeyState(0x01) # 현재 마우스 좌클릭 상태
		if cur_mouse_state != mouse_state: # 마우스 좌클릭 상태가 변경됐을 경우
			mouse_state = cur_mouse_state # 마우스 좌클릭 상태 갱신
			if mouse_state == -127 or mouse_state == -128: # 두번 실행 방지
				return # 마우스 좌클릭이 감지됐을 경우 스레드 종료

def detect_mouse_right_state(): # 마우스 우클릭 감지 함수
	th = threading.Thread(target=detect_mouse_right_state_thread, args=()) # 스레드 설정
	th.start() # 스레드 생성
	th.join() # 스레드가 종료될 때까지 대기
	return True # 마우스 우클릭이 감지됐을 경우의 반환

def detect_mouse_right_state_thread(): # 마우스 우클릭 감지 스레드
	mouse_state = win32api.GetKeyState(0x02) # 초기 마우스 우클릭 상태
	while True:
		cur_mouse_state = win32api.GetKeyState(0x02) # 현재 마우스 우클릭 상태
		if cur_mouse_state != mouse_state: # 마우스 우클릭 상태가 변경됐을 경우
			mouse_state = cur_mouse_state # 마우스 우클릭 상태 갱신
			if mouse_state == -127 or mouse_state == -128: # 두번 실행 방지
				return # 마우스 우클릭이 감지됐을 경우 스레드 종료

def input_keyboard(key): # 키보드 입력 함수
	for vk in virtual_key:
		if key.lower() == vk[0]:
			win32api.keybd_event(vk[1], 0, 0, 0)
			win32api.keybd_event(vk[1], 0, 2, 0)
			break

def keyboardInput(key): # 키보드 입력 함수
	keyboard.press(key) # key 눌림 상태 유지
	time.sleep(0.01) # 너무 빠른 입력으로 인한 키 입력 씹힘 방지 딜레이
	keyboard.release(key) # key 눌림 상태 해제

def keyboardInput_combination(key1, key2): # key1 + key2 입력 함수
	keyboard.press(key1) # key1 눌림 상태 유지
	keyboard.press(key2) # key2 눌림 상태 유지
	time.sleep(0.01) # 너무 빠른 입력으로 인한 키 입력 씹힘 방지 딜레이
	keyboard.release(key2) # key2 눌림 상태 해제
	keyboard.release(key1) # keyl 눌림 상태 해제

def input_combination_keyboard(key1, key2): # 두 키를 조합해서 입력하는 함수
	for vk1 in virtual_key:
		if key1.lower() == vk1[0]:
			for vk2 in virtual_key:
				if key2.lower() == vk2[0]:
					win32api.keybd_event(vk1[1], 0, 0, 0)
					win32api.keybd_event(vk2[1], 0, 0, 0)
					win32api.keybd_event(vk2[1], 0, 2, 0)
					win32api.keybd_event(vk1[1], 0, 2, 0)
					break

def input_down_keyboard(key): # 키보드 눌림 상태를 유지하는 함수
	for vk in virtual_key:
		if key.lower() == vk[0]:
			win32api.keybd_event(vk[1], 0, 0, 0)
			break

def input_up_keyboard(key): # 키보드 눌림 상태를 해제하는 함수
	for vk in virtual_key:
		if key.lower() == vk[0]:
			win32api.keybd_event(vk[1], 0, 2, 0)
			break

def detect_key_state(key): # 키보드 입력 감지 함수
	for vk in virtual_key:
		if key.lower() == vk[0]:
			th = threading.Thread(target=detect_key_state_thread, args=(vk,)) # 스레드 설정
			th.start() # 스레드 생성
			th.join() # 스레드가 종료될 때까지 대기
			return True # 키보드 입력이 감지됐을 경우의 반환

def detect_key_state_thread(vk): # 키보드 입력 감지 스레드
	key_state = win32api.GetKeyState(vk[1]) # 초기 키보드 입력 상태
	while True:
		cur_key_state = win32api.GetKeyState(vk[1]) # 현재 키보드 입력 상태
		if cur_key_state != key_state: # 키보드 입력 상태가 변경됐을 경우
			key_state = cur_key_state # 키보드 입력 상태 갱신
			if key_state == -127 or key_state == -128: # 두번 실행 방지
				return # 키보드 입력이 감지됐을 경우 스레드 종료

def get_realtime_pixel(): # 실시간으로 마우스 위치의 픽셀을 출력하는 함수
	prev = win32api.GetCursorPos()
	while True:
		mouse_p = win32api.GetCursorPos()
		if prev != mouse_p:
			print('Hex : ' + str(hex(win32gui.GetPixel(win32gui.GetDC(win32gui.GetDesktopWindow()), mouse_p[0], mouse_p[1]))) + ' Int : ' + str(win32gui.GetPixel(win32gui.GetDC(win32gui.GetDesktopWindow()), mouse_p[0], mouse_p[1])))
		prev = mouse_p

def get_pixel(x, y): # 설정한 위치의 픽셀을 반환하는 함수
	return win32gui.GetPixel(win32gui.GetDC(win32gui.GetDesktopWindow()), x, y)

def set_pixel(x, y, color): # 설정한 위치의 픽셀을 설정한 색으로 변경하는 함수
	hdc = win32gui.GetDC(win32gui.GetDesktopWindow())
	win32gui.SetPixel(hdc, x, y, color)

def getScreenshot(save_file, prog_start_pos_x, prog_start_pos_y, prog_end_pos_x, prog_end_pos_y): # 스크린샷 후 파일로 저장하는 함수
	im = ImageGrab.grab((prog_start_pos_x, prog_start_pos_y, prog_end_pos_x, prog_end_pos_y)) # 설정한 범위만큼 화면 스크린샷
	im.save(save_file) # 설정한 파일로 스크린샷 저장

def get_program_pos_size(application_program_work_name): # 실행중인 프로그램 위치 및 크기를 알려주는 함수(윈도우 작업 관리자의 응용 프로그램에 나오는 작업명을 인자로 받음)
	ret = []
	ret.append(application_program_work_name) # 입력한 응용 프로그램 작업명 추가
	ret.append(False) # 탐지 성공 여부 초기화
	ret.append(0) # 프로그램의 x 좌표가 저장될 인덱스(2) 초기화
	ret.append(0) # 프로그램의 y 좌표가 저장될 인덱스(3) 초기화
	ret.append(0) # 프로그램의 가로 크기가 저장될 인덱스(4) 초기화
	ret.append(0) # 프로그램의 세로 크기가 저장될 인덱스(5) 초기화
	win32gui.EnumWindows(get_program_pos_size_callback, ret) # 콜백함수 호출
	return ret[1], ret[2], ret[3], ret[4], ret[5] # 탐지 성공 여부(ret[1]), 위치(ret[2],ret[3]) , 크기(ret[4],ret[5]) 반환

def get_program_pos_size_callback(hwnd, ret): # 실행중인 프로그램 위치 및 크기를 알려주는 함수의 콜백함수
	rect = win32gui.GetWindowRect(hwnd) # 프로그램 위치 정보 저장
	pos_x = rect[0] # 프로그램의 x 좌표 저장
	pos_y = rect[1] # 프로그램의 y 좌표 저장
	size_x = rect[2] - pos_x # 프로그램의 가로 크기 저장
	size_y = rect[3] - pos_y # 프로그램의 세로 크기 저장
	if (pos_x <= 0 and pos_y <= 0) or (size_x <= 0 and size_y <= 0): # 위치 또는 크기가 0,0 보다 작거나 같을 경우(최대화 지원 안함)
		return
	else:
		application_program_work_name = str(win32gui.GetWindowText(hwnd)).lower().strip() # 현재 탐색된 응용 프로그램 작업명 저장
		if type(ret[0]) == unicode: # 입력한 응용 프로그램 작업명이 유니코드일 경우
			if str(ret[0].encode('utf-8')).encode('hex') == str(unicode(application_program_work_name, 'euc-kr').encode('utf-8')).encode('hex'): # 입력한 응용 프로그램 작업명이 현재 탐색된 응용 프로그램 작업명과 같을 경우
				ret[1] = True # 탐지 성공 설정 저장
				ret[2] = pos_x # 프로그램의 x 좌표 저장
				ret[3] = pos_y # 프로그램의 y 좌표 저장
				ret[4] = size_x # 프로그램의 가로 크기 저장
				ret[5] = size_y # 프로그램의 세로 크기 저장
				return
		else: # 입력한 응용 프로그램 작업명이 문자열일 경우
			if ret[0].lower() == application_program_work_name: # 입력한 응용 프로그램 작업명이 현재 탐색된 응용 프로그램 작업명과 같을 경우
				ret[1] = True # 탐지 성공 설정 저장
				ret[2] = pos_x # 프로그램의 x 좌표 저장
				ret[3] = pos_y # 프로그램의 y 좌표 저장
				ret[4] = size_x # 프로그램의 가로 크기 저장
				ret[5] = size_y # 프로그램의 세로 크기 저장
				return

def get_program_pos_size_include(application_program_work_name): # 실행중인 프로그램 위치 및 크기를 알려주는 함수(윈도우 작업 관리자의 응용 프로그램에 나오는 작업명을 인자로 받음)
	ret = []
	ret.append(application_program_work_name) # 입력한 응용 프로그램 작업명 추가
	ret.append(False) # 탐지 성공 여부 초기화
	ret.append(0) # 프로그램의 x 좌표가 저장될 인덱스(2) 초기화
	ret.append(0) # 프로그램의 y 좌표가 저장될 인덱스(3) 초기화
	ret.append(0) # 프로그램의 가로 크기가 저장될 인덱스(4) 초기화
	ret.append(0) # 프로그램의 세로 크기가 저장될 인덱스(5) 초기화
	win32gui.EnumWindows(get_program_pos_size_include_callback, ret) # 콜백함수 호출
	return ret[1], ret[2], ret[3], ret[4], ret[5] # 탐지 성공 여부(ret[1]), 위치(ret[2],ret[3]) , 크기(ret[4],ret[5]) 반환

def get_program_pos_size_include_callback(hwnd, ret): # 실행중인 프로그램 위치 및 크기를 알려주는 함수의 콜백함수
	rect = win32gui.GetWindowRect(hwnd) # 프로그램 위치 정보 저장
	pos_x = rect[0] # 프로그램의 x 좌표 저장
	pos_y = rect[1] # 프로그램의 y 좌표 저장
	size_x = rect[2] - pos_x # 프로그램의 가로 크기 저장
	size_y = rect[3] - pos_y # 프로그램의 세로 크기 저장
	if (pos_x <= 0 and pos_y <= 0) or (size_x <= 0 and size_y <= 0): # 위치 또는 크기가 0,0 보다 작거나 같을 경우(최대화 지원 안함)
		return
	else:
		application_program_work_name = str(win32gui.GetWindowText(hwnd)).lower().strip() # 현재 탐색된 응용 프로그램 작업명 저장
		if type(ret[0]) == unicode: # 입력한 응용 프로그램 작업명이 유니코드일 경우
			if str(ret[0].encode('utf-8')).encode('hex') in str(unicode(application_program_work_name, 'euc-kr').encode('utf-8')).encode('hex'): # 입력한 응용 프로그램 작업명이 현재 탐색된 응용 프로그램 작업명의 문자열에 포함돼 있을 경우
				ret[1] = True # 탐지 성공 설정 저장
				ret[2] = pos_x # 프로그램의 x 좌표 저장
				ret[3] = pos_y # 프로그램의 y 좌표 저장
				ret[4] = size_x # 프로그램의 가로 크기 저장
				ret[5] = size_y # 프로그램의 세로 크기 저장
				return
		else: # 입력한 응용 프로그램 작업명이 문자열일 경우
			if ret[0].lower() in application_program_work_name: # 입력한 응용 프로그램 작업명이 현재 탐색된 응용 프로그램 작업명의 문자열에 포함돼 있을 경우
				ret[1] = True # 탐지 성공 설정 저장
				ret[2] = pos_x # 프로그램의 x 좌표 저장
				ret[3] = pos_y # 프로그램의 y 좌표 저장
				ret[4] = size_x # 프로그램의 가로 크기 저장
				ret[5] = size_y # 프로그램의 세로 크기 저장
				return

def get_program_pos_size_maximum(application_program_work_name): # 실행중인 프로그램 위치 및 크기를 알려주는 함수(윈도우 작업 관리자의 응용 프로그램에 나오는 작업명을 인자로 받음)
	ret = []
	ret.append(application_program_work_name) # 입력한 응용 프로그램 작업명 추가
	ret.append(False) # 탐지 성공 여부 초기화
	ret.append(0) # 프로그램의 x 좌표가 저장될 인덱스(2) 초기화
	ret.append(0) # 프로그램의 y 좌표가 저장될 인덱스(3) 초기화
	ret.append(0) # 프로그램의 가로 크기가 저장될 인덱스(4) 초기화
	ret.append(0) # 프로그램의 세로 크기가 저장될 인덱스(5) 초기화
	win32gui.EnumWindows(get_program_pos_size_maximum_callback, ret) # 콜백함수 호출
	return ret[1], ret[2], ret[3], ret[4], ret[5] # 탐지 성공 여부(ret[1]), 위치(ret[2],ret[3]) , 크기(ret[4],ret[5]) 반환

def get_program_pos_size_maximum_callback(hwnd, ret): # 실행중인 프로그램 위치 및 크기를 알려주는 함수의 콜백함수
	rect = win32gui.GetWindowRect(hwnd) # 프로그램 위치 정보 저장
	pos_x = rect[0] # 프로그램의 x 좌표 저장
	pos_y = rect[1] # 프로그램의 y 좌표 저장
	size_x = rect[2] - pos_x # 프로그램의 가로 크기 저장
	size_y = rect[3] - pos_y # 프로그램의 세로 크기 저장
	application_program_work_name = str(win32gui.GetWindowText(hwnd)).lower().strip() # 현재 탐색된 응용 프로그램 작업명 저장
	if type(ret[0]) == unicode: # 입력한 응용 프로그램 작업명이 유니코드일 경우
		if str(ret[0].encode('utf-8')).encode('hex') == str(unicode(application_program_work_name, 'euc-kr').encode('utf-8')).encode('hex'): # 입력한 응용 프로그램 작업명이 현재 탐색된 응용 프로그램 작업명과 같을 경우
			if pos_x < 0 and pos_y < 0: # 프로그램이 최대화 상태일 경우(위치가 음수로 나옴)
				pos_x = 0 # x좌표 0으로 설정
				pos_y = 0 # y좌표 0으로 설정
			ret[1] = True # 탐지 성공 설정 저장
			ret[2] = pos_x # 프로그램의 x 좌표 저장
			ret[3] = pos_y # 프로그램의 y 좌표 저장
			ret[4] = size_x # 프로그램의 가로 크기 저장
			ret[5] = size_y # 프로그램의 세로 크기 저장
			return
	else: # 입력한 응용 프로그램 작업명이 문자열일 경우
		if ret[0].lower() == application_program_work_name: # 입력한 응용 프로그램 작업명이 현재 탐색된 응용 프로그램 작업명과 같을 경우
			if pos_x < 0 and pos_y < 0: # 프로그램이 최대화 상태일 경우(위치가 음수로 나옴)
				pos_x = 0 # x좌표 0으로 설정
				pos_y = 0 # y좌표 0으로 설정
			ret[1] = True # 탐지 성공 설정 저장
			ret[2] = pos_x # 프로그램의 x 좌표 저장
			ret[3] = pos_y # 프로그램의 y 좌표 저장
			ret[4] = size_x # 프로그램의 가로 크기 저장
			ret[5] = size_y # 프로그램의 세로 크기 저장
			return

def get_program_pos_size_include_maximum(application_program_work_name): # 실행중인 프로그램 위치 및 크기를 알려주는 함수(윈도우 작업 관리자의 응용 프로그램에 나오는 작업명을 인자로 받음)
	ret = []
	ret.append(application_program_work_name) # 입력한 응용 프로그램 작업명 추가
	ret.append(False) # 탐지 성공 여부 초기화
	ret.append(0) # 프로그램의 x 좌표가 저장될 인덱스(1) 초기화
	ret.append(0) # 프로그램의 y 좌표가 저장될 인덱스(2) 초기화
	ret.append(0) # 프로그램의 가로 크기가 저장될 인덱스(3) 초기화
	ret.append(0) # 프로그램의 세로 크기가 저장될 인덱스(4) 초기화
	win32gui.EnumWindows(get_program_pos_size_include_maximum_callback, ret) # 콜백함수 호출
	return ret[1], ret[2], ret[3], ret[4], ret[5] # 탐지 성공 여부(ret[1]), 위치(ret[2],ret[3]) , 크기(ret[4],ret[5]) 반환

def get_program_pos_size_include_maximum_callback(hwnd, ret): # 실행중인 프로그램 위치 및 크기를 알려주는 함수의 콜백함수
	rect = win32gui.GetWindowRect(hwnd) # 프로그램 위치 정보 저장
	pos_x = rect[0] # 프로그램의 x 좌표 저장
	pos_y = rect[1] # 프로그램의 y 좌표 저장
	size_x = rect[2] - pos_x # 프로그램의 가로 크기 저장
	size_y = rect[3] - pos_y # 프로그램의 세로 크기 저장
	application_program_work_name = str(win32gui.GetWindowText(hwnd)).lower().strip() # 현재 탐색된 응용 프로그램 작업명 저장
	if type(ret[0]) == unicode: # 입력한 응용 프로그램 작업명이 유니코드일 경우
		if str(ret[0].encode('utf-8')).encode('hex') in str(unicode(application_program_work_name, 'euc-kr').encode('utf-8')).encode('hex'): # 입력한 응용 프로그램 작업명이 현재 탐색된 응용 프로그램 작업명의 문자열에 포함돼 있을 경우
			if pos_x < 0 and pos_y < 0: # 프로그램이 최대화 상태일 경우(위치가 음수로 나옴)
				pos_x = 0 # x좌표 0으로 설정
				pos_y = 0 # y좌표 0으로 설정
			ret[1] = True # 탐지 성공 설정 저장
			ret[2] = pos_x # 프로그램의 x 좌표 저장
			ret[3] = pos_y # 프로그램의 y 좌표 저장
			ret[4] = size_x # 프로그램의 가로 크기 저장
			ret[5] = size_y # 프로그램의 세로 크기 저장
			return
	else: # 입력한 응용 프로그램 작업명이 문자열일 경우
		if ret[0].lower() in application_program_work_name: # 입력한 응용 프로그램 작업명이 현재 탐색된 응용 프로그램 작업명의 문자열에 포함돼 있을 경우
			if pos_x < 0 and pos_y < 0: # 프로그램이 최대화 상태일 경우(위치가 음수로 나옴)
				pos_x = 0 # x좌표 0으로 설정
				pos_y = 0 # y좌표 0으로 설정
			ret[1] = True # 탐지 성공 설정 저장
			ret[2] = pos_x # 프로그램의 x 좌표 저장
			ret[3] = pos_y # 프로그램의 y 좌표 저장
			ret[4] = size_x # 프로그램의 가로 크기 저장
			ret[5] = size_y # 프로그램의 세로 크기 저장
			return

# 템플릿 매칭 정확도를 높이기 위한 알고리즘 구현 요망(현재는 템플릿 매칭 방법이 3개 이상 맞을 경우로 설정돼 있음)
def templateMatching(image_file, template_image_file): # 템플릿 매칭을 통해 이미지(image_file) 내에 있는 특정 이미지(template_image_file)를 검출하는 함수(이미지 서치)
	img1 = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE) # 이미지 흑백으로 저장
	img2 = img1.copy() # 이미지 복사본 저장
	template = cv2.imread(template_image_file, cv2.IMREAD_GRAYSCALE) # 템플릿 이미지 흑백으로 저장
	w, h = template.shape[::-1] # 템플릿 이미지의 가로, 세로 길이 저장
	methods = ['cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED'] # 템플릿 매칭 방법이 저장된 리스트
	top_left_list = [] # 매칭된 거짓말 탐지기 이미지의 좌측 상단 좌표가 저장될 리스트
	duplication = [] # 중복된 좌표의 개수들이 저장될 리스트
	for meth in methods: # 템플릿 매칭 방법 수 만큼 반복
		img1 = img2.copy() # 이미지 복사본 이미지로 초기화
		method = eval(meth) # 템플릿 매칭 방법 설정
		try:
			res = cv2.matchTemplate(img1, template, method) # 이미지와 템플릿 이미지 비교
			min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res) # 템플릿 매칭 성공 시 최대값, 최소값, 위치값 저장
		except:
			continue
		if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]: # 템플릿 매칭 방법이 cv2.TM_SQDIFF 또는 cv2.TM_SQDIFF_NORMED 일 경우
			top_left = min_loc # 최소값을 좌측 상단으로 설정
		else: # 그 이외의 템플릿 매칭 방법일 경우
			top_left = max_loc # 최대값을 좌측 상단으로 설정
		top_left_list.append(top_left) # 리스트에 매칭된 이미지의 좌측 상단 좌표 추가
	for i in range(0, len(top_left_list)): # 리스트에 저장된 매칭된 이미지의 좌측 상단 좌표 수(템플릿 매칭 방법 수) 만큼 반복
		duplication.append(top_left_list.count(top_left_list[i])) # 리스트에 중복된 좌표의 개수 추가
	if max(duplication) >= 3: # 중복된 개수가 3개 이상일 경우(해당 값을 올리면 오탐을 방지할 수 있으나 진탐을 하지 못할 수도 있음)
		for i in range(0, len(duplication)): # 리스트에 저장된 중복된 좌표의 개수(템플릿 매칭 방법 수)만큼 반복
			if max(duplication) == duplication[i]: # 현재 값이 중복된 좌표의 개수들이 저장될 리스트에 있는 값들 중 최대값일 경우
				return True, top_left_list[i] # 매칭된 이미지의 좌측 상단 좌표 반환(템플릿 매칭 방법으로 가장 많이 나온 좌표 반환)
	return False, [0] # 템플릿 매칭 실패했을 경우의 반환

sem = threading.Semaphore(10) # 세마포어 설정

# 화면 전체를 대상으로 이미지 서치하는 함수(서치 대상 이미지 파일의 모든 픽셀을 화면 이미지의 픽셀과 비교해서 이미지 서치하는 함수)
def image_search_all_range(fname, error): # 이미지 파일, 오차값(이미지 파일의 픽셀값과 화면의 픽셀값을 비교할 때 일치하지 않아도 용납되는 픽셀의 최대 개수. 이미지 파일의 크기가 클 경우 오차값을 크게 하고 작을 경우 작게 설정해야 함)
    try:
        im = pilimg.open(fname) # 이미지 파일 정보 저장
        pix = np.array(im) # 이미지 파일의 픽셀값 배열로 구성 후 저장
        image_size_x = len(pix[0])-1 # 이미지 파일의 가로 크기
        image_size_y = len(pix)-1 # 이미지 파일의 세로 크기
        windows_pos_x = win32api.GetSystemMetrics(win32con.SM_CXSCREEN) # 화면 가로 크기
        windows_pos_y = win32api.GetSystemMetrics(win32con.SM_CYSCREEN) # 화면 세로 크기
        match = 0 # 이미지 일치 여부를 판단하는 변수
        break_var = 0 # 탈출 변수
        # y -> x 순으로 했으므로 설정한 범위 맨 위부터 가로로 서치하면서 내려옴(이미지 서치 시간의 효율성과 관련돼 있음)
        for w_y in range(0, windows_pos_y): # 화면 세로 크기만큼 반복
            for w_x in range(0, windows_pos_x): # 화면 가로 크기만큼 반복
                if w_x > windows_pos_x - image_size_x or w_y > windows_pos_y - image_size_y: # 화면 최우측 밑 최하단 처리
                    break # 범위를 넘어서므로 빠져나감
                cur_error = 0 # 현재 이미지 서치 오차값 초기화
                for x in range(0, image_size_y): # 이미지 파일의 세로 크기만큼 반복
                    if break_var == 1: # 탈출 변수 값이 1일 경우
                        break_var = 0 # 탈출 변수 값 초기화
                        break # 다음 화면 이미지와의 비교를 위해 빠져나감
                    for y in range(0, image_size_x): # 이미지 파일의 가로 크기만큼 반복
                        image_pixel = hex(pix[x][y][0] + pix[x][y][1] * 0x100 + pix[x][y][2] * 0x10000) # 이미지 파일의 픽셀값(1 pixel) 저장
                        windows_pixel = hex(win32gui.GetPixel(win32gui.GetDC(win32gui.GetActiveWindow()), w_x + x, w_y + y)) # 화면 픽셀값(1 pixel) 저장
                        if image_pixel == windows_pixel: # 이미지 파일의 픽셀값과 화면의 픽셀값이 같을 경우
                            match += 1 # 이미지 일치 변수 값 증가
                        else: # 이미지 파일의 픽셀값과 화면의 픽셀값이 다를 경우
                            cur_error += 1 # 현재 이미지 서치 오차값 증가
                            if error < cur_error: # 현재 이미지 서치 오차 값이 설정한 오차값보다 클 경우
                                break_var = 1 # 탈출 변수 값 설정
                                break # 이미지 파일의 이미지와 화면의 이미지가 같지 않으므로 빠져나감
                if match > image_size_x*image_size_y - error: # 이미지 일치 변수 값이 오차 범위 이내일 경우(이미지 파일의 이미지와 화면의 이미지가 비슷한 경우)
                    return True # 이미지 서치가 성공했을 경우의 반환
                match = 0 # 이미지 일치 변수 값 초기화
        return False # 이미지 서치가 실패했을 경우의 반환
    except Exception as e:
        return False # 이미지 서치가 실패했을 경우의 반환

# 화면 전체를 대상으로 이미지 서치하는 함수(서치 대상 이미지 파일의 일부 픽셀만 화면 이미지의 픽셀과 비교해서 빠르게 이미지 서치하는 함수)
def image_search_all_range_fast(fname, pixel_count, error): # 이미지 파일, 비교할 픽셀의 개수(이 값이 작아질수록 정확도는 낮아지지만 탐지 속도는 증가함), 오차값(이미지 파일의 픽셀값과 화면의 픽셀값을 비교할 때 일치하지 않아도 용납되는 픽셀의 최대 개수. 이미지 파일의 크기가 클 경우 오차값을 크게 하고 작을 경우 작게 설정해야 함)
	im = pilimg.open(fname) # 이미지 파일 정보 저장
	pix = np.array(im) # 이미지 파일의 픽셀값 배열로 구성 후 저장
	image_size_x = len(pix[0])-1 # 이미지 파일의 가로 크기
	image_size_y = len(pix)-1 # 이미지 파일의 세로 크기
	windows_pos_x = win32api.GetSystemMetrics(win32con.SM_CXSCREEN) # 화면 가로 크기
	windows_pos_y = win32api.GetSystemMetrics(win32con.SM_CYSCREEN) # 화면 세로 크기
	sem = threading.Semaphore(win32api.GetSystemMetrics(win32con.SM_CYSCREEN)) # 세마포어 설정
	threads = [] # 스레드 리스트
	# y -> x 순으로 했으므로 설정한 범위 맨 위부터 가로로 서치하면서 내려옴(이미지 서치 시간의 효율성과 관련돼 있음)
	for w_y in range(0, windows_pos_y): # 화면 세로 크기만큼 반복
		th = threading.Thread(target=image_search_all_range_fast_thread, args=(pix, image_size_x, image_size_y, windows_pos_x, windows_pos_y, w_y, pixel_count, sem, error,)) # 스레드 세팅
		th.start() # 스레드 생성
		threads.append(th) # 생성된 스레드 저장
		if len(threads) > 300: # 생성된 스레드의 수가 300개 초과일 경우
			for th in threads: # 생성된 스레드 개수만큼 반복
				th.join() # 스레드 종료 대기
			threads = [] # 스레드 리스트 초기화
	for th in threads: # 생성된 스레드 개수만큼 반복
		th.join() # 스레드 종료 대기

def image_search_all_range_fast_thread(pix, image_size_x, image_size_y, windows_pos_x, windows_pos_y, w_y, pixel_count, sem, error): # 화면 전체를 대상으로 이미지 서치하는 함수 스레드
    try:
        sem.acquire() # 임계영역 생성
        match = 0 # 이미지 일치 여부를 판단하는 변수
        for w_x in range(0, windows_pos_x): # 화면 가로 크기만큼 반복
            if w_x > windows_pos_x - image_size_x or w_y > windows_pos_y - image_size_y: # 화면 최우측 밑 최하단 처리
                break # 범위를 넘어서므로 빠져나감
            cur_error = 0 # 현재 이미지 서치 오차값 초기화
            for i in range(0, pixel_count): # 설정한 비교할 픽셀의 개수만큼 반복
                random_pixel_x = random.randrange(0, image_size_y + 1) # 이미지 파일 가로 크기 내의 랜덤한 값
                random_pixel_y = random.randrange(0, image_size_x + 1) # 이미지 파일 세로 크기 내의 랜덤한 값
                image_pixel = hex(pix[random_pixel_x][random_pixel_y][0] + pix[random_pixel_x][random_pixel_y][1] * 0x100 + pix[random_pixel_x][random_pixel_y][2] * 0x10000) # 랜덤한 위치의 이미지 파일의 픽셀값(1 pixel) 저장
                windows_pixel = hex(win32gui.GetPixel(win32gui.GetDC(win32gui.GetActiveWindow()), w_x + random_pixel_x, w_y + random_pixel_y)) # 화면 픽셀값(1 pixel) 저장
                if image_pixel == windows_pixel: # 이미지 파일의 픽셀값과 화면의 픽셀값이 같을 경우
                    match += 1 # 이미지 일치 변수 값 증가
                else: # 이미지 파일의 픽셀값과 화면의 픽셀값이 다를 경우
                    cur_error += 1 # 현재 이미지 서치 오차값 증가
                    if error < cur_error: # 현재 이미지 서치 오차 값이 설정한 오차값보다 클 경우
                        break # 이미지 파일의 이미지와 화면의 이미지가 같지 않으므로 빠져나감
            if match > pixel_count - error: # 이미지 일치 변수 값이 오차 범위 이내일 경우(이미지 파일의 이미지와 화면의 이미지가 비슷한 경우)
                ########################## 이미지 서치 성공했을 경우의 작업 추가 ##########################
                sem.release() # 임계영역 해제
                return
            match = 0 # 이미지 일치 변수 값 초기화
        sem.release() # 임계영역 해제
    except Exception as e:
        sem.release() # 임계영역 해제
        pass

# 화면 특정 범위를 대상으로 이미지 서치하는 함수(서치 대상 이미지 파일의 모든 픽셀을 화면 이미지의 픽셀과 비교해서 이미지 서치하는 함수)
def image_search_particular_range(fname, start_pos_x, start_pos_y, end_pos_x, end_pos_y, error): # 이미지 파일, 서치 시작 x좌표, 서치 시작 y좌표, 서치 마지막 x좌표, 서치 마지막 y좌표, 오차값(이미지 파일의 픽셀값과 화면의 픽셀값을 비교할 때 일치하지 않아도 용납되는 픽셀의 최대 개수. 이미지 파일의 크기가 클 경우 오차값을 크게 하고 작을 경우 작게 설정해야 함)
    try:
        im = pilimg.open(fname) # 이미지 파일 정보 저장
        pix = np.array(im) # 이미지 파일의 픽셀값 배열로 구성 후 저장
        image_size_x = len(pix[0])-1 # 이미지 파일의 가로 크기
        image_size_y = len(pix)-1 # 이미지 파일의 세로 크기
        match = 0 # 이미지 일치 여부를 판단하는 변수
        break_var = 0 # 탈출 변수
        if end_pos_x - start_pos_x < image_size_x or end_pos_y - start_pos_y < image_size_y: # 설정한 범위가 이미지 파일 크기보다 작을 경우
            print('[-] 설정한 범위가 이미지 파일 크기보다 작습니다.')
            return False # 이미지 서치가 실패했을 경우의 반환
        # y -> x 순으로 했으므로 설정한 범위 맨 위부터 가로로 서치하면서 내려옴(이미지 서치 시간의 효율성과 관련돼 있음)
        for w_y in range(start_pos_y, end_pos_y): # 설정한 세로 범위만큼 반복
            for w_x in range(start_pos_x, end_pos_x): # 설정한 가로 범위만큼 반복
                if w_x > end_pos_x - image_size_x or w_y > end_pos_y - image_size_y: # 화면 최우측 밑 최하단 처리
                    break # 범위를 넘어서므로 빠져나감
                cur_error = 0 # 현재 이미지 서치 오차값 초기화
                for x in range(0, image_size_y): # 이미지 파일의 세로 크기만큼 반복
                    if break_var == 1: # 탈출 변수 값이 1일 경우
                        break_var = 0 # 탈출 변수 값 초기화
                        break # 다음 화면 이미지와의 비교를 위해 빠져나감
                    for y in range(0, image_size_x): # 이미지 파일의 가로 크기만큼 반복
                        image_pixel = hex(pix[x][y][0] + pix[x][y][1] * 0x100 + pix[x][y][2] * 0x10000) # 이미지 파일의 픽셀값(1 pixel) 저장
                        windows_pixel = hex(win32gui.GetPixel(win32gui.GetDC(win32gui.GetActiveWindow()), w_x + x, w_y + y)) # 화면 픽셀값(1 pixel) 저장
                        if image_pixel == windows_pixel: # 이미지 파일의 픽셀값과 화면의 픽셀값이 같을 경우
                            match += 1 # 이미지 일치 변수 값 증가
                        else: # 이미지 파일의 픽셀값과 화면의 픽셀값이 다를 경우
                            cur_error += 1 # 현재 이미지 서치 오차값 증가
                            if error < cur_error: # 현재 이미지 서치 오차값이 설정한 오차값보다 클 경우
                                break_var = 1 # 탈출 변수 값 설정
                                break # 이미지 파일의 이미지와 화면의 이미지가 같지 않으므로 빠져나감
                if match > image_size_x*image_size_y - error: # 이미지 일치 변수 값이 오차 범위 이내일 경우(이미지 파일의 이미지와 화면의 이미지가 비슷한 경우)
                    return True # 이미지 서치가 성공했을 경우의 반환
                match = 0 # 이미지 일치 변수 값 초기화
        return False # 이미지 서치가 실패했을 경우의 반환
    except Exception as e:
        return False # 이미지 서치가 실패했을 경우의 반환

# 화면 특정 범위를 대상으로 이미지 서치하는 함수(서치 대상 이미지 파일의 일부 픽셀만 화면 이미지의 픽셀과 비교해서 빠르게 이미지 서치하는 함수)
def image_search_particular_range_fast(fname, start_pos_x, start_pos_y, end_pos_x, end_pos_y, pixel_count, error): # 이미지 파일, 서치 시작 x좌표, 서치 시작 y좌표, 서치 마지막 x좌표, 서치 마지막 y좌표, 비교할 픽셀의 개수(이 값이 작아질수록 정확도는 낮아지지만 탐지 속도는 증가함), 오차값(이미지 파일의 픽셀값과 화면의 픽셀값을 비교할 때 일치하지 않아도 용납되는 픽셀의 최대 개수. 이미지 파일의 크기가 클 경우 오차값을 크게 하고 작을 경우 작게 설정해야 함)
	im = pilimg.open(fname) # 이미지 파일 정보 저장
	pix = np.array(im) # 이미지 파일의 픽셀값 배열로 구성 후 저장
	image_size_x = len(pix[0])-1 # 이미지 파일의 가로 크기
	image_size_y = len(pix)-1 # 이미지 파일의 세로 크기
	sem = threading.Semaphore(end_pos_y - start_pos_y) # 세마포어 설정
	threads = [] # 스레드 리스트
	if end_pos_x - start_pos_x < image_size_x or end_pos_y - start_pos_y < image_size_y: # 설정한 범위가 이미지 파일 크기보다 작을 경우
		print('[-] 설정한 범위가 이미지 파일 크기보다 작습니다.')
		return
	# y -> x 순으로 했으므로 설정한 범위 맨 위부터 가로로 서치하면서 내려옴(이미지 서치 시간의 효율성과 관련돼 있음)
	for w_y in range(start_pos_y, end_pos_y): # 설정한 세로 범위만큼 반복
		th = threading.Thread(target=image_search_particular_range_fast_thread, args=(pix, image_size_x, image_size_y, w_y, start_pos_x, start_pos_y, end_pos_x, end_pos_y, pixel_count, sem, error,)) # 스레드 세팅
		th.start() # 스레드 생성
		threads.append(th) # 생성된 스레드 저장
		if len(threads) > 300: # 생성된 스레드의 수가 300개 초과일 경우
			for th in threads: # 생성된 스레드 개수만큼 반복
				th.join() # 스레드 종료 대기
			threads = [] # 스레드 리스트 초기화
	for th in threads: # 생성된 스레드 개수만큼 반복
		th.join() # 스레드 종료 대기

def image_search_particular_range_fast_thread(pix, image_size_x, image_size_y, w_y, start_pos_x, start_pos_y, end_pos_x, end_pos_y, pixel_count, sem, error): # 화면 특정 범위를 대상으로 이미지 서치하는 함수 스레드
    try:
        sem.acquire() # 임계영역 생성
        match = 0 # 이미지 일치 여부를 판단하는 변수
        for w_x in range(start_pos_x, end_pos_x): # 설정한 가로 범위만큼 반복
            if w_x > end_pos_x - image_size_x or w_y > end_pos_y - image_size_y: # 화면 최우측 밑 최하단 처리
                break # 범위를 넘어서므로 빠져나감
            cur_error = 0 # 현재 이미지 서치 오차값 초기화
            for i in range(0, pixel_count): # 설정한 비교할 픽셀의 개수만큼 반복
                random_pixel_x = random.randrange(0, image_size_y + 1) # 이미지 파일 가로 크기 내의 랜덤한 값
                random_pixel_y = random.randrange(0, image_size_x + 1) # 이미지 파일 세로 크기 내의 랜덤한 값
                image_pixel = hex(pix[random_pixel_x][random_pixel_y][0] + pix[random_pixel_x][random_pixel_y][1] * 0x100 + pix[random_pixel_x][random_pixel_y][2] * 0x10000) # 랜덤한 위치의 이미지 파일의 픽셀값(1 pixel) 저장
                windows_pixel = hex(win32gui.GetPixel(win32gui.GetDC(win32gui.GetActiveWindow()), w_x + random_pixel_x, w_y + random_pixel_y)) # 화면 픽셀값(1 pixel) 저장
                if image_pixel == windows_pixel: # 이미지 파일의 픽셀값과 화면의 픽셀값이 같을 경우
                    match += 1 # 이미지 일치 변수 값 증가
                else: # 이미지 파일의 픽셀값과 화면의 픽셀값이 다를 경우
                    cur_error += 1 # 현재 이미지 서치 오차값 증가
                    if error < cur_error: # 현재 이미지 서치 오차값이 설정한 오차값보다 클 경우
                        break # 이미지 파일의 이미지와 화면의 이미지가 같지 않으므로 빠져나감
            if match > pixel_count - error: # 이미지 일치 변수 값이 오차 범위 이내일 경우(이미지 파일의 이미지와 화면의 이미지가 비슷한 경우)
                ########################## 이미지 서치 성공했을 경우의 작업 추가 ##########################
                sem.release() # 임계영역 해제
                return
            match = 0 # 이미지 일치 변수 값 초기화
        sem.release() # 임계영역 해제
    except Exception as e:
        sem.release() # 임계영역 해제
        pass