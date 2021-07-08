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
from PIL import Image
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
		self.check_autoPotion = False # 자동 포션 매크로 체크 여부
		self.check_doubleAttack = False # 더블 어택 매크로 체크 여부
		self.check_autoHunt = False # 자동 사냥 매크로 체크 여부
		self.check_fp = False # 밥통작 매크로 체크 여부
		self.check_infiniteClick = False # 반복 마우스 좌클릭 매크로 체크 여부
		self.check_infiniteInput = False # 반복 설정한 단축키 입력 매크로 체크 여부
		self.pause_restart = 'F12' # 중지 및 재시작 키
		self.health_x = 60 # 체력 포션을 사용하는 체력바의 x좌표
		self.health_y = 505 # 체력 포션을 사용하는 체력바의 y좌표
		self.health_color = 0 # 체력이 부족할때의 체력바 픽셀값
		self.health_potion_key = '1' # 체력 포션 단축키
		self.doubleAttack_key = '2' # 더블 어택 단축키
		self.doubleAttack_delay = 11 # 더블 어택 재사용 대기 시간
		self.attack_delay = 10 # 몬스터 클릭 후 사냥 완료할 때까지의 대기 시간
		self.full_screenshot_file = os.getcwd() + '\\lieDetector_templateMatching.png' # 일랜시아 화면 스크린샷 파일
		self.front_template_image_file = 'C:\\monster_front_templateMatching.png' # 몬스터 정면 이미지 템플릿 파일
		self.back_template_image_file = 'C:\\monster_back_templateMatching.png' # 몬스터 후면 이미지 템플릿 파일
		self.leftside_template_image_file = 'C:\\monster_leftside_templateMatching.png' # 몬스터 좌측면 이미지 템플릿 파일
		self.rightside_template_image_file = 'C:\\monster_rightside_templateMatching.png' # 몬스터 우측면 이미지 템플릿 파일
		self.doubleAttack_delay_fp = 11 # 더블 어택(밥통작) 재사용 대기 시간
		self.doubleAttack_key_fp = '2' # 더블 어택(밥통작) 단축키
		self.holyMenu_key = 'Ctrl 1' # 홀리 메뉴 단축키
		self.characterName = '' # 캐릭터명
		self.infinite_key = '3' # 반복해서 입력할 단축키
		self.size_x = 430 # 프로그램의 가로 크기
		self.size_y = 550 # 프로그램의 세로 크기
		self.pos_x = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)/2 - self.size_x/2 # 처음 프로그램이 나타나는 x좌표(디폴트 중앙으로 설정)
		self.pos_y = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)/2 - self.size_y/1.7 # 처음 프로그램이 나타나는 y좌표(디폴트 중앙 조금 위로 설정)
		self.setupWindow() # 윈도우 설정
		self.setupButton() # 버튼 설정
		self.setupLabel() # 레이블 설정
		self.setupEdit() # 에디트 설정
		self.setupRadioBox() # 라디오 박스 설정
		self.setupCheckBox() # 체크 박스 설정
		self.setupStatusBar() # 상태 표시줄 설정

	def setupWindow(self): # 윈도우 특성 설정 함수
		title = 'Elancia Macro Program' # 타이틀
		self.setWindowTitle(title) # 윈도우 타이클 설정
		self.setGeometry(self.pos_x, self.pos_y, self.size_x, self.size_y) # 윈도우 위치, 크기 설정
		ico_binary = icoBinary.title_ico_binary_elancia # 타이틀 아이콘 바이너리
		fp = open(os.getcwd() + '\\tmp_title.ico', 'wb') # 임시 아이콘 파일 생성
		fp.write(ico_binary)
		fp.close()
		self.setWindowIcon(QIcon(os.getcwd() + '\\tmp_title.ico')) # 타이틀 아이콘 설정
		self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowMinMaxButtonsHint) # 닫기 버튼 비활성화
		self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint) # 최대화 버튼 비활성화
		self.setFixedSize(self.size_x, self.size_y) # 화면 크기 변경 금지 설정

	def setupButton(self): # 버튼 설정 함수
		self.btnStart = QPushButton('Start', self) # 매크로 동작 버튼 설정
		self.btnStart.resize(self.btnStart.sizeHint() * 1.5)
		self.btnStart.move(10, self.size_y - 60)
		self.btnStart.clicked.connect(self.start_func) # 매크로 동작 함수 적용
		self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
		self.btnPause = QPushButton('Pause', self) # 매크로 중지 버튼 설정
		self.btnPause.resize(self.btnPause.sizeHint() * 1.5)
		self.btnPause.move(160, self.size_y - 60)
		self.btnPause.clicked.connect(self.pause_func) # 매크로 중지 함수 적용
		self.btnPause.setDisabled(True) # 매크로 중지 버튼 비활성화
		self.btnExit = QPushButton('Exit', self) # 매크로 종료 버튼 설정
		self.btnExit.resize(self.btnExit.sizeHint() * 1.5)
		self.btnExit.move(310, self.size_y - 60)
		self.btnExit.clicked.connect(self.exit_func) # 매크로 종료 함수 적용
		self.btnHealth = QPushButton('Health', self) # 체력바 좌표와 픽셀값 설정 버튼 설정
		self.btnHealth.resize(self.btnHealth.sizeHint() / 1.0)
		self.btnHealth.move(100, 30)
		self.btnHealth.clicked.connect(self.setHealth) # 체력바 좌표와 픽셀값 설정 함수 적용
		self.btnHealth.setDisabled(True) # 체력바 좌표와 픽셀값 설정 버튼 비활성화

	def setupLabel(self): # 레이블 설정 함수
		title = 'Elancia Macro  ver 1.0 by.KHW' # 제목 레이블
		self.label_title = QLabel(title, self) # 제목 레이블 설정
		self.label_title.move(self.size_x/3.4, 10)
		self.label_title.resize(200, 15)
		content_autoPotion = unicode('자동 포션', 'utf-8') # 자동 포션 레이블
		self.label_content_autoPotion = QLabel(content_autoPotion, self) # 자동 포션 레이블 설정
		self.label_content_autoPotion.move(10, 35)
		self.label_content_autoPotion.resize(50, 15)
		content_doubleAttack = unicode('더블 어택', 'utf-8') # 더블 어택 레이블
		self.label_content_doubleAttack = QLabel(content_doubleAttack, self) # 더블 어택 레이블 설정
		self.label_content_doubleAttack.move(10, 120)
		self.label_content_doubleAttack.resize(50, 15)
		content_autoHunt = unicode('자동 사냥', 'utf-8') # 자동 사냥 레이블
		self.label_content_autoHunt = QLabel(content_autoHunt, self) # 자동 사냥 레이블 설정
		self.label_content_autoHunt.move(10, 220)
		self.label_content_autoHunt.resize(55, 15)
		content_fp = unicode('밥통작', 'utf-8') # 밥통작 레이블
		self.label_content_fp = QLabel(content_fp, self) # 밥통작 레이블 설정
		self.label_content_fp.move(10, 376)
		self.label_content_fp.resize(40, 15)

	def setupEdit(self): # 에디트 설정 함수
		self.lineEditLabel_pause_restart = QLabel('Pause & Restart : ', self) # 중지 및 재시작 키 레이블 설정
		self.lineEditLabel_pause_restart.move(self.size_x - 170, 35)
		self.lineEditLabel_pause_restart.resize(100, 15)
		self.lineEdit_pause_restart = QLineEdit(self.pause_restart, self) # 중지 및 재시작 키 에디트 설정
		self.lineEdit_pause_restart.move(self.size_x - 65, 32)
		self.lineEdit_pause_restart.resize(50, 20)
		self.lineEditLabel_health_x = QLabel('Health X Coordinate : ', self) # 체력 포션을 사용하는 체력바의 x좌표 레이블 설정
		self.lineEditLabel_health_x.move(10, 60)
		self.lineEditLabel_health_x.resize(120, 15)
		self.lineEdit_health_x = QLineEdit(str(self.health_x), self) # 체력 포션을 사용하는 체력바의 x좌표 에디트 설정
		self.lineEdit_health_x.move(135, 57)
		self.lineEdit_health_x.resize(50, 20)
		self.lineEdit_health_x.setDisabled(True) # 체력 포션을 사용하는 체력바의 x좌표 에디트 비활성화
		self.lineEditLabel_health_y = QLabel('Health Y Coordinate : ', self) # 체력 포션을 사용하는 체력바의 y좌표 레이블 설정
		self.lineEditLabel_health_y.move(10, 85)
		self.lineEditLabel_health_y.resize(120, 15)
		self.lineEdit_health_y = QLineEdit(str(self.health_y), self) # 체력 포션을 사용하는 체력바의 y좌표 에디트 설정
		self.lineEdit_health_y.move(135, 82)
		self.lineEdit_health_y.resize(50, 20)
		self.lineEdit_health_y.setDisabled(True) # 체력 포션을 사용하는 체력바의 y좌표 에디트 비활성화
		self.lineEditLabel_health_color = QLabel('Health Pixel Color : ', self) # 체력이 부족할때의 체력바 픽셀값 레이블 설정
		self.lineEditLabel_health_color.move(193, 60)
		self.lineEditLabel_health_color.resize(110, 15)
		self.lineEdit_health_color = QLineEdit(str(self.health_color), self) # 체력이 부족할때의 체력바 픽셀값 에디트 설정
		self.lineEdit_health_color.move(308, 57)
		self.lineEdit_health_color.resize(50, 20)
		self.lineEdit_health_color.setDisabled(True) # 체력이 부족할때의 체력바 픽셀값 에디트 비활성화
		self.lineEditLabel_health_potion_key = QLabel('Health Potion Key : ', self) # 체력 포션 단축키 레이블 설정
		self.lineEditLabel_health_potion_key.move(193, 85)
		self.lineEditLabel_health_potion_key.resize(110, 15)
		self.lineEdit_health_potion_key = QLineEdit(self.health_potion_key, self) # 체력 포션 단축키 에디트 설정
		self.lineEdit_health_potion_key.move(308, 82)
		self.lineEdit_health_potion_key.resize(50, 20)
		self.lineEdit_health_potion_key.setDisabled(True) # 체력 포션 단축키 에디트 비활성화
		self.lineEditLabel_doubleAttack_key = QLabel('Double Attack Key : ', self) # 더블 어택 단축키 레이블 설정
		self.lineEditLabel_doubleAttack_key.move(140, 155)
		self.lineEditLabel_doubleAttack_key.resize(110, 15)
		self.lineEdit_doubleAttack_key = QLineEdit(self.doubleAttack_key, self) # 더블 어택 단축키 에디트 설정
		self.lineEdit_doubleAttack_key.move(257, 152)
		self.lineEdit_doubleAttack_key.resize(50, 20)
		self.lineEdit_doubleAttack_key.setDisabled(True) # 더블 어택 단축키 에디트 비활성화
		self.lineEditLabel_doubleAttack_delay = QLabel('Double Attack Delay : ', self) # 더블 어택 재사용 대기 시간 레이블 설정
		self.lineEditLabel_doubleAttack_delay.move(140, 180)
		self.lineEditLabel_doubleAttack_delay.resize(120, 15)
		self.lineEdit_doubleAttack_delay = QLineEdit(str(self.doubleAttack_delay), self) # 더블 어택 재사용 대기 시간 에디트 설정
		self.lineEdit_doubleAttack_delay.move(267, 177)
		self.lineEdit_doubleAttack_delay.resize(50, 20)
		self.lineEdit_doubleAttack_delay.setDisabled(True) # 더블 어택 재사용 대기 시간 에디트 비활성화
		self.lineEditLabel_attack_delay = QLabel('Attack Delay : ', self) # 몬스터 클릭 후 사냥 완료할 때까지의 대기 시간 레이블 설정
		self.lineEditLabel_attack_delay.move(10, 245)
		self.lineEditLabel_attack_delay.resize(80, 15)
		self.lineEdit_attack_delay = QLineEdit(str(self.attack_delay), self) # 몬스터 클릭 후 사냥 완료할 때까지의 대기 시간 에디트 설정
		self.lineEdit_attack_delay.move(95, 242)
		self.lineEdit_attack_delay.resize(50, 20)
		self.lineEdit_attack_delay.setDisabled(True) # 몬스터 클릭 후 사냥 완료할 때까지의 대기 시간 에디트 비활성화
		self.lineEditLabel_front_template_image_file = QLabel('Front Template Image File : ', self) # 몬스터 정면 이미지 템플릿 파일 레이블 설정
		self.lineEditLabel_front_template_image_file.move(10, 270)
		self.lineEditLabel_front_template_image_file.resize(160, 15)
		self.lineEdit_front_template_image_file = QLineEdit(self.front_template_image_file, self) # 몬스터 정면 이미지 템플릿 파일 에디트 설정
		self.lineEdit_front_template_image_file.move(172, 267)
		self.lineEdit_front_template_image_file.resize(250, 20)
		self.lineEdit_front_template_image_file.setDisabled(True) # 몬스터 정면 이미지 템플릿 파일 에디트 비활성화
		self.lineEditLabel_back_template_image_file = QLabel('Back Template Image File : ', self) # 몬스터 후면 이미지 템플릿 파일 레이블 설정
		self.lineEditLabel_back_template_image_file.move(10, 295)
		self.lineEditLabel_back_template_image_file.resize(160, 15)
		self.lineEdit_back_template_image_file = QLineEdit(self.back_template_image_file, self) # 몬스터 후면 이미지 템플릿 파일 에디트 설정
		self.lineEdit_back_template_image_file.move(172, 292)
		self.lineEdit_back_template_image_file.resize(250, 20)
		self.lineEdit_back_template_image_file.setDisabled(True) # 몬스터 후면 이미지 템플릿 파일 에디트 비활성화
		self.lineEditLabel_leftside_template_image_file = QLabel('Leftside Template Image File : ', self) # 몬스터 좌측면 이미지 템플릿 파일 레이블 설정
		self.lineEditLabel_leftside_template_image_file.move(10, 320)
		self.lineEditLabel_leftside_template_image_file.resize(175, 15)
		self.lineEdit_leftside_template_image_file = QLineEdit(self.leftside_template_image_file, self) # 몬스터 좌측면 이미지 템플릿 파일 에디트 설정
		self.lineEdit_leftside_template_image_file.move(187, 317)
		self.lineEdit_leftside_template_image_file.resize(235, 20)
		self.lineEdit_leftside_template_image_file.setDisabled(True) # 몬스터 좌측면 이미지 템플릿 파일 에디트 비활성화
		self.lineEditLabel_rightside_template_image_file = QLabel('Rightside Template Image File : ', self) # 몬스터 우측면 이미지 템플릿 파일 레이블 설정
		self.lineEditLabel_rightside_template_image_file.move(10, 345)
		self.lineEditLabel_rightside_template_image_file.resize(180, 15)
		self.lineEdit_rightside_template_image_file = QLineEdit(self.rightside_template_image_file, self) # 몬스터 우측면 이미지 템플릿 파일 에디트 설정
		self.lineEdit_rightside_template_image_file.move(195, 342)
		self.lineEdit_rightside_template_image_file.resize(228, 20)
		self.lineEdit_rightside_template_image_file.setDisabled(True) # 몬스터 우측면 이미지 템플릿 파일 에디트 비활성화
		self.lineEditLabel_doubleAttack_delay_fp = QLabel('Double Attack Delay : ', self) # 더블 어택(밥통작) 재사용 대기 시간 레이블 설정
		self.lineEditLabel_doubleAttack_delay_fp.move(10, 400)
		self.lineEditLabel_doubleAttack_delay_fp.resize(120, 15)
		self.lineEdit_doubleAttack_delay_fp = QLineEdit(str(self.doubleAttack_delay_fp), self) # 더블 어택(밥통작) 재사용 대기 시간 에디트 설정
		self.lineEdit_doubleAttack_delay_fp.move(137, 397)
		self.lineEdit_doubleAttack_delay_fp.resize(50, 20)
		self.lineEdit_doubleAttack_delay_fp.setDisabled(True) # 더블 어택(밥통작) 재사용 대기 시간 에디트 비활성화
		self.lineEditLabel_doubleAttack_key_fp = QLabel('Double Attack Key : ', self) # 더블 어택(밥통작) 단축키 레이블 설정
		self.lineEditLabel_doubleAttack_key_fp.move(10, 425)
		self.lineEditLabel_doubleAttack_key_fp.resize(110, 15)
		self.lineEdit_doubleAttack_key_fp = QLineEdit(self.doubleAttack_key_fp, self) # 더블 어택(밥통작) 단축키 에디트 설정
		self.lineEdit_doubleAttack_key_fp.move(127, 422)
		self.lineEdit_doubleAttack_key_fp.resize(50, 20)
		self.lineEdit_doubleAttack_key_fp.setDisabled(True) # 더블 어택(밥통작) 단축키 에디트 비활성화
		self.lineEditLabel_holyMenu_key = QLabel('Holy Menu Key : ', self) # 홀리 메뉴 단축키 레이블 설정
		self.lineEditLabel_holyMenu_key.move(185, 425)
		self.lineEditLabel_holyMenu_key.resize(100, 15)
		self.lineEdit_holyMenu_key = QLineEdit(self.holyMenu_key, self) # 홀리 메뉴 단축키 에디트 설정
		self.lineEdit_holyMenu_key.move(287, 422)
		self.lineEdit_holyMenu_key.resize(50, 20)
		self.lineEdit_holyMenu_key.setDisabled(True) # 홀리 메뉴 단축키 에디트 비활성화
		self.lineEditLabel_characterName = QLabel(unicode('※ Character Name : ', 'utf-8'), self) # 캐릭터명 레이블 설정
		self.lineEditLabel_characterName.move(10, 463)
		self.lineEditLabel_characterName.resize(120, 15)
		self.lineEdit_characterName = QLineEdit(self.characterName, self) # 캐릭터명 에디트 설정
		self.lineEdit_characterName.move(135, 460)
		self.lineEdit_characterName.resize(100, 20)
		self.lineEdit_infiniteInput_key = QLineEdit(self.infinite_key, self) # 반복해서 입력할 단축키 에디트 설정
		self.lineEdit_infiniteInput_key.move(373, 232)
		self.lineEdit_infiniteInput_key.resize(50, 20)
		self.lineEdit_infiniteInput_key.setDisabled(True) # 반복해서 입력할 단축키 에디트 비활성화

	def setupRadioBox(self): # 라디오 박스 설정 함수
		self.groupBox_doubleAttack = QGroupBox('Choose', self) # 라디오 박스 그룹
		self.groupBox_doubleAttack.move(10, 145)
		self.groupBox_doubleAttack.resize(120, 60)
		self.radiobox_doubleAttack_autoRepeat = QRadioButton('Auto Repeat', self) # 더블 어택 자동 반복 매크로 라디오 박스 설정
		self.radiobox_doubleAttack_autoRepeat.move(18, 155)
		self.radiobox_doubleAttack_autoRepeat.clicked.connect(self.doubleAttack_autoRepeat_radio) # 더블 어택 자동 반복 매크로 라디오 박스 체크/해제 설정 함수 적용
		self.radiobox_doubleAttack_autoRepeat.setChecked(True) # 디폴트 선택
		self.radiobox_doubleAttack_autoRepeat.setEnabled(False) # 더블 어택 자동 반복 매크로 라디오 박스 비활성화
		self.radiobox_doubleAttack_withAutoHunt = QRadioButton('With Auto Hunt', self) # 더블 어택이 자동 사냥 매크로와 같이 동작하는 매크로 라디오 박스 설정
		self.radiobox_doubleAttack_withAutoHunt.move(18, 175)
		self.radiobox_doubleAttack_withAutoHunt.clicked.connect(self.doubleAttack_withAutoHunt_radio) # 더블 어택이 자동 사냥 매크로와 같이 동작하는 매크로 라디오 박스 체크/해제 설정 함수 적용
		self.radiobox_doubleAttack_withAutoHunt.setEnabled(False) # 더블 어택이 자동 사냥 매크로와 같이 동작하는 매크로 라디오 박스 비활성화

	def setupCheckBox(self): # 체크 박스 설정 함수
		self.checkbox_autoPotion = QCheckBox('', self) # 자동 포션 매크로 체크 박스 설정
		self.checkbox_autoPotion.move(70, 34)
		self.checkbox_autoPotion.resize(15, 15)
		self.checkbox_autoPotion.stateChanged.connect(self.autoPotion_check) # 자동 포션 매크로 체크/해제 설정 함수 적용
		self.checkbox_doubleAttack = QCheckBox('', self) # 더블 어택 매크로 체크 박스 설정
		self.checkbox_doubleAttack.move(70, 119)
		self.checkbox_doubleAttack.resize(15, 15)
		self.checkbox_doubleAttack.stateChanged.connect(self.doubleAttack_check) # 더블 어택 매크로 체크/해제 설정 함수 적용
		self.checkbox_autoHunt = QCheckBox('', self) # 자동 사냥 매크로 체크 박스 설정
		self.checkbox_autoHunt.move(70, 219)
		self.checkbox_autoHunt.resize(15, 15)
		self.checkbox_autoHunt.stateChanged.connect(self.autoHunt_check) # 자동 사냥 매크로 체크/해제 설정 함수 적용
		self.checkbox_fp = QCheckBox('', self) # 밥통작 매크로 체크 박스 설정
		self.checkbox_fp.move(54, 375)
		self.checkbox_fp.resize(15, 15)
		self.checkbox_fp.stateChanged.connect(self.fp_check) # 밥통작 매크로 체크/해제 설정 함수 적용
		self.checkbox_infiniteClick = QCheckBox('Infinite Click', self) # 반복 마우스 좌클릭 매크로 체크 박스 설정
		self.checkbox_infiniteClick.move(250, 215)
		self.checkbox_infiniteClick.resize(90, 15)
		self.checkbox_infiniteClick.stateChanged.connect(self.infiniteClick_check) # 반복 마우스 좌클릭 매크로 체크/해제 설정 함수 적용
		self.checkbox_infiniteInput = QCheckBox('Infinite Input Key : ', self) # 반복 설정한 단축키 입력 매크로 체크 박스 설정
		self.checkbox_infiniteInput.move(250, 235)
		self.checkbox_infiniteInput.resize(120, 15)
		self.checkbox_infiniteInput.stateChanged.connect(self.infiniteInput_check) # 반복 설정한 단축키 입력 매크로 체크/해제 설정 함수 적용

	def setupStatusBar(self): # 상태 표시줄 설정 함수
		self.statusBar = QStatusBar(self) # 상태 표시줄 설정
		self.setStatusBar(self.statusBar)
		self.statusBar.showMessage('Not Setted') # 초기 상태 표시줄 내용

	def set_coordinate_pixel_thread(self, key, vk, key_state): # 체력바 좌표와 픽셀값 설정 스레드
		while True:
			try:
				sem.acquire() # 임계영역 생성
				cur_key_state = win32api.GetKeyState(vk[1]) # 현재 키보드 입력 상태
				if cur_key_state != key_state: # 키보드 입력 상태가 변경됐을 경우
					key_state = cur_key_state # 키보드 입력 상태 갱신
					if key_state == -127 or key_state == -128: # 두번 실행 방지
						if key == 'enter': # 입력한 키가 엔터 키일 경우
							self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
							self.btnHealth.setEnabled(True) # 체력바 좌표와 픽셀값 설정 버튼 활성화
							self.lineEdit_pause_restart.setEnabled(True) # 중지 및 재시작 키 에디트 활성화
							self.lineEdit_characterName.setEnabled(True) # 캐릭터명 에디트 활성화
							self.checkbox_autoPotion.setEnabled(True) # 자동 포션 매크로 체크 박스 활성화
							self.checkbox_doubleAttack.setEnabled(True) # 더블 어택 매크로 체크 박스 활성화
							self.checkbox_autoHunt.setEnabled(True) # 자동 사냥 매크로 체크 박스 활성화
							if self.check_doubleAttack == True: # 더블 어택 매크로가 체크되어 있을 경우
								self.radiobox_doubleAttack_autoRepeat.setEnabled(True) # 더블 어택 자동 반복 매크로 라디오 박스 활성화
								self.radiobox_doubleAttack_withAutoHunt.setEnabled(True) # 더블 어택이 자동 사냥 매크로와 같이 동작하는 매크로 라디오 박스 활성화
								self.lineEdit_doubleAttack_key.setEnabled(True) # 더블 어택 단축키 에디트 활성화
								self.lineEdit_doubleAttack_delay.setEnabled(True) # 더블 어택 재사용 대기 시간 에디트 활성화
							if self.check_autoHunt == True: # 자동 사냥 매크로가 체크되어 있을 경우
								self.lineEdit_attack_delay.setEnabled(True) # 몬스터 클릭 후 사냥 완료할 때까지의 대기 시간 에디트 활성화
								self.lineEdit_front_template_image_file.setEnabled(True) # 몬스터 정면 이미지 템플릿 파일 에디트 활성화
								self.lineEdit_back_template_image_file.setEnabled(True) # 몬스터 후면 이미지 템플릿 파일 에디트 활성화
								self.lineEdit_leftside_template_image_file.setEnabled(True) # 몬스터 좌측면 이미지 템플릿 파일 에디트 활성화
								self.lineEdit_rightside_template_image_file.setEnabled(True) # 몬스터 우측면 이미지 템플릿 파일 에디트 활성화
							sem.release() # 임계영역 해제
							return # 스레드 종료
				else: # 키보드 입력 상태가 변경되지 않았을 경우
					current_pos_x = myMacro.get_mouse_pos()[0] # 현재 마우스 x좌표 저장
					current_pos_y = myMacro.get_mouse_pos()[1] - 3 # 현재 마우스 y좌표 저장(메이플 마우스 포인터 때문에 화면의 픽셀이 제대로 잡히지 않음.(메이플 마우스 포인터의 픽셀이 잡힘) 따라서 현재 마우스 포인터 위치에서 2만큼 위쪽 픽셀의 값을 저장함으로써 화면의 픽셀값이 잡히도록 설정)
					currnet_pos_pixel = QPixmap.grabWindow(QApplication.desktop().winId()).toImage().pixel(current_pos_x, current_pos_y) # 현재 마우스 위치의 픽셀 값(16진수) 저장
					current_pixel_color = (qBlue(currnet_pos_pixel) * 65536 + qGreen(currnet_pos_pixel) * 256 + qRed(currnet_pos_pixel)) # 픽셀 값 10진수로 변경
					self.lineEdit_health_x.setText(str(current_pos_x)) # 체력 포션을 사용하는 체력바의 x좌표 에디트의 값을 현재 마우스 x좌표로 변경
					self.lineEdit_health_y.setText(str(current_pos_y)) # 체력 포션을 사용하는 체력바의 y좌표 에디트의 값을 현재 마우스 y좌표로 변경
					self.lineEdit_health_color.setText(str(current_pixel_color)) # 체력이 부족할때의 체력바 픽셀값 에디트의 값을 현재 마우스 위치의 픽셀 값으로 변경
				sem.release() # 임계영역 해제
			except Exception, e:
				sem.release() # 임계영역 해제
				pass	

	def setHealth(self): # 체력바 좌표와 픽셀값 설정 함수
		try:
			if self.check_autoPotion == True: # 자동 포션 매크로가 체크되어 있을 경우
				self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
				self.btnHealth.setDisabled(True) # 체력바 좌표와 픽셀값 설정 버튼 비활성화
				self.lineEdit_pause_restart.setDisabled(True) # 중지 및 재시작 키 에디트 비활성화
				self.lineEdit_characterName.setDisabled(True) # 캐릭터명 에디트 비활성화
				self.checkbox_autoPotion.setDisabled(True) # 자동 포션 매크로 체크 박스 비활성화
				self.checkbox_doubleAttack.setDisabled(True) # 더블 어택 매크로 체크 박스 비활성화
				self.checkbox_autoHunt.setDisabled(True) # 자동 사냥 매크로 체크 박스 비활성화
				if self.check_doubleAttack == True: # 더블 어택 매크로가 체크되어 있을 경우
					self.radiobox_doubleAttack_autoRepeat.setDisabled(True) # 더블 어택 자동 반복 매크로 라디오 박스 비활성화
					self.radiobox_doubleAttack_withAutoHunt.setDisabled(True) # 더블 어택이 자동 사냥 매크로와 같이 동작하는 매크로 라디오 박스 비활성화
					self.lineEdit_doubleAttack_key.setDisabled(True) # 더블 어택 단축키 에디트 비활성화
					self.lineEdit_doubleAttack_delay.setDisabled(True) # 더블 어택 재사용 대기 시간 에디트 비활성화
				if self.check_autoHunt == True: # 자동 사냥 매크로가 체크되어 있을 경우
					self.lineEdit_attack_delay.setDisabled(True) # 몬스터 클릭 후 사냥 완료할 때까지의 대기 시간 에디트 비활성화
					self.lineEdit_front_template_image_file.setDisabled(True) # 몬스터 정면 이미지 템플릿 파일 에디트 비활성화
					self.lineEdit_back_template_image_file.setDisabled(True) # 몬스터 후면 이미지 템플릿 파일 에디트 비활성화
					self.lineEdit_leftside_template_image_file.setDisabled(True) # 몬스터 좌측면 이미지 템플릿 파일 에디트 비활성화
					self.lineEdit_rightside_template_image_file.setDisabled(True) # 몬스터 우측면 이미지 템플릿 파일 에디트 비활성화
				self.statusBar.showMessage('Input \'enter\' key to complete setting') # 상태 표시줄 내용 갱신
				for vk in myMacro.virtual_key:
					if 'enter' == vk[0]: # 엔터 키일 경우
						key_state_enter = win32api.GetKeyState(vk[1]) # 엔터 키 초기 입력 상태
						th_set_health_coordinate_pixel = threading.Thread(target=self.set_coordinate_pixel_thread, args=('enter', vk, key_state_enter,)) # 체력바 좌표와 픽셀값 설정 스레드 설정
						th_set_health_coordinate_pixel.start() # 스레드 생성
						break
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def autoPotion_check(self): # 자동 포션 매크로 체크/해제 설정 함수
		try:
			if self.check_autoPotion == True: # 자동 포션 매크로가 체크되어 있을 경우
				self.check_autoPotion = False # 자동 포션 매크로 체크 해제 설정
				self.btnHealth.setDisabled(True) # 체력바 좌표와 픽셀값 설정 버튼 비활성화
				self.lineEdit_health_x.setDisabled(True) # 체력 포션을 사용하는 체력바의 x좌표 에디트 비활성화
				self.lineEdit_health_y.setDisabled(True) # 체력 포션을 사용하는 체력바의 y좌표 에디트 비활성화
				self.lineEdit_health_color.setDisabled(True) # 체력이 부족할때의 체력바 픽셀값 에디트 비활성화
				self.lineEdit_health_potion_key.setDisabled(True) # 체력 포션 단축키 에디트 비활성화
				if self.check_autoPotion == False and self.check_doubleAttack == False and self.check_autoHunt == False: # 자동 포션, 더블 어택, 자동 사냥 매크로가 모두 체크되어 있지 않을 경우
					self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
					self.checkbox_fp.setEnabled(True) # 밥통작 매크로 체크 박스 활성화
					self.checkbox_infiniteInput.setEnabled(True) # 반복 설정한 단축키 입력 매크로 활성화
					self.checkbox_infiniteClick.setEnabled(True) # 반복 마우스 좌클릭 매크로 활성화
				self.statusBar.showMessage('Auto Potion Unchecked') # 상태 표시줄 내용 갱신
			elif self.check_autoPotion == False: # 자동 포션 매크로가 체크되어 있지 않을 경우
				if self.check_autoPotion == False and self.check_doubleAttack == False and self.check_autoHunt == False: # 자동 포션, 더블 어택, 자동 사냥 매크로가 모두 체크되어 있지 않을 경우
					self.checkbox_fp.setDisabled(True) # 밥통작 매크로 체크 박스 비활성화
					self.checkbox_infiniteInput.setDisabled(True) # 반복 설정한 단축키 입력 매크로 비활성화
					self.checkbox_infiniteClick.setDisabled(True) # 반복 마우스 좌클릭 매크로 비활성화
				self.check_autoPotion = True # 자동 포션 매크로 체크 설정
				self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
				self.btnHealth.setEnabled(True) # 체력바 좌표와 픽셀값 설정 버튼 활성화
				self.lineEdit_health_x.setEnabled(True) # 체력 포션을 사용하는 체력바의 x좌표 에디트 활성화
				self.lineEdit_health_y.setEnabled(True) # 체력 포션을 사용하는 체력바의 y좌표 에디트 활성화
				self.lineEdit_health_color.setEnabled(True) # 체력이 부족할때의 체력바 픽셀값 에디트 활성화
				self.lineEdit_health_potion_key.setEnabled(True) # 체력 포션 단축키 에디트 활성화
				self.statusBar.showMessage('Auto Potion Checked') # 상태 표시줄 내용 갱신
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def doubleAttack_check(self): # 더블 어택 매크로 체크/해제 설정 함수
		try:
			if self.check_doubleAttack == True: # 더블 어택 매크로가 체크되어 있을 경우
				self.check_doubleAttack = False # 더블 어택 매크로 체크 해제 설정
				self.radiobox_doubleAttack_autoRepeat.setDisabled(True) # 더블 어택 자동 반복 매크로 라디오 박스 비활성화
				self.radiobox_doubleAttack_withAutoHunt.setDisabled(True) # 더블 어택이 자동 사냥 매크로와 같이 동작하는 매크로 라디오 박스 비활성화
				self.lineEdit_doubleAttack_key.setDisabled(True) # 더블 어택 단축키 에디트 비활성화
				self.lineEdit_doubleAttack_delay.setDisabled(True) # 더블 어택 재사용 대기 시간 에디트 비활성화
				if self.check_autoPotion == False and self.check_doubleAttack == False and self.check_autoHunt == False: # 자동 포션, 더블 어택, 자동 사냥 매크로가 모두 체크되어 있지 않을 경우
					self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
					self.checkbox_fp.setEnabled(True) # 밥통작 매크로 체크 박스 활성화
					self.checkbox_infiniteInput.setEnabled(True) # 반복 설정한 단축키 입력 매크로 활성화
					self.checkbox_infiniteClick.setEnabled(True) # 반복 마우스 좌클릭 매크로 활성화
				self.statusBar.showMessage('Double Attack Unchecked') # 상태 표시줄 내용 갱신
			elif self.check_doubleAttack == False : # 더블 어택 매크로가 체크되어 있지 않을 경우
				if self.check_autoPotion == False and self.check_doubleAttack == False and self.check_autoHunt == False: # 자동 포션, 더블 어택, 자동 사냥 매크로가 모두 체크되어 있지 않을 경우
					self.checkbox_fp.setDisabled(True) # 밥통작 매크로 체크 박스 비활성화
					self.checkbox_infiniteInput.setDisabled(True) # 반복 설정한 단축키 입력 매크로 비활성화
					self.checkbox_infiniteClick.setDisabled(True) # 반복 마우스 좌클릭 매크로 비활성화
				self.check_doubleAttack = True # 더블 어택 매크로 체크 설정
				self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
				self.radiobox_doubleAttack_autoRepeat.setEnabled(True) # 더블 어택 자동 반복 매크로 라디오 박스 활성화
				self.radiobox_doubleAttack_withAutoHunt.setEnabled(True) # 더블 어택이 자동 사냥 매크로와 같이 동작하는 매크로 라디오 박스 활성화
				self.lineEdit_doubleAttack_key.setEnabled(True) # 더블 어택 단축키 에디트 활성화
				if self.radiobox_doubleAttack_autoRepeat.isChecked() == True: # 더블 어택 자동 반복 매크로가 체크되어 있을 경우
					self.lineEdit_doubleAttack_delay.setEnabled(True) # 더블 어택 재사용 대기 시간 에디트 활성화
				self.statusBar.showMessage('Double Attack Checked') # 상태 표시줄 내용 갱신
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def autoHunt_check(self): # 자동 사냥 매크로 체크/해제 설정 함수
		try:
			if self.check_autoHunt == True: # 자동 사냥 매크로가 체크되어 있을 경우
				self.check_autoHunt = False # 자동 사냥 매크로 체크 해제 설정
				self.lineEdit_attack_delay.setDisabled(True) # 몬스터 클릭 후 사냥 완료할 때까지의 대기 시간 에디트 비활성화
				self.lineEdit_front_template_image_file.setDisabled(True) # 몬스터 정면 이미지 템플릿 파일 에디트 비활성화
				self.lineEdit_back_template_image_file.setDisabled(True) # 몬스터 후면 이미지 템플릿 파일 에디트 비활성화
				self.lineEdit_leftside_template_image_file.setDisabled(True) # 몬스터 좌측면 이미지 템플릿 파일 에디트 비활성화
				self.lineEdit_rightside_template_image_file.setDisabled(True) # 몬스터 우측면 이미지 템플릿 파일 에디트 비활성화
				if self.check_autoPotion == False and self.check_doubleAttack == False and self.check_autoHunt == False: # 자동 포션, 더블 어택, 자동 사냥 매크로가 모두 체크되어 있지 않을 경우
					self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
					self.checkbox_fp.setEnabled(True) # 밥통작 매크로 체크 박스 활성화
					self.checkbox_infiniteInput.setEnabled(True) # 반복 설정한 단축키 입력 매크로 활성화
					self.checkbox_infiniteClick.setEnabled(True) # 반복 마우스 좌클릭 매크로 활성화
				self.statusBar.showMessage('Auto Hunt Unchecked') # 상태 표시줄 내용 갱신
			elif self.check_autoHunt == False: # 자동 사냥 매크로가 체크되어 있지 않을 경우
				if self.check_autoPotion == False and self.check_doubleAttack == False and self.check_autoHunt == False: # 자동 포션, 더블 어택, 자동 사냥 매크로가 모두 체크되어 있지 않을 경우
					self.checkbox_fp.setDisabled(True) # 밥통작 매크로 체크 박스 비활성화
					self.checkbox_infiniteInput.setDisabled(True) # 반복 설정한 단축키 입력 매크로 비활성화
					self.checkbox_infiniteClick.setDisabled(True) # 반복 마우스 좌클릭 매크로 비활성화
				self.check_autoHunt = True # 자동 사냥 매크로 체크 설정
				self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
				self.lineEdit_attack_delay.setEnabled(True) # 몬스터 클릭 후 사냥 완료할 때까지의 대기 시간 에디트 활성화
				self.lineEdit_front_template_image_file.setEnabled(True) # 몬스터 정면 이미지 템플릿 파일 에디트 활성화
				self.lineEdit_back_template_image_file.setEnabled(True) # 몬스터 후면 이미지 템플릿 파일 에디트 활성화
				self.lineEdit_leftside_template_image_file.setEnabled(True) # 몬스터 좌측면 이미지 템플릿 파일 에디트 활성화
				self.lineEdit_rightside_template_image_file.setEnabled(True) # 몬스터 우측면 이미지 템플릿 파일 에디트 활성화
				self.statusBar.showMessage('Auto Hunt Checked') # 상태 표시줄 내용 갱신
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신
				
	def fp_check(self): # 밥통작 매크로 체크/해제 설정 함수
		try:
			if self.check_fp == True: # 밥통작 매크로가 체크되어 있을 경우
				self.check_fp = False # 밥통작 매크로 체크 해제 설정
				self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
				self.lineEdit_doubleAttack_delay_fp.setDisabled(True) # 더블 어택(밥통작) 재사용 대기 시간 에디트 비활성화
				self.lineEdit_doubleAttack_key_fp.setDisabled(True) # 더블 어택(밥통작) 단축키 에디트 비활성화
				self.lineEdit_holyMenu_key.setDisabled(True) # 홀리 메뉴 단축키 에디트 비활성화
				self.checkbox_autoPotion.setEnabled(True) # 자동 포션 매크로 체크 박스 활성화
				self.checkbox_doubleAttack.setEnabled(True) # 더블 어택 매크로 체크 박스 활성화
				self.checkbox_autoHunt.setEnabled(True) # 자동 사냥 매크로 체크 박스 활성화
				self.checkbox_infiniteInput.setEnabled(True) # 반복 설정한 단축키 입력 매크로 활성화
				self.checkbox_infiniteClick.setEnabled(True) # 반복 마우스 좌클릭 매크로 활성화
				self.statusBar.showMessage('FP Unchecked') # 상태 표시줄 내용 갱신
			elif self.check_fp == False: # 밥통작 매크로가 체크되어 있지 않을 경우
				self.check_fp = True # 밥통작 매크로 체크 설정
				self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
				self.lineEdit_doubleAttack_delay_fp.setEnabled(True) # 더블 어택(밥통작) 재사용 대기 시간 에디트 활성화
				self.lineEdit_doubleAttack_key_fp.setEnabled(True) # 더블 어택(밥통작) 단축키 에디트 활성화
				self.lineEdit_holyMenu_key.setEnabled(True) # 홀리 메뉴 단축키 에디트 활성화
				self.checkbox_autoPotion.setDisabled(True) # 자동 포션 매크로 체크 박스 비활성화
				self.checkbox_doubleAttack.setDisabled(True) # 더블 어택 매크로 체크 박스 비활성화
				self.checkbox_autoHunt.setDisabled(True) # 자동 사냥 매크로 체크 박스 비활성화
				self.checkbox_infiniteInput.setDisabled(True) # 반복 설정한 단축키 입력 매크로 비활성화
				self.checkbox_infiniteClick.setDisabled(True) # 반복 마우스 좌클릭 매크로 비활성화
				self.statusBar.showMessage('FP Checked') # 상태 표시줄 내용 갱신
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def infiniteClick_check(self): # 반복 마우스 좌클릭 매크로 체크/해제 설정 함수
		try:
			if self.check_infiniteClick == True: # 반복 마우스 좌클릭 매크로가 체크되어 있을 경우
				self.check_infiniteClick = False # 반복 마우스 좌클릭 매크로 체크 해제 설정
				self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
				self.checkbox_infiniteInput.setEnabled(True) # 반복 설정한 단축키 입력 매크로 체크 박스 활성화
				self.checkbox_autoPotion.setEnabled(True) # 자동 포션 매크로 체크 박스 활성화
				self.checkbox_doubleAttack.setEnabled(True) # 더블 어택 매크로 체크 박스 활성화
				self.checkbox_autoHunt.setEnabled(True) # 자동 사냥 매크로 체크 박스 활성화
				self.checkbox_fp.setEnabled(True) # 밥통작 매크로 체크 박스 활성화
			elif self.check_infiniteClick == False: # 반복 마우스 좌클릭 매크로가 체크되어 있지 않을 경우
				self.check_infiniteClick = True # 반복 마우스 좌클릭 매크로 체크 설정
				self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
				self.checkbox_infiniteInput.setDisabled(True) # 반복 설정한 단축키 입력 매크로 체크 박스 비활성화
				self.checkbox_autoPotion.setDisabled(True) # 자동 포션 매크로 체크 박스 비활성화
				self.checkbox_doubleAttack.setDisabled(True) # 더블 어택 매크로 체크 박스 비활성화
				self.checkbox_autoHunt.setDisabled(True) # 자동 사냥 매크로 체크 박스 비활성화
				self.checkbox_fp.setDisabled(True) # 밥통작 매크로 체크 박스 비활성화
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def infiniteInput_check(self): # 반복 설정한 단축키 입력 매크로 체크/해제 설정 함수
		try:
			if self.check_infiniteInput == True: # 반복 설정한 단축키 입력 매크로가 체크되어 있을 경우
				self.check_infiniteInput = False # 반복 설정한 단축키 입력 매크로 체크 해제 설정
				self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
				self.checkbox_infiniteClick.setEnabled(True) # 반복 마우스 좌클릭 매크로 체크 박스 활성화
				self.lineEdit_infiniteInput_key.setDisabled(True) # 반복해서 입력할 단축키 에디트 비활성화
				self.checkbox_autoPotion.setEnabled(True) # 자동 포션 매크로 체크 박스 활성화
				self.checkbox_doubleAttack.setEnabled(True) # 더블 어택 매크로 체크 박스 활성화
				self.checkbox_autoHunt.setEnabled(True) # 자동 사냥 매크로 체크 박스 활성화
				self.checkbox_fp.setEnabled(True) # 밥통작 매크로 체크 박스 활성화
			elif self.check_infiniteInput == False: # 반복 설정한 단축키 입력 매크로가 체크되어 있지 않을 경우
				self.check_infiniteInput = True # 반복 설정한 단축키 입력 매크로 체크 설정
				self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
				self.checkbox_infiniteClick.setDisabled(True) # 반복 마우스 좌클릭 매크로 체크 박스 비활성화
				self.lineEdit_infiniteInput_key.setEnabled(True) # 반복해서 입력할 단축키 에디트 활성화
				self.checkbox_autoPotion.setDisabled(True) # 자동 포션 매크로 체크 박스 비활성화
				self.checkbox_doubleAttack.setDisabled(True) # 더블 어택 매크로 체크 박스 비활성화
				self.checkbox_autoHunt.setDisabled(True) # 자동 사냥 매크로 체크 박스 비활성화
				self.checkbox_fp.setDisabled(True) # 밥통작 매크로 체크 박스 비활성화
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def doubleAttack_autoRepeat_radio(self): # 더블 어택 자동 반복 매크로 라디오 박스 체크/해제 설정 함수
		try:
			self.lineEdit_doubleAttack_delay.setEnabled(True) # 더블 어택 재사용 대기 시간 에디트 활성화
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def doubleAttack_withAutoHunt_radio(self): # 더블 어택이 자동 사냥 매크로와 같이 동작하는 매크로 라디오 박스 체크/해제 설정 함수
		try:
			self.lineEdit_doubleAttack_delay.setDisabled(True) # 더블 어택 재사용 대기 시간 에디트 비활성화
		except Exception, e:
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
						if key_state == -127 or key_state == -128: # 두번 실행 방지
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
			if self.start == True: # 매크로가 동작중인 경우
				exit_var = True # 스레드 종료 변수 값 설정
				self.start = False # 시작 버튼 눌림 여부 값 변경
				self.statusBar.showMessage('Pause') # 상태 표시줄 내용 갱신
				self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
				self.btnPause.setDisabled(True) # 매크로 중지 버튼 비활성화
				self.lineEdit_pause_restart.setEnabled(True) # 중지 및 재시작 키 에디트 활성화
				self.lineEdit_characterName.setEnabled(True) # 캐릭터명 에디트 활성화
				for vk in myMacro.virtual_key:
					if self.pause_restart == vk[0]: # 설정한 재시작 키일 경우
						key_state_restart = win32api.GetKeyState(vk[1]) # 설정한 재시작 키 초기 입력 상태
						th_restart = threading.Thread(target=self.restart_thread, args=(self.pause_restart, vk, key_state_restart,)) # 설정한 단축키로 매크로 재시작하는 스레드 설정
						th_restart.start() # 스레드 생성
						break
				if self.check_infiniteClick == True: # 반복 마우스 좌클릭 매크로일 경우
					self.checkbox_infiniteClick.setEnabled(True) # 반복 마우스 좌클릭 매크로 체크 박스 활성화
					return
				elif self.check_infiniteInput == True: # 반복 설정한 단축키 입력 매크로일 경우
					self.checkbox_infiniteInput.setEnabled(True) # 반복 설정한 단축키 입력 매크로 체크 박스 활성화
					self.lineEdit_infiniteInput_key.setEnabled(True) # 반복해서 입력할 단축키 에디트 활성화
					return
				if self.check_fp == True: # 밥통작 매크로일 경우
					self.checkbox_fp.setEnabled(True) # 밥통작 매크로 체크 박스 활성화
					self.lineEdit_doubleAttack_delay_fp.setEnabled(True) # 더블 어택(밥통작) 재사용 대기 시간 에디트 활성화
					self.lineEdit_doubleAttack_key_fp.setEnabled(True) # 더블 어택(밥통작) 단축키 에디트 활성화
					self.lineEdit_holyMenu_key.setEnabled(True) # 홀리 메뉴 단축키 에디트 활성화
					return
				self.checkbox_autoPotion.setEnabled(True) # 자동 포션 매크로 체크 박스 활성화
				self.checkbox_doubleAttack.setEnabled(True) # 더블 어택 매크로 체크 박스 활성화
				self.checkbox_autoHunt.setEnabled(True) # 자동 사냥 매크로 체크 박스 활성화
				if self.check_autoPotion == True: # 자동 포션 매크로일 경우
					self.btnHealth.setEnabled(True) # 체력바 좌표와 픽셀값 설정 버튼 활성화
					self.lineEdit_health_x.setEnabled(True) # 체력 포션을 사용하는 체력바의 x좌표 에디트 활성화
					self.lineEdit_health_y.setEnabled(True) # 체력 포션을 사용하는 체력바의 y좌표 에디트 활성화
					self.lineEdit_health_color.setEnabled(True) # 체력이 부족할때의 체력바 픽셀값 에디트 활성화
					self.lineEdit_health_potion_key.setEnabled(True) # 체력 포션 단축키 에디트 활성화
				if self.check_doubleAttack == True: # 더블 어택 매크로일 경우
					self.radiobox_doubleAttack_autoRepeat.setEnabled(True) # 더블 어택 자동 반복 매크로 라디오 박스 활성화
					self.radiobox_doubleAttack_withAutoHunt.setEnabled(True) # 더블 어택이 자동 사냥 매크로와 같이 동작하는 매크로 라디오 박스 활성화
					self.lineEdit_doubleAttack_key.setEnabled(True) # 더블 어택 단축키 에디트 활성화
					self.lineEdit_doubleAttack_delay.setEnabled(True) # 더블 어택 재사용 대기 시간 에디트 활성화
				if self.check_autoHunt == True: # 자동 사냥 매크로일 경우
					self.lineEdit_attack_delay.setEnabled(True) # 몬스터 클릭 후 사냥 완료할 때까지의 대기 시간 에디트 활성화
					self.lineEdit_front_template_image_file.setEnabled(True) # 몬스터 정면 이미지 템플릿 파일 에디트 활성화
					self.lineEdit_back_template_image_file.setEnabled(True) # 몬스터 후면 이미지 템플릿 파일 에디트 활성화
					self.lineEdit_leftside_template_image_file.setEnabled(True) # 몬스터 좌측면 이미지 템플릿 파일 에디트 활성화
					self.lineEdit_rightside_template_image_file.setEnabled(True) # 몬스터 우측면 이미지 템플릿 파일 에디트 활성화
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def start_func(self): # 매크로 동작 함수
		try:
			global exit_var
			self.characterName = unicode(self.lineEdit_characterName.text().toUtf8(),'utf8', 'ignore').encode('cp949') # 설정한 캐릭터명 저장
			if self.characterName == '': # 캐릭터명을 입력하지 않았을 경우
				self.statusBar.showMessage('Need to input character name !!') # 상태 표시줄 내용 갱신
				return
			if exit_var == True: # 스레드 종료 변수 값이 설정된 경우(중지 후 다시 시작했을 경우)
				exit_var = False # 스레드 종료 변수 값 초기화
			self.start = True # 시작 버튼 눌림 여부 값 변경
			self.statusBar.showMessage('Start') # 상태 표시줄 내용 갱신
			self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
			self.btnPause.setEnabled(True) # 매크로 중지 버튼 활성화
			self.lineEdit_pause_restart.setDisabled(True) # 중지 및 재시작 키 에디트 비활성화
			self.lineEdit_characterName.setDisabled(True) # 캐릭터명 에디트 비활성화
			self.pause_restart = str(self.lineEdit_pause_restart.text()).lower() # 설정한 중지 키 저장
			for vk in myMacro.virtual_key:
				if self.pause_restart == vk[0]: # 설정한 중지 키일 경우
					key_state_pause = win32api.GetKeyState(vk[1]) # 설정한 중지 키 초기 입력 상태
					th_pause = threading.Thread(target=self.pause_thread, args=(self.pause_restart, vk, key_state_pause,)) # 설정한 단축키로 매크로 중지하는 스레드 설정
					th_pause.start() # 스레드 생성
					break
			if self.check_infiniteClick == True: # 반복 마우스 좌클릭 매크로일 경우
				self.checkbox_infiniteClick.setDisabled(True) # 반복 마우스 좌클릭 매크로 체크 박스 비활성화
				th_infiniteClick_macro = threading.Thread(target=self.infiniteClick_macro_thread, args=()) # 반복 마우스 좌클릭 매크로 스레드 설정
				th_infiniteClick_macro.start() # 스레드 생성
				return
			elif self.check_infiniteInput == True: # 반복 설정한 단축키 입력 매크로일 경우
				self.checkbox_infiniteInput.setDisabled(True) # 반복 설정한 단축키 입력 매크로 체크 박스 비활성화
				self.lineEdit_infiniteInput_key.setDisabled(True) # 반복해서 입력할 단축키 에디트 비활성화
				th_infiniteInput_macro = threading.Thread(target=self.infiniteInput_macro_thread, args=()) # 반복 설정한 단축키 입력 매크로 스레드 설정
				th_infiniteInput_macro.start() # 스레드 생성
				return
			if self.check_fp == True: # 밥통작 매크로일 경우
				self.doubleAttack_delay_fp = int(self.lineEdit_doubleAttack_delay_fp.text()) # 설정한 더블 어택(밥통작) 재사용 대기 시간 저장
				self.doubleAttack_key_fp = str(self.lineEdit_doubleAttack_key_fp.text()).lower() # 설정한 더블 어택(밥통작) 단축키 저장
				self.holyMenu_key = str(self.lineEdit_holyMenu_key.text()).lower() # 설정한 홀리 메뉴 단축키 저장
				self.checkbox_fp.setDisabled(True) # 밥통작 매크로 체크 박스 비활성화
				self.lineEdit_doubleAttack_delay_fp.setDisabled(True) # 더블 어택(밥통작) 재사용 대기 시간 에디트 비활성화
				self.lineEdit_doubleAttack_key_fp.setDisabled(True) # 더블 어택(밥통작) 단축키 에디트 비활성화
				self.lineEdit_holyMenu_key.setDisabled(True) # 홀리 메뉴 단축키 에디트 비활성화
				th_fp_macro = threading.Thread(target=self.fp_macro_thread, args=()) # 밥통작 매크로 스레드 설정
				th_fp_macro.start() # 스레드 생성
				return
			self.btnHealth.setDisabled(True) # 체력바 좌표와 픽셀값 설정 버튼 비활성화
			self.checkbox_autoPotion.setDisabled(True) # 자동 포션 매크로 체크 박스 비활성화
			self.checkbox_doubleAttack.setDisabled(True) # 더블 어택 매크로 체크 박스 비활성화
			self.checkbox_autoHunt.setDisabled(True) # 자동 사냥 매크로 체크 박스 비활성화
			if self.check_autoPotion == True: # 자동 포션 매크로일 경우
				self.health_x = int(self.lineEdit_health_x.text()) # 설정한 체력 포션을 사용하는 체력바의 x좌표 저장
				self.health_y = int(self.lineEdit_health_y.text()) # 설정한 체력 포션을 사용하는 체력바의 y좌표 저장
				self.health_color = int(self.lineEdit_health_color.text()) # 설정한 체력이 부족할때의 체력바 픽셀값 저장
				self.health_potion_key = str(self.lineEdit_health_potion_key.text()).lower() # 설정한 체력 포션 단축키 저장
				self.lineEdit_health_x.setDisabled(True) # 체력 포션을 사용하는 체력바의 x좌표 에디트 비활성화
				self.lineEdit_health_y.setDisabled(True) # 체력 포션을 사용하는 체력바의 y좌표 에디트 비활성화
				self.lineEdit_health_color.setDisabled(True) # 체력이 부족할때의 체력바 픽셀값 에디트 비활성화
				self.lineEdit_health_potion_key.setDisabled(True) # 체력 포션 단축키 에디트 비활성화
				th_autoPotion_macro = threading.Thread(target=self.autoPotion_macro_thread, args=()) # 자동 포션 매크로 스레드 설정
				th_autoPotion_macro.start() # 스레드 생성
			if self.check_doubleAttack == True: # 더블 어택 매크로일 경우
				self.doubleAttack_key = str(self.lineEdit_doubleAttack_key.text()).lower() # 설정한 더블 어택 단축키 저장
				self.radiobox_doubleAttack_autoRepeat.setDisabled(True) # 더블 어택 자동 반복 매크로 라디오 박스 비활성화
				self.radiobox_doubleAttack_withAutoHunt.setDisabled(True) # 더블 어택이 자동 사냥 매크로와 같이 동작하는 매크로 라디오 박스 비활성화
				self.lineEdit_doubleAttack_key.setDisabled(True) # 더블 어택 단축키 에디트 비활성화
				self.lineEdit_doubleAttack_delay.setDisabled(True) # 더블 어택 재사용 대기 시간 에디트 비활성화
				if self.radiobox_doubleAttack_autoRepeat.isChecked() == True: # 더블 어택 자동 반복 매크로일 경우
					self.doubleAttack_delay = int(self.lineEdit_doubleAttack_delay.text()) # 설정한 더블 어택 재사용 대기 시간 저장
					th_doubleAttack_macro = threading.Thread(target=self.doubleAttack_macro_thread, args=()) # 더블 어택 매크로 스레드 설정
					th_doubleAttack_macro.start() # 스레드 생성
			if self.check_autoHunt == True: # 자동 사냥 매크로일 경우
				self.attack_delay = int(self.lineEdit_attack_delay.text()) # 설정한 몬스터 클릭 후 사냥 완료할 때까지의 대기 시간 저장 
				self.front_template_image_file = str(self.lineEdit_front_template_image_file.text()).lower() # 설정한 몬스터 정면 이미지 템플릿 파일 저장
				self.back_template_image_file = str(self.lineEdit_back_template_image_file.text()).lower() # 설정한 몬스터 후면 이미지 템플릿 파일 저장
				self.leftside_template_image_file = str(self.lineEdit_leftside_template_image_file.text()).lower() # 설정한 몬스터 좌측면 이미지 템플릿 파일 저장
				self.rightside_template_image_file = str(self.lineEdit_rightside_template_image_file.text()).lower() # 설정한 몬스터 우측면 이미지 템플릿 파일 저장
				self.lineEdit_attack_delay.setDisabled(True) # 몬스터 클릭 후 사냥 완료할 때까지의 대기 시간 에디트 비활성화
				self.lineEdit_front_template_image_file.setDisabled(True) # 몬스터 정면 이미지 템플릿 파일 에디트 비활성화
				self.lineEdit_back_template_image_file.setDisabled(True) # 몬스터 후면 이미지 템플릿 파일 에디트 비활성화
				self.lineEdit_leftside_template_image_file.setDisabled(True) # 몬스터 좌측면 이미지 템플릿 파일 에디트 비활성화
				self.lineEdit_rightside_template_image_file.setDisabled(True) # 몬스터 우측면 이미지 템플릿 파일 에디트 비활성화
				th_autoHunt_macro = threading.Thread(target=self.autoHunt_macro_thread, args=()) # 자동 사냥 매크로 스레드 설정
				th_autoHunt_macro.start() # 스레드 생성
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신
			
	def pause_thread(self, key, vk, key_state): # 설정한 단축키로 매크로 중지하는 스레드
		global exit_var
		while True:
			try:
				sem.acquire() # 임계영역 생성
				if exit_var == True or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
					sem.release() # 임계영역 해제
					return # 스레드 종료
				elif self.start == True: # 매크로가 동작중인 경우
					cur_key_state = win32api.GetKeyState(vk[1]) # 현재 키보드 입력 상태
					if cur_key_state != key_state: # 키보드 입력 상태가 변경됐을 경우
						key_state = cur_key_state # 키보드 입력 상태 갱신
						if key_state == -127 or key_state == -128: # 두번 실행 방지
							if key == self.pause_restart: # 입력한 키가 설정한 중지 키일 경우
								self.pause_func() # 매크로 중지 함수 실행
								sem.release() # 임계영역 해제
								return # 스레드 종료
				sem.release() # 임계영역 해제
			except Exception, e:
				sem.release() # 임계영역 해제
				pass

	def fp_macro_thread(self): # 밥통작 매크로 스레드
		try:
			global exit_var
			holyMenu_key = self.holyMenu_key.split(' ')
			count = 0
			while True:
				try:
					sem.acquire() # 임계영역 생성
					if exit_var == True or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
						sem.release() # 임계영역 해제
						return # 스레드 종료
					elif self.start == True: # 매크로가 동작중인 경우
						state, prog_pos_x, prog_pos_y, prog_size_x, prog_size_y = myMacro.get_program_pos_size_include_maximum(self.characterName) # 일랜시아 프로그램의 위치 및 크기 저장
						if state: # 일랜시아 프로그램의 위치 및 크기를 제대로 찾았을 경우
							myMacro.move_mouse(prog_pos_x + 3, prog_pos_y + 3) # 일랜시아 프로그램으로 마우스 이동
							myMacro.click_mouse_left(0,0) # 마우스 좌클릭
							if count == 15:
								myMacro.keyboardInput_combination(holyMenu_key[0], holyMenu_key[1]) # 홀리 메뉴 사용
								time.sleep(2)
								myMacro.keyboardInput('enter')
								count = 0
							myMacro.keyboardInput(self.doubleAttack_key_fp) # 더블 어택 사용
							count += 1
							time.sleep(self.doubleAttack_delay_fp) # 더블 어택 재사용 대기 시간 만큼 대기
					sem.release() # 임계영역 해제
				except Exception, e:
					sem.release() # 임계영역 해제
					pass
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def autoPotion_macro_thread(self): # 자동 포션 매크로 스레드
		global exit_var
		while True:
			try:
				sem.acquire() # 임계영역 생성
				if exit_var == True or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
					sem.release() # 임계영역 해제
					return # 스레드 종료
				elif self.start == True: # 매크로가 동작중인 경우
					state, prog_pos_x, prog_pos_y, prog_size_x, prog_size_y = myMacro.get_program_pos_size_include_maximum(self.characterName) # 일랜시아 프로그램의 위치 및 크기 저장
					if state: # 일랜시아 프로그램의 위치 및 크기를 제대로 찾았을 경우
						health_pos_pixel = QPixmap.grabWindow(QApplication.desktop().winId()).toImage().pixel(self.health_x, self.health_y) # 체력바 위치의 픽셀 값(16진수) 저장
						health_pixel_color = (qBlue(health_pos_pixel) * 65536 + qGreen(health_pos_pixel) * 256 + qRed(health_pos_pixel)) # 픽셀 값 10진수로 변경
						if self.health_color == health_pixel_color: # 체력이 체력바의 설정한 구간 이하로 떨어졌을 경우
							myMacro.keyboardInput(self.health_potion_key) # 체력 포션 단축키 입력
				sem.release() # 임계영역 해제
			except Exception, e:
				sem.release() # 임계영역 해제
				pass

	def doubleAttack_macro_thread(self): # 더블 어택 매크로 스레드
		global exit_var
		while True:
			try:
				sem.acquire() # 임계영역 생성
				if exit_var == True or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
					sem.release() # 임계영역 해제
					return # 스레드 종료
				elif self.start == True: # 매크로가 동작중인 경우
					state, prog_pos_x, prog_pos_y, prog_size_x, prog_size_y = myMacro.get_program_pos_size_include_maximum(self.characterName) # 일랜시아 프로그램의 위치 및 크기 저장
					if state: # 일랜시아 프로그램의 위치 및 크기를 제대로 찾았을 경우
						myMacro.keyboardInput(self.doubleAttack_key) # 더블 어택 단축키 입력
						time.sleep(self.doubleAttack_delay) # 더블 어택 재사용 대기 시간 만큼 대기
				sem.release() # 임계영역 해제
			except Exception, e:
				sem.release() # 임계영역 해제
				pass

	def autoHunt_macro_thread(self): # 자동 사냥 매크로 스레드
		global exit_var
		while True:
			try:
				sem.acquire() # 임계영역 생성
				if exit_var == True or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
					sem.release() # 임계영역 해제
					return # 스레드 종료
				elif self.start == True: # 매크로가 동작중인 경우
					state, prog_pos_x, prog_pos_y, prog_size_x, prog_size_y = myMacro.get_program_pos_size_include_maximum(self.characterName) # 일랜시아 프로그램의 위치 및 크기 저장
					if state: # 일랜시아 프로그램의 위치 및 크기를 제대로 찾았을 경우
						myMacro.getScreenshot(self.full_screenshot_file, prog_pos_x, prog_pos_y, prog_pos_x + prog_size_x, prog_pos_y + prog_size_y) # 일랜시아 화면 스크린샷 후 파일로 저장
						for i in range(0, 4):
							template_image_file = '' # 몬스터 이미지 템플릿 파일
							# 몬스터의 4방향 이미지 파일의 템플릿 매칭 우선순위 설정
							if i == 0:
								template_image_file = self.leftside_template_image_file # 몬스터 좌측면 이미지 템플릿 파일 저장
							elif i == 1:
								template_image_file = self.rightside_template_image_file # 몬스터 우측면 이미지 템플릿 파일 저장
							elif i == 2:
								template_image_file = self.front_template_image_file # 몬스터 정면 이미지 템플릿 파일 저장
							elif i == 3:
								template_image_file = self.back_template_image_file # 몬스터 후면 이미지 템플릿 파일 저장
							confirm, detected_pos = myMacro.templateMatching(self.full_screenshot_file, template_image_file) # 템플릿 매칭을 통해 몬스터 이미지 검출
							if confirm: # 몬스터 이미지를 검출했을 경우
								i = Image.open(template_image_file) # 몬스터 이미지 템플릿 파일 오픈
								width, height = i.size # 몬스터 이미지 템플릿 파일의 가로, 세로 크기 저장
								if self.check_doubleAttack == True and self.radiobox_doubleAttack_withAutoHunt.isChecked() == True: # 더블 어택 매크로와 더블 어택이 자동 사냥 매크로와 같이 동작하는 매크로가 모두 체크되어 있을 경우
									myMacro.keyboardInput(self.doubleAttack_key) # 더블 어택 단축키 입력
								myMacro.move_mouse(prog_pos_x + detected_pos[0] + width/2, prog_pos_y + detected_pos[1] + height/2) # 몬스터의 중앙으로 마우스 이동
								myMacro.click_mouse_left(0,0) # 몬스터 좌클릭
								break
						time.sleep(self.attack_delay) # 몬스터 클릭 후 사냥 완료할 때까지 대기
				sem.release() # 임계영역 해제
			except Exception, e:
				sem.release() # 임계영역 해제
				pass

	def infiniteClick_macro_thread(self): # 반복 마우스 좌클릭 매크로 스레드
		global exit_var
		time.sleep(3) # 대기 시간
		while True:
			try:
				sem.acquire() # 임계영역 생성
				if exit_var == True or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
					sem.release() # 임계영역 해제
					return # 스레드 종료
				elif self.start == True: # 매크로가 동작중인 경우
					myMacro.click_mouse_left(0,0) # 마우스 좌클릭
					time.sleep(0.01)
				sem.release() # 임계영역 해제
			except Exception, e:
				sem.release() # 임계영역 해제
				pass

	def infiniteInput_macro_thread(self): # 반복 설정한 단축키 입력 매크로 스레드
		global exit_var
		time.sleep(3) # 대기 시간
		while True:
			try:
				sem.acquire() # 임계영역 생성
				if exit_var == True or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
					sem.release() # 임계영역 해제
					return # 스레드 종료
				elif self.start == True: # 매크로가 동작중인 경우
					myMacro.keyboardInput(self.infinite_key) # 설정한 반복해서 입력할 단축키 입력
					time.sleep(0.01)
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