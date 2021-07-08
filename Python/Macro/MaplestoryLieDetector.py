#-*- coding: utf-8 -*-
import os
import sys
import time
import win32api
import win32con
import threading
import numpy as np
import cv2
import keyboard
import pyperclip
import clipboard
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import icoBinary
import myMacro

sem = threading.Semaphore(10) # 세마포어 설정
exit_var = False # 스레드 종료 변수
exit_var_pause = False # restart_thread 스레드 종료 변수

class MacroClass(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self.start = False # 시작 버튼 눌림 여부
		self.application_program_maple_work_name = 'MapleStory' # 메이플 응용 프로그램 작업명
		self.application_program_kakao_work_name = '' # 카카오톡 응용 프로그램 작업명(채팅방 이름)
		self.full_screenshot_file = os.getcwd() + '\\lieDetector_screenshot.png' # 메이플 화면 스크린샷 파일
		self.template_image_file = '' # 거짓말 탐지기 이미지 템플릿 파일
		self.captcha_screenshot_file = os.getcwd() + '\\captcha_screenshot.png' # 거짓말 탐지기 이미지 내 캡차 스크린샷 파일
		self.captcha_screenshot_start_x = 0 # 거짓말 탐지기 이미지 내 캡차 스크린샷 최좌측 x좌표
		self.captcha_screenshot_start_y = 110 # 거짓말 탐지기 이미지 내 캡차 스크린샷 최상단 y좌표
		self.captcha_screenshot_x = 240 # 거짓말 탐지기 이미지 가로 길이
		self.captcha_screenshot_y = 220 # 거짓말 탐지기 이미지 세로 길이
		self.kakao_image_open_button_minus_pos_x = 90 # 카카오톡 좌측 하단으로부터 사진 전송 버튼까지의 x 거리
		self.kakao_image_open_button_minus_pos_y = 20 # 카카오톡 좌측 하단으로부터 사진 전송 버튼까지의 y 거리
		self.kakao_receive_color = 3402751 # 카카오톡에서 거짓말 탐지기 해제 코드 전송했을 때 글자 주변에 나타나는 색깔(디폴트 노란색(0x33ebff))
		self.kakao_receive_color_minus_pos_x = 33 # 카카오톡 우측 하단으로부터 거짓말 탐지기 해제 코드 전송했을 때 글자 주변에 나타나는 색깔이 있는 특정 지점까지의 x 거리
		self.kakao_receive_color_minus_pos_y = 116 # 카카오톡 우측 하단으로부터 거짓말 탐지기 해제 코드 전송했을 때 글자 주변에 나타나는 색깔이 있는 특정 지점까지의 y 거리
		self.kakao_receive_code_minus_pos_x = 53 # 카카오톡 우측 하단으로부터 거짓말 탐지기 해제 코드 전송했을 때 나타나는 글자의 특정 지점까지의 x 거리
		self.kakao_receive_code_minus_pos_y = 128 # 카카오톡 우측 하단으로부터 거짓말 탐지기 해제 코드 전송했을 때 나타나는 글자의 특정 지점까지의 y 거리
		self.suspend_continue_code = '계속' # 거짓말 탐지기 오탐 시 현재 작업(거짓말 탐지기 해제 코드 입력하는 작업)을 중지하고 메이플 매크로를 다시 재개하는 코드
		self.macro_pause_restart = 'F12' # 메이플 매크로 중지 및 재시작 단축키
		self.size_x = 450 # 프로그램의 가로 크기
		self.size_y = 190 # 프로그램의 세로 크기
		self.pos_x = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)/2 - self.size_x/2 # 처음 프로그램이 나타나는 x좌표(디폴트 중앙으로 설정)
		self.pos_y = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)/2 - self.size_y/1.2 # 처음 프로그램이 나타나는 y좌표(디폴트 중앙 조금 위로 설정)
		self.setupWindow() # 윈도우 설정
		self.setupButton() # 버튼 설정
		self.setupLabel() # 레이블 설정
		self.setupEdit() # 에디트 설정
		self.setupStatusBar() # 상태 표시줄 설정

	def setupWindow(self): # 윈도우 특성 설정 함수
		title = 'Maplestory LieDetector Program' # 타이틀
		self.setWindowTitle(title) # 윈도우 타이클 설정
		self.setGeometry(self.pos_x, self.pos_y, self.size_x, self.size_y) # 윈도우 위치, 크기 설정
		ico_binary = icoBinary.title_ico_binary_maplestory_liedetector # 타이틀 아이콘 바이너리
		fp = open(os.getcwd() + '\\tmp_title.ico', 'wb') # 임시 아이콘 파일 생성
		fp.write(ico_binary)
		fp.close()
		self.setWindowIcon(QIcon(os.getcwd() + '\\tmp_title.ico')) # 타이틀 아이콘 설정
		self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowMinMaxButtonsHint) # 닫기 버튼 비활성화
		self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint) # 최대화 버튼 비활성화
		self.setFixedSize(self.size_x, self.size_y) # 화면 크기 변경 금지

	def setupButton(self): # 버튼 설정 함수
		self.btnStart = QPushButton('Start', self) # 프로그램 동작 버튼 설정
		self.btnStart.resize(self.btnStart.sizeHint() * 1.25)
		self.btnStart.setFixedWidth(130)
		self.btnStart.move(10, self.size_y - 50)
		self.btnStart.clicked.connect(self.start_func) # 프로그램 동작 함수 적용
		self.btnStart.setDisabled(True) # 프로그램 동작 버튼 비활성화
		self.btnPause = QPushButton('Pause', self) # 프로그램 중지 버튼 설정
		self.btnPause.resize(self.btnPause.sizeHint() * 1.25)
		self.btnPause.setFixedWidth(130)
		self.btnPause.move(160, self.size_y - 50)
		self.btnPause.clicked.connect(self.pause_func) # 프로그램 중지 함수 적용
		self.btnPause.setDisabled(True) # 프로그램 중지 버튼 비활성화
		self.btnExit = QPushButton('Exit', self) # 프로그램 종료 버튼 설정
		self.btnExit.resize(self.btnExit.sizeHint() * 1.25)
		self.btnExit.setFixedWidth(130)
		self.btnExit.move(310, self.size_y - 50)
		self.btnExit.clicked.connect(self.exit_func) # 프로그램 종료 함수 적용
		self.btnCheck = QPushButton('Check', self) # 프로그램 위치 및 크기 체크 버튼 설정
		self.btnCheck.setFixedWidth(50)
		self.btnCheck.setFixedHeight(50)
		self.btnCheck.move(395, 35)
		self.btnCheck.clicked.connect(self.check_pos_size_func) # 프로그램 위치 및 크기 체크 함수 적용

	def setupLabel(self): # 레이블 설정 함수
		title = 'Maplestory LieDetector  ver 1.0 by.KHW' # 제목 레이블
		self.label_title = QLabel(title, self) # 제목 레이블 설정
		self.label_title.move(self.size_x/4, 10)
		self.label_title.resize(230, 15)

	def setupEdit(self): # 에디트 설정 함수
		self.lineEditLabel_application_program_maple_work_name = QLabel('Maplestory Application Program Work Name : ', self) # 메이플 응용 프로그램 작업명 레이블 설정
		self.lineEditLabel_application_program_maple_work_name.move(10, 40)
		self.lineEditLabel_application_program_maple_work_name.resize(260, 15)
		self.lineEdit_application_program_maple_work_name = QLineEdit(self.application_program_maple_work_name, self) # 메이플 응용 프로그램 작업명 에디트 설정
		self.lineEdit_application_program_maple_work_name.move(272, 37)
		self.lineEdit_application_program_maple_work_name.resize(120, 20)
		self.lineEditLabel_application_program_kakao_work_name = QLabel('KakaoTalk Application Program Work Name(Chat Room) : ', self) # 카카오톡 응용 프로그램 작업명(채팅방 이름) 레이블 설정
		self.lineEditLabel_application_program_kakao_work_name.move(10, 65)
		self.lineEditLabel_application_program_kakao_work_name.resize(330, 15)
		self.lineEdit_application_program_kakao_work_name = QLineEdit(self.application_program_kakao_work_name, self) # 카카오톡 응용 프로그램 작업명(채팅방 이름) 에디트 설정
		self.lineEdit_application_program_kakao_work_name.move(342, 62)
		self.lineEdit_application_program_kakao_work_name.resize(50, 20)
		self.lineEditLabel_template_image_file = QLabel('LieDetector Template Image File : ', self) # 거짓말 탐지기 이미지 템플릿 파일 레이블 설정
		self.lineEditLabel_template_image_file.move(10, 90)
		self.lineEditLabel_template_image_file.resize(190, 15)
		self.lineEdit_template_image_file = QLineEdit(self.template_image_file, self) # 거짓말 탐지기 이미지 템플릿 파일 에디트 설정
		self.lineEdit_template_image_file.move(205, 87)
		self.lineEdit_template_image_file.resize(240, 20)
		self.lineEdit_template_image_file.setDisabled(True) # 거짓말 탐지기 이미지 템플릿 파일 에디트 비활성화
		self.lineEditLabel_suspend_continue_code = QLabel('Maplestory Macro Restart Code : ', self) # 메이플 매크로 재개 코드 레이블 설정
		self.lineEditLabel_suspend_continue_code.move(10, 115)
		self.lineEditLabel_suspend_continue_code.resize(190, 15)
		self.lineEdit_suspend_continue_code = QLineEdit(unicode(self.suspend_continue_code, 'utf-8'), self) # 메이플 매크로 재개 코드 에디트 설정
		self.lineEdit_suspend_continue_code.move(202, 112)
		self.lineEdit_suspend_continue_code.resize(50, 20)
		self.lineEdit_suspend_continue_code.setDisabled(True) # 메이플 매크로 재개 코드 에디트 비활성화
		self.lineEditLabel_macro_pause_restart = QLabel('Macro Pause & Restart : ', self) # 메이플 매크로 중지 및 재시작 단축키 레이블 설정
		self.lineEditLabel_macro_pause_restart.move(261, 115)
		self.lineEditLabel_macro_pause_restart.resize(140, 15)
		self.lineEdit_macro_pause_restart = QLineEdit(self.macro_pause_restart, self) # 메이플 매크로 중지 및 재시작 단축키 에디트 설정
		self.lineEdit_macro_pause_restart.move(405, 112)
		self.lineEdit_macro_pause_restart.resize(40, 20)
		self.lineEdit_macro_pause_restart.setDisabled(True) # 메이플 매크로 재개 코드 에디트 비활성화

	def setupStatusBar(self): # 상태 표시줄 설정 함수
		self.statusBar = QStatusBar(self) # 상태 표시줄 설정
		self.setStatusBar(self.statusBar)
		self.statusBar.showMessage('Not Setted') # 초기 상태 표시줄 내용

	def check_pos_size_func(self): # 프로그램 위치 및 크기 체크 함수
		try:
			self.application_program_maple_work_name = str(self.lineEdit_application_program_maple_work_name.text()).lower() # 설정한 메이플 응용 프로그램 작업명 저장
			self.application_program_kakao_work_name = unicode(self.lineEdit_application_program_kakao_work_name.text().toUtf8(),'utf8', 'ignore').encode('cp949') # 설정한 카카오톡 응용 프로그램 작업명(채팅방 이름) 저장
			state, prog_pos_x, prog_pos_y, prog_size_x, prog_size_y = myMacro.get_program_pos_size(self.application_program_maple_work_name) # 메이플 프로그램 위치 및 크기 저장
			if state == True: # 메이플 프로그램의 위치 및 크기를 제대로 찾았을 경우
				if self.application_program_kakao_work_name != '': # 카카오톡 응용 프로그램 작업명(채팅방 이름)이 공백이 아닐 경우
					state2, prog_pos_x2, prog_pos_y2, prog_size_x2, prog_size_y2 = myMacro.get_program_pos_size(self.application_program_kakao_work_name) # 카카오톡(채팅방) 프로그램 위치 및 크기 저장
					if state2 == True: # 카카오톡(채팅방) 프로그램의 위치 및 크기를 제대로 찾았을 경우
						self.btnStart.setEnabled(True) # 프로그램 동작 버튼 활성화
						self.lineEdit_template_image_file.setEnabled(True) # 거짓말 탐지기 이미지 템플릿 파일 에디트 활성화
						self.lineEdit_suspend_continue_code.setEnabled(True) # 메이플 매크로 재개 코드 에디트 활성화
						self.lineEdit_macro_pause_restart.setEnabled(True) # 메이플 매크로 중지 및 재시작 단축키 에디트 활성화
					else: # 카카오톡(채팅방) 프로그램의 위치 및 크기를 제대로 찾지 못했을 경우
						self.btnStart.setDisabled(True) # 프로그램 동작 버튼 비활성화
						self.lineEdit_template_image_file.setDisabled(True) # 거짓말 탐지기 이미지 템플릿 파일 에디트 비활성화
						self.lineEdit_suspend_continue_code.setDisabled(True) # 메이플 매크로 재개 코드 에디트 비활성화
						self.lineEdit_macro_pause_restart.setDisabled(True) # 메이플 매크로 중지 및 재시작 단축키 에디트 비활성화
						content = unicode('1. 프로그램(카카오톡(채팅방))이 실행 중이지 않을 경우 프로그램을 실행해야 합니다.\n2. 프로그램(카카오톡(채팅방))을 최소화하면 안 되고 화면에 떠있어야 합니다.\n3. 응용 프로그램 작업명을 올바르게 입력해야 합니다.', 'utf-8') # 에러 내용
						QMessageBox.critical(self, 'Error', content) # 에러 메세지 박스
				else: # 카카오톡 응용 프로그램 작업명(채팅방 이름)이 공백일 경우
					self.btnStart.setDisabled(True) # 프로그램 동작 버튼 비활성화
					self.lineEdit_template_image_file.setDisabled(True) # 거짓말 탐지기 이미지 템플릿 파일 에디트 비활성화
					self.lineEdit_suspend_continue_code.setDisabled(True) # 메이플 매크로 재개 코드 에디트 비활성화
					self.lineEdit_macro_pause_restart.setDisabled(True) # 메이플 매크로 중지 및 재시작 단축키 에디트 비활성화
					content = unicode('카카오톡 응용 프로그램 작업명(채팅방 이름)을 입력해야 합니다.', 'utf-8') # 에러 내용
					QMessageBox.critical(self, 'Error', content) # 에러 메세지 박스
			else: # 메이플, 카카오톡(채팅방) 프로그램의 위치 및 크기를 제대로 찾지 못했을 경우
				self.btnStart.setDisabled(True) # 프로그램 동작 버튼 비활성화
				self.lineEdit_template_image_file.setDisabled(True) # 거짓말 탐지기 이미지 템플릿 파일 에디트 비활성화
				self.lineEdit_suspend_continue_code.setDisabled(True) # 메이플 매크로 재개 코드 에디트 비활성화
				self.lineEdit_macro_pause_restart.setDisabled(True) # 메이플 매크로 중지 및 재시작 단축키 에디트 비활성화
				content = unicode('1. 프로그램(메이플)이 실행 중이지 않을 경우 프로그램을 실행해야 합니다.\n2. 프로그램(메이플)을 최소화하면 안 되고 화면에 떠있어야 합니다.\n3. 응용 프로그램 작업명을 올바르게 입력해야 합니다.', 'utf-8') # 에러 내용
				QMessageBox.critical(self, 'Error', content) # 에러 메세지 박스
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def exit_func(self): # 프로그램 종료 함수
		try:
			global exit_var
			global exit_var_pause
			exit_var = True # 스레드 종료 변수 값 설정
			exit_var_pause = True # restart_thread 스레드 종료 변수 값 설정
			self.start = False # 시작 버튼 눌림 여부 값 변경
			os.remove(os.getcwd() + '\\lieDetector_screenshot.png') # 메이플 화면 스크린샷 파일 삭제
			os.remove(os.getcwd() + '\\lieDetector_templateMatching.png') # 거짓말 탐지기 이미지 템플릿 파일 삭제
			os.remove(os.getcwd() + '\\captcha_screenshot.png') # 거짓말 탐지기 이미지 내 캡차 스크린샷 파일 삭제
			QApplication.quit() # 종료 이벤트 발생(QCoreApplication.instance().quit)
		except Exception, e:
			QApplication.quit() # 종료 이벤트 발생(QCoreApplication.instance().quit)

	def pause_func(self): # 프로그램 중지 함수
		try:
			global exit_var
			if self.start: # 프로그램이 동작중인 경우
				exit_var = True # 스레드 종료 변수 값 설정
				self.start = False # 시작 버튼 눌림 여부 값 변경
				self.statusBar.showMessage('Pause') # 상태 표시줄 내용 갱신
				self.btnStart.setEnabled(True) # 프로그램 동작 버튼 활성화
				self.btnPause.setDisabled(True) # 프로그램 중지 버튼 비활성화
				self.btnCheck.setEnabled(True) # 프로그램 위치 및 크기 체크 버튼 활성화
				self.lineEdit_application_program_maple_work_name.setEnabled(True) # 메이플 응용 프로그램 작업명 에디트 활성화
				self.lineEdit_application_program_kakao_work_name.setEnabled(True) # 카카오톡 응용 프로그램 작업명(채팅방 이름) 에디트 활성화
				self.lineEdit_template_image_file.setEnabled(True) # 거짓말 탐지기 이미지 템플릿 파일 에디트 활성화
				self.lineEdit_suspend_continue_code.setEnabled(True) # 메이플 매크로 재개 코드 에디트 활성화
				self.lineEdit_macro_pause_restart.setEnabled(True) # 메이플 매크로 중지 및 재시작 단축키 에디트 활성화
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def start_func(self): # 프로그램 동작 함수
		try:
			global exit_var
			if exit_var: # 스레드 종료 변수 값이 설정된 경우(중지 후 다시 시작했을 경우)
				exit_var = False # 스레드 종료 변수 값 초기화
			self.start = True # 시작 버튼 눌림 여부 값 변경
			self.statusBar.showMessage('Start') # 상태 표시줄 내용 갱신
			self.btnStart.setDisabled(True) # 프로그램 동작 버튼 비활성화
			self.btnPause.setEnabled(True) # 프로그램 중지 버튼 활성화
			self.btnCheck.setDisabled(True) # 프로그램 위치 및 크기 체크 버튼 비활성화
			self.lineEdit_application_program_maple_work_name.setDisabled(True) # 메이플 응용 프로그램 작업명 에디트 비활성화
			self.lineEdit_application_program_kakao_work_name.setDisabled(True) # 카카오톡 응용 프로그램 작업명(채팅방 이름) 에디트 비활성화
			self.lineEdit_template_image_file.setDisabled(True) # 거짓말 탐지기 이미지 템플릿 파일 에디트 비활성화
			self.lineEdit_suspend_continue_code.setDisabled(True) # 메이플 매크로 재개 코드 에디트 비활성화
			self.lineEdit_macro_pause_restart.setDisabled(True) # 메이플 매크로 중지 및 재시작 단축키 에디트 비활성화
			self.template_image_file = str(self.lineEdit_template_image_file.text()).lower() # 설정한 거짓말 탐지기 이미지 템플릿 파일 저장
			if '' == self.template_image_file: # 거짓말 탐지기 이미지 템플릿 파일을 설정하지 않았을 경우
				self.template_image_file = os.getcwd() + '\\lieDetector_templateMatching.png' # 디폴트 거짓말 탐지기 이미지 템플릿 파일 저장
				image_binary = icoBinary.maplestory_liedetector_template_image_file # 거짓말 탐지기 이미지 템플릿 파일 바이너리
				fp = open(self.template_image_file, 'wb') # 임시 아이콘 파일 생성
				fp.write(image_binary)
				fp.close()
			self.suspend_continue_code = unicode(self.lineEdit_suspend_continue_code.text().toUtf8(),'utf8', 'ignore') # 설정한 메이플 매크로 재개 코드 저장
			self.macro_pause_restart = str(self.lineEdit_macro_pause_restart.text()).lower() # 설정한 메이플 매크로 중지 및 재시작 단축키 저장
			th_lieDetect = threading.Thread(target=self.lieDetect_thread, args=()) # 거짓말 탐지기 탐지 및 알림 스레드 설정
			th_lieDetect.start() # 스레드 생성
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def stopMacro(self): # 매크로 중지할 때 필요한 작업을 수행하는 함수
		try:
			myMacro.keyboardInput(self.macro_pause_restart) # 메이플 매크로 중지 및 재시작 단축키 입력
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def imageUpload(self, prog_pos_x2, prog_pos_y2, prog_size_x2, prog_size_y2): # 거짓말 탐지기 이미지 내 캡차 스크린샷 파일을 카카오톡(채팅방)에 업로드하는 함수
		try:
			myMacro.move_mouse(prog_pos_x2 + self.kakao_image_open_button_minus_pos_x, prog_pos_y2 + prog_size_y2 - self.kakao_image_open_button_minus_pos_y) # 카카오톡 채팅방 좌측 하단에 있는 사진 전송 버튼으로 마우스 이동
			myMacro.click_mouse_left(0,0) # 카카오톡 채팅방 좌측 하단에 있는 사진 전송 버튼 좌클릭
			pyperclip.copy(self.captcha_screenshot_file) # 거짓말 탐지기 이미지 내 캡차 스크린샷 파일명(경로 포함) 클립보드에 저장
			time.sleep(2) # 업로드할 파일 선택 윈도우가 열릴 때까지 대기
			myMacro.keyboardInput_combination('ctrl', 'v') # Ctrl + v 입력해서 거짓말 탐지기 이미지 내 캡차 스크린샷 파일명(경로 포함) 입력
			myMacro.keyboardInput('enter') # enter 입력해서 거짓말 탐지기 이미지 내 캡차 스크린샷 파일 업로드
			return True # 업로드에 성공했을 경우의 반환
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신
			return False # 업로드에 실패했을 경우의 반환

	def distributeHangul(self, code): # 한글의 초성, 중성, 종성 분리하는 함수
		try:
			cho_list = [u'ㄱ', u'ㄲ', u'ㄴ', u'ㄷ', u'ㄸ', u'ㄹ', u'ㅁ', u'ㅂ', u'ㅃ', u'ㅅ',
						u'ㅆ', u'ㅇ', u'ㅈ', u'ㅉ', u'ㅊ', u'ㅋ', u'ㅌ', u'ㅍ', u'ㅎ'] # 초성 리스트
			jung_list = [u'ㅏ', u'ㅐ', u'ㅑ', u'ㅒ', u'ㅓ', u'ㅔ', u'ㅕ', u'ㅖ', u'ㅗ', u'ㅘ', u'ㅙ', 
						 u'ㅚ', u'ㅛ', u'ㅜ', u'ㅝ', u'ㅞ', u'ㅟ', u'ㅠ', u'ㅡ', u'ㅢ', u'ㅣ'] # 중성 리스트
			jong_list = [u'', u'ㄱ', u'ㄲ', u'ㄳ', u'ㄴ', u'ㄵ', u'ㄶ', u'ㄷ', u'ㄹ', u'ㄺ', u'ㄻ', u'ㄼ', u'ㄽ', u'ㄾ', u'ㄿ',
						 u'ㅀ', u'ㅁ', u'ㅂ', u'ㅄ', u'ㅅ', u'ㅆ', u'ㅇ', u'ㅈ', u'ㅊ', u'ㅋ', u'ㅌ', u'ㅍ', u'ㅎ'] # 종성 리스트
			code_list = [] # 분리된 초성, 중성, 종성이 차례대로 저장될 리스트
			for i in range(0, len(code)): # 한글의 글자 수 만큼 반복
				unicode_value = ord(code[i]) - 0xAC00 # 한 글자의 유니코드 값 저장
				jong = unicode_value % 28 # 종성 인덱스 저장
				jung = ((unicode_value - jong) / 28) % 21 # 중성 인덱스 저장
				cho = (((unicode_value - jong) / 28) - jung) / 21 # 초성 인덱스 저장
				code_list.append(cho_list[cho]) # 초성 리스트에 추가
				if jung_list[jung] == u'ㅘ': # 중성에서 분리할 수 있는 문자일 경우
					code_list.append(u'ㅗ') # 첫 번째 분리 문자 중성 리스트에 추가
					code_list.append(u'ㅏ') # 두 번째 분리 문자 중성 리스트에 추가
				elif jung_list[jung] == u'ㅙ':
					code_list.append(u'ㅗ')
					code_list.append(u'ㅐ')
				elif jung_list[jung] == u'ㅚ':
					code_list.append(u'ㅗ')
					code_list.append(u'ㅣ')
				elif jung_list[jung] == u'ㅝ':
					code_list.append(u'ㅜ')
					code_list.append(u'ㅓ')
				elif jung_list[jung] == u'ㅞ':
					code_list.append(u'ㅜ')
					code_list.append(u'ㅔ')
				elif jung_list[jung] == u'ㅟ':
					code_list.append(u'ㅜ')
					code_list.append(u'ㅣ')
				elif jung_list[jung] == u'ㅢ':
					code_list.append(u'ㅡ')
					code_list.append(u'ㅣ')
				else: # 중성에서 분리할 수 없는 문자일 경우
					code_list.append(jung_list[jung]) # 중성 리스트에 추가
				if jong_list[jong] == u'': # 종성이 없을 경우(받침이 없는 경우)
					continue
				elif jong_list[jong] == u'ㄳ': # 종성에서 분리할 수 있는 문자일 경우
					code_list.append(u'ㄱ') # 첫 번째 분리 문자 종성 리스트에 추가
					code_list.append(u'ㅅ') # 두 번째 분리 문자 종성 리스트에 추가
				elif jong_list[jong] == u'ㄵ':
					code_list.append(u'ㄴ')
					code_list.append(u'ㅈ')
				elif jong_list[jong] == u'ㄶ':
					code_list.append(u'ㄴ')
					code_list.append(u'ㅎ')
				elif jong_list[jong] == u'ㄺ':
					code_list.append(u'ㄹ')
					code_list.append(u'ㄱ')
				elif jong_list[jong] == u'ㄻ':
					code_list.append(u'ㄹ')
					code_list.append(u'ㅁ')
				elif jong_list[jong] == u'ㄼ':
					code_list.append(u'ㄹ')
					code_list.append(u'ㅂ')
				elif jong_list[jong] == u'ㄽ':
					code_list.append(u'ㄹ')
					code_list.append(u'ㅅ')
				elif jong_list[jong] == u'ㄾ':
					code_list.append(u'ㄹ')
					code_list.append(u'ㅌ')
				elif jong_list[jong] == u'ㄿ':
					code_list.append(u'ㄹ')
					code_list.append(u'ㅍ')
				elif jong_list[jong] == u'ㅀ':
					code_list.append(u'ㄹ')
					code_list.append(u'ㅎ')
				elif jong_list[jong] == u'ㅄ':
					code_list.append(u'ㅂ')
					code_list.append(u'ㅅ')
				else: # 종성에서 분리할 수 없는 문자일 경우
					code_list.append(jong_list[jong]) # 종성 리스트에 추가
			return code_list # 분리된 초성, 중성, 종성이 차례대로 저장된 리스트 반환
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신
			return [] # 한글의 초성, 중성, 종성 분리에 실패했을 경우의 반환

	def receiveCode(self, prog_pos_x2, prog_pos_y2, prog_size_x2, prog_size_y2): # 거짓말 탐지기 해제 코드 받은 후 저장하는 함수
		try:
			exit = 0 # 탈출 변수 초기화
			while exit <= 60: # 탈출 값이 60 이상일 경우 반복문 탈출(카카오톡(채팅방)에 카톡 확인을 못했거나 오탐 등의 이유로 거짓말 탐지기 해제 코드를 전송하지 않아도 특정 시간이 지나면 매크로를 재개하기 위해 탈출 필요)
				kakao_receive_color_pos_x = prog_pos_x2 + prog_size_x2 - self.kakao_receive_color_minus_pos_x # 거짓말 탐지기 해제 코드 전송했을 때 글자 주변에 나타나는 색깔이 있는 특정 지점의 x 좌표
				kakao_receive_color_pos_y = prog_pos_y2 + prog_size_y2 - self.kakao_receive_color_minus_pos_y # 거짓말 탐지기 해제 코드 전송했을 때 글자 주변에 나타나는 색깔이 있는 특정 지점의 y 좌표
				kakao_receive_code_pos_x = prog_pos_x2 + prog_size_x2 - self.kakao_receive_code_minus_pos_x # 거짓말 탐지기 해제 코드 전송했을 때 나타나는 글자의 특정 지점의 x 좌표
				kakao_receive_code_pos_y = prog_pos_y2 + prog_size_y2 - self.kakao_receive_code_minus_pos_y # 거짓말 탐지기 해제 코드 전송했을 때 나타나는 글자의 특정 지점의 y 좌표
				kakao_receive_color_pos_pixel = QPixmap.grabWindow(QApplication.desktop().winId()).toImage().pixel(kakao_receive_color_pos_x, kakao_receive_color_pos_y) # 거짓말 탐지기 해제 코드 전송했을 때 글자 주변에 나타나는 색깔이 있는 특정 지점의 픽셀 값(16진수) 저장
				kakao_receive_color_pixel_color = (qBlue(kakao_receive_color_pos_pixel) * 65536 + qGreen(kakao_receive_color_pos_pixel) * 256 + qRed(kakao_receive_color_pos_pixel)) # 픽셀 값 10진수로 변경
				if self.kakao_receive_color == kakao_receive_color_pixel_color: # 거짓말 탐지기 해제 코드 전송했을 때 글자 주변에 나타나는 색깔이 설정한 색일 경우(카카오톡 기본 테마를 사용하고 있어서 전송된 글자 주변에 나타나는 색깔이 노란색임. 평소에는 해당 위치가 배경색이나 특정 이미지의 색깔이지만 문자가 전송되면 해당 부분이 노란색으로 변경되는 것을 이용함. 만약 PC 카카오톡 테마를 바꿔서 전송된 글자 주변의 색깔이 다를 경우 그에 맞게 설정해야 함)
					myMacro.move_mouse(kakao_receive_code_pos_x, kakao_receive_code_pos_y) # 거짓말 탐지기 해제 코드 전송했을 때 나타나는 글자의 위치로 마우스 이동
					myMacro.click_mouse_left(0,0) # 거짓말 탐지기 해제 코드 전송했을 때 나타나는 글자 더블 클릭
					myMacro.click_mouse_left(0,0)
					time.sleep(0.1) # 더블 클릭 후 드래그 박스가 보일 때까지 잠시 대기
					myMacro.keyboardInput_combination('ctrl', 'c') # Ctrl + c 입력해서 거짓말 탐지기 해제 코드 클립보드에 저장
					code = clipboard.paste() # 클립보드에 저장된 거짓말 탐지기 해제 코드 저장
					code_list = self.distributeHangul(code) # 거짓말 탐지기 해제 코드의 초성, 중성, 종성 분리해서 리스트에 저장
					suspend_continue_code_list = self.distributeHangul(self.suspend_continue_code) # 거짓말 탐지기 오탐 시 현재 작업(거짓말 탐지기 해제 코드 입력하는 작업)을 중지하고 매크로를 다시 재개하는 코드의 초성, 중성, 종성 분리해서 리스트에 저장
					suspend_continue_count = 0 # 거짓말 탐지기 해제 코드가 거짓말 탐지기 오탐 시 현재 작업을 중지하고 매크로를 다시 재개하는 코드와 같은지 판단하기 위한 카운트 변수
					if len(code_list) == 0 or len(suspend_continue_code_list) == 0: # 거짓말 탐지기 해제 코드 또는 매크로 재개 코드의 초성, 중성, 종성 분리에 실패했을 경우
						return False # 거짓말 탐지기 해제 코드 또는 매크로 재개 코드의 초성, 중성, 종성 분리에 실패했을 경우의 반환
					if len(code_list) == len(suspend_continue_code_list): # 거짓말 탐지기 해제 코드와 거짓말 탐지기 오탐 시 현재 작업을 중지하고 매크로를 다시 재개하는 코드의 길이가 같을 경우
						for i in range(0, len(suspend_continue_code_list)): # 거짓말 탐지기 오탐 시 현재 작업을 중지하고 매크로를 다시 재개하는 코드의 길이만큼 반복
							if code_list[i] == suspend_continue_code_list[i]: # 거짓말 탐지기 해제 코드와 거짓말 탐지기 오탐 시 현재 작업을 중지하고 매크로를 다시 재개하는 코드의 문자가 같을 경우
								suspend_continue_count += 1 # 카운트 변수 값 증가
							else: # 거짓말 탐지기 해제 코드와 거짓말 탐지기 오탐 시 현재 작업을 중지하고 매크로를 다시 재개하는 코드의 문자가 다를 경우
								break
						if suspend_continue_count == len(suspend_continue_code_list): # 카운트 변수 값이 거짓말 탐지기 오탐 시 현재 작업을 중지하고 매크로를 다시 재개하는 코드의 길이와 같을 경우(거짓말 탐지기 해제 코드와 거짓말 탐지기 오탐 시 현재 작업을 중지하고 매크로를 다시 재개하는 코드의 문자들이 모두 일치할 경우)
							return False # 현재 작업 중지 및 매크로 재개를 위해 의도적으로 실패 값 반환
					return code_list # 거짓말 탐지기 해제 코드의 초성, 중성, 종성이 저장된 리스트 반환
				exit += 1 # 탈출 변수 값 증가
				time.sleep(1) # 부하를 줄이기 위한 딜레이
			return False # 거짓말 탐지기 해제 코드를 전송받지 못했을 경우의 반환
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신
			return False # 거짓말 탐지기 해제 코드를 전송받지 못했을 경우의 반환

	def inputCode(self, code_list, prog_pos_x, prog_pos_y, detected_pos): # 거짓말 탐지기 해제 코드를 입력하는 함수
		try:
			myMacro.move_mouse(prog_pos_x + detected_pos[0] + self.captcha_screenshot_x/2, prog_pos_y + detected_pos[1] + self.captcha_screenshot_y/2) # 메이플 화면 내의 거짓말 탐지기 이미지 중앙으로 마우스 이동
			myMacro.click_mouse_left(0,0) # 거짓말 탐지기 이미지 더블 클릭
			myMacro.click_mouse_left(0,0)
			time.sleep(0.3) # 딜레이
			myMacro.input_keyboard('hanguel') # 한/영 키 입력(거짓말 탐지기의 경우 한글만 나오기 때문에 영어로 키가 설정돼 있어야 함(디폴트 영어))
			time.sleep(0.3) # 딜레이
			for i in range(0, len(code_list)): # 거짓말 탐지기 해제 코드의 초성, 중성, 종성의 개수만큼 반복
				input_key = '' # 입력할 키 저장 변수
				if code_list[i] == u'ㅂ': # 해당 문자일 경우
					input_key = 'q' # 입력할 키 저장
				elif code_list[i] == u'ㅃ': # 쌍자음, 쌍모음일 경우
					input_key = 'q' # 입력할 키 저장
					myMacro.keyboardInput_combination('shift', input_key) # Shift + input_key 입력
					continue
				elif code_list[i] == u'ㅈ':
					input_key = 'w'
				elif code_list[i] == u'ㅉ':
					input_key = 'w'
					myMacro.keyboardInput_combination('shift', input_key)
					continue
				elif code_list[i] == u'ㄷ':
					input_key = 'e'
				elif code_list[i] == u'ㄸ':
					input_key = 'e'
					myMacro.keyboardInput_combination('shift', input_key)
					continue
				elif code_list[i] == u'ㄱ':
					input_key = 'r'
				elif code_list[i] == u'ㄲ':
					input_key = 'r'
					myMacro.keyboardInput_combination('shift', input_key)
					continue
				elif code_list[i] == u'ㅅ':
					input_key = 't'
				elif code_list[i] == u'ㅆ':
					input_key = 't'
					myMacro.keyboardInput_combination('shift', input_key)
					continue
				elif code_list[i] == u'ㅛ':
					input_key = 'y'
				elif code_list[i] == u'ㅕ':
					input_key = 'u'
				elif code_list[i] == u'ㅑ':
					input_key = 'i'
				elif code_list[i] == u'ㅐ':
					input_key = 'o'
				elif code_list[i] == u'ㅒ':
					input_key = 'o'
					myMacro.keyboardInput_combination('shift', input_key)
					continue
				elif code_list[i] == u'ㅔ':
					input_key = 'p'
				elif code_list[i] == u'ㅖ':
					input_key = 'p'
					myMacro.keyboardInput_combination('shift', input_key)
					continue
				elif code_list[i] == u'ㅁ':
					input_key = 'a'
				elif code_list[i] == u'ㄴ':
					input_key = 's'
				elif code_list[i] == u'ㅇ':
					input_key = 'd'
				elif code_list[i] == u'ㄹ':
					input_key = 'f'
				elif code_list[i] == u'ㅎ':
					input_key = 'g'
				elif code_list[i] == u'ㅗ':
					input_key = 'h'
				elif code_list[i] == u'ㅓ':
					input_key = 'j'
				elif code_list[i] == u'ㅏ':
					input_key = 'k'
				elif code_list[i] == u'ㅣ':
					input_key = 'l'
				elif code_list[i] == u'ㅋ':
					input_key = 'z'
				elif code_list[i] == u'ㅌ':
					input_key = 'x'
				elif code_list[i] == u'ㅊ':
					input_key = 'c'
				elif code_list[i] == u'ㅍ':
					input_key = 'v'
				elif code_list[i] == u'ㅠ':
					input_key = 'b'
				elif code_list[i] == u'ㅜ':
					input_key = 'n'
				elif code_list[i] == u'ㅡ':
					input_key = 'm'
				myMacro.keyboardInput(input_key) # 키 입력
				time.sleep(0.1) # 딜레이
			myMacro.input_keyboard('hanguel') # 영어로 키를 초기화 하기 위해 한/영 키 입력
			time.sleep(0.1) # 딜레이
			myMacro.keyboardInput('enter') # 거짓말 탐지기 해제 코드 입력 후 마지막으로 엔터 입력
			time.sleep(2) # 거짓말 탐지기 해제 후 나오는 창이 나올 때까지 대기
			myMacro.keyboardInput('enter') # 거짓말 탐지기 해제 후 나오는 창을 닫기 위해 엔터 입력
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def startMacro(self, prog_pos_x, prog_pos_y, prog_size_x, prog_size_y): # 매크로 시작할 때 필요한 작업을 수행하는 함수
		try:
			myMacro.move_mouse(prog_pos_x + prog_size_x/20, prog_pos_y + prog_size_y/20) # 메이플 프로그램 화면 좌측 상단으로 마우스 이동
			myMacro.click_mouse_left(0,0) # 메이플 프로그램 화면 좌측 상단 좌클릭
			myMacro.keyboardInput(self.macro_pause_restart) # 메이플 매크로 중지 및 재시작 단축키 입력
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def lieDetect_thread(self): # 거짓말 탐지기 탐지 및 알림 스레드
		global exit_var
		while True:
			try:
				sem.acquire() # 임계영역 생성
				if exit_var or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
					sem.release() # 임계영역 해제
					return # 스레드 종료
				elif self.start == True: # 매크로가 동작중인 경우
					state, prog_pos_x, prog_pos_y, prog_size_x, prog_size_y = myMacro.get_program_pos_size(self.application_program_maple_work_name) # 메이플 프로그램의 위치 및 크기 저장
					if state == True: # 메이플 프로그램의 위치 및 크기를 제대로 찾았을 경우
						myMacro.getScreenshot(self.full_screenshot_file, prog_pos_x, prog_pos_y, prog_pos_x + prog_size_x, prog_pos_y + prog_size_y) # 메이플 화면 스크린샷 후 파일로 저장
						state2, detected_pos = myMacro.templateMatching(self.full_screenshot_file, self.template_image_file) # 템플릿 매칭을 통해 거짓말 탐지기 이미지 검출
						if state2 == True: # 거짓말 탐지기 이미지를 검출했을 경우
							self.stopMacro() # 매크로 중지할 때 필요한 작업 수행
							myMacro.getScreenshot(self.captcha_screenshot_file, prog_pos_x + detected_pos[0] + self.captcha_screenshot_start_x, prog_pos_y + detected_pos[1] + self.captcha_screenshot_start_y, prog_pos_x + detected_pos[0] + self.captcha_screenshot_x, prog_pos_y + detected_pos[1] + self.captcha_screenshot_y) # 검출한 거짓말 탐지기 이미지 내 캡차 스크린샷 후 파일로 저장
							state3, prog_pos_x2, prog_pos_y2, prog_size_x2, prog_size_y2 = myMacro.get_program_pos_size(self.application_program_kakao_work_name) # 카카오톡(채팅방) 프로그램의 위치 및 크기 저장
							if state3 == True: # 카카오톡(채팅방) 프로그램의 위치 및 크기를 제대로 찾았을 경우
								state4 = self.imageUpload(prog_pos_x2, prog_pos_y2, prog_size_x2, prog_size_y2) # 거짓말 탐지기 이미지 내 캡차 스크린샷 파일을 카카오톡(채팅방)에 업로드
								if state4 == True: # 거짓말 탐지기 이미지 내 캡차 스크린샷 파일을 카카오톡(채팅방)에 업로드 했을 경우
									code_list = self.receiveCode(prog_pos_x2, prog_pos_y2, prog_size_x2, prog_size_y2) # 거짓말 탐지기 해제 코드 받은 후 저장
									if code_list: # 거짓말 탐지기 해제 코드를 제대로 받았을 경우
										self.inputCode(code_list, prog_pos_x, prog_pos_y, detected_pos) # 거짓말 탐지기 해제 코드 입력
										self.startMacro(prog_pos_x, prog_pos_y, prog_size_x, prog_size_y) # 매크로 시작할 때 필요한 작업 수행
									else: # 거짓말 탐지기 해제 코드를 받지 못한 경우
										self.startMacro(prog_pos_x, prog_pos_y, prog_size_x, prog_size_y) # 매크로 시작할 때 필요한 작업 수행
								else: # 거짓말 탐지기 이미지 내 캡차 스크린샷 파일을 카카오톡(채팅방)에 업로드 하지 못했을 경우
									self.startMacro(prog_pos_x, prog_pos_y, prog_size_x, prog_size_y) # 매크로 시작할 때 필요한 작업 수행
							else: # 카카오톡(채팅방) 프로그램의 위치 및 크기를 제대로 찾지 못했을 경우
								self.startMacro(prog_pos_x, prog_pos_y, prog_size_x, prog_size_y) # 매크로 시작할 때 필요한 작업 수행
				time.sleep(1) # 부하를 줄이기 위한 딜레이
				sem.release() # 임계영역 해제
			except Exception, e:
				sem.release() # 임계영역 해제
				pass

def main():
	try:
		app = QApplication(sys.argv)
		gui = MacroClass() # 객체 생성
		gui.show() # 윈도우 화면에 표시
		os.remove(os.getcwd() + '\\tmp_title.ico') # 임시 아이콘 파일 삭제
		sys.exit(app.exec_()) # 종료 이벤트 발생 시 프로그램 종료
	except Exception, e:
		print '[-] ', e

if __name__ == '__main__':
	main()