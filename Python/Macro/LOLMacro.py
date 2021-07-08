#-*- coding: utf-8 -*-
import os
import sys
import time
import win32api
import win32con
import threading
import keyboard
import pyperclip
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import icoBinary
import myMacro
import myMacro2

sem = threading.Semaphore(10) # 세마포어 설정
exit_var = False # 스레드 종료 변수
exit_var_pause = False # restart_thread 스레드 종료 변수

class MacroClass(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self.actives = [] # 설정 파일의 내용이 저장될 리스트
		self.start = False # 시작 버튼 눌림 여부
		self.check_size1 = False # 창 크기 1024 x 576 체크 여부
		self.check_size2 = False # 창 크기 1280 x 720 체크 여부
		self.check_active1 = False # 동작 1 체크 여부
		self.check_active2 = False # 동작 2 체크 여부
		self.input_duration_time = 0.3 # 입력 지속 시간
		self.position = '미드' # 포지션
		self.champion = '제드' # 챔피언
		self.application_program_work_name = 'league of legends' # 응용 프로그램 작업명
		self.program_size_x = 0 # 프로그램 가로 크기
		self.program_size_y = 0 # 프로그램 세로 크기
		self.accept_x_right = 0 # 수락 버튼 범위 최우측
		self.accept_x_left = 0 # 수락 버튼 범위 최좌측
		self.accept_y_up = 0 # 수락 버튼 범위 최상단
		self.accept_y_down = 0 # 수락 버튼 범위 최하단
		self.chat_x_right = 0 # 채팅창 범위 최우측
		self.chat_x_left = 0 # 채팅창 범위 최좌측
		self.chat_y_up = 0 # 채팅창 범위 최상단
		self.chat_y_down = 0 # 채팅창 범위 최하단
		self.chat_middle_pos_x = 0 # 채팅창 중앙 x좌표
		self.chat_middle_pos_y = 0 # 채팅창 중앙 y좌표
		self.name_order_middle_pos_x = 0 # 이름순 정렬 버튼 중앙 x좌표
		self.name_order_middle_pos_y = 0 # 이름순 정렬 버튼 중앙 y좌표
		self.workmanship_order_middle_pos_x = 0 # 숙련도 기준 정렬 버튼 중앙 x좌표
		self.workmanship_order_middle_pos_y = 0 # 숙련도 기준 정렬 버튼 중앙 y좌표
		self.champion_search_middle_pos_x = 0 # 챔피언 검색창 중앙 x좌표
		self.champion_search_middle_pos_y = 0 # 챔피언 검색창 중앙 y좌표
		self.champion_box_middle_pos_x_active1 = 0 # 챔피언 박스 중앙 x좌표(동작 1)
		self.champion_box_middle_pos_y_active1 = 0 # 챔피언 박스 중앙 y좌표(동작 1)
		self.champion_box_middle_pos_x_active2 = 0 # 챔피언 박스 중앙 x좌표(동작 2)
		self.champion_box_middle_pos_y_active2 = 0 # 챔피언 박스 중앙 y좌표(동작 2)
		self.pause_restart = 'F12' # 중지 및 재시작 키
		self.size_x = 600 # 프로그램의 가로 크기
		self.size_y = 370 # 프로그램의 세로 크기
		self.pos_x = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)/2 - self.size_x/2 # 처음 프로그램이 나타나는 x좌표(디폴트 중앙으로 설정)
		self.pos_y = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)/2 - self.size_y/1.5 # 처음 프로그램이 나타나는 y좌표(디폴트 중앙 조금 위로 설정)
		self.setupWindow() # 윈도우 설정
		self.setupButton() # 버튼 설정
		self.setupLabel() # 레이블 설정
		self.setupEdit() # 에디트 설정
		self.setupRadioBox() # 라디오 박스 설정
		self.setupCheckBox() # 체크 박스 설정
		self.setupStatusBar() # 상태 표시줄 설정

	def setupWindow(self): # 윈도우 특성 설정 함수
		title = 'LOL Macro Program' # 타이틀
		self.setWindowTitle(title) # 윈도우 타이클 설정
		self.setGeometry(self.pos_x, self.pos_y, self.size_x, self.size_y) # 윈도우 위치, 크기 설정
		ico_binary = icoBinary.title_ico_binary_lol # 타이틀 아이콘 바이너리
		fp = open(os.getcwd() + '\\tmp_title.ico', 'wb') # 임시 아이콘 파일 생성
		fp.write(ico_binary)
		fp.close()
		self.setWindowIcon(QIcon(os.getcwd() + '\\tmp_title.ico')) # 타이틀 아이콘 설정
		self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowMinMaxButtonsHint) # 닫기 버튼 비활성화
		self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint) # 최대화 버튼 비활성화
		self.setFixedSize(self.size_x, self.size_y) # 화면 크기 변경 금지

	def setupButton(self): # 버튼 설정 함수
		self.btnFile = QPushButton('File Open', self) # 설정 파일 오픈 버튼 설정
		self.btnFile.resize(self.btnFile.sizeHint() * 1.25)
		self.btnFile.move(10, self.size_y - 60)
		self.btnFile.clicked.connect(self.setup_file) # 설정 파일에서 설정 정보 가져오는 함수 적용
		self.btnFile.setDisabled(True) # 설정 파일 오픈 버튼 비활성화
		self.btnStart = QPushButton('Start', self) # 매크로 동작 버튼 설정
		self.btnStart.resize(self.btnStart.sizeHint() * 1.25)
		self.btnStart.move(110, self.size_y - 60)
		self.btnStart.clicked.connect(self.start_func) # 매크로 동작 함수 적용
		self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
		self.btnPause = QPushButton('Pause', self) # 매크로 중지 버튼 설정
		self.btnPause.resize(self.btnPause.sizeHint() * 1.25)
		self.btnPause.move(210, self.size_y - 60)
		self.btnPause.clicked.connect(self.pause_func) # 매크로 중지 함수 적용
		self.btnPause.setDisabled(True) # 매크로 중지 버튼 비활성화
		self.btnExit = QPushButton('Exit', self) # 매크로 종료 버튼 설정
		self.btnExit.resize(self.btnExit.sizeHint() * 1.25)
		self.btnExit.move(310, self.size_y - 60)
		self.btnExit.clicked.connect(self.exit_func) # 매크로 종료 함수 적용
		self.btnCheck = QPushButton('Check', self) # 프로그램 위치 및 크기 체크 버튼 설정
		self.btnCheck.resize(self.btnCheck.sizeHint() / 1.15)
		self.btnCheck.move(self.size_x - 177, 80)
		self.btnCheck.clicked.connect(self.check_pos_size_func) # 프로그램 위치 및 크기 체크 함수 적용

	def setupLabel(self): # 레이블 설정 함수
		title = 'LOL Macro  ver 1.0 by.KHW' # 제목 레이블
		self.label_title = QLabel(title, self) # 제목 레이블 설정
		self.label_title.move(self.size_x/2.7, 10)
		self.label_title.resize(170, 15)
		content = unicode('동작 1 : 설정한 포지션 및 숙련도 제일 높은 챔피언 픽\n1. 수락 버튼 수동 클릭\n2. 수락 버튼 클릭 직후부터 설정한 시간 동안 채팅창에 포지션 자동 입력\n3. 숙련도 제일 높은 챔피언 자동 픽\n\n동작 2 : 설정한 포지션 및 챔피언 픽\n1. 수락 버튼 수동 클릭 시 채팅창 박스 자동 표시\n2. 채팅창 박스 내부 수동 클릭\n3. 채팅창 내부 클릭 직후부터 설정한 시간 동안 채팅창에 포지션 자동 입력\n4. 설정한 챔피언 자동 픽', 'utf-8') # 내용 레이블
		self.label_content = QLabel(content, self) # 내용 레이블 설정
		self.label_content.move(10, 35)
		self.label_content.resize(400, 140)

	def setupEdit(self): # 에디트 설정 함수
		self.lineEditLabel_pause_restart = QLabel('Pause & Restart : ', self) # 중지 및 재시작 키 레이블 설정
		self.lineEditLabel_pause_restart.move(self.size_x - 165, 35)
		self.lineEditLabel_pause_restart.resize(100, 15)
		self.lineEdit_pause_restart = QLineEdit(self.pause_restart, self) # 중지 및 재시작 키 에디트 설정
		self.lineEdit_pause_restart.move(self.size_x - 60, 32)
		self.lineEdit_pause_restart.resize(50, 20)
		self.lineEditLabel_input_duration_time = QLabel(unicode('Input Duration Time : ', 'utf-8'), self) # 입력 지속 시간 레이블 설정
		self.lineEditLabel_input_duration_time.move(self.size_x - 182, 153)
		self.lineEditLabel_input_duration_time.resize(150, 15)
		self.lineEdit_input_duration_time = QLineEdit(str(self.input_duration_time), self) # 입력 지속 시간 에디트 설정
		self.lineEdit_input_duration_time.move(self.size_x - 60, 150)
		self.lineEdit_input_duration_time.resize(50, 20)
		self.lineEdit_input_duration_time.setDisabled(True) # 입력 지속 시간 에디트 비활성화
		self.lineEditLabel_position = QLabel(unicode('Position : ', 'utf-8'), self) # 포지션 레이블 설정
		self.lineEditLabel_position.move(self.size_x - 118, 178)
		self.lineEditLabel_position.resize(60, 15)
		self.lineEdit_position = QLineEdit(unicode(self.position, 'utf-8'), self) # 포지션 에디트 설정
		self.lineEdit_position.move(self.size_x - 60, 175)
		self.lineEdit_position.resize(50, 20)
		self.lineEdit_position.setDisabled(True) # 포지션 에디트 비활성화
		self.lineEditLabel_champion = QLabel(unicode('Champion : ', 'utf-8'), self) # 챔피언 레이블 설정
		self.lineEditLabel_champion.move(self.size_x - 130, 203)
		self.lineEditLabel_champion.resize(70, 15)
		self.lineEdit_champion = QLineEdit(unicode(self.champion, 'utf-8'), self) # 챔피언 에디트 설정
		self.lineEdit_champion.move(self.size_x - 60, 200)
		self.lineEdit_champion.resize(50, 20)
		self.lineEdit_champion.setDisabled(True) # 챔피언 에디트 비활성화
		self.lineEditLabel_application_program_work_name = QLabel(unicode('Application Program Work Name : ', 'utf-8'), self) # 응용 프로그램 작업명 레이블 설정
		self.lineEditLabel_application_program_work_name.move(self.size_x - 200, 228)
		self.lineEditLabel_application_program_work_name.resize(190, 15)
		self.lineEdit_application_program_work_name = QLineEdit(self.application_program_work_name, self) # 응용 프로그램 작업명 에디트 설정
		self.lineEdit_application_program_work_name.move(self.size_x - 120, 250)
		self.lineEdit_application_program_work_name.resize(110, 20)

	def setupRadioBox(self): # 라디오 박스 설정 함수
		self.groupBox = QGroupBox(unicode('Choose', 'utf-8'), self) # 라디오 박스 그룹
		self.groupBox.move(self.size_x - 110, 85)
		self.groupBox.resize(100, 60)
		self.radiobox_skill = QRadioButton('Skill Macro', self) # 스킬 매크로 라디오 박스 설정
		self.radiobox_skill.move(self.size_x - 100, 95)
		self.radiobox_skill.clicked.connect(self.skill_radio) # 스킬 매크로 라디오 박스 체크/해제 설정 함수 적용
		self.radiobox_pick = QRadioButton('Pick Macro', self) # 픽 매크로 라디오 박스 설정
		self.radiobox_pick.move(self.size_x - 100, 115)
		self.radiobox_pick.clicked.connect(self.pick_radio) # 픽 매크로 라디오 박스 체크/해제 설정 함수 적용
		self.radiobox_pick.setChecked(True) # 디폴트 선택

	def setupCheckBox(self): # 체크 박스 설정 함수
		self.checkbox_active1 = QCheckBox(unicode('Work 1', 'utf-8'), self) # 동작 1 체크 박스 설정
		self.checkbox_active1.move(self.size_x - 175, 104)
		self.checkbox_active1.resize(60, 15)
		self.checkbox_active1.stateChanged.connect(self.active1_check) # 동작 1 체크/해제 설정 함수 적용
		self.checkbox_active1.setDisabled(True) # 동작 1 체크 박스 비활성화
		self.checkbox_active2 = QCheckBox(unicode('Work 2', 'utf-8'), self) # 동작 2 체크 박스 설정
		self.checkbox_active2.move(self.size_x - 175, 124)
		self.checkbox_active2.resize(60, 15)
		self.checkbox_active2.stateChanged.connect(self.active2_check) # 동작 2 체크/해제 설정 함수 적용
		self.checkbox_active2.setDisabled(True) # 동작 2 체크 박스 비활성화
		self.checkbox_size1 = QCheckBox(unicode('1024 x 576', 'utf-8'), self) # 창 크기 1024 x 576 체크 박스 설정
		self.checkbox_size1.move(self.size_x - 175, 61)
		self.checkbox_size1.resize(80, 15)
		self.checkbox_size1.stateChanged.connect(self.size1_check) # 창 크기 1024 x 576 체크/해제 설정 함수 적용
		self.checkbox_size1.setDisabled(True) # 창 크기 1024 x 576 체크 박스 비활성화
		self.checkbox_size2 = QCheckBox(unicode('1280 x 720', 'utf-8'), self) # 창 크기 1280 x 720 체크 박스 설정
		self.checkbox_size2.move(self.size_x - 90, 60)
		self.checkbox_size2.resize(80, 15)
		self.checkbox_size2.stateChanged.connect(self.size2_check) # 창 크기 1280 x 720 체크/해제 설정 함수 적용
		self.checkbox_size2.setDisabled(True) # 창 크기 1280 x 720 체크 박스 비활성화

	def setupStatusBar(self): # 상태 표시줄 설정 함수
		self.statusBar = QStatusBar(self) # 상태 표시줄 설정
		self.setStatusBar(self.statusBar)
		self.statusBar.showMessage('Not Setted') # 초기 상태 표시줄 내용

	def size1_check(self): # 창 크기 1024 x 576 체크/해제 설정 함수
		try:
			if self.check_size1 == True: # 창 크기 1024 x 576 가 체크되어 있을 경우
				self.check_size1 = False # 창 크기 1024 x 576 체크 해제 설정
				if self.radiobox_pick.isChecked() == True: # 픽 매크로 라디오 박스가 체크되어 있을 경우
					self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
				self.btnPause.setDisabled(True) # 매크로 중지 버튼 비활성화
				self.btnCheck.setEnabled(True) # 프로그램 위치 및 크기 체크 버튼 활성화
				self.checkbox_size1.setDisabled(True) # 창 크기 1024 x 576 체크 박스 비활성화
				self.lineEdit_input_duration_time.setDisabled(True) # 입력 지속 시간 에디트 비활성화
				self.lineEdit_position.setDisabled(True) # 포지션 에디트 비활성화
				self.lineEdit_champion.setDisabled(True) # 챔피언 에디트 비활성화
				self.lineEdit_application_program_work_name.setDisabled(True) # 응용 프로그램 작업명 에디트 비활성화
				self.checkbox_active1.setDisabled(True) # 동작 1 체크 박스 비활성화
				self.checkbox_active2.setDisabled(True) # 동작 2 체크 박스 비활성화
			elif self.check_size1 == False: # 창 크기 1024 x 576 가 체크되어 있지 않을 경우
				self.check_size1 = True # 창 크기 1024 x 576 체크 설정
				self.program_size_x = 1024 # 롤 프로그램 가로 크기 설정
				self.program_size_y = 576 # 롤 프로그램 세로 크기 설정
				self.accept_x_right = 590 # 수락 버튼 범위 최우측
				self.accept_x_left = 430 # 수락 버튼 범위 최좌측
				self.accept_y_up = 425 # 수락 버튼 범위 최상단
				self.accept_y_down = 470 # 수락 버튼 범위 최하단
				self.chat_x_right = 255 # 채팅창 범위 최우측
				self.chat_x_left = 21 # 채팅창 범위 최좌측
				self.chat_y_up = 420 # 채팅창 범위 최상단
				self.chat_y_down = 557 # 채팅창 범위 최하단
				self.chat_middle_pos_x = 140 # 채팅창 중앙 x좌표
				self.chat_middle_pos_y = 545 # 채팅창 중앙 y좌표
				self.name_order_middle_pos_x = 535 # 이름순 정렬 버튼 중앙 x좌표
				self.name_order_middle_pos_y = 85 # 이름순 정렬 버튼 중앙 y좌표
				self.workmanship_order_middle_pos_x = 535 # 숙련도 기준 정렬 버튼 중앙 x좌표
				self.workmanship_order_middle_pos_y = 138 # 숙련도 기준 정렬 버튼 중앙 y좌표
				self.champion_search_middle_pos_x = 665 # 챔피언 검색창 중앙 x좌표
				self.champion_search_middle_pos_y = 84 # 챔피언 검색창 중앙 y좌표
				self.champion_box_middle_pos_x_active1 = 390 # 챔피언 박스 중앙 x좌표(동작 1)
				self.champion_box_middle_pos_y_active1 = 138 # 챔피언 박스 중앙 y좌표(동작 1)
				self.champion_box_middle_pos_x_active2 = 307 # 챔피언 박스 중앙 x좌표(동작 2)
				self.champion_box_middle_pos_y_active2 = 137 # 챔피언 박스 중앙 y좌표(동작 2)
				self.checkbox_size1.setChecked(True) # 창 크기 1280 x 720 체크 박스 체크
				self.checkbox_size2.setDisabled(True) # 창 크기 1280 x 720 체크 박스 비활성화
				self.btnCheck.setDisabled(True) # 프로그램 위치 및 크기 체크 버튼 비활성화
				if self.radiobox_pick.isChecked() == True: # 픽 매크로 라디오 박스가 체크되어 있을 경우
					self.lineEdit_application_program_work_name.setEnabled(True) # 응용 프로그램 작업명 에디트 활성화
					if self.check_active1 == True: # 동작 1이 체크되어 있는 경우
						self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
						self.checkbox_active1.setEnabled(True) # 동작 1 체크 박스 활성화
						self.lineEdit_input_duration_time.setEnabled(True) # 입력 지속 시간 에디트 활성화
						self.lineEdit_position.setEnabled(True) # 포지션 에디트 활성화
					elif self.check_active2 == True: # 동작 2가 체크되어 있는 경우
						self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
						self.checkbox_active2.setEnabled(True) # 동작 2 체크 박스 활성화
						self.lineEdit_input_duration_time.setEnabled(True) # 입력 지속 시간 에디트 활성화
						self.lineEdit_position.setEnabled(True) # 포지션 에디트 활성화
						self.lineEdit_champion.setEnabled(True) # 챔피언 에디트 활성화
					elif self.check_active1 == False and self.check_active2 == False: # 동작 1, 동작 2 모두 체크되어 있지 않을 경우
						self.checkbox_active1.setEnabled(True) # 동작 1 체크 박스 활성화
						self.checkbox_active2.setEnabled(True) # 동작 2 체크 박스 활성화
				elif self.radiobox_skill.isChecked() == True: # 스킬 매크로 라디오 박스가 체크되어 있을 경우
					self.checkbox_active1.setDisabled(True) # 동작 1 체크 박스 비활성화
					self.checkbox_active2.setDisabled(True) # 동작 2 체크 박스 비활성화
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def size2_check(self): # 창 크기 1280 x 720 체크/해제 설정 함수
		try:
			if self.check_size2 == True: # 창 크기 1280 x 720 가 체크되어 있을 경우
				self.check_size2 = False # 창 크기 1280 x 720 체크 해제 설정
				if self.radiobox_pick.isChecked() == True: # 픽 매크로 라디오 박스가 체크되어 있을 경우
					self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
				self.btnPause.setDisabled(True) # 매크로 중지 버튼 비활성화
				self.btnCheck.setEnabled(True) # 프로그램 위치 및 크기 체크 버튼 활성화
				self.checkbox_size2.setEnabled(True) # 창 크기 1280 x 720 체크 박스 비활성화
				self.lineEdit_input_duration_time.setDisabled(True) # 입력 지속 시간 에디트 비활성화
				self.lineEdit_position.setDisabled(True) # 포지션 에디트 비활성화
				self.lineEdit_champion.setDisabled(True) # 챔피언 에디트 비활성화
				self.lineEdit_application_program_work_name.setDisabled(True) # 응용 프로그램 작업명 에디트 비활성화
				self.checkbox_active1.setDisabled(True) # 동작 1 체크 박스 비활성화
				self.checkbox_active2.setDisabled(True) # 동작 2 체크 박스 비활성화
			elif self.check_size2 == False: # 창 크기 1280 x 720 가 체크되어 있지 않을 경우
				self.check_size2 = True # 창 크기 1280 x 720 체크 설정
				self.program_size_x = 1280 # 롤 프로그램 가로 크기
				self.program_size_y = 720 # 롤 프로그램 세로 크기
				self.accept_x_right = 735 # 수락 버튼 범위 최우측
				self.accept_x_left = 545 # 수락 버튼 범위 최좌측
				self.accept_y_up = 532 # 수락 버튼 범위 최상단
				self.accept_y_down = 585 # 수락 버튼 범위 최하단
				self.chat_x_right = 320 # 채팅창 범위 최우측
				self.chat_x_left = 25 # 채팅창 범위 최좌측
				self.chat_y_up = 525 # 채팅창 범위 최상단
				self.chat_y_down = 700 # 채팅창 범위 최하단
				self.chat_middle_pos_x = 170 # 채팅창 중앙 x좌표
				self.chat_middle_pos_y = 682 # 채팅창 중앙 y좌표
				self.name_order_middle_pos_x = 670 # 이름순 정렬 버튼 중앙 x좌표
				self.name_order_middle_pos_y = 105 # 이름순 정렬 버튼 중앙 y좌표
				self.workmanship_order_middle_pos_x = 670 # 숙련도 기준 정렬 버튼 중앙 x좌표
				self.workmanship_order_middle_pos_y = 170 # 숙련도 기준 정렬 버튼 중앙 y좌표
				self.champion_search_middle_pos_x = 830 # 챔피언 검색창 중앙 x좌표
				self.champion_search_middle_pos_y = 105 # 챔피언 검색창 중앙 y좌표
				self.champion_box_middle_pos_x_active1 = 485 # 챔피언 박스 중앙 x좌표(동작 1)
				self.champion_box_middle_pos_y_active1 = 170 # 챔피언 박스 중앙 y좌표(동작 1)
				self.champion_box_middle_pos_x_active2 = 385 # 챔피언 박스 중앙 x좌표(동작 2)
				self.champion_box_middle_pos_y_active2 = 170 # 챔피언 박스 중앙 y좌표(동작 2)
				self.checkbox_size1.setDisabled(True) # 창 크기 1024 x 576 체크 박스 비활성화
				self.btnCheck.setDisabled(True) # 프로그램 위치 및 크기 체크 버튼 비활성화
				if self.radiobox_pick.isChecked() == True: # 픽 매크로 라디오 박스가 체크되어 있을 경우
					self.lineEdit_application_program_work_name.setEnabled(True) # 응용 프로그램 작업명 에디트 활성화
					if self.check_active1 == True: # 동작 1이 체크되어 있는 경우
						self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
						self.checkbox_active1.setEnabled(True) # 동작 1 체크 박스 활성화
						self.lineEdit_input_duration_time.setEnabled(True) # 입력 지속 시간 에디트 활성화
						self.lineEdit_position.setEnabled(True) # 포지션 에디트 활성화
					elif self.check_active2 == True: # 동작 2가 체크되어 있는 경우
						self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
						self.checkbox_active2.setEnabled(True) # 동작 2 체크 박스 활성화
						self.lineEdit_input_duration_time.setEnabled(True) # 입력 지속 시간 에디트 활성화
						self.lineEdit_position.setEnabled(True) # 포지션 에디트 활성화
						self.lineEdit_champion.setEnabled(True) # 챔피언 에디트 활성화
					elif self.check_active1 == False and self.check_active2 == False: # 동작 1, 동작 2 모두 체크되어 있지 않을 경우
						self.checkbox_active1.setEnabled(True) # 동작 1 체크 박스 활성화
						self.checkbox_active2.setEnabled(True) # 동작 2 체크 박스 활성화
				elif self.radiobox_skill.isChecked() == True: # 스킬 매크로 라디오 박스가 체크되어 있을 경우
					self.checkbox_active1.setDisabled(True) # 동작 1 체크 박스 비활성화
					self.checkbox_active2.setDisabled(True) # 동작 2 체크 박스 비활성화
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def skill_radio(self): # 스킬 매크로 라디오 박스 체크/해제 설정 함수
		try:
			self.btnFile.setEnabled(True) # 설정 파일 오픈 버튼 활성화
			self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
			self.btnCheck.setDisabled(True) # 프로그램 위치 및 크기 체크 버튼 비활성화
			self.checkbox_size1.setDisabled(True) # 창 크기 1024 x 576 체크 박스 비활성화
			self.checkbox_size2.setDisabled(True) # 창 크기 1280 x 720 체크 박스 비활성화
			self.checkbox_active1.setDisabled(True) # 동작 1 체크 박스 비활성화
			self.checkbox_active2.setDisabled(True) # 동작 2 체크 박스 비활성화
			self.lineEdit_input_duration_time.setDisabled(True) # 입력 지속 시간 에디트 비활성화
			self.lineEdit_position.setDisabled(True) # 포지션 에디트 비활성화
			self.lineEdit_champion.setDisabled(True) # 챔피언 에디트 비활성화
			self.lineEdit_application_program_work_name.setDisabled(True) # 응용 프로그램 작업명 에디트 비활성화
			self.label_content.clear() # 레이블 클리어
			self.label_content.resize(400, 280)
			content = unicode('[동작 종류]\n1. 키보드 : 단순 입력, 지속 입력\nex) q 입력 - q, w 2.5초간 입력 - w^2.5\n\n2. 마우스 : 좌클릭, 우클릭, 이동\nex) 좌클릭 - leftclick, 우클릭 - rightclick\nex) 500 픽셀만큼 오른쪽으로 마우스 이동 - move^500,0\nex) 300 픽셀만큼 왼쪽으로 마우스 이동 - move^-300,0\nex) 100 픽셀만큼 아래로 마우스 이동 - move^0,100\nex) 200 픽셀만큼 위로 마우스 이동 - move^0,-200\nex) x,y 픽셀만큼 마우스 이동 - move^x,y\n\n[파일 구성 방법]\n1. 각 동작들은 한 줄에 입력\n2. 각 줄의 맨 앞은 핫키로 지정. 핫키 구분자는 : 문자(콜론)\n3. 동작 종류 입력 후 딜레이 시간(초)을 입력하되 공백으로 구분\n4. 딜레이 시간을 입력하지 않으면 안 되므로 불필요한 경우 0으로 입력\nex) q 입력하고 1초 후에 w 입력하는 동작을 핫키 s로 설정 - s: q 1.0 w\nex) e 입력 후 딜레이 없이 r 입력하는 동작을 핫키 shift로 설정 - shift: e 0 r\n', 'utf-8') # 내용 레이블
			self.label_content.setText(content) # 동작 종류 내용으로 레이블 갱신
			self.statusBar.showMessage('Skill Macro') # 상태 표시줄 내용 갱신
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def pick_radio(self): # 픽 매크로 라디오 박스 체크/해제 설정 함수
		try:
			self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
			self.btnFile.setDisabled(True) # 설정 파일 오픈 버튼 비활성화
			self.lineEdit_application_program_work_name.setEnabled(True) # 응용 프로그램 작업명 에디트 활성화
			if self.check_size1 == True or self.check_size2 == True: # 창 크기 1024 x 576 또는 1280 x 720 가 체크되어 있을 경우
				if self.check_size1 == True: # 창 크기 1024 x 576 이 체크되어 있을 경우
					self.checkbox_size1.setEnabled(True) # 창 크기 1024 x 576 체크 박스 활성화
				elif self.check_size2 == True: # 창 크기 1280 x 720 가 체크되어 있을 경우
					self.checkbox_size2.setEnabled(True) # 창 크기 1280 x 720 체크 박스 활성화
				if self.check_active1 == True: # 동작 1이 체크되어 있을 경우
					self.checkbox_active1.setEnabled(True) # 동작 1 체크 박스 활성화
					self.lineEdit_input_duration_time.setEnabled(True) # 입력 지속 시간 에디트 활성화
					self.lineEdit_position.setEnabled(True) # 포지션 에디트 활성화
				elif self.check_active2 == True: # 동작 2가 체크되어 있을 경우
					self.lineEdit_input_duration_time.setEnabled(True) # 입력 지속 시간 에디트 활성화
					self.checkbox_active2.setEnabled(True) # 동작 2 체크 박스 활성화
					self.lineEdit_position.setEnabled(True) # 포지션 에디트 활성화
					self.lineEdit_champion.setEnabled(True) # 챔피언 에디트 활성화
				elif self.check_active1 == False and self.check_active2 == False: # 동작 1, 동작 2 모두 체크되어 있지 않을 경우
					self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
					self.checkbox_active1.setEnabled(True) # 동작 1 체크 박스 활성화
					self.checkbox_active2.setEnabled(True) # 동작 2 체크 박스 활성화
			elif self.check_size1 == False and self.check_size2 == False: # 창 크기 1024 x 576, 1280 x 720 모두 체크되어 있지 않을 경우
				self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
				self.btnCheck.setEnabled(True) # 프로그램 위치 및 크기 체크 버튼 활성화
				self.checkbox_active1.setDisabled(True) # 동작 1 체크 박스 비활성화
				self.checkbox_active2.setDisabled(True) # 동작 2 체크 박스 비활성화
			self.label_content.clear() # 레이블 클리어
			self.label_content.resize(400, 140)
			content = unicode('동작 1 : 설정한 포지션 및 숙련도 제일 높은 챔피언 픽\n1. 수락 버튼 수동 클릭\n2. 수락 버튼 클릭 직후부터 설정한 시간 동안 채팅창에 포지션 자동 입력\n3. 숙련도 제일 높은 챔피언 자동 픽\n\n동작 2 : 설정한 포지션 및 챔피언 픽\n1. 수락 버튼 수동 클릭 시 채팅창 박스 자동 표시\n2. 채팅창 박스 내부 수동 클릭\n3. 채팅창 내부 클릭 직후부터 설정한 시간 동안 채팅창에 포지션 자동 입력\n4. 설정한 챔피언 자동 픽', 'utf-8') # 내용 레이블
			self.label_content.setText(content) # 동작 종류 내용으로 레이블 갱신
			self.statusBar.showMessage('Pick Macro') # 상태 표시줄 내용 갱신
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def active1_check(self): # 동작 1 체크/해제 설정 함수
		try:
			if self.check_active1 == True: # 동작 1이 체크되어 있을 경우
				self.check_active1 = False # 동작 1 체크 해제 설정
				self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
				self.checkbox_active2.setEnabled(True) # 동작 2 체크 박스 활성화
				self.lineEdit_input_duration_time.setDisabled(True) # 입력 지속 시간 에디트 비활성화
				self.lineEdit_position.setDisabled(True) # 포지션 에디트 비활성화
				self.statusBar.showMessage('Active1 Unchecked') # 상태 표시줄 내용 갱신
			elif self.check_active1 == False: # 동작 1이 체크 해제되어 있을 경우
				self.check_active1 = True # 동작 1 체크 설정
				self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
				self.checkbox_active2.setDisabled(True) # 동작 2 체크 박스 비활성화
				self.lineEdit_input_duration_time.setEnabled(True) # 입력 지속 시간 에디트 활성화
				self.lineEdit_position.setEnabled(True) # 포지션 에디트 활성화
				self.lineEdit_input_duration_time.setText('3') # 입력 지속 시간 에디트 디폴트 설정 적용
				self.statusBar.showMessage('Active1 Checked') # 상태 표시줄 내용 갱신
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def active2_check(self): # 동작2 체크/해제 설정 함수
		try:
			if self.check_active2 == True: # 동작 2가 체크되어 있을 경우
				self.check_active2 = False # 동작 2 체크 해제 설정
				self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
				self.checkbox_active1.setEnabled(True) # 동작 1 체크 박스 활성화
				self.lineEdit_input_duration_time.setDisabled(True) # 입력 지속 시간 에디트 비활성화
				self.lineEdit_position.setDisabled(True) # 포지션 에디트 비활성화
				self.lineEdit_champion.setDisabled(True) # 챔피언 에디트 비활성화
				self.statusBar.showMessage('Active2 Unchecked') # 상태 표시줄 내용 갱신
			elif self.check_active2 == False: # 동작 2가 체크 해제되어 있을 경우
				self.check_active2 = True # 동작 2 체크 설정
				self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
				self.checkbox_active1.setDisabled(True) # 동작 1 체크 박스 비활성화
				self.lineEdit_input_duration_time.setEnabled(True) # 입력 지속 시간 에디트 활성화
				self.lineEdit_position.setEnabled(True) # 포지션 에디트 활성화
				self.lineEdit_champion.setEnabled(True) # 챔피언 에디트 활성화
				self.lineEdit_input_duration_time.setText('0.3') # 입력 지속 시간 에디트 디폴트 설정 적용
				self.statusBar.showMessage('Active2 Checked') # 상태 표시줄 내용 갱신
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def check_pos_size_func(self): # 프로그램 위치 및 크기 체크 함수
		try:
			self.application_program_work_name = str(self.lineEdit_application_program_work_name.text()).lower() # 설정한 응용 프로그램 작업명 저장
			state, prog_pos_x, prog_pos_y, prog_size_x, prog_size_y = myMacro.get_program_pos_size(self.application_program_work_name) # 프로그램 위치 및 크기 저장
			if state: # 프로그램의 위치 및 크기를 제대로 찾았을 경우
				if prog_size_x == 1024 and prog_size_y == 576: # 프로그램 크기가 1024 x 576 일 경우
					self.checkbox_size1.setEnabled(True) # 창 크기 1024 x 576 체크 박스 활성화
					self.checkbox_size1.click() # 창 크기 1024 x 576 체크 박스 체크
				elif prog_size_x == 1280 and prog_size_y == 720: # 프로그램 크기가 1280 x 720 일 경우
					self.checkbox_size2.setEnabled(True) # 창 크기 1280 x 720 체크 박스 활성화
					self.checkbox_size2.click() # 창 크기 1280 x 720 체크 박스 체크
			else: # 프로그램의 위치 및 크기를 제대로 찾지 못했을 경우
				content = unicode('1. 프로그램(LOL)이 실행 중이지 않을 경우 프로그램을 실행해야 합니다.\n2. 프로그램(LOL)을 최소화하면 안 되고 화면에 떠있어야 합니다.\n3. 응용 프로그램 작업명을 올바르게 입력해야 합니다.', 'utf-8') # 에러 내용
				QMessageBox.critical(self, 'Error', content) # 에러 메세지 박스
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def isNumber(self, s): # 문자열에 숫자만 있는지 판별하기 위한 함수(설정 파일의 딜레이 시간과 동작의 위치가 올바른지 확인하기 위해)
		try:
			float(s)
			return True
		except ValueError:
			return False

	def setup_file(self): # 설정 파일에서 설정 정보 가져오는 함수
		try:
			fname = QFileDialog.getOpenFileName(self) # 설정 파일 오픈
			content = '' # 설정 파일 내용이 저장될 변수
			line_hotkey_list = [] # 핫키가 있는 첫 번째 위치의 내용이 저장될 리스트(핫키 중복 예방)
			duplication = False # 핫키가 중복됐는지 확인하기 위한 변수
			position_error = False # 설정 파일의 딜레이 시간과 동작의 위치가 올바른지 확인하기 위한 변수
			key_error = False # 키를 올바르게 설정했는지 확인하기 위한 변수
			fp = open(fname)
			active = fp.readlines() # 설정 파일 한 라인씩 저장
			fp.close()
			fp = open(fname)
			empty = fp.read() # 설정 파일 내용 저장
			fp.close()
			self.actives = [] # 설정 파일의 내용이 저장될 리스트 초기화
			if len(empty) == 0: # 설정 파일의 내용이 없을 경우
				self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
				self.statusBar.showMessage('[-] Error : Configuration file is empty !!') # 상태 표시줄 내용 갱신
				return
			for l in range(0, len(active)): # 설정 파일 한 라인씩 반복
				if active[l] == '': # 해당 라인이 공백일 경우(설정된 내용이 없을 경우)
					continue
				line = active[l].lower().strip() # 해당 라인 저장
				tmp_line_hotkey = line.split(' ')[0] # 해당 라인을 공백으로 구분 후 핫키가 있는 첫 번째 위치의 문자열 저장
				only_line_hotkey_activeName = tmp_line_hotkey.split(':')[0] # 핫키 저장
				if ':' not in tmp_line_hotkey: # 핫키가 있는 첫 번째 위치에 핫키 구분자(콜론)가 없을 경우
					continue
				for hotkey in line_hotkey_list: # 중복된 핫키가 있는지 확인
					if tmp_line_hotkey == hotkey: # 중복된 핫키가 있을 경우
						duplication = True # 핫키가 중복됐는지 확인하기 위한 변수 값 변경
						break
				if duplication: # 핫키가 중복됐을 경우
					duplication = False # 핫키가 중복됐는지 확인하기 위한 변수 값 초기화
					continue
				tmp_hotkey_confirm = False # 핫키를 올바르게 설정했는지 확인하기 위한 변수
				for vk in myMacro.virtual_key:
					if only_line_hotkey_activeName == vk[0]: # 설정한 핫키일 경우
						tmp_hotkey_confirm = True # 핫키를 올바르게 설정했는지 확인하기 위한 변수 값 설정
						break
				if tmp_hotkey_confirm == True: # 핫키를 올바르게 설정했을 경우
					for i in range(1, len(line.split(' '))): # 첫 번째는 동작이 아니므로('핫키:' 임) 인덱스 1부터 시작
						if i%2 == 0 and i != 1: # 딜레이 시간 위치일 경우(숫자만 있어야 함)
							if not self.isNumber(line.split(' ')[i]): # 딜레이 시간(숫자)이 있어야 할 위치에 숫자가 아닌 문자가 있을 경우
								position_error = True # 설정 파일의 딜레이 시간과 동작의 위치가 올바른지 확인하기 위한 변수 값 변경
								break
						elif i%2 == 1: # 키 위치일 경우
							if 'leftclick' == line.split(' ')[i] or 'rightclick' == line.split(' ')[i]: # 좌클릭 또는 우클릭일 경우
								continue
							elif '^' in line.split(' ')[i]:
								if 'move' == line.split(' ')[i].split('^')[0]: # 마우스 이동일 경우
									if ',' in line.split(' ')[i].split('^')[1]: # 마우스 이동 좌표 설정 부분에 , 문자(반점)가 있을 경우
										if not self.isNumber(line.split(' ')[i].split('^')[1].split(',')[0]) or not self.isNumber(line.split(' ')[i].split('^')[1].split(',')[1]): # 마우스 이동 좌표 중 문자가 있을 경우(숫자만 있어야 함)
											key_error = True # 키를 올바르게 설정했는지 확인하기 위한 변수 값 설정
											break
									else: # 마우스 이동 좌표 설정 부분에 , 문자(반점)가 없을 경우
										key_error = True # 키를 올바르게 설정했는지 확인하기 위한 변수 값 설정
										break
								else: # 지속 입력일 경우
									continue_confirm_count = 0 # 지속 입력의 키와 딜레이 시간을 올바르게 설정했는지 확인하기 위한 변수
									for vk in myMacro.virtual_key:
										if line.split(' ')[i].split('^')[0] == vk[0]: # 설정한 키일 경우
											continue_confirm_count += 1 # 지속 입력의 키와 딜레이 시간을 올바르게 설정했는지 확인하기 위한 변수 값 증가
											break
									if self.isNumber(line.split(' ')[i].split('^')[1]): # 딜레이 시간(숫자)이 있어야 할 위치가 숫자일 경우
										continue_confirm_count += 1 # 지속 입력의 키와 딜레이 시간을 올바르게 설정했는지 확인하기 위한 변수 값 증가
									if continue_confirm_count != 2: # 지속 입력의 키 또는 딜레이 시간을 올바르게 설정하지 않았을 경우
										key_error = True # 키를 올바르게 설정했는지 확인하기 위한 변수 값 설정
										break
							else: # 단순 입력일 경우
								input_confirm = False # 단순 입력 키를 올바르게 설정했는지 확인하기 위한 변수
								for vk in myMacro.virtual_key:
									if line.split(' ')[i] == vk[0]: # 설정한 키일 경우
										input_confirm = True # 단순 입력 키를 올바르게 설정했는지 확인하기 위한 변수 값 설정
										break
								if input_confirm == False: # 단순 입력 키를 올바르게 설정하지 않았을 경우
									key_error = True # 키를 올바르게 설정했는지 확인하기 위한 변수 값 설정
									break
					if position_error == True: # 딜레이 시간(숫자)이 있어야 할 위치에 숫자가 아닌 문자가 있을 경우
						position_error = False # 설정 파일의 딜레이 시간과 동작의 위치가 올바른지 확인하기 위한 변수 값 초기화
						continue
					if key_error == True: # 키를 올바르게 설정하지 않았을 경우
						key_error = False # 키를 올바르게 설정했는지 확인하기 위한 변수 값 초기화
						continue
				elif tmp_hotkey_confirm == False: # 핫키를 올바르게 설정하지 않았을 경우
					continue
				self.actives.append(line) # 설정 파일의 내용이 저장될 리스트에 해당 라인 추가
				content += line + '\n' # 설정 파일 내용 추가
				line_hotkey_list.append(tmp_line_hotkey) # 리스트에 핫키가 있는 첫 번째 위치 추가
			self.label_content.clear() # 레이블 클리어
			self.label_content.resize(400, 250)
			self.label_content.setText(content) # 설정 파일 내용으로 레이블 갱신
			self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
			self.statusBar.showMessage('Setted') # 상태 표시줄 내용 갱신
		except Exception, e:
			self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def exit_func(self): # 매크로 종료 함수
		try:
			global exit_var
			global exit_var_pause
			exit_var = True # 스레드 종료 변수 값 설정
			exit_var_pause = True # restart_thread 스레드 종료 변수 값 설정
			self.start = False # 시작 버튼 눌림 여부 값 변경
			QApplication.quit() # 종료 이벤트 발생(QCoreApplication.instance().quit)
		except Exception, e:
			print '[-] ', e

	def restart_thread(self, key, vk, key_state): # 설정한 단축키로 매크로 재시작하는 스레드
		global exit_var_pause
		while True:
			try:
				sem.acquire() # 임계영역 생성
				if exit_var_pause == True: # 스레드 종료 변수 값이 설정됐을 경우
					sem.release() # 임계영역 해제
					return
				if self.start == True: # 매크로가 동작했을 경우(버튼을 통해 매크로를 재시작한 경우)
					sem.release() # 임계영역 해제
					return # 스레드 종료
				elif self.start == False: # 매크로가 중지중인 경우
					cur_key_state = win32api.GetKeyState(vk[1]) # 현재 키보드 입력 상태
					if cur_key_state != key_state: # 키보드 입력 상태가 변경됐을 경우
						key_state = cur_key_state # 키보드 입력 상태 갱신
						if key_state == -127 or key_state == -128: # 두 번 실행 방지
							if key == self.pause_restart: # 입력한 키가 설정한 재시작 키일 경우
								self.btnStart.click() # Start 버튼 클릭 이벤트 발생(self.start_func 함수를 직접 호출하지 않고 Start 버튼 클릭 이벤트를 발생시켜 self.start_func 함수를 호출한 이유는 직접 호출 시 재귀로인한 오류가 발생하기 때문임)
								sem.release() # 임계영역 해제
								return # 스레드 종료
				sem.release() # 임계영역 해제
			except Exception, e:
				sem.release() # 임계영역 해제
				pass

	def pause_func(self): # 매크로 중지 함수
		try:
			global exit_var
			if self.start: # 매크로가 동작중인 경우
				exit_var = True # 스레드 종료 변수 값 설정
				self.start = False # 시작 버튼 눌림 여부 값 변경
				self.statusBar.showMessage('Pause') # 상태 표시줄 내용 갱신
				self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
				self.btnPause.setDisabled(True) # 매크로 중지 버튼 비활성화
				self.lineEdit_pause_restart.setEnabled(True) # 중지 및 재시작 키 에디트 활성화
				self.radiobox_pick.setEnabled(True) # 픽 매크로 라디오 박스 활성화
				self.radiobox_skill.setEnabled(True) # 스킬 매크로 라디오 박스 활성화
				if self.check_size1 == True: # 창 크기 1024 x 576 가 체크되어 있을 경우
					self.checkbox_size1.setEnabled(True) # 창 크기 1024 x 576 체크 박스 활성화
				elif self.check_size2 == True: # 창 크기 1280 x 720 가 체크되어 있을 경우
					self.checkbox_size2.setEnabled(True) # 창 크기 1280 x 720 체크 박스 활성화
				if self.radiobox_skill.isChecked() == True: # 스킬 매크로일 경우
					self.btnFile.setEnabled(True) # 설정 파일 오픈 버튼 활성화
				elif self.radiobox_pick.isChecked() == True: # 픽 매크로일 경우
					self.lineEdit_application_program_work_name.setEnabled(True) # 응용 프로그램 작업명 에디트 활성화
					self.lineEdit_input_duration_time.setEnabled(True) # 입력 지속 시간 에디트 활성화
					self.lineEdit_position.setEnabled(True) # 포지션 에디트 활성화
					if self.check_active1 == True: # 동작 1이 체크되어 있을 경우
						self.checkbox_active1.setEnabled(True) # 동작 1 체크 박스 활성화
					elif self.check_active2 == True: # 동작 2가 체크되어 있을 경우
						self.checkbox_active2.setEnabled(True) # 동작 2 체크 박스 활성화
						self.lineEdit_champion.setEnabled(True) # 챔피언 에디트 활성화
				for vk in myMacro.virtual_key:
					if self.pause_restart == vk[0]: # 설정한 재시작 키일 경우
						key_state_restart = win32api.GetKeyState(vk[1]) # 설정한 재시작 키 초기 입력 상태
						th_restart = threading.Thread(target=self.restart_thread, args=(self.pause_restart, vk, key_state_restart,)) # 설정한 단축키로 매크로 재시작하는 스레드 설정
						th_restart.start() # 스레드 생성
						break
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def start_func(self): # 매크로 동작 함수
		try:
			global exit_var
			if exit_var: # 스레드 종료 변수 값이 설정된 경우(중지 후 다시 시작했을 경우)
				exit_var = False # 스레드 종료 변수 값 초기화
			self.start = True # 시작 버튼 눌림 여부 값 변경
			self.statusBar.showMessage('Start') # 상태 표시줄 내용 갱신
			self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
			self.btnPause.setEnabled(True) # 매크로 중지 버튼 활성화
			self.lineEdit_pause_restart.setDisabled(True) # 중지 및 재시작 키 에디트 비활성화
			if self.check_size1 == True: # 창 크기 1024 x 576 일 경우
				self.checkbox_size1.setDisabled(True) # 창 크기 1024 x 576 체크 박스 비활성화
			elif self.check_size2 == True: # 창 크기 1280 x 720 일 경우
				self.checkbox_size2.setDisabled(True) # 창 크기 1280 x 720 체크 박스 비활성화
			self.radiobox_pick.setDisabled(True) # 픽 매크로 라디오 박스 비활성화
			self.radiobox_skill.setDisabled(True) # 스킬 매크로 라디오 박스 비활성화
			self.pause_restart = str(self.lineEdit_pause_restart.text()).lower() # 설정한 중지 키 저장
			if self.radiobox_skill.isChecked() == True: # 스킬 매크로일 경우
				self.btnFile.setDisabled(True) # 설정 파일 오픈 버튼 비활성화
				duplication = False # 핫키와 중지 키 중복 여부
				for active in self.actives:
					hotkey = active.split(' ')[0] # 공백으로 구분 후 핫키가 있는 첫 번째 위치 저장
					hotkey = hotkey[:-1].lower() # 핫키 구분자(콜론)를 제거한 순수 핫키 추출 후 소문자 변환해서 저장
					if self.pause_restart == hotkey: # 핫키와 설정한 중지 키가 같을 경우
						duplication = True # 중복 여부 값 변경
					for vk in myMacro.virtual_key:
						if hotkey == vk[0]: # 설정한 핫키일 경우
							th_skill = threading.Thread(target=self.skill_macro_thread, args=(hotkey, vk, active,)) # 스킬 매크로 스레드 설정
							th_skill.start() # 스레드 생성
				if duplication: # 핫키 중에서 설정한 중지 키와 같은 키가 있을 경우
					self.pause_restart = 'None' # 중지 키 비활성화
					self.lineEdit.clear() # 에디트 클리어
					self.lineEdit.setText(self.pause_restart) # 에디트 비활성화 상태로 설정
				else: # 핫키 중에서 설정한 중지 키와 같은 키가 없을 경우(안겹치므로 설정한 중지 키 입력 감지 스레드 생성)
					for vk in myMacro.virtual_key:
						if self.pause_restart == vk[0]: # 설정한 중지 키일 경우
							key_state_pause = win32api.GetKeyState(vk[1]) # 설정한 중지 키 초기 입력 상태
							th_pause = threading.Thread(target=self.pause_thread, args=(self.pause_restart, vk, key_state_pause,)) # 설정한 중지 키 입력 감지 스레드 설정
							th_pause.start() # 스레드 생성
							break
			elif self.radiobox_pick.isChecked() == True: # 픽 매크로일 경우
				self.input_duration_time = float(self.lineEdit_input_duration_time.text()) # 설정한 입력 지속 시간 저장
				self.application_program_work_name = str(self.lineEdit_application_program_work_name.text()).lower() # 설정한 응용 프로그램 작업명 저장
				self.lineEdit_application_program_work_name.setDisabled(True) # 응용 프로그램 작업명 에디트 비활성화
				self.lineEdit_input_duration_time.setDisabled(True) # 입력 지속 시간 에디트 비활성화
				self.lineEdit_position.setDisabled(True) # 포지션 에디트 비활성화
				for vk in myMacro.virtual_key:
					if self.pause_restart == vk[0]: # 설정한 중지 키일 경우
						key_state_pause = win32api.GetKeyState(vk[1]) # 설정한 중지 키 초기 입력 상태
						th_pause = threading.Thread(target=self.pause_thread, args=(self.pause_restart, vk, key_state_pause,)) # 설정한 중지 키 입력 감지 스레드 설정
						th_pause.start() # 스레드 생성
						break
				if self.check_active1 == True: # 동작 1이 체크되어 있을 경우
					self.checkbox_active1.setDisabled(True) # 동작 1 체크 박스 비활성화
					th_workmanship_pick = threading.Thread(target=self.workmanship_pick_macro_thread, args=()) # 설정한 포지션 및 숙련도 제일 높은 챔피언 픽하는 스레드 설정
					th_workmanship_pick.start() # 스레드 생성
				elif self.check_active2 == True: # 동작 2가 체크되어 있을 경우
					self.checkbox_active2.setDisabled(True) # 동작 2 체크 박스 비활성화
					self.lineEdit_champion.setDisabled(True) # 챔피언 에디트 비활성화
					th_pick = threading.Thread(target=self.pick_macro_thread, args=()) # 설정한 포지션 및 챔피언 픽하는 스레드 설정
					th_pick.start() # 스레드 생성
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def pause_thread(self, key, vk, key_state): # 설정한 단축키로 매크로 중지하는 스레드
		global exit_var
		while True:
			try:
				sem.acquire() # 임계영역 생성
				if exit_var or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
					sem.release() # 임계영역 해제
					return # 스레드 종료
				elif self.start == True: # 매크로가 동작중인 경우
					cur_key_state = win32api.GetKeyState(vk[1]) # 현재 키보드 입력 상태
					if cur_key_state != key_state: # 키보드 입력 상태가 변경됐을 경우
						key_state = cur_key_state # 키보드 입력 상태 갱신
						if key_state == -127 or key_state == -128: # 두 번 실행 방지
							if key == self.pause_restart: # 입력한 키가 설정한 재시작 키일 경우
								self.pause_func() # 매크로 중지 함수 실행
								sem.release() # 임계영역 해제
								return # 스레드 종료
				sem.release() # 임계영역 해제
			except Exception, e:
				sem.release() # 임계영역 해제
				pass

	def skill_macro_thread(self, key, vk, active): # 스킬 매크로 스레드
		global exit_var
		while True:
			try:
				sem.acquire() # 임계영역 생성
				if exit_var or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
					sem.release() # 임계영역 해제
					return # 스레드 종료
				elif self.start == True: # 매크로가 동작중인 경우
					if keyboard.is_pressed(key): # 키보드 입력이 감지됐을 경우
						act = active.split(' ') # 설정 파일 내용 저장
						for i in range(0, len(act)):
							if act[i] == key + ':' and i == 0: # 핫키 구분자일 경우
								continue
							elif i%2 == 0 and i != 1: # 딜레이 시간일 경우
								time.sleep(float(act[i])) # 딜레이 시간만큼 정지
							elif i%2 == 1 or i == 1: # 동작일 경우
								if 'move' in act[i]: # 마우스 이동일 경우
									move_x = act[i].split('^')[1].split(',')[0] # 이동할 x값 저장
									move_y = act[i].split('^')[1].split(',')[1] # 이동할 y값 저장
									myMacro.move_mouse_game(int(move_x), int(move_y)) # 설정한 좌표로 마우스 이동
								else: # 마우스 이동이 아닐 경우
									if '^' in act[i]: # 지속 입력일 경우
										duration_time = float(act[i].split('^')[1]) # 지속 시간 저장
										act_key = act[i].split('^')[0] # 입력 키 저장
										for vk in myMacro.virtual_key:
											if act_key.lower() == vk[0]:
												myMacro2.PressKey(vk[1]) # 키보드 눌림 상태 유지
												time.sleep(duration_time) # 지속 시간만큼 대기
												myMacro2.ReleaseKey(vk[1]) # 키보드 눌림 상태 해제
												break
									else: # 지속 입력이 아닐 경우
										if 'leftclick' in act[i]: # 마우스 좌클릭일 경우
											myMacro.click_mouse_left(0,0) # 마우스 좌클릭
										elif 'rightclick' in act[i]: # 마우스 우클릭일 경우
											myMacro.click_mouse_right(0,0) # 마우스 우클릭
										else: # 키보드 입력일 경우
											for vk in myMacro.virtual_key:
												if act[i].lower() == vk[0]:
													myMacro2.PressKey(vk[1]) # 키보드 입력
													myMacro2.ReleaseKey(vk[1])
													break
				sem.release() # 임계영역 해제
			except Exception ,e:
				sem.release() # 임계영역 해제
				pass

	def workmanship_pick_macro_thread(self): # 설정한 포지션 및 숙련도 제일 높은 챔피언 픽하는 스레드
		if self.input_duration_time > 13.0: # 입력 지속 시간을 13초 이상으로 설정한 경우(수락창 나오고 나서 10초 후에 창이 닫히는데 지연 시간까지 합해서 최대 13초)
			self.input_duration_time = 13.0 # 입력 지속 시간을 최대 13초로 설정
		while True:
			try:
				sem.acquire() # 임계영역 생성
				if exit_var or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
					sem.release() # 임계영역 해제
					return # 스레드 종료
				elif self.start == True: # 매크로가 동작중인 경우
					if myMacro.detect_mouse_left_state(): # 마우스 좌클릭이 감지됐을 경우
						cur_pos = myMacro.get_mouse_pos() # 현재 마우스 좌표 저장
						cur_x = cur_pos[0] # 현재 마우스 x좌표 저장
						cur_y = cur_pos[1] # 현재 마우스 y좌표 저장
						state, prog_pos_x, prog_pos_y, prog_size_x, prog_size_y = myMacro.get_program_pos_size(self.application_program_work_name) # 프로그램 위치 및 크기 저장
						if state: # 프로그램의 위치 및 크기를 제대로 찾았을 경우
							if prog_size_x == self.program_size_x and prog_size_y == self.program_size_y: # 프로그램의 크기가 설정한 크기와 같을 경우
								if cur_x < prog_pos_x + self.accept_x_right and cur_x > prog_pos_x + self.accept_x_left: # 마우스 좌클릭한 위치가 수락 버튼의 가로 범위 내에 있을 경우
									if cur_y < prog_pos_y + self.accept_y_down and cur_y > prog_pos_y + self.accept_y_up: # 마우스 좌클릭한 위치가 수락 버튼의 세로 범위 내에 있을 경우
										myMacro.click_mouse_left(0,0) # 수락 버튼 클릭
										count = 0
										while count < self.input_duration_time * 10: # 설정한 시간(초)동안 반복
											myMacro.move_mouse(prog_pos_x + self.chat_middle_pos_x, prog_pos_y + self.chat_middle_pos_y) # 채팅창 중앙으로 마우스 이동
											myMacro.click_mouse_left(0,0) # 채팅창 클릭
											pyperclip.copy(unicode(self.lineEdit_position.text().toUtf8(),'utf8', 'ignore').encode('cp949')) # 클립보드에 포지션 복사
											myMacro.input_combination_keyboard('ctrl', 'v') # ctrl + v 입력
											myMacro.input_keyboard('enter') # 엔터 키 입력
											time.sleep(0.1)
											count += 1
										myMacro.move_mouse(prog_pos_x + self.name_order_middle_pos_x, prog_pos_y + self.name_order_middle_pos_y) # 이름순 정렬 버튼 중앙으로 마우스 이동
										myMacro.click_mouse_left(0,0) # 이름순 정렬 버튼 클릭
										time.sleep(0.3)
										myMacro.move_mouse(prog_pos_x + self.workmanship_order_middle_pos_x, prog_pos_y + self.workmanship_order_middle_pos_y) # 숙련도 기준 정렬 버튼 중앙으로 마우스 이동
										myMacro.click_mouse_left(0,0) # 숙련도 기준 정렬 버튼 클릭
										myMacro.move_mouse(prog_pos_x + self.champion_box_middle_pos_x_active1, prog_pos_y + self.champion_box_middle_pos_y_active1) # 챔피언 박스 중앙으로 마우스 이동
										myMacro.click_mouse_left(0,0) # 챔피언 클릭
										self.pause_func() # 매크로 중지 함수 실행
										sem.release() # 임계영역 해제
										return
				sem.release() # 임계영역 해제
			except Exception, e:
				sem.release() # 임계영역 해제
				pass

	def pick_macro_thread(self): # 설정한 포지션 및 챔피언 픽하는 스레드
		if self.input_duration_time > 0.3: # 입력 지속 시간을 0.3초 이상으로 설정한 경우(0.3초 이상으로 설정하면 빠르고 지속적인 입력으로 인해 위쪽에 경고 메세지가 나오는데 이 메세지가 챔피언 검색창을 가림)
			self.input_duration_time = 0.3 # 입력 지속 시간을 최대 0.3초로 설정
		accept_button = False # 수락 버튼 누름 여부
		while True:
			try:
				sem.acquire() # 임계영역 생성
				if exit_var or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
					sem.release() # 임계영역 해제
					return # 스레드 종료
				elif self.start == True: # 매크로가 동작중인 경우
					if myMacro.detect_mouse_left_state(): # 마우스 좌클릭이 감지됐을 경우
						cur_pos = myMacro.get_mouse_pos() # 현재 마우스 좌표 저장
						cur_x = cur_pos[0] # 현재 마우스 x좌표 저장
						cur_y = cur_pos[1] # 현재 마우스 y좌표 저장
						state, prog_pos_x, prog_pos_y, prog_size_x, prog_size_y = myMacro.get_program_pos_size(self.application_program_work_name) # 프로그램 위치 및 크기 저장
						if state: # 프로그램의 위치 및 크기를 제대로 찾았을 경우
							if prog_size_x == self.program_size_x and prog_size_y == self.program_size_y: # 프로그램 크기가 설정한 크기와 같을 경우
								if cur_x < prog_pos_x + self.accept_x_right and cur_x > prog_pos_x + self.accept_x_left: # 마우스 좌클릭한 위치가 수락 버튼의 가로 범위 내에 있을 경우
									if cur_y < prog_pos_y + self.accept_y_down and cur_y > prog_pos_y + self.accept_y_up: # 마우스 좌클릭한 위치가 수락 버튼의 세로 범위 내에 있을 경우
										accept_button = True # 수락 버튼 누름 설정
										for x in range(prog_pos_x + self.chat_x_left, prog_pos_x + self.chat_x_right): # 채팅창 가로 길이만큼 반복
											for thickness in range(0, 1): # 가로 두께 굵게 하기
												myMacro.set_pixel(x, prog_pos_y + self.chat_y_up + thickness, 0x0000ff) # 채팅창 상단 가로 그리기
												myMacro.set_pixel(x, prog_pos_y + self.chat_y_down + thickness, 0x0000ff) # 채팅창 하단 가로 그리기
											for thickness in range(0, 1): # 가로 두께 굵게 하기
												myMacro.set_pixel(x, prog_pos_y + self.chat_y_up - thickness, 0x0000ff) # 채팅창 상단 가로 그리기
												myMacro.set_pixel(x, prog_pos_y + self.chat_y_down - thickness, 0x0000ff) # 채팅창 하단 가로 그리기
										for y in range(prog_pos_y + self.chat_y_up, prog_pos_y + self.chat_y_down): # 채팅창 세로 길이만큼 반복
											for thickness in range(0, 1): # 세로 두께 굵게 하기
												myMacro.set_pixel(prog_pos_x + self.chat_x_right + thickness, y, 0x0000ff) # 채팅창 우측 세로 그리기
												myMacro.set_pixel(prog_pos_x + self.chat_x_left + thickness, y, 0x0000ff) # 채팅창 좌측 세로 그리기
											for thickness in range(0, 1): # 세로 두께 굵게 하기
												myMacro.set_pixel(prog_pos_x + self.chat_x_right - thickness, y, 0x0000ff) # 채팅창 우측 세로 그리기
												myMacro.set_pixel(prog_pos_x + self.chat_x_left - thickness, y, 0x0000ff) # 채팅창 좌측 세로 그리기
										continue
								if accept_button: # 수락 버튼이 눌렸을 경우
									if cur_x < prog_pos_x + self.chat_x_right and cur_x > prog_pos_x + self.chat_x_left: # 마우스 좌클릭한 위치가 채팅창의 가로 범위 내에 있을 경우
										if cur_y < prog_pos_y + self.chat_y_down and cur_y > prog_pos_y + self.chat_y_up: # 마우스 좌클릭한 위치가 채팅창의 세로 범위 내에 있을 경우
											count = 0
											while count < self.input_duration_time * 10: # 설정한 시간(초)동안 반복
												myMacro.move_mouse(prog_pos_x + self.chat_middle_pos_x, prog_pos_y + self.chat_middle_pos_y) # 채팅창 위치로 마우스 이동
												myMacro.click_mouse_left(0,0) # 채팅창 클릭
												pyperclip.copy(unicode(self.lineEdit_position.text().toUtf8(),'utf8', 'ignore').encode('cp949')) # 클립보드에 포지션 복사
												myMacro.input_combination_keyboard('ctrl', 'v') # ctrl + v 입력
												myMacro.input_keyboard('enter') # 엔터 키 입력
												time.sleep(0.1)
												count += 1
											myMacro.move_mouse(prog_pos_x + self.champion_search_middle_pos_x, prog_pos_y + self.champion_search_middle_pos_y) # 챔피언 검색창 중앙으로 마우스 이동
											myMacro.click_mouse_left(0,0) # 챔피언 검색창 클릭
											pyperclip.copy(unicode(self.lineEdit_champion.text().toUtf8(),'utf8', 'ignore').encode('cp949')) # 클립보드에 챔피언 복사
											myMacro.input_combination_keyboard('ctrl', 'v') # ctrl + v 입력
											myMacro.input_keyboard('enter') # 엔터 키 입력
											time.sleep(0.3)
											myMacro.move_mouse(prog_pos_x + self.champion_box_middle_pos_x_active2, prog_pos_y + self.champion_box_middle_pos_y_active2) # 챔피언 박스 중앙으로 마우스 이동
											myMacro.click_mouse_left(0,0) # 챔피언 클릭
											self.pause_func() # 매크로 중지 함수 실행
											sem.release() # 임계영역 해제
											return
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