#-*- coding: utf-8 -*-
import os
import sys
import time
import win32api
import win32con
import threading
import keyboard
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
		self.actives = [] # 설정 파일의 내용이 저장될 리스트
		self.start = False # 시작 버튼 눌림 여부
		self.check_potion = False # 포션 매크로 체크 여부
		self.check_onlyPotion = False # Only 포션 매크로 체크 여부
		self.pause_restart = 'F12' # 중지 및 재시작 키
		self.health_x = 740 # 체력 포션을 사용하는 체력바의 x좌표
		self.health_y = 726 # 체력 포션을 사용하는 체력바의 y좌표
		self.mana_x = 645 # 마나 포션을 사용하는 마나바의 x좌표
		self.mana_y = 742 # 마나 포션을 사용하는 마나바의 y좌표
		self.health_color = 8222586 # 체력이 부족할때의 체력바 픽셀값
		self.mana_color = 8222586 # 마나가 부족할때의 마나바 픽셀값
		self.health_potion_key = 'A' # 체력 포션 단축키
		self.mana_potion_key = 'S' # 마나 포션 단축키
		self.size_x = 670 # 프로그램의 가로 크기
		self.size_y = 330 # 프로그램의 세로 크기
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
		title = 'Maplestory Macro Program' # 타이틀
		self.setWindowTitle(title) # 윈도우 타이클 설정
		self.setGeometry(self.pos_x, self.pos_y, self.size_x, self.size_y) # 윈도우 위치, 크기 설정
		ico_binary = icoBinary.title_ico_binary_maplestory # 타이틀 아이콘 바이너리
		fp = open(os.getcwd() + '\\tmp_title.ico', 'wb') # 임시 아이콘 파일 생성
		fp.write(ico_binary)
		fp.close()
		self.setWindowIcon(QIcon(os.getcwd() + '\\tmp_title.ico')) # 타이틀 아이콘 설정
		self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowMinMaxButtonsHint) # 닫기 버튼 비활성화
		self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint) # 최대화 버튼 비활성화
		self.setFixedSize(self.size_x, self.size_y) # 화면 크기 변경 금지 설정

	def setupButton(self): # 버튼 설정 함수
		self.btnFile = QPushButton('File Open', self) # 설정 파일 오픈 버튼 설정
		self.btnFile.resize(self.btnFile.sizeHint() * 1.25)
		self.btnFile.move(10, self.size_y - 60)
		self.btnFile.clicked.connect(self.setup_file) # 설정 파일에서 설정 정보 가져오는 함수 적용
		self.btnStart = QPushButton('Start', self) # 매크로 동작 버튼 설정
		self.btnStart.resize(self.btnStart.sizeHint() * 1.25)
		self.btnStart.move(120, self.size_y - 60)
		self.btnStart.clicked.connect(self.start_func) # 매크로 동작 함수 적용
		self.btnStart.setDisabled(True) # 매크로 중지 버튼 비활성화
		self.btnPause = QPushButton('Pause', self) # 매크로 중지 버튼 설정
		self.btnPause.resize(self.btnPause.sizeHint() * 1.25)
		self.btnPause.move(240, self.size_y - 60)
		self.btnPause.clicked.connect(self.pause_func) # 매크로 중지 함수 적용
		self.btnPause.setDisabled(True) # 매크로 중지 버튼 비활성화
		self.btnExit = QPushButton('Exit', self) # 매크로 종료 버튼 설정
		self.btnExit.resize(self.btnExit.sizeHint() * 1.25)
		self.btnExit.move(360, self.size_y - 60)
		self.btnExit.clicked.connect(self.exit_func) # 매크로 종료 함수 적용
		self.btnHealth = QPushButton('Health', self) # 체력바 좌표와 픽셀값 설정 버튼 설정
		self.btnHealth.resize(self.btnHealth.sizeHint() / 1.3)
		self.btnHealth.move(460, 100)
		self.btnHealth.clicked.connect(self.setHealth) # 체력바 좌표와 픽셀값 설정 함수 적용
		self.btnHealth.setDisabled(True) # 체력바 좌표와 픽셀값 설정 버튼 비활성화
		self.btnMana = QPushButton('Mana', self) # 마나바 좌표와 픽셀값 설정 버튼 설정
		self.btnMana.resize(self.btnMana.sizeHint() / 1.3)
		self.btnMana.move(520, 100)
		self.btnMana.clicked.connect(self.setMana) # 마나바 좌표와 픽셀값 설정 함수 적용
		self.btnMana.setDisabled(True) # 마나바 좌표와 픽셀값 설정 버튼 비활성화

	def setupLabel(self): # 레이블 설정 함수
		title = 'Maplestory Macro  ver 1.0 by.KHW' # 제목 레이블
		self.label_title = QLabel(title, self) # 제목 레이블 설정
		self.label_title.move(self.size_x/2.8, 10)
		self.label_title.resize(200, 15)
		content = unicode('[동작 종류]\n1. 키보드 : 단순 입력, 지속 입력, 조합 입력\nex) f1 입력 - f1, ctrl 3.5초간 입력 - ctrl^3.5\nex) 위 방향 키와 alt 같이 입력 - up+alt\n\n2. 마우스 : 좌클릭, 우클릭, 이동\nex) 좌클릭 - leftclick, 우클릭 - rightclick\nex) x,y 픽셀만큼 마우스 이동 - move^x,y\n\n[파일 구성 방법]\n1. 각 동작들은 한 줄에 입력\n2. 각 줄의 맨 앞은 핫키로 지정. 핫키 구분자는 : 문자(콜론)\n3. 동작 종류 입력 후 딜레이 시간(초)을 입력하되 공백으로 구분\n4. 딜레이 시간을 입력하지 않으면 안 되므로 불필요한 경우 0으로 입력\nex) q 입력하고 0.5초 후에 w 입력하는 동작을 핫키 space로 설정 - space: q 0.5 w\nex) 1 입력 후 딜레이 없이 2 입력하는 동작을 핫키 shift로 설정 - shift: 1 0 2\n', 'utf-8') # 내용 레이블
		self.label_content = QLabel(content, self) # 내용 레이블 설정
		self.label_content.move(10, 35)
		self.label_content.resize(455, 240)

	def setupEdit(self): # 에디트 설정 함수
		self.lineEditLabel_pause_restart = QLabel('Pause & Restart : ', self) # 중지 및 재시작 키 레이블 설정
		self.lineEditLabel_pause_restart.move(self.size_x - 170, 35)
		self.lineEditLabel_pause_restart.resize(100, 15)
		self.lineEdit_pause_restart = QLineEdit(self.pause_restart, self) # 중지 및 재시작 키 에디트 설정
		self.lineEdit_pause_restart.move(self.size_x - 65, 32) # 에디트 위치
		self.lineEdit_pause_restart.resize(50, 20) # 에디트 크기
		self.lineEditLabel_health_x = QLabel('Health X Coordinate : ', self) # 체력 포션을 사용하는 체력바의 x좌표 레이블 설정
		self.lineEditLabel_health_x.move(self.size_x - 190, 130)
		self.lineEditLabel_health_x.resize(120, 15)
		self.lineEdit_health_x = QLineEdit(str(self.health_x), self) # 체력 포션을 사용하는 체력바의 x좌표 에디트 설정
		self.lineEdit_health_x.move(self.size_x - 60, 127)
		self.lineEdit_health_x.resize(50, 20)
		self.lineEdit_health_x.setDisabled(True) # 체력 포션을 사용하는 체력바의 x좌표 에디트 비활성화
		self.lineEditLabel_health_y = QLabel('Health Y Coordinate : ', self) # 체력 포션을 사용하는 체력바의 y좌표 레이블 설정
		self.lineEditLabel_health_y.move(self.size_x - 190, 155)
		self.lineEditLabel_health_y.resize(120, 15)
		self.lineEdit_health_y = QLineEdit(str(self.health_y), self) # 체력 포션을 사용하는 체력바의 y좌표 에디트 설정
		self.lineEdit_health_y.move(self.size_x - 60, 152)
		self.lineEdit_health_y.resize(50, 20)
		self.lineEdit_health_y.setDisabled(True) # 체력 포션을 사용하는 체력바의 y좌표 에디트 비활성화
		self.lineEditLabel_mana_x = QLabel('Mana X Coordinate  : ', self) # 마나 포션을 사용하는 마나바의 x좌표 레이블 설정
		self.lineEditLabel_mana_x.move(self.size_x - 190, 180)
		self.lineEditLabel_mana_x.resize(120, 15)
		self.lineEdit_mana_x = QLineEdit(str(self.mana_x), self) # 마나 포션을 사용하는 마나바의 x좌표 에디트 설정
		self.lineEdit_mana_x.move(self.size_x - 60, 177)
		self.lineEdit_mana_x.resize(50, 20)
		self.lineEdit_mana_x.setDisabled(True) # 마나 포션을 사용하는 마나바의 x좌표 에디트 비활성화
		self.lineEditLabel_mana_y = QLabel('Mana Y Coordinate  : ', self) # 마나 포션을 사용하는 마나바의 y좌표 레이블 설정
		self.lineEditLabel_mana_y.move(self.size_x - 190, 205)
		self.lineEditLabel_mana_y.resize(120, 15)
		self.lineEdit_mana_y = QLineEdit(str(self.mana_y), self) # 마나 포션을 사용하는 마나바의 y좌표 에디트 설정
		self.lineEdit_mana_y.move(self.size_x - 60, 202)
		self.lineEdit_mana_y.resize(50, 20)
		self.lineEdit_mana_y.setDisabled(True) # 마나 포션을 사용하는 마나바의 y좌표 에디트 비활성화
		self.lineEditLabel_health_color = QLabel('Health Pixel Color    : ', self) # 체력이 부족할때의 체력바 픽셀값 레이블 설정
		self.lineEditLabel_health_color.move(self.size_x - 190, 230)
		self.lineEditLabel_health_color.resize(120, 15)
		self.lineEdit_health_color = QLineEdit(str(self.health_color), self) # 체력이 부족할때의 체력바 픽셀값 에디트 설정
		self.lineEdit_health_color.move(self.size_x - 60, 227)
		self.lineEdit_health_color.resize(50, 20)
		self.lineEdit_health_color.setDisabled(True) # 체력이 부족할때의 체력바 픽셀값 에디트 비활성화
		self.lineEditLabel_mana_color = QLabel('Mana Pixel Color	 : ', self) # 마나가 부족할때의 마나바 픽셀값 레이블 설정
		self.lineEditLabel_mana_color.move(self.size_x - 190, 255)
		self.lineEditLabel_mana_color.resize(120, 15)
		self.lineEdit_mana_color = QLineEdit(str(self.mana_color), self) # 마나가 부족할때의 마나바 픽셀값 에디트 설정
		self.lineEdit_mana_color.move(self.size_x - 60, 252)
		self.lineEdit_mana_color.resize(50, 20)
		self.lineEdit_mana_color.setDisabled(True) # 마나가 부족할때의 마나바 픽셀값 에디트 비활성화
		self.lineEditLabel_health_potion_key = QLabel('Health Potion Key    : ', self) # 체력 포션 단축키 레이블 설정
		self.lineEditLabel_health_potion_key.move(self.size_x - 190, 280)
		self.lineEditLabel_health_potion_key.resize(120, 15)
		self.lineEdit_health_potion_key = QLineEdit(str(self.health_potion_key), self) # 체력 포션 단축키 에디트 설정
		self.lineEdit_health_potion_key.move(self.size_x - 60, 277)
		self.lineEdit_health_potion_key.resize(50, 20)
		self.lineEdit_health_potion_key.setDisabled(True) # 체력 포션 단축키 에디트 비활성화
		self.lineEditLabel_mana_potion_key = QLabel('Mana Potion Key	 : ', self) # 마나 포션 단축키 레이블 설정
		self.lineEditLabel_mana_potion_key.move(self.size_x - 190, 305)
		self.lineEditLabel_mana_potion_key.resize(120, 15)
		self.lineEdit_mana_potion_key = QLineEdit(str(self.mana_potion_key), self) # 마나 포션 단축키 에디트 설정
		self.lineEdit_mana_potion_key.move(self.size_x - 60, 302)
		self.lineEdit_mana_potion_key.resize(50, 20)
		self.lineEdit_mana_potion_key.setDisabled(True) # 마나 포션 단축키 에디트 비활성화

	def setupRadioBox(self): # 라디오 박스 설정 함수
		self.groupBox = QGroupBox(unicode('Choose', 'utf-8'), self) # 라디오 박스 그룹
		self.groupBox.move(self.size_x - 90, 60)
		self.groupBox.resize(80, 60)
		self.radiobox_hotkey = QRadioButton('Hotkey', self) # 핫키 매크로 라디오 박스 설정
		self.radiobox_hotkey.move(self.size_x - 80, 70)
		self.radiobox_hotkey.setChecked(True) # 디폴트 선택
		self.radiobox_hotkey.clicked.connect(self.hotkey) # 핫키 매크로 함수 적용
		self.radiobox_loop = QRadioButton('Loop', self) # 반복 매크로 라디오 박스 설정
		self.radiobox_loop.move(self.size_x - 80, 90)
		self.radiobox_loop.clicked.connect(self.loop) # 반복 매크로 함수 적용

	def setupCheckBox(self): # 체크 박스 설정 함수
		self.checkbox_potion = QCheckBox(unicode('Potion', 'utf-8'), self) # 포션 매크로 체크 박스 설정
		self.checkbox_potion.move(self.size_x - 190, 60)
		self.checkbox_potion.resize(60, 15)
		self.checkbox_potion.stateChanged.connect(self.potion) # 포션 매크로 설정 함수 적용
		self.checkbox_onlyPotion = QCheckBox(unicode('Only Potion', 'utf-8'), self) # Only 포션 매크로 체크 박스 설정
		self.checkbox_onlyPotion.move(self.size_x - 190, 80)
		self.checkbox_onlyPotion.resize(90, 15)
		self.checkbox_onlyPotion.stateChanged.connect(self.onlyPotion) # Only 포션 매크로 설정 함수 적용

	def setupStatusBar(self): # 상태 표시줄 설정 함수
		self.statusBar = QStatusBar(self) # 상태 표시줄 설정
		self.setStatusBar(self.statusBar)
		self.statusBar.showMessage('Not Setted') # 처음 상태 표시줄 내용 설정

	def set_coordinate_pixel_thread(self, key, vk, key_state, health_mana): # 체력바 좌표와 픽셀값 설정 스레드
		while True:
			try:
				sem.acquire() # 임계영역 생성
				cur_key_state = win32api.GetKeyState(vk[1]) # 현재 키보드 입력 상태
				if cur_key_state != key_state: # 키보드 입력 상태가 변경됐을 경우
					key_state = cur_key_state # 키보드 입력 상태 갱신
					if key_state == -127 or key_state == -128: # 두 번 실행 방지
						if key == 'enter': # 입력한 키가 엔터 키일 경우
							self.btnFile.setEnabled(True) # 설정 파일 오픈 버튼 활성화
							self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
							self.btnHealth.setEnabled(True) # 체력바 좌표와 픽셀값 설정 버튼 활성화
							self.btnMana.setEnabled(True) # 마나바 좌표와 픽셀값 설정 버튼 비활성화
							self.lineEdit_pause_restart.setEnabled(True) # 중지 및 재시작 키 에디트 활성화
							if health_mana == 'health': # 체력바 좌표와 픽셀값 설정일 경우
								self.lineEdit_mana_x.setEnabled(True) # 마나 포션을 사용하는 마나바의 x좌표 에디트 활성화
								self.lineEdit_mana_y.setEnabled(True) # 마나 포션을 사용하는 마나바의 y좌표 에디트 활성화
								self.lineEdit_mana_color.setEnabled(True) # 마나가 부족할때의 마나바 픽셀값 에디트 활성화
								self.lineEdit_mana_potion_key.setEnabled(True) # 마나 포션 단축키 에디트 활성화
							elif health_mana == 'mana': # 마나바 좌표와 픽셀값 설정
								self.lineEdit_health_x.setEnabled(True) # 체력 포션을 사용하는 체력바의 x좌표 에디트 활성화
								self.lineEdit_health_y.setEnabled(True) # 체력 포션을 사용하는 체력바의 y좌표 에디트 활성화
								self.lineEdit_health_color.setEnabled(True) # 체력이 부족할때의 체력바 픽셀값 에디트 활성화
								self.lineEdit_health_potion_key.setEnabled(True) # 체력 포션 단축키 에디트 활성화
							if self.check_potion == True: # 포션 매크로가 체크되어 있었을 경우
								self.radiobox_hotkey.setEnabled(True) # 핫키 매크로 라디오 박스 활성화
								self.radiobox_loop.setEnabled(True) # 반복 매크로 라디오 박스 활성화
								self.checkbox_potion.setEnabled(True) # 포션 매크로 체크 박스 활성화
							elif self.check_onlyPotion == True: # Only 포션 매크로가 체크되어 있었을 경우
								self.checkbox_onlyPotion.setEnabled(True) # Only 포션 매크로 체크 박스 활성화
							sem.release() # 임계영역 해제
							return # 스레드 종료
				else: # 키보드 입력 상태가 변경되지 않았을 경우
					current_pos_x = myMacro.get_mouse_pos()[0] # 현재 마우스 x좌표 저장
					current_pos_y = myMacro.get_mouse_pos()[1] - 2 # 현재 마우스 y좌표 저장(메이플 마우스 포인터 때문에 화면의 픽셀이 제대로 잡히지 않음.(메이플 마우스 포인터의 픽셀이 잡힘) 따라서 현재 마우스 포인터 위치에서 2만큼 위쪽 픽셀의 값을 저장함으로써 화면의 픽셀값이 잡히도록 설정)
					currnet_pos_pixel = QPixmap.grabWindow(QApplication.desktop().winId()).toImage().pixel(current_pos_x, current_pos_y) # 현재 마우스 위치의 픽셀값(16진수) 저장
					current_pixel_color = (qBlue(currnet_pos_pixel) * 65536 + qGreen(currnet_pos_pixel) * 256 + qRed(currnet_pos_pixel)) # 현재 마우스 위치의 픽셀값 10진수로 변경
					if health_mana == 'health': # 체력바 좌표와 픽셀값 설정일 경우
						self.lineEdit_health_x.setText(str(current_pos_x)) # 체력 포션을 사용하는 체력바의 x좌표 에디트의 값을 현재 마우스 x좌표로 변경
						self.lineEdit_health_y.setText(str(current_pos_y)) # 체력 포션을 사용하는 체력바의 y좌표 에디트의 값을 현재 마우스 y좌표로 변경
						self.lineEdit_health_color.setText(str(current_pixel_color)) # 체력이 부족할때의 체력바 픽셀값 에디트의 값을 현재 마우스 위치의 픽셀값으로 변경
					elif health_mana == 'mana': # 마나바 좌표와 픽셀값 설정
						self.lineEdit_mana_x.setText(str(current_pos_x)) # 체력 포션을 사용하는 체력바의 x좌표 에디트의 값을 현재 마우스 x좌표로 변경
						self.lineEdit_mana_y.setText(str(current_pos_y)) # 체력 포션을 사용하는 체력바의 y좌표 에디트의 값을 현재 마우스 y좌표로 변경
						self.lineEdit_mana_color.setText(str(current_pixel_color)) # 체력이 부족할때의 체력바 픽셀값 에디트의 값을 현재 마우스 위치의 픽셀값으로 변경
				sem.release() # 임계영역 해제
			except Exception, e:
				sem.release() # 임계영역 해제
				pass

	def setHealth(self): # 체력바 좌표와 픽셀값 설정 함수
		try:
			if self.check_potion == True or self.check_onlyPotion == True: # 포션 매크로 또는 Only 포션 매크로가 체크되어 있을 경우
				self.btnFile.setDisabled(True) # 설정 파일 오픈 버튼 비활성화
				self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
				self.btnHealth.setDisabled(True) # 체력바 좌표와 픽셀값 설정 버튼 비활성화
				self.btnMana.setDisabled(True) # 마나바 좌표와 픽셀값 설정 버튼 비활성화
				self.lineEdit_pause_restart.setDisabled(True) # 중지 및 재시작 키 에디트 비활성화
				self.lineEdit_mana_x.setDisabled(True) # 마나 포션을 사용하는 마나바의 x좌표 에디트 비활성화
				self.lineEdit_mana_y.setDisabled(True) # 마나 포션을 사용하는 마나바의 y좌표 에디트 비활성화
				self.lineEdit_mana_color.setDisabled(True) # 마나가 부족할때의 마나바 픽셀값 에디트 비활성화
				self.lineEdit_mana_potion_key.setDisabled(True) # 마나 포션 단축키 에디트 비활성화
				self.radiobox_hotkey.setDisabled(True) # 핫키 매크로 라디오 박스 비활성화
				self.radiobox_loop.setDisabled(True) # 반복 매크로 라디오 박스 비활성화
				self.checkbox_potion.setDisabled(True) # 포션 매크로 체크 박스 비활성화
				self.checkbox_onlyPotion.setDisabled(True) # Only 포션 매크로 체크 박스 비활성화
				self.statusBar.showMessage('Input \'enter\' key to complete setting') # 상태 표시줄 내용 갱신
				for vk in myMacro.virtual_key:
					if 'enter' == vk[0]: # 엔터 키일 경우
						key_state_enter = win32api.GetKeyState(vk[1]) # 엔터 키 초기 입력 상태
						th_set_health_coordinate_pixel = threading.Thread(target=self.set_coordinate_pixel_thread, args=('enter', vk, key_state_enter, 'health',)) # 체력바 좌표와 픽셀값 설정 스레드 설정
						th_set_health_coordinate_pixel.start() # 스레드 생성
						break
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def setMana(self): # 마나바 좌표와 픽셀값 설정 함수
		try:
			if self.check_potion == True or self.check_onlyPotion == True: # 포션 매크로 또는 Only 포션 매크로가 체크되어 있을 경우
				self.btnFile.setDisabled(True) # 설정 파일 오픈 버튼 비활성화
				self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
				self.btnHealth.setDisabled(True) # 체력바 좌표와 픽셀값 설정 버튼 비활성화
				self.btnMana.setDisabled(True) # 마나바 좌표와 픽셀값 설정 버튼 비활성화
				self.lineEdit_pause_restart.setDisabled(True) # 중지 및 재시작 키 에디트 비활성화
				self.lineEdit_health_x.setDisabled(True) # 체력 포션을 사용하는 체력바의 x좌표 에디트 비활성화
				self.lineEdit_health_y.setDisabled(True) # 체력 포션을 사용하는 체력바의 y좌표 에디트 비활성화
				self.lineEdit_health_color.setDisabled(True) # 체력이 부족할때의 체력바 픽셀값 에디트 비활성화
				self.lineEdit_health_potion_key.setDisabled(True) # 체력 포션 단축키 에디트 비활성화
				self.radiobox_hotkey.setDisabled(True) # 핫키 매크로 라디오 박스 비활성화
				self.radiobox_loop.setDisabled(True) # 반복 매크로 라디오 박스 비활성화
				self.checkbox_potion.setDisabled(True) # 포션 매크로 체크 박스 비활성화
				self.checkbox_onlyPotion.setDisabled(True) # Only 포션 매크로 체크 박스 비활성화
				self.statusBar.showMessage('Input \'enter\' key to complete setting') # 상태 표시줄 내용 갱신
				for vk in myMacro.virtual_key:
					if 'enter' == vk[0]: # 엔터 키일 경우
						key_state_enter = win32api.GetKeyState(vk[1]) # 엔터 키 초기 입력 상태
						th_set_mana_coordinate_pixel = threading.Thread(target=self.set_coordinate_pixel_thread, args=('enter', vk, key_state_enter, 'mana',)) # 마나바 좌표와 픽셀값 설정 스레드 설정
						th_set_mana_coordinate_pixel.start() # 스레드 생성
						break
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def hotkey(self): # 핫키 매크로 함수
		try:
			self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
			self.actives = [] # 설정 파일의 내용이 저장될 리스트 초기화
			self.label_content.clear() # 레이블 클리어
			self.label_content.resize(455, 240)
			content = unicode('[동작 종류]\n1. 키보드 : 단순 입력, 지속 입력, 조합 입력\nex) f1 입력 - f1, ctrl 3.5초간 입력 - ctrl^3.5\nex) 위 방향 키와 alt 같이 입력 - up+alt\n\n2. 마우스 : 좌클릭, 우클릭, 이동\nex) 좌클릭 - leftclick, 우클릭 - rightclick\nex) x,y 픽셀만큼 마우스 이동 - move^x,y\n\n[파일 구성 방법]\n1. 각 동작들은 한 줄에 입력\n2. 각 줄의 맨 앞은 핫키로 지정. 핫키 구분자는 : 문자(콜론)\n3. 동작 종류 입력 후 딜레이 시간(초)을 입력하되 공백으로 구분\n4. 딜레이 시간을 입력하지 않으면 안 되므로 불필요한 경우 0으로 입력\nex) q 입력하고 0.5초 후에 w 입력하는 동작을 핫키 space로 설정 - space: q 0.5 w\nex) 1 입력 후 딜레이 없이 2 입력하는 동작을 핫키 shift로 설정 - shift: 1 0 2\n', 'utf-8') # 핫키 매크로 내용 레이블
			self.label_content.setText(content) # 핫키 매크로 내용으로 레이블 갱신
			self.statusBar.showMessage('Hotkey') # 상태 표시줄 내용 갱신
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def loop(self): # 반복 매크로 함수
		try:
			self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
			self.actives = [] # 설정 파일의 내용이 저장될 리스트 초기화
			self.label_content.clear() # 레이블 클리어
			self.label_content.resize(440, 210)
			content = unicode('[파일 구성 방법]\n1. 각 동작들은 한 줄에 입력\n2. 동작 문법 - 동작이름: 동작1 딜레이시간 동작2 딜레이시간 ... 동작n\nex) attack이라는 동작 이름으로 ctrl 입력 후 0.5초 후에 shift 입력하도록 설정\n-> attack: ctrl 0.5 shift\nex) moveAttack이라는 동작 이름으로 shift 입력 후 0.8초 후에 좌측으로 2초간\n이동하도록 설정 -> moveAttack: shift 0.8 left^2\n3. 동작 이름은 고유의 값이므로 겹치지 않게 설정\n4. 동작 조합은 마지막 줄에 한 번만 입력\n5. 동작 조합 문법\n - combination전체반복횟수: 동작1&동작1반복횟수 ... 동작n&동작n반복횟수\nex) attack 동작만 10번 반복하는 동작 조합을 2번 반복\n-> combination2: attack&10\nex) attack 동작을 5번 반복 후 potion 동작을 2번 반복하는 동작 조합을 무한 반복\n-> combination0: attack&5 potion&2', 'utf-8') # 반복 매크로 내용
			self.label_content.setText(content) # 반복 매크로 내용으로 레이블 갱신
			self.statusBar.showMessage('Loop') # 상태 표시줄 내용 갱신
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def potion(self): # 포션 매크로 함수
		try:
			if self.check_potion == True: # 포션 매크로가 체크되어 있을 경우
				self.check_potion = False # 포션 매크로 체크 해제 설정
				self.btnHealth.setDisabled(True) # 체력바 좌표와 픽셀값 설정 버튼 비활성화
				self.btnMana.setDisabled(True) # 마나바 좌표와 픽셀값 설정 버튼 비활성화
				self.checkbox_onlyPotion.setEnabled(True) # Only 포션 매크로 체크 박스 활성화
				self.lineEdit_health_x.setDisabled(True) # 체력 포션을 사용하는 체력바의 x좌표 에디트 비활성화
				self.lineEdit_health_y.setDisabled(True) # 체력 포션을 사용하는 체력바의 y좌표 에디트 비활성화
				self.lineEdit_mana_x.setDisabled(True) # 마나 포션을 사용하는 마나바의 x좌표 에디트 비활성화
				self.lineEdit_mana_y.setDisabled(True) # 마나 포션을 사용하는 마나바의 y좌표 에디트 비활성화
				self.lineEdit_health_color.setDisabled(True) # 체력이 부족할때의 체력바 픽셀값 에디트 비활성화
				self.lineEdit_mana_color.setDisabled(True) # 마나가 부족할때의 마나바 픽셀값 에디트 비활성화
				self.lineEdit_health_potion_key.setDisabled(True) # 체력 포션 단축키 에디트 비활성화
				self.lineEdit_mana_potion_key.setDisabled(True) # 마나 포션 단축키 에디트 비활성화
				self.statusBar.showMessage('Potion Unchecked') # 상태 표시줄 내용 갱신
			elif self.check_potion == False and self.check_onlyPotion == False: # 포션 매크로와 Only 포션 매크로 모두 체크 안 돼 있을 경우
				self.check_potion = True # 포션 매크로 체크 설정
				self.btnHealth.setEnabled(True) # 체력바 좌표와 픽셀값 설정 버튼 활성화
				self.btnMana.setEnabled(True) # 마나바 좌표와 픽셀값 설정 버튼 활성화
				self.checkbox_onlyPotion.setDisabled(True) # Only 포션 매크로 체크 박스 비활성화
				self.lineEdit_health_x.setEnabled(True) # 체력 포션을 사용하는 체력바의 x좌표 에디트 활성화
				self.lineEdit_health_y.setEnabled(True) # 체력 포션을 사용하는 체력바의 y좌표 에디트 활성화
				self.lineEdit_mana_x.setEnabled(True) # 마나 포션을 사용하는 마나바의 x좌표 에디트 활성화
				self.lineEdit_mana_y.setEnabled(True) # 마나 포션을 사용하는 마나바의 y좌표 에디트 활성화
				self.lineEdit_health_color.setEnabled(True) # 체력이 부족할때의 체력바 픽셀값 에디트 활성화
				self.lineEdit_mana_color.setEnabled(True) # 마나가 부족할때의 마나바 픽셀값 에디트 활성화
				self.lineEdit_health_potion_key.setEnabled(True) # 체력 포션 단축키 에디트 활성화
				self.lineEdit_mana_potion_key.setEnabled(True) # 마나 포션 단축키 에디트 활성화
				self.statusBar.showMessage('Potion Checked') # 상태 표시줄 내용 갱신
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def onlyPotion(self): # Only 포션 매크로 함수
		try:
			if self.check_onlyPotion == True: # Only 포션 매크로가 체크되어 있을 경우
				self.check_onlyPotion = False # Only 포션 매크로 체크 해제 설정
				self.btnFile.setEnabled(True) # 설정 파일 오픈 버튼 활성화
				self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
				self.btnHealth.setDisabled(True) # 체력바 좌표와 픽셀값 설정 버튼 비활성화
				self.btnMana.setDisabled(True) # 마나바 좌표와 픽셀값 설정 버튼 비활성화
				self.checkbox_potion.setEnabled(True) # 포션 매크로 체크 박스 활성화
				self.radiobox_loop.setEnabled(True) # 반복 매크로 라디오 박스 활성화
				self.radiobox_hotkey.setEnabled(True) # 핫키 매크로 라디오 박스 활성화
				self.lineEdit_health_x.setDisabled(True) # 체력 포션을 사용하는 체력바의 x좌표 에디트 비활성화
				self.lineEdit_health_y.setDisabled(True) # 체력 포션을 사용하는 체력바의 y좌표 에디트 비활성화
				self.lineEdit_mana_x.setDisabled(True) # 마나 포션을 사용하는 마나바의 x좌표 에디트 비활성화
				self.lineEdit_mana_y.setDisabled(True) # 마나 포션을 사용하는 마나바의 y좌표 에디트 비활성화
				self.lineEdit_health_color.setDisabled(True) # 체력이 부족할때의 체력바 픽셀값 에디트 비활성화
				self.lineEdit_mana_color.setDisabled(True) # 마나가 부족할때의 마나바 픽셀값 에디트 비활성화
				self.lineEdit_health_potion_key.setDisabled(True) # 체력 포션 단축키 에디트 비활성화
				self.lineEdit_mana_potion_key.setDisabled(True) # 마나 포션 단축키 에디트 비활성화
				self.statusBar.showMessage('Only Potion Unchecked') # 상태 표시줄 내용 갱신
			elif self.check_potion == False and self.check_onlyPotion == False: # 포션 매크로와 Only 포션 매크로 모두 체크 안 돼 있을 경우
				self.check_onlyPotion = True # Only 포션 매크로 체크 설정
				self.btnFile.setDisabled(True) # 설정 파일 오픈 버튼 비활성화
				self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
				self.btnHealth.setEnabled(True) # 체력바 좌표와 픽셀값 설정 버튼 활성화
				self.btnMana.setEnabled(True) # 마나바 좌표와 픽셀값 설정 버튼 활성화
				self.checkbox_potion.setDisabled(True) # 포션 매크로 체크 박스 비활성화
				self.radiobox_loop.setDisabled(True) # 반복 매크로 라디오 박스 비활성화
				self.radiobox_hotkey.setDisabled(True) # 핫키 매크로 라디오 박스 비활성화
				self.lineEdit_health_x.setEnabled(True) # 체력 포션을 사용하는 체력바의 x좌표 에디트 활성화
				self.lineEdit_health_y.setEnabled(True) # 체력 포션을 사용하는 체력바의 y좌표 에디트 활성화
				self.lineEdit_mana_x.setEnabled(True) # 마나 포션을 사용하는 마나바의 x좌표 에디트 활성화
				self.lineEdit_mana_y.setEnabled(True) # 마나 포션을 사용하는 마나바의 y좌표 에디트 활성화
				self.lineEdit_health_color.setEnabled(True) # 체력이 부족할때의 체력바 픽셀값 에디트 활성화
				self.lineEdit_mana_color.setEnabled(True) # 마나가 부족할때의 마나바 픽셀값 에디트 활성화
				self.lineEdit_health_potion_key.setEnabled(True) # 체력 포션 단축키 에디트 활성화
				self.lineEdit_mana_potion_key.setEnabled(True) # 마나 포션 단축키 에디트 활성화
				self.statusBar.showMessage('Only Potion Checked') # 상태 표시줄 내용 갱신
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
			line_hotkey_activeName = [] # 핫키(동작 이름)가 있는 첫 번째 위치의 내용이 저장될 리스트(핫키(동작 이름) 중복 예방)
			combination_activeName = [] # 동작 조합을 구성하는 동작 이름들이 저장될 리스트(동작 조합의 동작 이름 확인)
			duplication = False # 핫키(동작 이름)가 중복됐는지 확인하기 위한 변수
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
			if self.radiobox_loop.isChecked() == True: # 반복 매크로일 경우
				if 'combination' not in active[-1].split(' ')[0]: # 반복 매크로 설정 파일의 마지막 줄에 combination 문자열이 없을 경우(조합 설정을 안했을 경우)
					self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
					self.statusBar.showMessage('[-] Error : Need \'combination\' string in last line !!') # 상태 표시줄 내용 갱신
					return
			elif self.radiobox_hotkey.isChecked() == True: # 핫키 매크로일 경우
				if 'combination' in active[-1].split(' ')[0]: # 핫키 매크로 설정 파일의 마지막 줄에 combination 문자열이 있을 경우(반복 매크로 설정 파일을 핫키 매크로에서 잘못 사용했을 경우)
					self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
					self.statusBar.showMessage('[-] Error : This file use in Loop(Choose Loop) !!') # 상태 표시줄 내용 갱신
					return
			for l in range(0, len(active)): # 설정 파일 한 라인씩 반복
				if active[l] == '': # 해당 라인이 공백일 경우(설정된 내용이 없을 경우)
					continue
				line = active[l].lower().strip() # 해당 라인 저장
				tmp_line_hotkey_activeName = line.split(' ')[0] # 해당 라인을 공백으로 구분 후 핫키(동작 이름)가 있는 첫 번째 위치의 문자열 저장
				only_line_hotkey_activeName = tmp_line_hotkey_activeName.split(':')[0] # 핫키(동작 이름) 저장
				if ':' not in tmp_line_hotkey_activeName: # 핫키가 있는 첫 번째 위치에 핫키 구분자(콜론)가 없을 경우
					continue
				for hotkey_activeName in line_hotkey_activeName: # 중복된 핫키가 있는지 확인
					if tmp_line_hotkey_activeName == hotkey_activeName: # 중복된 핫키가 있을 경우
						duplication = True # 핫키(동작 이름)가 중복됐는지 확인하기 위한 변수 값 변경
						break
				if duplication == True: # 핫키(동작 이름)가 중복됐을 경우
					duplication = False # 핫키(동작 이름)가 중복됐는지 확인하기 위한 변수 값 초기화
					continue
				if self.radiobox_hotkey.isChecked() == True: # 핫키 매크로일 경우
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
								elif '+' in line.split(' ')[i]: # 조합 입력일 경우
									combination_confirm_count = 0 # 조합 키들을 올바르게 설정했는지 확인하기 위한 변수
									for vk in myMacro.virtual_key:
										if line.split(' ')[i].split('+')[0] == vk[0]: # 조합 입력의 첫 번째 키일 경우
											combination_confirm_count += 1 # 조합 키들을 올바르게 설정했는지 확인하기 위한 변수 값 증가
										elif line.split(' ')[i].split('+')[1] == vk[0]: # 조합 입력의 두 번째 키일 경우
											combination_confirm_count += 1 # 조합 키들을 올바르게 설정했는지 확인하기 위한 변수 값 증가
									if combination_confirm_count != 2: # 조합 키들 중 올바르지 않은 키가 있을 경우
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
				elif self.radiobox_loop.isChecked() == True: # 반복 매크로일 경우
					if l != len(active)-1: # 반복 매크로 설정 파일의 마지막 줄이 아닐 경우
						for i in range(1, len(line.split(' '))): # 첫 번째는 동작이 아니므로('동작이름:' 임) 인덱스 1부터 시작
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
								elif '+' in line.split(' ')[i]: # 조합 입력일 경우
									combination_confirm_count = 0 # 조합 키들을 올바르게 설정했는지 확인하기 위한 변수
									for vk in myMacro.virtual_key:
										if line.split(' ')[i].split('+')[0] == vk[0]: # 조합 입력의 첫 번째 키일 경우
											combination_confirm_count += 1 # 조합 키들을 올바르게 설정했는지 확인하기 위한 변수 값 증가
										elif line.split(' ')[i].split('+')[1] == vk[0]: # 조합 입력의 두 번째 키일 경우
											combination_confirm_count += 1 # 조합 키들을 올바르게 설정했는지 확인하기 위한 변수 값 증가
									if combination_confirm_count != 2: # 조합 키들 중 올바르지 않은 키가 있을 경우
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
						if key_error == True: # 키를 올바르게 설정하지 않았을 경우
							key_error = False # 키를 올바르게 설정했는지 확인하기 위한 변수 값 초기화
							continue
						if position_error == True: # 딜레이 시간(숫자)이 있어야 할 위치에 숫자가 아닌 문자가 있을 경우
							position_error = False # 설정 파일의 딜레이 시간과 동작의 위치가 올바른지 확인하기 위한 변수 값 초기화
							continue
						combination_activeName.append(only_line_hotkey_activeName) # 동작 이름 추가
					elif l == len(active)-1: # 반복 매크로 설정 파일의 마지막 줄일 경우
						for i in range(1, len(line.split(' '))): # 첫 번째는 동작이 아니므로('combination전체반복횟수:' 임) 인덱스 1부터 시작
							if '&' not in line.split(' ')[i]: # 설정 파일의 동작 조합을 구성하는 각 동작들에 & 문자가 없을 경우
								self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
								self.statusBar.showMessage('[-] Error : Invalid last line(\'combination\') setting !!') # 상태 표시줄 내용 갱신
								return
							if not self.isNumber(line.split(' ')[i].split('&')[1]): # 설정 파일의 동작 조합을 구성하는 각 동작들의 반복 횟수가 숫자가 아닐 경우
								self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
								self.statusBar.showMessage('[-] Error : Invalid last line(\'combination\') setting !!') # 상태 표시줄 내용 갱신
								return
							tmp_activeName_confirm = False # 동작 이름을 올바르게 설정했는지 확인하기 위한 변수
							for activeName in combination_activeName: # 동작 조합의 동작 개수만큼 반복
								if activeName == line.split(' ')[i].split('&')[0]: # 설정 파일의 동작 조합을 구성하는 동작 이름이 있을 경우
									tmp_activeName_confirm = True # 동작 이름을 올바르게 설정했는지 확인하기 위한 변수 값 설정
									break
							if tmp_activeName_confirm == False: # 설정 파일의 동작 조합을 구성하는 동작 이름이 없을 경우
								self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
								self.statusBar.showMessage('[-] Error : Invalid last line(\'combination\') setting !!') # 상태 표시줄 내용 갱신
								return
				self.actives.append(line) # 설정 파일의 내용이 저장될 리스트에 해당 라인 추가
				content += line + '\n' # 설정 파일 내용 추가
				line_hotkey_activeName.append(tmp_line_hotkey_activeName) # 임시 리스트에 핫키가 있는 첫 번째 위치 추가
			self.label_content.clear() # 레이블 클리어
			self.label_content.resize(450, 230)
			self.label_content.setText(content) # 설정 파일 내용으로 레이블 갱신
			self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
			if self.radiobox_hotkey.isChecked() == True: # 핫키 매크로일 경우
				self.statusBar.showMessage('Hotkey Setted') # 상태 표시줄 내용 갱신
			elif self.radiobox_loop.isChecked() == True: # 반복 매크로일 경우
				self.statusBar.showMessage('Loop Setted') # 상태 표시줄 내용 갱신
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
			if self.start == True: # 매크로가 동작중인 경우
				exit_var = True # 스레드 종료 변수 값 설정
				self.start = False # 시작 버튼 눌림 여부 값 변경
				self.statusBar.showMessage('Pause') # 상태 표시줄 내용 갱신
				self.btnStart.setEnabled(True) # 매크로 동작 버튼 활성화
				self.btnPause.setDisabled(True) # 매크로 중지 버튼 비활성화
				self.lineEdit_pause_restart.setEnabled(True) # 중지 및 재시작 키 에디트 활성화
				if self.check_potion == True: # 포션 매크로일 경우
					self.btnHealth.setEnabled(True) # 체력바 좌표와 픽셀값 설정 버튼 활성화
					self.btnMana.setEnabled(True) # 마나바 좌표와 픽셀값 설정 버튼 활성화
					self.btnFile.setEnabled(True) # 설정 파일 오픈 버튼 활성화
					self.checkbox_potion.setEnabled(True) # 포션 매크로 체크 박스 활성화
					self.radiobox_loop.setEnabled(True) # 반복 매크로 라디오 박스 활성화
					self.radiobox_hotkey.setEnabled(True) # 핫키 매크로 라디오 박스 활성화
					self.lineEdit_health_x.setEnabled(True) # 체력 포션을 사용하는 체력바의 x좌표 에디트 활성화
					self.lineEdit_health_y.setEnabled(True) # 체력 포션을 사용하는 체력바의 y좌표 에디트 활성화
					self.lineEdit_mana_x.setEnabled(True) # 마나 포션을 사용하는 마나바의 x좌표 에디트 활성화
					self.lineEdit_mana_y.setEnabled(True) # 마나 포션을 사용하는 마나바의 y좌표 에디트 활성화
					self.lineEdit_health_color.setEnabled(True) # 체력이 부족할때의 체력바 픽셀값 에디트 활성화
					self.lineEdit_mana_color.setEnabled(True) # 마나가 부족할때의 마나바 픽셀값 에디트 활성화
					self.lineEdit_health_potion_key.setEnabled(True) # 체력 포션 단축키 에디트 활성화
					self.lineEdit_mana_potion_key.setEnabled(True) # 마나 포션 단축키 에디트 활성화
				elif self.check_onlyPotion == True: # Only 포션 매크로일 경우
					self.btnHealth.setEnabled(True) # 체력바 좌표와 픽셀값 설정 버튼 활성화
					self.btnMana.setEnabled(True) # 마나바 좌표와 픽셀값 설정 버튼 활성화
					self.checkbox_onlyPotion.setEnabled(True) # Only 포션 매크로 체크 박스 활성화
					self.lineEdit_health_x.setEnabled(True) # 체력 포션을 사용하는 체력바의 x좌표 에디트 활성화
					self.lineEdit_health_y.setEnabled(True) # 체력 포션을 사용하는 체력바의 y좌표 에디트 활성화
					self.lineEdit_mana_x.setEnabled(True) # 마나 포션을 사용하는 마나바의 x좌표 에디트 활성화
					self.lineEdit_mana_y.setEnabled(True) # 마나 포션을 사용하는 마나바의 y좌표 에디트 활성화
					self.lineEdit_health_color.setEnabled(True) # 체력이 부족할때의 체력바 픽셀값 에디트 활성화
					self.lineEdit_mana_color.setEnabled(True) # 마나가 부족할때의 마나바 픽셀값 에디트 활성화
					self.lineEdit_health_potion_key.setEnabled(True) # 체력 포션 단축키 에디트 활성화
					self.lineEdit_mana_potion_key.setEnabled(True) # 마나 포션 단축키 에디트 활성화
				elif self.check_potion == False and self.check_onlyPotion == False: # 포션 매크로도 Only 포션 매크로도 아닐 경우
					self.btnFile.setEnabled(True) # 설정 파일 오픈 버튼 활성화	   
					self.radiobox_loop.setEnabled(True) # 반복 매크로 라디오 박스 활성화
					self.radiobox_hotkey.setEnabled(True) # 핫키 매크로 라디오 박스 활성화
					self.checkbox_potion.setEnabled(True) # 포션 매크로 체크 박스 활성화
					self.checkbox_onlyPotion.setEnabled(True) # Only 포션 매크로 체크 박스 활성화
				for vk in myMacro.virtual_key:
					if self.pause_restart == vk[0]: # 설정한 재시작 키일 경우
						key_state_restart = win32api.GetKeyState(vk[1]) # 설정한 재시작 키 초기 입력 상태
						th_pause_restart = threading.Thread(target=self.restart_thread, args=(self.pause_restart, vk, key_state_restart,)) # 설정한 단축키로 매크로 재시작하는 스레드 설정
						th_pause_restart.start() # 스레드 생성
						break
		except Exception, e:
			self.statusBar.showMessage('[-] Error : ' + str(e)) # 상태 표시줄 내용 갱신

	def start_func(self): # 매크로 동작 함수
		try:
			global exit_var
			if exit_var == True: # 스레드 종료 변수 값이 설정된 경우(중지 후 다시 시작했을 경우)
				exit_var = False # 스레드 종료 변수 값 초기화
			self.start = True # 시작 버튼 눌림 여부 값 변경
			self.statusBar.showMessage('Start') # 상태 표시줄 내용 갱신
			self.btnFile.setDisabled(True) # 설정 파일 오픈 버튼 비활성화
			self.btnStart.setDisabled(True) # 매크로 동작 버튼 비활성화
			self.btnPause.setEnabled(True) # 매크로 중지 버튼 활성화
			self.lineEdit_pause_restart.setDisabled(True) # 중지 및 재시작 키 에디트 비활성화
			self.lineEdit_health_x.setDisabled(True) # 체력 포션을 사용하는 체력바의 x좌표 에디트 비활성화
			self.lineEdit_health_y.setDisabled(True) # 체력 포션을 사용하는 체력바의 y좌표 에디트 비활성화
			self.lineEdit_mana_x.setDisabled(True) # 마나 포션을 사용하는 마나바의 x좌표 에디트 비활성화
			self.lineEdit_mana_y.setDisabled(True) # 마나 포션을 사용하는 마나바의 y좌표 에디트 비활성화
			self.lineEdit_health_color.setDisabled(True) # 체력이 부족할때의 체력바 픽셀값 에디트 비활성화
			self.lineEdit_mana_color.setDisabled(True) # 마나가 부족할때의 마나바 픽셀값 에디트 비활성화
			self.lineEdit_health_potion_key.setDisabled(True) # 체력 포션 단축키 에디트 비활성화
			self.lineEdit_mana_potion_key.setDisabled(True) # 마나 포션 단축키 에디트 비활성화
			self.pause_restart = str(self.lineEdit_pause_restart.text()).lower() # 설정한 중지 키 저장
			if self.check_onlyPotion == True: # Only 포션 매크로일 경우
				self.btnHealth.setDisabled(True) # 체력바 좌표와 픽셀값 설정 버튼 비활성화
				self.btnMana.setDisabled(True) # 마나바 좌표와 픽셀값 설정 버튼 비활성화
				self.checkbox_onlyPotion.setDisabled(True) # Only 포션 매크로 체크 박스 비활성화
				self.health_x = int(self.lineEdit_health_x.text()) # 체력 포션을 사용하는 체력바의 x좌표 저장
				self.health_y = int(self.lineEdit_health_y.text()) # 체력 포션을 사용하는 체력바의 y좌표 저장
				self.mana_x = int(self.lineEdit_mana_x.text()) # 마나 포션을 사용하는 마나바의 x좌표 저장
				self.mana_y = int(self.lineEdit_mana_y.text()) # 마나 포션을 사용하는 마나바의 y좌표 저장
				self.health_color = int(self.lineEdit_health_color.text()) # 체력이 부족할때의 체력바 픽셀값 저장
				self.mana_color = int(self.lineEdit_mana_color.text()) # 마나가 부족할때의 마나바 픽셀값 저장
				self.health_potion_key = str(self.lineEdit_health_potion_key.text()).lower() # 체력 포션 단축키 저장
				self.mana_potion_key = str(self.lineEdit_mana_potion_key.text()).lower() # 마나 포션 단축키 저장
				for vk in myMacro.virtual_key:
					if self.pause_restart == vk[0]: # 설정한 중지 키일 경우
						key_state_pause = win32api.GetKeyState(vk[1]) # 설정한 중지 키 초기 입력 상태
						th_pause = threading.Thread(target=self.pause_thread, args=(self.pause_restart, vk, key_state_pause,)) # 설정한 중지 키 입력 감지 스레드 설정
						th_pause.start() # 스레드 생성
						break
				th_onlyPotion = threading.Thread(target=self.potion_macro_thread, args=()) # Only 포션 매크로 스레드 설정
				th_onlyPotion.start() # 스레드 생성
				return
			self.radiobox_loop.setDisabled(True) # 반복 매크로 라디오 박스 비활성화
			self.radiobox_hotkey.setDisabled(True) # 핫키 매크로 라디오 박스 비활성화
			if self.check_potion == True: # 포션 매크로일 경우
				self.btnHealth.setDisabled(True) # 체력바 좌표와 픽셀값 설정 버튼 비활성화
				self.btnMana.setDisabled(True) # 마나바 좌표와 픽셀값 설정 버튼 비활성화
				self.checkbox_potion.setDisabled(True) # 포션 매크로 체크 박스 비활성화
				self.health_x = int(self.lineEdit_health_x.text()) # 체력 포션을 사용하는 체력바의 x좌표 저장
				self.health_y = int(self.lineEdit_health_y.text()) # 체력 포션을 사용하는 체력바의 y좌표 저장
				self.mana_x = int(self.lineEdit_mana_x.text()) # 마나 포션을 사용하는 마나바의 x좌표 저장
				self.mana_y = int(self.lineEdit_mana_y.text()) # 마나 포션을 사용하는 마나바의 y좌표 저장
				self.health_color = int(self.lineEdit_health_color.text()) # 체력이 부족할때의 체력바 픽셀값 저장
				self.mana_color = int(self.lineEdit_mana_color.text()) # 마나가 부족할때의 마나바 픽셀값 저장
				self.health_potion_key = str(self.lineEdit_health_potion_key.text()).lower() # 체력 포션 단축키 저장
				self.mana_potion_key = str(self.lineEdit_mana_potion_key.text()).lower() # 마나 포션 단축키 저장
				th_potion = threading.Thread(target=self.potion_macro_thread, args=()) # 포션 매크로 스레드 설정
				th_potion.start() # 스레드 생성
			elif self.check_potion == False and self.check_onlyPotion == False: # 포션 매크로도 Only 포션 매크로도 아닐 경우
				self.checkbox_potion.setDisabled(True) # 포션 매크로 체크 박스 비활성화
				self.checkbox_onlyPotion.setDisabled(True) # Only 포션 매크로 체크 박스 비활성화
			if self.radiobox_hotkey.isChecked() == True: # 핫키 매크로일 경우
				duplication = False # 핫키와 중지 키 중복 여부
				for active in self.actives:
					hotkey = active.split(' ')[0] # 공백으로 구분 후 핫키가 있는 첫 번째 위치 저장
					hotkey = hotkey[:-1].lower() # 핫키 구분자(콜론) 제거해서 순수히 핫키만 저장, 핫키 소문자 변환
					if self.pause_restart == hotkey: # 핫키와 설정한 중지 키가 같을 경우(겹치면 안됨)
						duplication = True # 중복 여부 값 변경
					for vk in myMacro.virtual_key:
						if hotkey == vk[0]: # 설정한 핫키일 경우
							key_state = win32api.GetKeyState(vk[1]) # 핫키 초기 입력 상태
							th_hotkey = threading.Thread(target=self.hotkey_macro_thread, args=(hotkey, vk, key_state, active)) # 핫키 입력 감지 스레드 설정
							th_hotkey.start() # 스레드 생성
				if duplication == True: # 핫키 중에서 설정한 중지 키와 같은 키가 있을 경우(겹치면 안됨)
					self.pause_restart = 'None' # 중지 키 비활성화
					self.lineEdit_pause_restart.clear() # 에디트 클리어
					self.lineEdit_pause_restart.setText(self.pause_restart) # 에디트 비활성화 상태로 설정
				else: # 핫키 중에서 설정한 중지 키와 같은 키가 없을 경우(안겹치므로 설정한 중지 키 입력 감지 스레드 구성)
					for vk in myMacro.virtual_key:
						if self.pause_restart == vk[0]: # 설정한 중지 키일 경우
							key_state_pause = win32api.GetKeyState(vk[1]) # 설정한 중지 키 초기 입력 상태
							th_pause = threading.Thread(target=self.pause_thread, args=(self.pause_restart, vk, key_state_pause,)) # 설정한 중지 키 입력 감지 스레드 설정
							th_pause.start() # 스레드 생성
							break
			elif self.radiobox_loop.isChecked() == True: # 반복 매크로일 경우
				for vk in myMacro.virtual_key:
					if self.pause_restart == vk[0]: # 설정한 중지 키일 경우
						key_state_pause = win32api.GetKeyState(vk[1]) # 설정한 중지 키 초기 입력 상태
						th_pause = threading.Thread(target=self.pause_thread, args=(self.pause_restart, vk, key_state_pause,)) # 설정한 중지 키 입력 감지 스레드 설정
						th_pause.start() # 스레드 생성
						break
				th_loop = threading.Thread(target=self.loop_macro_thread, args=()) # 반복 매크로 스레드 설정
				th_loop.start() # 스레드 생성
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
						if key_state == -127 or key_state == -128: # 두 번 실행 방지
							if key == self.pause_restart: # 입력한 키가 설정한 중지 키일 경우
								self.pause_func() # 매크로 중지 함수 실행
								sem.release() # 임계영역 해제
								return # 스레드 종료
				sem.release() # 임계영역 해제
			except Exception, e:
				sem.release() # 임계영역 해제
				pass

	def hotkey_macro_thread(self, key, vk, key_state, active): # 핫키 매크로 스레드
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
						if key_state == -127 or key_state == -128: # 두 번 실행 방지
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
											continue_time = act[i].split('^')[1] # 지속 시간 저장
											input_key = act[i].split('^')[0] # 입력 키 저장
											keyboard.press(input_key) # 키 눌림 상태 유지
											time.sleep(float(continue_time)) # 지속 시간만큼 대기
											keyboard.release(input_key) # 키 눌림 상태 해제
										elif '+' in act[i]: # 조합 입력일 경우
											first_key = act[i].split('+')[0] # 조합해서 입력할 키 중 첫 번째 키 저장
											second_key = act[i].split('+')[1] # 조합해서 입력할 키 중 두 번째 키 저장
											keyboard.press(first_key) # 첫 번째 키 눌림 상태 유지
											keyboard.press(second_key) # 두 번째 키 눌림 상태 유지
											time.sleep(0.01) # 너무 빠른 입력으로 인한 키 입력 씹힘 방지 딜레이
											keyboard.release(second_key) # 두 번째 키 눌림 상태 해제
											keyboard.release(first_key) # 첫 번째 키 눌림 상태 해제
										else: # 지속 입력 및 조합 입력이 아닐 경우
											if 'leftclick' in act[i]: # 마우스 좌클릭일 경우
												myMacro.click_mouse_left(0,0) # 마우스 좌클릭
											elif 'rightclick' in act[i]: # 마우스 우클릭일 경우
												myMacro.click_mouse_right(0,0) # 마우스 우클릭
											else: # 키보드 입력일 경우
												keyboard.press(act[i]) # 키 눌림 상태 유지
												time.sleep(0.01) # 너무 빠른 입력으로 인한 키 입력 씹힘 방지 딜레이
												keyboard.release(act[i]) # 키 눌림 상태 해제
				sem.release() # 임계영역 해제
			except Exception, e:
				sem.release() # 임계영역 해제
				pass

	def loop_macro_thread(self): # 반복 매크로 스레드
		try:
			time.sleep(3) # 3초간 대기(게임 화면 띄우는 등의 준비 시간)
			loop_count = int(self.actives[-1].split(' ')[0].split('n')[-1][:-1]) # 전체 반복 횟수
			active_count = len(self.actives[-1].split(' ')) # combination 동작 개수
			exit_count = 0 # 반복문 탈출 변수
			while exit_count <= loop_count: # 전체 반복 횟수만큼 반복
				try:
					sem.acquire() # 임계영역 생성
					if loop_count != 0: # 무한 반복이 아닐 경우
						exit_count += 1 # 반복문 탈출 변수 증가
					for a in range(1, active_count): # 제일 마지막 줄의 첫 번째는 동작이 아니므로(combination 문자열과 전체 반복 횟수 및 구분자(:)임) 인덱스 1부터 시작
						active_name = self.actives[-1].split(' ')[a].split('&')[0] # 동작 이름
						active_sub_count = int(self.actives[-1].split(' ')[a].split('&')[-1]) # 동작 반복 횟수
						for b in range(0, len(self.actives) - 1): # 제일 마지막 줄을 제외하고 반복
							if active_name == self.actives[b].split(' ')[0][:-1]: # 동작 이름이 같을 경우
								act = self.actives[b].split(' ') # 설정 파일의 동작 한 줄 저장
								for c in range(0, active_sub_count): # 동작 반복 횟수만큼 반복
									for i in range(1, len(act)): # 첫 번째는 동작이 아니므로(동작 이름과 구분자(:)임) 인덱스 1부터 시작
										if self.start == False: # 매크로 중지 함수가 실행돼서 시작 상태가 아닐 경우
											sem.release() # 임계영역 해제
											return
										if i%2 == 0 and i != 1: # 딜레이 시간일 경우
											time.sleep(float(act[i])) # 딜레이 시간만큼 정지
										elif i%2 == 1 or i == 1: # 동작일 경우
											if 'move' in act[i]: # 마우스 이동일 경우
												move_x = act[i].split('^')[1].split(',')[0] # 이동할 x값 저장
												move_y = act[i].split('^')[1].split(',')[1] # 이동할 y값 저장
												myMacro.move_mouse_game(int(move_x), int(move_y)) # 설정한 좌표로 마우스 이동
											else: # 마우스 이동이 아닐 경우
												if '^' in act[i]: # 지속 입력일 경우
													continue_time = act[i].split('^')[1] # 지속 시간 저장
													input_key = act[i].split('^')[0] # 입력 키 저장
													keyboard.press(input_key) # 키 눌림 상태 유지
													time.sleep(float(continue_time)) # 지속 시간만큼 대기
													keyboard.release(input_key) # 키 눌림 상태 해제
												elif '+' in act[i]: # 조합 입력일 경우
													first_key = act[i].split('+')[0] # 조합해서 입력할 키 중 첫 번째 키
													second_key = act[i].split('+')[1] # 조합해서 입력할 키 중 두 번째 키
													keyboard.press(first_key) # 첫 번째 키 눌림 상태 유지
													keyboard.press(second_key) # 두 번째 키 눌림 상태 유지
													time.sleep(0.01) # 너무 빠른 입력으로 인한 키 입력 씹힘 방지 딜레이 시간
													keyboard.release(second_key) # 두 번째 키 눌림 상태 해제
													keyboard.release(first_key) # 첫 번째 키 눌림 상태 해제
												else: # 지속 입력 및 조합 입력이 아닐 경우
													if 'leftclick' in act[i]: # 마우스 좌클릭일 경우
														myMacro.click_mouse_left(0,0) # 마우스 좌클릭
													elif 'rightclick' in act[i]: # 마우스 우클릭일 경우
														myMacro.click_mouse_right(0,0) # 마우스 우클릭
													else: # 키보드 입력일 경우
														keyboard.press(act[i]) # 키 눌림 상태 유지
														time.sleep(0.01) # 너무 빠른 입력으로 인한 키 입력 씹힘 방지 딜레이 시간
														keyboard.release(act[i]) # 키 눌림 상태 해제
								break
					sem.release() # 임계영역 해제
				except Exception, e:
					sem.release() # 임계영역 해제
					pass
		except Exception, e:
			return

	def potion_macro_thread(self): # 포션 매크로 스레드
		global exit_var
		while True:
			try:
				sem.acquire() # 임계영역 생성
				if exit_var == True: # 스레드 종료 변수가 설정됐을 경우
					sem.release() # 임계영역 해제
					return
				else:
					health_pixel = QPixmap.grabWindow(QApplication.desktop().winId()).toImage().pixel(self.health_x, self.health_y) # 체력바 위치의 픽셀값(16진수) 저장
					mana_pixel = QPixmap.grabWindow(QApplication.desktop().winId()).toImage().pixel(self.mana_x, self.mana_y) # 마나바 위치의 픽셀값(16진수) 저장
					cur_health_color = (qBlue(health_pixel) * 65536 + qGreen(health_pixel) * 256 + qRed(health_pixel)) # 체력바 위치의 픽셀값 10진수로 변경
					cur_mana_color = (qBlue(mana_pixel) * 65536 + qGreen(mana_pixel) * 256 + qRed(mana_pixel)) # 마나바 위치의 픽셀값 10진수로 변경
					if self.health_color == cur_health_color: # 체력이 체력바의 설정한 구간 이하로 떨어졌을 경우
						keyboard.press_and_release(self.health_potion_key) # 체력 포션 단축키 입력
					if self.mana_color == cur_mana_color: # 마나가 마나바의 설정한 구간 이하로 떨어졌을 경우
						keyboard.press_and_release(self.mana_potion_key) # 마나 포션 단축키 입력
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