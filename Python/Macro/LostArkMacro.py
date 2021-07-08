# -*- coding: utf-8 -*-
import os
import sys
import time
import math
import win32api
import win32gui
import win32con
import threading
import keyboard
import cv2
import numpy as np
from PIL import ImageGrab, Image
from PyQt4 import QtGui, QtCore
import LostArkBinary
import myMacro

sem = threading.Semaphore(10) # 세마포어 설정
actionThreadExit = False # 매크로 동작 스레드 종료 변수
restartThreadExit = False # 매크로 재시작 스레드 종료 변수
fishtrapTime = 0 # 통발 낚시 제어 시간

class MainClass(object):
    def __init__(self, dialog):
        try:
            self.dialog = dialog # 다이얼로그 저장
            self.start = False # 시작 버튼 눌림 여부
            self.actives = [] # 설정 파일의 내용이 저장될 리스트
            self.readyTime = '3' # 매크로 동작 전 대기 시간
            self.pauseRestartKey = 'F12' # 매크로 중지 및 재시작 키
            self.progWidth = 270 # 프로그램 가로 크기
            self.progHeight = 310 # 프로그램 세로 크기
            self.progPosX = win32api.GetSystemMetrics(win32con.SM_CXSCREEN) / 2 - self.progWidth / 2 # 처음 프로그램이 나타나는 x좌표
            self.progPosY = win32api.GetSystemMetrics(win32con.SM_CYSCREEN) / 2 - self.progHeight / 1.5 # 처음 프로그램이 나타나는 y좌표
            self.fishingKey = 'w' # 찌낚시 스킬 키
            self.castnetKey = 'q' # 투망 낚시 스킬 키
            self.fishingDirection = 0 # 낚시터 방향
            self.fishingWaitTime = '7' # 찌낚시 후 다음 찌낚시까지 대기 시간
            self.fishtrapWaitTime = '4' # 통발 설치 및 회수 대기 시간
            self.itemUsePeriod = '5' # 낚시 도구 장착 주기
            self.turnPeriod = '0.008' # 끌망 시 선박 회전 주기
            self.repairPeriod = '200' # 끌망 시 선박 내구도 수리 주기
            self.setWindow() # 윈도우 설정
            self.setTab() # 탭 설정
            self.setButton() # 버튼 설정
            self.setLabel() # 레이블 설정
            self.setLineEdit() # 에디트 설정
            self.setComboBox() # 콤보 박스 설정
            self.setCheckBox() # 체크 박스 설정
            self.setupStatusBar() # 상태 표시줄 설정
        except Exception as e:
            print(e)
    
    def setWindow(self): # 윈도우 설정 함수
        try:
            self.dialog.setWindowTitle('LostArk Macro Program') # 윈도우 타이틀 설정
            self.dialog.setGeometry(self.progPosX, self.progPosY, self.progWidth, self.progHeight) # 윈도우 위치 및 크기 설정
            with open(os.getcwd() + '\\TempLostArkIcon.png', 'wb') as fp:
                fp.write(LostArkBinary.iconImage) # 아이콘 이미지 파일 생성
            self.dialog.setWindowIcon(QtGui.QIcon(os.getcwd() + '\\TempLostArkIcon.png')) # 타이틀 아이콘 설정
            self.dialog.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowMinMaxButtonsHint) # 닫기 버튼 비활성화
            self.dialog.setWindowFlags(self.dialog.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint) # 최대화 버튼 비활성화
            self.dialog.setFixedSize(self.progWidth, self.progHeight) # 화면 크기 변경 금지 설정
        except Exception as e:
            print(e)
    
    def setTab(self): # 탭 설정 함수
        try:
            self.tabs = QtGui.QTabWidget(self.dialog) # 탭 생성
            self.tabs.setGeometry(QtCore.QRect(10, 10, self.progWidth - 20, self.progHeight - 30)) # 탭 위치 및 크기 설정
            self.tabs.setStyleSheet('QTabBar::tab {height: 25px; width: 80px;}') # 탭 바 크기 설정
            self.tabSkill = QtGui.QWidget() # 스킬 매크로 탭 생성
            self.tabFishing = QtGui.QWidget() # 낚시 매크로 탭 생성
            self.tabSailing = QtGui.QWidget() # 항해 매크로 탭 생성
            self.tabs.addTab(self.tabSkill, 'Skill') # 스킬 매크로 탭 추가
            self.tabs.addTab(self.tabFishing, 'Fish') # 낚시 매크로 탭 추가
            self.tabs.addTab(self.tabSailing, 'Sail') # 항해 매크로 탭 추가
            self.tabs.setCurrentIndex(1) # 기본 탭 설정
        except Exception as e:
            print(e)
    
    def setButton(self): # 버튼 설정 함수
        try:
            self.btnStart = QtGui.QPushButton('Start', self.dialog) # 매크로 시작 버튼 생성
            self.btnStart.setGeometry(QtCore.QRect(17, 250, 71, 31)) # 매크로 시작 버튼 위치 및 크기 설정
            self.btnStart.clicked.connect(self.macroStart) # 매크로 시작 이벤트 핸들러 설정
            self.btnPause = QtGui.QPushButton('Pause', self.dialog) # 매크로 중지 버튼 생성
            self.btnPause.setGeometry(QtCore.QRect(97, 250, 71, 31)) # 매크로 중지 버튼 위치 및 크기 설정
            self.btnPause.clicked.connect(self.macroPause) # 매크로 중지 이벤트 핸들러 설정
            self.btnPause.setDisabled(True) # 매크로 중지 버튼 비활성화
            self.btnExit = QtGui.QPushButton('Exit', self.dialog) # 매크로 종료 버튼 생성
            self.btnExit.setGeometry(QtCore.QRect(177, 250, 71, 31)) # 매크로 종료 버튼 위치 및 크기 설정
            self.btnExit.clicked.connect(self.macroExit) # 매크로 종료 이벤트 핸들러 설정
            self.btnKeyList = QtGui.QPushButton('Key List', self.tabSkill) # 키 목록 확인 버튼 생성
            self.btnKeyList.setGeometry(QtCore.QRect(125, 35, 71, 31)) # 키 목록 확인 버튼 위치 및 크기 설정
            self.btnKeyList.clicked.connect(self.keyList) # 키 목록 확인 이벤트 핸들러 설정
            self.btnKeyList.setToolTip(str('설정 가능한 키 목록')) # 키 목록 확인 버튼 툴팁
            self.btnFile = QtGui.QPushButton('Setup File Open', self.tabSkill) # 스킬 설정 파일 선택 버튼 생성
            self.btnFile.setGeometry(QtCore.QRect(120, 170, 115, 35)) # 스킬 설정 파일 선택 버튼 위치 및 크기 설정
            self.btnFile.clicked.connect(self.setupFile) # 스킬 설정 파일 선택 이벤트 핸들러 설정
            self.btnFile.setToolTip(str('설정 파일 열기')) # 스킬 설정 파일 선택 버튼 툴팁
            self.btnSetupMethod = QtGui.QPushButton('Setup Method', self.tabSkill) # 파일 설정 방법 확인 버튼 생성
            self.btnSetupMethod.setGeometry(QtCore.QRect(145, 135, 90, 31)) # 파일 설정 방법 확인 버튼 위치 및 크기 설정
            self.btnSetupMethod.clicked.connect(self.setupMethod) # 파일 설정 방법 확인 이벤트 핸들러 설정
            self.btnSetupMethod.setToolTip(str('파일 설정 방법')) # 파일 설정 방법 확인 버튼 툴팁
        except Exception as e:
            print(e)
    
    def setLabel(self): # 레이블 설정 함수
        try:
            self.labelSkillPauseRestartKey = QtGui.QLabel('Pause & Restart Key : ', self.tabSkill) # 스킬 매크로 중지 및 재시작 키 레이블 생성
            self.labelSkillPauseRestartKey.setGeometry(QtCore.QRect(10, 10, 124, 16)) # 스킬 매크로 중지 및 재시작 키 레이블 위치 및 크기 설정
            self.labelSkillPauseRestartKey.setToolTip(str('매크로 중지 및 재시작 키')) # 스킬 매크로 중지 및 재시작 키 레이블 툴팁
            self.labelSkillKeyboard = QtGui.QLabel('1. Keyboard', self.tabSkill) # 키보드 매크로 설명 레이블
            self.labelSkillKeyboard.setGeometry(QtCore.QRect(10, 30, 70, 16))
            self.labelSkillKeyboard.setToolTip(str('키보드 매크로'))
            self.labelSkillKeyboardSimpleInput = QtGui.QLabel('Simple Input : f1', self.tabSkill)
            self.labelSkillKeyboardSimpleInput.setGeometry(QtCore.QRect(10, 50, 90, 16))
            self.labelSkillKeyboardSimpleInput.setToolTip(str('단순 입력 : f1 키 입력'))
            self.labelSkillKeyboardContinuousInput = QtGui.QLabel('Continuous Input : q^3.5', self.tabSkill)
            self.labelSkillKeyboardContinuousInput.setGeometry(QtCore.QRect(10, 70, 140, 16))
            self.labelSkillKeyboardContinuousInput.setToolTip(str('지속 입력 : q 키 3.5초 동안 입력'))
            self.labelSkillKeyboardCombinationInput = QtGui.QLabel('Combination Input : shift+w', self.tabSkill)
            self.labelSkillKeyboardCombinationInput.setGeometry(QtCore.QRect(10, 90, 160, 16))
            self.labelSkillKeyboardCombinationInput.setToolTip(str('조합 입력 : shift 키와 w 키 같이 입력'))
            self.labelSkillMouse = QtGui.QLabel('2. Mouse', self.tabSkill) # 마우스 매크로 설명 레이블
            self.labelSkillMouse.setGeometry(QtCore.QRect(10, 110, 60, 16))
            self.labelSkillMouse.setToolTip(str('마우스 매크로'))
            self.labelSkillMouseLeftClick = QtGui.QLabel('Left Click : leftclick', self.tabSkill)
            self.labelSkillMouseLeftClick.setGeometry(QtCore.QRect(10, 130, 110, 16))
            self.labelSkillMouseLeftClick.setToolTip(str('마우스 좌클릭'))
            self.labelSkillMouseRightClick = QtGui.QLabel('Right Click : rightclick', self.tabSkill)
            self.labelSkillMouseRightClick.setGeometry(QtCore.QRect(10, 150, 130, 16))
            self.labelSkillMouseRightClick.setToolTip(str('마우스 우클릭'))
            self.labelSkillMouseMove = QtGui.QLabel('Move : move^x,y', self.tabSkill)
            self.labelSkillMouseMove.setGeometry(QtCore.QRect(10, 170, 100, 16))
            self.labelSkillMouseMove.setToolTip(str('마우스 이동 : 현재 마우스 위치로부터 x,y 픽셀만큼 이동'))
            self.labelFishingReadyTime = QtGui.QLabel('Ready Time : ', self.tabFishing) # 낚시 매크로 동작 전 대기 시간 레이블 생성
            self.labelFishingReadyTime.setGeometry(QtCore.QRect(10, 10, 76, 16)) # 낚시 매크로 동작 전 대기 시간 레이블 위치 및 크기 설정
            self.labelFishingReadyTime.setToolTip(str('낚시 매크로 동작 전 대기 시간(초)')) # 낚시 매크로 동작 전 대기 시간 레이블 툴팁
            self.labelFishingKey = QtGui.QLabel('Fishing Key : ', self.tabFishing) # 낚시 스킬 키 레이블 생성
            self.labelFishingKey.setGeometry(QtCore.QRect(10, 40, 74, 16)) # 낚시 스킬 키 레이블 위치 및 크기 설정
            self.labelFishingKey.setToolTip(str('낚시 스킬 키')) # 낚시 스킬 키 레이블 툴팁
            self.labelFishingDirection = QtGui.QLabel('Fishing Direction : ', self.tabFishing) # 낚시터 방향 레이블 생성
            self.labelFishingDirection.setGeometry(QtCore.QRect(10, 70, 101, 16)) # 낚시터 방향 레이블 위치 및 크기 설정
            self.labelFishingDirection.setToolTip(str('낚시터 방향')) # 낚시터 방향 레이블 툴팁
            self.labelFishingWaitTime = QtGui.QLabel('Fishing Wait Time : ', self.tabFishing) # 찌낚시 후 다음 찌낚시까지 대기 시간 레이블 생성
            self.labelFishingWaitTime.setGeometry(QtCore.QRect(10, 100, 108, 16)) # 찌낚시 후 다음 찌낚시까지 대기 시간 레이블 위치 및 크기 설정
            self.labelFishingWaitTime.setToolTip(str('찌낚시 후 다음 찌낚시까지 대기 시간')) # 찌낚시 후 다음 찌낚시까지 대기 시간 레이블 툴팁
            self.labelFishtrapWaitTime = QtGui.QLabel('Fish trap Wait Time : ', self.tabFishing) # 통발 설치 및 회수 대기 시간 레이블 생성
            self.labelFishtrapWaitTime.setGeometry(QtCore.QRect(10, 130, 116, 16)) # 통발 설치 및 회수 대기 시간 레이블 위치 및 크기 설정
            self.labelFishtrapWaitTime.setToolTip(str('통발 설치 및 회수 대기 시간')) # 통발 설치 및 회수 대기 시간 레이블 툴팁
            self.labelItemUsePeriod = QtGui.QLabel('Fishing tackle Use Period : ', self.tabFishing) # 낚시 도구 장착 주기 레이블 생성
            self.labelItemUsePeriod.setGeometry(QtCore.QRect(10, 160, 151, 16)) # 낚시 도구 장착 주기 레이블 위치 및 크기 설정
            self.labelItemUsePeriod.setToolTip(str('낚시 도구 장착 주기로 설정한 횟수만큼 찌낚시 후 인벤토리에 낚시 도구가 있을 경우 낚시 도구를 장착한다.')) # 낚시 도구 장착 주기 레이블 툴팁
            self.labelFishingPauseRestartKey = QtGui.QLabel('Pause & Restart Key : ', self.tabFishing) # 낚시 매크로 중지 및 재시작 키 레이블 생성
            self.labelFishingPauseRestartKey.setGeometry(QtCore.QRect(10, 190, 124, 16)) # 낚시 매크로 중지 및 재시작 키 레이블 위치 및 크기 설정
            self.labelFishingPauseRestartKey.setToolTip(str('매크로 중지 및 재시작 키')) # 낚시 매크로 중지 및 재시작 키 레이블 툴팁
            self.labelSailingReadyTime = QtGui.QLabel('Ready Time : ', self.tabSailing) # 항해 매크로 동작 전 대기 시간 레이블 생성
            self.labelSailingReadyTime.setGeometry(QtCore.QRect(10, 10, 76, 16)) # 항해 매크로 동작 전 대기 시간 레이블 위치 및 크기 설정
            self.labelSailingReadyTime.setToolTip(str('항해 매크로 동작 전 대기 시간(초)')) # 항해 매크로 동작 전 대기 시간 레이블 툴팁
            self.labelSailingTurnPeriod = QtGui.QLabel('Turn Period : ', self.tabSailing) # 끌망 시 선박 회전 주기 레이블 생성
            self.labelSailingTurnPeriod.setGeometry(QtCore.QRect(10, 40, 73, 16)) # 끌망 시 선박 회전 주기 레이블 위치 및 크기 설정
            self.labelSailingTurnPeriod.setToolTip(str('끌망 시 선박 회전 주기(초)')) # 끌망 시 선박 회전 주기 레이블 툴팁
            self.labelSailingRepairPeriod = QtGui.QLabel('Repair Period : ', self.tabSailing) # 끌망 시 선박 내구도 수리 주기 레이블 생성
            self.labelSailingRepairPeriod.setGeometry(QtCore.QRect(10, 70, 83, 16)) # 끌망 시 선박 내구도 수리 주기 레이블 위치 및 크기 설정
            self.labelSailingRepairPeriod.setToolTip(str('끌망 시 선박 내구도 수리 주기(초)')) # 끌망 시 선박 내구도 수리 주기 레이블 툴팁
            self.labelSailingPauseRestartKey = QtGui.QLabel('Pause & Restart Key : ', self.tabSailing) # 항해 매크로 중지 및 재시작 키 레이블 생성
            self.labelSailingPauseRestartKey.setGeometry(QtCore.QRect(10, 100, 124, 16)) # 항해 매크로 중지 및 재시작 키 레이블 위치 및 크기 설정
            self.labelSailingPauseRestartKey.setToolTip(str('매크로 중지 및 재시작 키')) # 항해 매크로 중지 및 재시작 키 레이블 툴팁
        except Exception as e:
            print(e)
    
    def setLineEdit(self): # 에디트 설정 함수
        try:
            self.lineEditSkillPauseRestartKey = QtGui.QLineEdit(self.pauseRestartKey, self.tabSkill) # 스킬 매크로 중지 및 재시작 키 에디트 생성
            self.lineEditSkillPauseRestartKey.setGeometry(QtCore.QRect(144, 8, 50, 20)) # 스킬 매크로 중지 및 재시작 키 에디트 위치 및 크기 설정
            self.lineEditSkillPauseRestartKey.setToolTip(str('매크로 중지 및 재시작 키')) # 스킬 매크로 중지 및 재시작 키 에디트 툴팁
            self.lineEditFishingReadyTime = QtGui.QLineEdit(self.readyTime, self.tabFishing) # 낚시 매크로 동작 전 대기 시간 에디트 생성
            self.lineEditFishingReadyTime.setGeometry(QtCore.QRect(96, 8, 50, 20)) # 낚시 매크로 동작 전 대기 시간 에디트 위치 및 크기 설정
            self.lineEditFishingReadyTime.setToolTip(str('낚시 매크로 동작 전 대기 시간(초)')) # 낚시 매크로 동작 전 대기 시간 에디트 툴팁
            self.lineEditFishingWaitTime = QtGui.QLineEdit(self.fishingWaitTime, self.tabFishing) # 찌낚시 후 다음 찌낚시까지 대기 시간 에디트 생성
            self.lineEditFishingWaitTime.setGeometry(QtCore.QRect(128, 98, 50, 20)) # 찌낚시 후 다음 찌낚시까지 대기 시간 에디트 위치 및 크기 설정
            self.lineEditFishingWaitTime.setToolTip(str('찌낚시 후 다음 찌낚시까지 대기 시간')) # 찌낚시 후 다음 찌낚시까지 대기 시간 에디트 툴팁
            self.lineEditFishtrapWaitTime = QtGui.QLineEdit(self.fishtrapWaitTime, self.tabFishing) # 통발 설치 및 회수 대기 시간 에디트 생성
            self.lineEditFishtrapWaitTime.setGeometry(QtCore.QRect(136, 128, 50, 20)) # 통발 설치 및 회수 대기 시간 에디트 위치 및 크기 설정
            self.lineEditFishtrapWaitTime.setToolTip(str('통발 설치 및 회수 대기 시간')) # 통발 설치 및 회수 대기 시간 에디트 툴팁
            self.lineEditFishtrapWaitTime.setDisabled(True) # 통발 설치 및 회수 대기 시간 에디트 비활성화
            self.lineEditItemUsePeriod = QtGui.QLineEdit(self.itemUsePeriod, self.tabFishing) # 낚시 도구 장착 주기 에디트 생성
            self.lineEditItemUsePeriod.setGeometry(QtCore.QRect(171, 158, 50, 20)) # 낚시 도구 장착 주기 에디트 위치 및 크기 설정
            self.lineEditItemUsePeriod.setToolTip(str('낚시 도구 장착 주기로 설정한 횟수만큼 찌낚시 후 인벤토리에 낚시 도구가 있을 경우 낚시 도구를 장착한다.')) # 낚시 도구 장착 주기 에디트 툴팁
            self.lineEditFishingPauseRestartKey = QtGui.QLineEdit(self.pauseRestartKey, self.tabFishing) # 낚시 매크로 중지 및 재시작 키 에디트 생성
            self.lineEditFishingPauseRestartKey.setGeometry(QtCore.QRect(144, 188, 50, 20)) # 낚시 매크로 중지 및 재시작 키 에디트 위치 및 크기 설정
            self.lineEditFishingPauseRestartKey.setToolTip(str('매크로 중지 및 재시작 키')) # 낚시 매크로 중지 및 재시작 키 에디트 툴팁
            self.lineEditSailingReadyTime = QtGui.QLineEdit(self.readyTime, self.tabSailing) # 항해 매크로 동작 전 대기 시간 에디트 생성
            self.lineEditSailingReadyTime.setGeometry(QtCore.QRect(96, 8, 50, 20)) # 항해 매크로 동작 전 대기 시간 에디트 위치 및 크기 설정
            self.lineEditSailingReadyTime.setToolTip(str('항해 매크로 동작 전 대기 시간(초)')) # 항해 매크로 동작 전 대기 시간 에디트 툴팁
            self.lineEditSailingTurnPeriod = QtGui.QLineEdit(self.turnPeriod, self.tabSailing) # 끌망 시 선박 회전 주기 에디트 생성
            self.lineEditSailingTurnPeriod.setGeometry(QtCore.QRect(93, 38, 50, 20)) # 끌망 시 선박 회전 주기 에디트 위치 및 크기 설정
            self.lineEditSailingTurnPeriod.setToolTip(str('끌망 시 선박 회전 주기(초)')) # 끌망 시 선박 회전 주기 에디트 툴팁
            self.lineEditSailingRepairPeriod = QtGui.QLineEdit(self.repairPeriod, self.tabSailing) # 끌망 시 선박 내구도 수리 주기 에디트 생성
            self.lineEditSailingRepairPeriod.setGeometry(QtCore.QRect(103, 68, 50, 20)) # 끌망 시 선박 내구도 수리 주기 에디트 위치 및 크기 설정
            self.lineEditSailingRepairPeriod.setToolTip(str('끌망 시 선박 내구도 수리 주기(초)')) # 끌망 시 선박 내구도 수리 주기 에디트 툴팁
            self.lineEditSailingPauseRestartKey = QtGui.QLineEdit(self.pauseRestartKey, self.tabSailing) # 항해 매크로 중지 및 재시작 키 에디트 생성
            self.lineEditSailingPauseRestartKey.setGeometry(QtCore.QRect(144, 98, 50, 20)) # 항해 매크로 중지 및 재시작 키 에디트 위치 및 크기 설정
            self.lineEditSailingPauseRestartKey.setToolTip(str('매크로 중지 및 재시작 키')) # 항해 매크로 중지 및 재시작 키 에디트 툴팁
        except Exception as e:
            print(e)
    
    def setComboBox(self): # 콤보 박스 설정 함수
        try:
            self.comboBoxFishingKey = QtGui.QComboBox(self.tabFishing) # 찌낚시 스킬 키 콤보 박스 생성
            self.comboBoxFishingKey.setGeometry(QtCore.QRect(94, 36, 60, 25)) # 찌낚시 스킬 키 콤보 박스 위치 및 크기 설정
            self.comboBoxFishingKey.addItems(['W', 'Q', 'E', 'R', 'A', 'S', 'D', 'F']) # 찌낚시 스킬 키 콤보 박스에 추가
            self.comboBoxFishingKey.currentIndexChanged.connect(self.selectFishingKey) # 찌낚시 스킬 키 콤보 박스 이벤트 핸들러 설정
            self.comboBoxFishingKey.setToolTip(str('찌낚시 스킬 키')) # 찌낚시 스킬 키 콤보 박스 툴팁
            self.comboBoxCastnetKey = QtGui.QComboBox(self.tabFishing) # 투망 낚시 스킬 키 콤보 박스 생성
            self.comboBoxCastnetKey.setGeometry(QtCore.QRect(160, 36, 60, 25)) # 투망 낚시 스킬 키 콤보 박스 위치 및 크기 설정
            self.comboBoxCastnetKey.addItems(['Q', 'W', 'E', 'R', 'A', 'S', 'D', 'F']) # 투망 낚시 스킬 키 콤보 박스에 추가
            self.comboBoxCastnetKey.currentIndexChanged.connect(self.selectCastnetKey) # 투망 낚시 스킬 키 콤보 박스 이벤트 핸들러 설정
            self.comboBoxCastnetKey.setToolTip(str('투망 낚시 스킬 키')) # 투망 낚시 스킬 키 콤보 박스 툴팁
            self.comboBoxCastnetKey.setDisabled(True) # 투망 낚시 스킬 키 콤보 박스 비활성화
            self.comboBoxFishingDirection = QtGui.QComboBox(self.tabFishing) # 낚시터 방향 콤보 박스 생성
            self.comboBoxFishingDirection.setGeometry(QtCore.QRect(121, 66, 60, 25)) # 낚시터 방향 콤보 박스 위치 및 크기 설정
            self.comboBoxFishingDirection.addItems(['12:00', '1:30', '3:00', '4:30', '6:00', '7:30', '9:00', '10:30']) # 낚시터 방향 콤보 박스에 추가
            self.comboBoxFishingDirection.currentIndexChanged.connect(self.selectFishingDirection) # 낚시터 방향 콤보 박스 이벤트 핸들러 설정
            self.comboBoxFishingDirection.setToolTip(str('낚시터 방향')) # 낚시터 방향 콤보 박스 툴팁
        except Exception as e:
            print(e)
    
    def setCheckBox(self): # 체크 박스 설정 함수
        try:
            self.checkBoxCastnet = QtGui.QCheckBox('', self.tabFishing) # 투망 낚시 사용 여부 체크 박스 생성
            self.checkBoxCastnet.setGeometry(QtCore.QRect(225, 40, 15, 15)) # 투망 낚시 사용 여부 체크 박스 위치 및 크기 설정
            self.checkBoxCastnet.stateChanged.connect(self.setCastnet) # 투망 낚시 사용 여부 체크 박스 이벤트 핸들러 설정
            self.checkBoxCastnet.setToolTip(str('투망 낚시 사용 여부')) # 투망 낚시 사용 여부 체크 박스 툴팁
            self.checkBoxFishtrap = QtGui.QCheckBox('', self.tabFishing) # 통발 낚시 사용 여부 체크 박스 생성
            self.checkBoxFishtrap.setGeometry(QtCore.QRect(192, 130, 15, 15)) # 통발 낚시 사용 여부 체크 박스 위치 및 크기 설정
            self.checkBoxFishtrap.stateChanged.connect(self.setFishtrap) # 통발 낚시 사용 여부 체크 박스 이벤트 핸들러 설정
            self.checkBoxFishtrap.setToolTip(str('통발 낚시 사용 여부')) # 통발 낚시 사용 여부 체크 박스 툴팁
        except Exception as e:
            print(e)
    
    def setupStatusBar(self): # 상태 표시줄 설정 함수
        try:
            self.labelStatusBar = QtGui.QLabel('Wait', self.dialog) # 상태 표시줄로 사용할 레이블 생성
            self.labelStatusBar.setGeometry(QtCore.QRect(5, self.progHeight - 16, self.progWidth, 16)) # 상태 표시줄 레이블 위치 및 크기 설정
        except Exception as e:
            print(e)
    
    def selectFishingKey(self, select): # 찌낚시 스킬 키 콤보 박스 이벤트 핸들러 함수
        try:
            if select == 0:
                self.fishingKey = 'q' # 찌낚시 스킬 키 저장
            elif select == 1:
                self.fishingKey = 'w'
            elif select == 2:
                self.fishingKey = 'e'
            elif select == 3:
                self.fishingKey = 'r'
            elif select == 4:
                self.fishingKey = 'a'
            elif select == 5:
                self.fishingKey = 's'
            elif select == 6:
                self.fishingKey = 'd'
            elif select == 7:
                self.fishingKey = 'f'
        except Exception as e:
            print(e)
    
    def selectCastnetKey(self, select):  # 투망 낚시 스킬 키 콤보 박스 이벤트 핸들러 함수
        try:
            if select == 0:
                self.castnetKey = 'q' # 투망 낚시 스킬 키 저장
            elif select == 1:
                self.castnetKey = 'w'
            elif select == 2:
                self.castnetKey = 'e'
            elif select == 3:
                self.castnetKey = 'r'
            elif select == 4:
                self.castnetKey = 'a'
            elif select == 5:
                self.castnetKey = 's'
            elif select == 6:
                self.castnetKey = 'd'
            elif select == 7:
                self.castnetKey = 'f'
        except Exception as e:
            print(e)
    
    def selectFishingDirection(self, select): # 낚시터 방향 콤보 박스 이벤트 핸들러 함수
        try:
            self.fishingDirection = select # 낚시터 방향 저장
        except Exception as e:
            print(e)
    
    def setCastnet(self): # 투망 낚시 사용 여부 체크 박스 이벤트 핸들러 함수
        try:
            if self.checkBoxCastnet.isChecked() == True: # 투망 낚시 사용 여부 체크 박스가 체크되어 있을 경우
                self.comboBoxCastnetKey.setEnabled(True) # 투망 낚시 스킬 키 콤보 박스 활성화
            else: # 투망 낚시 사용 여부 체크 박스가 체크되어 있지 않을 경우
                self.comboBoxCastnetKey.setDisabled(True) # 투망 낚시 스킬 키 콤보 박스 비활성화
        except Exception as e:
            print(e)
    
    def setFishtrap(self): # 통발 낚시 사용 여부 체크 박스 이벤트 핸들러 함수
        try:
            if self.checkBoxFishtrap.isChecked() == True: # 통발 낚시 사용 여부 체크 박스가 체크되어 있을 경우
                self.lineEditFishtrapWaitTime.setEnabled(True) # 통발 설치 및 회수 대기 시간 에디트 활성화
            else: # 통발 낚시 사용 여부 체크 박스가 체크되어 있지 않을 경우
                self.lineEditFishtrapWaitTime.setDisabled(True) # 통발 설치 및 회수 대기 시간 에디트 비활성화
        except Exception as e:
            print(e)
    
    def keyList(self): # 키 목록 확인 이벤트 핸들러 함수
        try:
            QtGui.QMessageBox.information(self.dialog, 'Key List', 'a  b  c  d  e  f  g  h  i  j  k  l  m  n  o  p  q  r  s  t  u  v  w  x  y  z\n0  1  2  3  4  5  6  7  8  9\nf1  f2  f3  f4  f5  f6  f7  f8  f9  f10  f11  f12\n=  ,  -  .  /  `  [  \\  ]  \'\nctrl  shift  alt  space  tab  capslock  esc  windows  enter  backspace\nleft  up  right  down    ins  del  pgup  pgdown  end  home  numlock\nscrolllock  printscreen  hanguel  hanja') # 키 목록 메시지 박스
        except Exception as e:
            print(e)
    
    def setupMethod(self): # 파일 설정 방법 확인 이벤트 핸들러 함수
        try:
            QtGui.QMessageBox.information(self.dialog, 'Setup Method', str('1. 각 동작들은 한 줄에 입력\n2. 각 줄의 맨 앞은 핫키로 지정. 핫키 구분자는 콜론(:)\n3. 동작 종류 입력 후 딜레이 시간(초)을 입력하되 공백으로 구분\nex) q 입력하고 0.5초 후에 w 입력하는 동작을 핫키 ctrl로 설정\n-> ctrl: q 0.5 w\nex) f 3초간 입력 후 딜레이 없이 f1 입력하는 동작을 핫키 shift로 설정\n-> shift: f^3 0 f1')) # 파일 설정 방법 메시지 박스
        except Exception as e:
            print(e)
    
    def setupFile(self): # 설정 파일에서 설정 정보 가져오는 함수
        try:
            self.actives = [] # 설정 파일의 내용이 저장될 리스트 초기화
            fileName = QtGui.QFileDialog.getOpenFileName(self.dialog) # 설정 파일 오픈
            hotkeyList = [] # 핫키 리스트
            content = '' # 설정 내용
            with open(fileName, 'r') as fp:
                for line in fp.readlines():
                    if line == '': # 해당 라인이 공백일 경우(설정된 내용이 없을 경우)
                        continue
                    line = line.lower().strip() # 해당 라인 저장
                    if ':' not in line.split(' ')[0]: # 핫키가 있는 첫 번째 위치에 핫키 구분자(:)가 없을 경우
                        continue
                    if len([vk for vk in myMacro.virtual_key if vk[0] == line.split(' ')[0].split(':')[0]]) != 1: # 핫키를 올바르게 설정하지 않았을 경우
                        continue
                    if len([hotkey for hotkey in hotkeyList if hotkey == line.split(' ')[0].split(':')[0]]) != 0: # 중복된 핫키가 있을 경우
                        continue
                    hotkeyList.append(line.split(' ')[0].split(':')[0]) # 핫키 추가
                    error = False # 설정 파일 문법 오류 존재 여부
                    for i in range(1, len(line.split(' '))):
                        if i % 2 == 0 and i != 1: # 딜레이 시간 위치일 경우
                            try:
                                float(line.split(' ')[i])
                            except: # 딜레이 시간 위치에 숫자가 아닌 문자가 있을 경우
                                error = True # 설정 파일 문법 오류 존재 여부 값 변경
                                break
                        elif i % 2 == 1: # 키 위치일 경우
                            if '^' in line.split(' ')[i]:
                                if 'move' == line.split(' ')[i].split('^')[0]: # 마우스 이동일 경우
                                    if ',' in line.split(' ')[i].split('^')[1]: # 마우스 이동 좌표 설정 부분에 콤마가 있을 경우
                                        try:
                                            int(line.split(' ')[i].split('^')[1].split(',')[0])
                                            int(line.split(' ')[i].split('^')[1].split(',')[1])
                                        except: # 마우스 이동 좌표가 숫자가 아닐 경우
                                            error = True # 설정 파일 문법 오류 존재 여부 값 변경
                                            break
                                    else: # 마우스 이동 좌표 설정 부분에 콤마가 없을 경우
                                        error = True # 설정 파일 문법 오류 존재 여부 값 변경
                                        break
                                else: # 지속 입력일 경우
                                    if len([vk for vk in myMacro.virtual_key if vk[0] == line.split(' ')[i].split('^')[0]]) != 1: # 지속 입력 키를 올바르게 설정하지 않았을 경우
                                        error = True # 설정 파일 문법 오류 존재 여부 값 변경
                                        break
                                    try:
                                        float(line.split(' ')[i].split('^')[1])
                                    except: # 딜레이 시간(숫자)이 있어야 할 위치에 숫자가 아닌 문자가 있을 경우
                                        error = True # 설정 파일 문법 오류 존재 여부 값 변경
                                        break
                            elif '+' in line.split(' ')[i]: # 조합 입력일 경우
                                if len([vk for vk in myMacro.virtual_key if vk[0] == line.split(' ')[i].split('+')[0] or vk[0] == line.split(' ')[i].split('+')[1]]) != 2: # 조합 입력의 두 키를 올바르게 설정하지 않았을 경우
                                    error = True # 설정 파일 문법 오류 존재 여부 값 변경
                                    break
                            else: # 단순 입력일 경우
                                if 'leftclick' == line.split(' ')[i] or 'rightclick' == line.split(' ')[i]: # 마우스 좌클릭 또는 우클릭일 경우
                                    pass
                                elif len([vk for vk in myMacro.virtual_key if vk[0] == line.split(' ')[i]]) == 1: # 단순 입력 키를 올바르게 입력했을 경우
                                    pass
                                else: # 단순 입력 키를 올바르게 입력하지 않았을 경우
                                    error = True # 설정 파일 문법 오류 존재 여부 값 변경ㄷ
                                    break
                    if error == True: # 설정 파일에 문법 오류가 존재할 경우
                        continue
                    content += line + '\n' # 설정 내용 추가
                    self.actives.append(line) # 설정 파일의 내용이 저장될 리스트에 해당 라인 추가
            if len(self.actives) != 0: # 설정이 됐을 경우
                self.labelStatusBar.setText('Setted') # 상태 표시줄 내용 갱신
            else: # 설정이 되지 않았을 경우
                self.labelStatusBar.setText('Not Setted') # 상태 표시줄 내용 갱신
            QtGui.QMessageBox.information(self.dialog, 'Setting Contents', content) # 설정 내용 메시지 박스
        except Exception as e:
            self.labelStatusBar.setText('Not Setted') # 상태 표시줄 내용 갱신
            print(e)
    
    def macroExit(self): # 매크로 종료 함수
        try:
            global actionThreadExit, restartThreadExit
            actionThreadExit = True # 매크로 동작 스레드 종료 변수 값 변경
            restartThreadExit = True # 매크로 재시작 스레드 종료 변수 값 변경
            self.start = False # 시작 버튼 눌림 여부 값 변경
            QtGui.QApplication.quit() # 종료 이벤트 발생
        except Exception as e:
            print(e)
    
    def macroPause(self): # 매크로 중지 함수
        try:
            global actionThreadExit
            if self.start == True: # 매크로가 동작 중인 경우
                actionThreadExit = True # 스레드 종료 변수 값 변경
                self.start = False # 시작 버튼 눌림 여부 값 변경
                self.btnStart.setEnabled(True) # 매크로 시작 버튼 활성화
                self.btnPause.setDisabled(True) # 매크로 중지 버튼 비활성화
                self.tabs.setEnabled(True) # 모든 탭 활성화
                self.labelStatusBar.setText('Pause') # 상태 표시줄 내용 갱신
                for vk in myMacro.virtual_key:
                    if self.pauseRestartKey == vk[0]: # 설정한 매크로 재시작 키일 경우
                        pauseRestartKeyState = win32api.GetKeyState(vk[1]) # 설정한 매크로 재시작 키 초기 입력 상태 저장
                        restartThread = threading.Thread(target=self.restartDetectThread, args=(self.pauseRestartKey, vk, pauseRestartKeyState,)) # 설정한 매크로 재시작 키 입력 감지 스레드 생성
                        restartThread.start() # 설정한 매크로 재시작 키 입력 감지 스레드 실행
                        break
        except Exception as e:
            print(e)
    
    def macroStart(self): # 매크로 시작 함수
        try:
            global actionThreadExit
            if actionThreadExit == True: # 매크로 동작 스레드 종료 변수 값이 설정된 경우(중지 후 다시 시작했을 경우)
                actionThreadExit = False # 매크로 동작 스레드 종료 변수 값 변경
            self.start = True # 시작 버튼 눌림 여부 값 변경
            self.btnStart.setDisabled(True) # 매크로 시작 버튼 비활성화
            self.btnPause.setEnabled(True) # 매크로 중지 버튼 활성화
            self.tabs.setDisabled(True) # 모든 탭 비활성화
            self.labelStatusBar.setText('Start') # 상태 표시줄 내용 갱신
            if self.tabs.currentIndex() == 0: # 스킬 매크로일 경우
                if len(self.actives) != 0: # 설정이 됐을 경우
                    self.pauseRestartKey = str(self.lineEditSkillPauseRestartKey.text()).lower() # 매크로 중지 및 재시작 키 저장
                    if [i for i in range(len(myMacro.virtual_key)) if myMacro.virtual_key[i][0] == self.pauseRestartKey] == []: # 매크로 중지 및 재시작 키를 잘못 입력했을 경우
                        self.lineEditSkillPauseRestartKey.clear() # 스킬 매크로 중지 및 재시작 키 에디트 초기화
                    for active in self.actives:
                        hotkey = active.split(' ')[0][:-1].lower() # 핫키 저장
                        if self.pauseRestartKey == hotkey: # 핫키와 설정한 중지 키가 같을 경우(겹치면 안 됨)
                            continue
                        for vk in myMacro.virtual_key:
                            if hotkey == vk[0]: # 설정한 핫키일 경우
                                hotKeyState = win32api.GetKeyState(vk[1]) # 핫키 초기 입력 상태
                                skillThread = threading.Thread(target=self.skillMacroThread, args=(vk, hotKeyState, active)) # 스킬 매크로 스레드 생성
                                skillThread.start() # 스킬 매크로 스레드 실행
                else: # 설정이 되지 않았을 경우
                    actionThreadExit = True # 스레드 종료 변수 값 변경
                    self.start = False # 시작 버튼 눌림 여부 값 변경
                    self.btnStart.setEnabled(True) # 매크로 시작 버튼 활성화
                    self.btnPause.setDisabled(True) # 매크로 중지 버튼 비활성화
                    self.tabs.setEnabled(True) # 모든 탭 활성화
                    self.labelStatusBar.setText('Need Set')
                    return
            elif self.tabs.currentIndex() == 1: # 낚시 매크로일 경우
                self.readyTime = float(self.lineEditFishingReadyTime.text()) # 매크로 동작 전 대기 시간 저장
                if self.readyTime < 3.0: # 매크로 동작 전 대기 시간이 3초 미만일 경우
                    self.readyTime = 3.0
                self.fishingWaitTime = float(self.lineEditFishingWaitTime.text()) # 찌낚시 후 다음 찌낚시까지 대기 시간 저장
                if self.fishingWaitTime < 7.0: # 찌낚시 후 다음 찌낚시까지 대기 시간이 7초 미만일 경우
                    self.fishingWaitTime = 7.0
                self.fishtrapWaitTime = float(self.lineEditFishtrapWaitTime.text()) # 통발 설치 및 회수 대기 시간 저장
                if self.fishtrapWaitTime < 4.0: # 통발 설치 및 회수 대기 시간이 4초 미만일 경우
                    self.fishtrapWaitTime = 4.0
                self.itemUsePeriod = int(self.lineEditItemUsePeriod.text()) # 낚시 도구 장착 주기 저장
                if self.itemUsePeriod < 5: # 낚시 도구 장착 주기가 30 미만일 경우
                    self.itemUsePeriod = 5
                self.pauseRestartKey = str(self.lineEditFishingPauseRestartKey.text()).lower() # 매크로 중지 및 재시작 키 저장
                if [i for i in range(len(myMacro.virtual_key)) if myMacro.virtual_key[i][0] == self.pauseRestartKey] == []: # 매크로 중지 및 재시작 키를 잘못 입력했을 경우
                    self.lineEditFishingPauseRestartKey.clear() # 낚시 매크로 중지 및 재시작 키 에디트 초기화
                fishingThread = threading.Thread(target=self.fishingMacroThread, args=()) # 낚시 매크로 스레드 생성
                fishingThread.start() # 낚시 매크로 스레드 실행
            elif self.tabs.currentIndex() == 2: # 항해 매크로일 경우
                self.readyTime = float(self.lineEditSailingReadyTime.text()) # 매크로 동작 전 대기 시간 저장
                if self.readyTime < 3.0: # 매크로 동작 전 대기 시간이 3초 미만일 경우
                    self.readyTime = 3.0
                self.turnPeriod = float(self.lineEditSailingTurnPeriod.text()) # 끌망 시 선박 회전 주기 저장
                self.repairPeriod = float(self.lineEditSailingRepairPeriod.text()) # 끌망 시 선박 내구도 수리 주기 저장
                if self.repairPeriod < 30: # 선박 내구도 수리 주기가 30초 미만일 경우
                    self.repairPeriod = 30
                elif self.repairPeriod > 300: # 선박 내구도 수리 주기가 300초 초과일 경우
                    self.repairPeriod = 300
                self.pauseRestartKey = str(self.lineEditSailingPauseRestartKey.text()).lower() # 매크로 중지 및 재시작 키 저장
                sailingThread = threading.Thread(target=self.sailingMacroThread, args=()) # 항해 매크로 스레드 생성
                sailingThread.start() # 항해 매크로 스레드 실행
            for vk in myMacro.virtual_key:
                if self.pauseRestartKey == vk[0]: # 설정한 매크로 중지 키일 경우
                    pauseRestartKeyState = win32api.GetKeyState(vk[1]) # 설정한 매크로 중지 키 초기 입력 상태 저장
                    pauseThread = threading.Thread(target=self.pauseDetectThread, args=(self.pauseRestartKey, vk, pauseRestartKeyState,)) # 설정한 매크로 중지 키 입력 감지 스레드 생성
                    pauseThread.start() # 설정한 매크로 중지 키 입력 감지 스레드 실행
                    break
        except Exception as e:
            self.labelStatusBar.setText('Error') # 상태 표시줄 내용 갱신
            print(e)
    
    def pauseDetectThread(self, key, vk, keyState): # 설정한 매크로 중지 키 입력 감지 스레드
        global actionThreadExit, sem
        while True:
            try:
                sem.acquire() # 임계영역 생성
                if actionThreadExit == True or self.start == False: # 매크로 동작 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
                    sem.release() # 임계영역 해제
                    return # 스레드 종료
                elif self.start == True: # 매크로가 동작 중인 경우
                    currentKeyState = win32api.GetKeyState(vk[1]) # 현재 키보드 입력 상태 저장
                    if currentKeyState != keyState: # 키보드 입력 상태가 변경됐을 경우
                        keyState = currentKeyState # 키보드 입력 상태 갱신
                        if keyState == -127 or keyState == -128: # 두 번 실행 방지
                            if key == self.pauseRestartKey: # 입력한 키가 설정한 매크로 중지 키일 경우
                                self.macroPause() # 매크로 중지 함수 실행
                                sem.release() # 임계영역 해제
                                return # 스레드 종료
                sem.release() # 임계영역 해제
            except Exception as e:
                sem.release() # 임계영역 해제
                pass
    
    def restartDetectThread(self, key, vk, keyState): # 설정한 매크로 재시작 키 입력 감지 스레드
        global restartThreadExit, sem
        while True:
            try:
                sem.acquire() # 임계영역 생성
                if restartThreadExit == True: # 매크로 재시작 스레드 종료 변수 값이 설정됐을 경우ㄱ
                    sem.release() # 임계영역 해제
                    return
                if self.start == True: # 버튼을 통해 매크로를 재시작한 경우
                    sem.release() # 임계영역 해제
                    return # 스레드 종료
                elif self.start == False: # 매크로가 중지 중인 경우
                    currentKeyState = win32api.GetKeyState(vk[1]) # 현재 키보드 입력 상태 저장
                    if currentKeyState != keyState: # 키보드 입력 상태가 변경됐을 경우
                        keyState = currentKeyState # 키보드 입력 상태 갱신
                        if keyState == -127 or keyState == -128: # 두 번 실행 방지
                            if key == self.pauseRestartKey: # 입력한 키가 설정한 매크로 재시작 키일 경우
                                self.btnStart.click() # Start 버튼 클릭 이벤트 발생(self.macroStart 함수를 직접 호출하지 않고 Start 버튼 클릭 이벤트를 발생시켜 self.macroStart 함수를 호출한 이유는 직접 호출 시 재귀로 인한 오류가 발생하기 때문)
                                sem.release() # 임계영역 해제
                                return # 스레드 종료
                sem.release() # 임계영역 해제
            except Exception as e:
                sem.release() # 임계영역 해제
                pass
    
    def skillMacroThread(self, vk, hotKeyState, active): # 스킬 매크로 스레드
        global actionThreadExit, sem
        while True:
            try:
                sem.acquire() # 임계영역 생성
                if actionThreadExit == True or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
                    sem.release() # 임계영역 해제
                    return # 스레드 종료
                elif self.start == True: # 매크로가 동작 중인 경우
                    currentKeyState = win32api.GetKeyState(vk[1]) # 현재 키보드 입력 상태 저장
                    if currentKeyState != hotKeyState: # 키보드 입력 상태가 변경됐을 경우
                        hotKeyState = currentKeyState # 키보드 입력 상태 갱신
                        if hotKeyState == -127 or hotKeyState == -128: # 두 번 실행 방지
                            act = active.split(' ') # 설정 파일 내용 저장
                            for i in range(1, len(act)):
                                if i % 2 == 0 and i != 1: # 딜레이 시간일 경우
                                    time.sleep(float(act[i])) # 딜레이 시간만큼 정지
                                elif i % 2 == 1 or i == 1: # 동작일 경우
                                    if 'move' in act[i]: # 마우스 이동일 경우
                                        myMacro.move_mouse_game(int(act[i].split('^')[1].split(',')[0]), int(act[i].split('^')[1].split(',')[1])) # 설정한 값만큼 마우스 이동
                                    else: # 마우스 이동이 아닐 경우
                                        if '^' in act[i]: # 지속 입력일 경우
                                            keyboard.press(act[i].split('^')[0]) # 키 눌림 상태 유지
                                            time.sleep(float(act[i].split('^')[1])) # 지속 시간만큼 대기
                                            keyboard.release(act[i].split('^')[0]) # 키 눌림 상태 해제
                                        elif '+' in act[i]: # 조합 입력일 경우
                                            keyboard.press(act[i].split('+')[0]) # 첫 번째 키 눌림 상태 유지
                                            keyboard.press(act[i].split('+')[1]) # 두 번째 키 눌림 상태 유지
                                            time.sleep(0.1) # 너무 빠른 입력으로 인한 키 입력 씹힘 방지 딜레이
                                            keyboard.release(act[i].split('+')[1]) # 두 번째 키 눌림 상태 해제
                                            keyboard.release(act[i].split('+')[0]) # 첫 번째 키 눌림 상태 해제
                                        else: # 지속 입력 및 조합 입력이 아닐 경우
                                            if 'leftclick' in act[i]: # 마우스 좌클릭일 경우
                                                myMacro.click_mouse_left(0, 0) # 마우스 좌클릭
                                            elif 'rightclick' in act[i]: # 마우스 우클릭일 경우
                                                myMacro.click_mouse_right(0, 0) # 마우스 우클릭
                                            else: # 단순 입력일 경우
                                                keyboard.press(act[i]) # 키 눌림 상태 유지
                                                time.sleep(0.1) # 너무 빠른 입력으로 인한 키 입력 씹힘 방지 딜레이
                                                keyboard.release(act[i]) # 키 눌림 상태 해제
                sem.release() # 임계영역 해제
            except Exception as e:
                sem.release() # 임계영역 해제
                pass
    
    def sailingMacroThread(self): # 항해 매크로 스레드
        try:
            global actionThreadExit, sem
            sem.acquire() # 임계영역 생성
            screenWidth = win32api.GetSystemMetrics(win32con.SM_CXSCREEN) # 윈도우 가로 크기
            screenHeight = win32api.GetSystemMetrics(win32con.SM_CYSCREEN) # 윈도우 세로 크기
            repairTemplateImage = self.getTemplateImage(LostArkBinary.sailingRepairImage) # 선박 내구도 수리 템플릿 이미지 흑백으로 저장
            repairImageWidth, repairImageHeight = Image.open(os.getcwd() + '\\TempLostArkTemplateImage.png').size[0], Image.open(os.getcwd() + '\\TempLostArkTemplateImage.png').size[1] # 선박 내구도 수리 템플릿 이미지 가로, 세로 크기 저장
            os.remove(os.getcwd() + '\\TempLostArkTemplateImage.png') # 선박 내구도 수리 템플릿 이미지 삭제
            repairNeed = False # 선박 내구도 수리 필요 유무
            time.sleep(self.readyTime) # 매크로 동작 전 대기
            myMacro.keyboardInput('e') # 끌망 스킬 활성화
            repairTime = time.time() # 선박 내구도 수리 제어 시간 초기화
            myMacro.move_mouse(screenWidth / 2 + int(screenHeight / 3.5), screenHeight / 2) # 마우스 바다로 이동
            time.sleep(0.1) # 씹힘 방지 대기 시간
            myMacro.click_mouse_down_right() # 마우스 우클릭 유지
            while True:
                if actionThreadExit == True or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
                    myMacro.click_mouse_up_right() # 마우스 우클릭 해제
                    myMacro.keyboardInput('e') # 끌망 스킬 비활성화
                    sem.release() # 임계영역 해제
                    return # 스레드 종료
                elif self.start == True: # 매크로가 동작 중인 경우
                    if win32gui.GetPixel(win32gui.GetDC(win32gui.GetDesktopWindow()), int(screenWidth / 20), screenHeight - 5) > 10000000: # 행운의 기운이 5퍼센트 초과일 경우
                        timeDifference = self.getTimeDifference(repairTime) # 선박 내구도 수리 제어 시간 차 계산
                        if timeDifference > self.repairPeriod or repairNeed == True: # 선박 내구도 수리 주기이거나 수리가 필요한 경우
                            myMacro.click_mouse_up_right() # 마우스 우클릭 해제
                            myMacro.keyboardInput('z') # 정박 모드 진입
                            time.sleep(2)
                            result, upLeftX, upLeftY = self.templateMatching(repairTemplateImage, self.transformGreyFrame(0, 0, screenWidth, screenHeight), 4)
                            if result == True: # 선박 내구도 수리 버튼을 찾았을 경우
                                repairNeed = False # 선박 내구도 수리 필요 유무 변경
                                myMacro.move_mouse(upLeftX + repairImageWidth / 2, upLeftY + repairImageHeight / 2) # 선박 내구도 수리 버튼 중앙으로 마우스 이동
                                time.sleep(0.1) # 씹힘 방지 대기 시간
                                myMacro.click_mouse_left(0, 0) # 선박 내구도 수리 버튼 클릭
                                time.sleep(1)
                                myMacro.keyboardInput('enter') # 선박 내구도 수리
                                time.sleep(1)
                                myMacro.keyboardInput('esc') # 정박 모드 탈출
                                time.sleep(3)
                                myMacro.keyboardInput('e') # 끌망 스킬 활성화
                                myMacro.move_mouse(screenWidth / 2 + int(screenHeight / 3.5), screenHeight / 2) # 마우스 바다로 이동
                                time.sleep(0.1) # 씹힘 방지 대기 시간
                                myMacro.click_mouse_down_right() # 마우스 우클릭 유지
                            else: # 선박 내구도 수리 버튼을 찾지 못했을 경우(선박 내구도 수리 가능 지역에서 벗어났을 경우)
                                repairNeed = True # 선박 내구도 수리 필요 유무 변경
                                myMacro.keyboardInput('esc') # 정박 모드 탈출
                                time.sleep(2)
                                myMacro.move_mouse(screenWidth / 2, screenHeight / 7)
                                time.sleep(0.1) # 씹힘 방지 대기 시간
                                myMacro.click_mouse_right(0, 0) # 선박 위쪽으로 이동
                                time.sleep(10)
                                myMacro.move_mouse(screenWidth / 4, screenHeight / 2)
                                time.sleep(0.1) # 씹힘 방지 대기 시간
                                myMacro.click_mouse_right(0, 0) # 선박 왼쪽으로 이동
                                time.sleep(5)
                            repairTime = time.time() # 선박 내구도 수리 제어 시간 초기화
                        else: # 선박 내구도 수리 주기가 아닐 경우
                            for i in range(0, 360): # 360도 회전
                                x = int(screenHeight / 3.5) * math.cos(math.pi * i / 180) # 회전할 x좌표
                                y = int(screenHeight / 3.5) * math.sin(math.pi * i / 180) # 회전할 y좌표
                                myMacro.move_mouse(screenWidth / 2 + x, screenHeight / 2 + y) # 회전할 좌표로 마우스 이동
                                time.sleep(self.turnPeriod) # 선박 회전 주기만큼 대기
                    else: # 행운의 기운이 5퍼센트 이하일 경우
                        self.macroPause()
                        time.sleep(3)
        except Exception as e:
            sem.release() # 임계영역 해제
            print(e)
    
    def fishingMacroThread(self): # 낚시 매크로 스레드
        try:
            global actionThreadExit, fishtrapTime, sem
            sem.acquire() # 임계영역 생성
            screenWidth = win32api.GetSystemMetrics(win32con.SM_CXSCREEN) # 윈도우 가로 크기
            screenHeight = win32api.GetSystemMetrics(win32con.SM_CYSCREEN) # 윈도우 세로 크기
            detectTemplateImage = self.getTemplateImage(LostArkBinary.fishingDetectImage) # 물고기가 찌를 물었을 때 나오는 아이콘 템플릿 이미지 흑백으로 저장
            os.remove(os.getcwd() + '\\TempLostArkTemplateImage.png') # 물고기가 찌를 물었을 때 나오는 아이콘 템플릿 이미지 파일 삭제
            itemTemplateImage = self.getTemplateImage(LostArkBinary.fishingItemImage) # 낚시 도구 템플릿 이미지 흑백으로 저장
            itemImageWidth, itemImageHeight = Image.open(os.getcwd() + '\\TempLostArkTemplateImage.png').size[0], Image.open(os.getcwd() + '\\TempLostArkTemplateImage.png').size[1] # 낚시 도구 템플릿 이미지 가로, 세로 크기 저장
            os.remove(os.getcwd() + '\\TempLostArkTemplateImage.png') # 낚시 도구 템플릿 이미지 삭제
            skillTemplateImage = self.getTemplateImage(LostArkBinary.fishingSkillImage) # 낚시 스킬 템플릿 이미지 흑백으로 저장
            os.remove(os.getcwd() + '\\TempLostArkTemplateImage.png') # 낚시 스킬 템플릿 이미지  삭제
            buffTemplateImage = self.getTemplateImage(LostArkBinary.buffImage) # 짜릿한 손맛 3버프 템플릿 이미지 흑백으로 저장
            os.remove(os.getcwd() + '\\TempLostArkTemplateImage.png') # 짜릿한 손맛 3버프 템플릿 이미지 삭제
            perfectTemplateImage = self.getTemplateImage(LostArkBinary.perfectImage) # 투망 낚시 PERFECT 템플릿 이미지 흑백으로 저장
            os.remove(os.getcwd() + '\\TempLostArkTemplateImage.png') # 짜릿한 손맛 3버프 템플릿 이미지 삭제
            centerLeftX, centerUpY, centerRightX, centerDownY = (screenWidth / 2) / 6.83, (screenWidth / 2) / 6.83, (screenHeight / 2) / 3.84, (screenHeight / 2) / 7.68 # 화면 중앙을 기준으로 하는 낚시 범위
            targetRectangle = [int(screenWidth / 2 - centerLeftX), int(screenHeight / 2 - centerUpY), int(screenWidth / 2 + centerRightX), int(screenHeight / 2 + centerDownY)] # 낚시 범위 박스
            completionCount = 0 # 낚시 완료 횟수(실패 및 오탐 포함)
            fishingCount, castnetCount, fishtrapCount = 0, 0, 0 # 찌낚시, 투망 낚시, 통발 낚시 완료 횟수(실패 및 오탑 포함)
            baseTime = 0 # 낚시 흐름 제어 시간
            fishingAction = False # 찌낚시 동작 여부 확인 변수
            fishingDirectionList = [ # 낚시터 방향
                [int(screenWidth / 2), 0], # 12시
                [screenWidth, 0], # 1시 반
                [screenWidth, int(screenHeight / 2)], # 3시
                [screenWidth, screenHeight], # 4시 반
                [int(screenWidth / 2), screenHeight], # 6시
                [0, screenHeight], # 7시 반
                [0, int(screenHeight / 2)], # 9시
                [0, 0] # 10시 반
            ]
            # cv2.imshow('Test', np.array(ImageGrab.grab(bbox=(targetRectangle[0], targetRectangle[1], targetRectangle[2], targetRectangle[3])))) # Test
            time.sleep(self.readyTime) # 매크로 동작 전 대기
            if actionThreadExit == True or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
                sem.release() # 임계영역 해제
                return # 스레드 종료
            if self.checkBoxFishtrap.isChecked() == True: # 통발 낚시 사용 여부 체크 박스가 체크되어 있을 경우
                if fishtrapTime == 0: # 통발 낚시 제어 시간이 설정되지 않았을 경우(통발이 설치되지 않았을 경우)
                    fishtrapTime = self.fishtrapFishing(True) # 통발 설치
            if self.templateMatching(skillTemplateImage, self.transformGreyFrame(0, 0, screenWidth, screenHeight), 4)[0] == False: # 생활 스킬창으로 전환된 상태가 아닐 경우
                myMacro.keyboardInput('b') # 스킬 전환 키 입력
            if fishingAction == False: # 찌낚시 동작 중이지 않은 경우
                baseTime = self.fishing(fishingDirectionList) # 낚시 시작
                fishingAction = True # 찌낚시 동작 여부 확인 변수 값 변경
            while True:
                if actionThreadExit == True or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
                    break # 스레드 종료
                elif self.start == True: # 매크로가 동작 중인 경우
                    # screenFrame = ImageGrab.grab(bbox=(targetRectangle[0], targetRectangle[1], targetRectangle[2], targetRectangle[3])) # Test
                    # frame = np.array(screenFrame) # Test
                    timeDifference = self.getTimeDifference(baseTime) # 낚시 흐름 제어 시간 차 계산
                    # 찌낚시 실패했을 경우
                    if timeDifference > 30: # 30초 동안 낚시를 진행하지 않았을 경우(찌낚시는 30초 안에 끝나야 정상)
                        completionCount += 1 # 낚시 완료 횟수 증가
                        if completionCount % self.itemUsePeriod == 0: # 낚시 도구 장착 타이밍일 경우
                            self.useItem(itemTemplateImage, screenWidth, screenHeight, itemImageWidth, itemImageHeight) # 낚시 도구 장착
                        if self.checkBoxFishtrap.isChecked() == True: # 통발 낚시 사용 여부 체크 박스가 체크되어 있을 경우
                            if self.getTimeDifference(fishtrapTime) > 300: # 통발을 설치한 후 5분이 지났을 경우
                                fishtrapTime = self.fishtrapFishing(False) # 통발 회수
                                fishtrapCount += 1 # 통발 낚시 완료 횟수 증가
                                self.labelStatusBar.setText('Fishing : ' + str(fishingCount) + '   Castnet : ' + str(castnetCount) + '   Fishtrap : ' + str(fishtrapCount)) # 상태 표시줄 내용 갱신
                                time.sleep(self.fishtrapWaitTime) # 통발을 설치할 수 있을 때까지 대기
                                if actionThreadExit == True or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
                                    break # 스레드 종료
                                fishtrapTime = self.fishtrapFishing(True) # 통발 재설치
                        if actionThreadExit == True or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
                            break # 스레드 종료
                        baseTime = self.fishing(fishingDirectionList) # 낚시 재개
                        fishingAction = True # 찌낚시 동작 여부 확인 변수 값 변경
                    # 찌낚시 성공했을 경우
                    if fishingAction == False: # 찌낚시 동작 중이지 않은 경우
                        completionCount += 1 # 낚시 완료 횟수 증가
                        if completionCount % self.itemUsePeriod == 0: # 낚시 도구 장착 타이밍일 경우
                            self.useItem(itemTemplateImage, screenWidth, screenHeight, itemImageWidth, itemImageHeight) # 낚시 도구 장착
                        if self.checkBoxFishtrap.isChecked() == True: # 통발 낚시 사용 여부 체크 박스가 체크되어 있을 경우
                            if self.getTimeDifference(fishtrapTime) > 300: # 통발을 설치한 후 5분이 지났을 경우
                                fishtrapTime = self.fishtrapFishing(False) # 통발 회수
                                fishtrapCount += 1 # 통발 낚시 완료 횟수 증가
                                self.labelStatusBar.setText('Fishing : ' + str(fishingCount) + '   Castnet : ' + str(castnetCount) + '   Fishtrap : ' + str(fishtrapCount)) # 상태 표시줄 내용 갱신
                                time.sleep(self.fishtrapWaitTime) # 통발을 설치할 수 있을 때까지 대기
                                if actionThreadExit == True or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
                                    break # 스레드 종료
                                fishtrapTime = self.fishtrapFishing(True) # 통발 재설치
                        if actionThreadExit == True or self.start == False: # 스레드 종료 변수 값이 설정됐거나 매크로를 중지한 경우
                            break # 스레드 종료
                        baseTime = self.fishing(fishingDirectionList) # 낚시 재개
                        fishingAction = True # 찌낚시 동작 여부 확인 변수 값 변경
                    else: # 찌낚시 동작 중인 경우
                        if timeDifference < 5: # 낚시를 시작한 지 5초가 안됐을 경우(템플릿 매칭 오탐으로 인한 실패 방지)
                            pass
                        else:
                            if self.templateMatching(detectTemplateImage, self.transformGreyFrame(targetRectangle[0], targetRectangle[1], targetRectangle[2], targetRectangle[3]), 5)[0] == True: # 물고기가 찌를 물었을 때 나오는 아이콘을 탐지했을 경우
                                myMacro.keyboardInput(self.fishingKey) # 찌낚시 스킬 사용
                                fishingAction = False # 찌낚시 동작 여부 확인 변수 값 변경
                                completionCount += 1 # 낚시 완료 횟수 증가
                                fishingCount += 1 # 찌낚시 완료 횟수 증가
                                time.sleep(self.fishingWaitTime) # 다음 낚시까지 대기
                                if self.checkBoxCastnet.isChecked() == True: # 투망 낚시 사용 여부 체크 박스가 체크되어 있을 경우
                                    if self.templateMatching(buffTemplateImage, self.transformGreyFrame(0, 0, screenWidth, screenHeight), 4)[0] == True: # 짜릿한 손맛 3버프 아이콘을 탐지했을 경우
                                        self.castnetFishing(perfectTemplateImage, screenWidth, screenHeight) # 투망 낚시
                                        castnetCount += 1 # 통발 낚시 완료 횟수 증가
                                        time.sleep(5) # 투망 회수할 때까지 대기
                                self.labelStatusBar.setText('Fishing : ' + str(fishingCount) + '   Castnet : ' + str(castnetCount) + '   Fishtrap : ' + str(fishtrapCount)) # 상태 표시줄 내용 갱신
                                baseTime = time.time() # 낚시 흐름 제어 시간 설정
                    # cv2.rectangle(frame, (targetRectangle[0], targetRectangle[1]), (targetRectangle[2], targetRectangle[3]), (255, 255, 0), 2) # Test
                    # cv2.imshow('Test', frame) # Test
                    if cv2.waitKey(1) & 0xFF == 27: # ESC 입력 시 종료
                        break
            sem.release() # 임계영역 해제
            cv2.destroyAllWindows()
        except Exception as e:
            sem.release() # 임계영역 해제
            print(e)
    
    def getTemplateImage(self, binary): # 템플릿 이미지 반환 함수
        try:
            with open(os.getcwd() + '\\TempLostArkTemplateImage.png', 'wb') as fp:
                fp.write(binary) # 템플릿 이미지 파일 생성
            return cv2.imread(os.getcwd() + '\\TempLostArkTemplateImage.png', cv2.IMREAD_GRAYSCALE) # 템플릿 이미지 흑백으로 변환 후 반환
        except Exception as e:
            print(e)
    
    def getTimeDifference(self, baseTime): # 낚시 흐름 제어 시간 차 계산 함수
        try:
            return int(time.time() - baseTime) # 낚시 흐름 제어 시간 차 반환
        except Exception as e:
            print(e)
    
    def transformGreyFrame(self, startPosX, startPosY, endPosX, endPosY): # 프레임 흑백 변환 함수
        try:
            screenFrame = ImageGrab.grab(bbox=(startPosX, startPosY, endPosX, endPosY)) # 윈도우 프레임
            frame = np.array(screenFrame) # 프레임
            return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # 프레임 흑백 변환 후 반환
        except Exception as e:
            print(e)
    
    def useItem(self, itemTemplateImage, screenWidth, screenHeight, itemImageWidth, itemImageHeight): # 낚시 도구 장착 함수
        try:
            myMacro.keyboardInput('i') # 인벤토리 키 입력
            time.sleep(3) # 인벤토리가 열릴 때까지 대기
            result, upLeftX, upLeftY = self.templateMatching(itemTemplateImage, self.transformGreyFrame(0, 0, screenWidth, screenHeight), 3)
            if result == True: # 낚시 도구를 탐지했을 경우
                myMacro.move_mouse(upLeftX + int(itemImageWidth / 2), upLeftY + int(itemImageHeight / 2)) # 낚시 도구로 마우스 이동
                time.sleep(0.1) # 씹힘 방지 대기 시간
                myMacro.click_mouse_right(0, 0) # 낚시 도구 장착
        except Exception as e:
            print(e)
    
    def fishing(self, fishingDirectionList): # 찌낚시 스킬 사용 함수
        try:
            myMacro.move_mouse(fishingDirectionList[self.fishingDirection][0], fishingDirectionList[self.fishingDirection][1]) # 낚시터 방향으로 마우스 이동
            myMacro.keyboardInput(self.fishingKey) # 찌낚시 스킬 키 입력
            return time.time() # 초기화된 낚시 흐름 제어 시간 반환
        except Exception as e:
            print(e)
    
    def fishtrapFishing(self, method): # 통발 낚시 스킬 사용 함수
        try:
            myMacro.keyboardInput('g') # 통발 낚시 스킬 키 입력
            time.sleep(self.fishtrapWaitTime) # 통발 설치 또는 회수하는 동안 대기
            if method == True: # 통발 설치인 경우
                return time.time() # 초기화된 통발 낚시 제어 시간 반환
            else: # 통발 회수인 경우
                return 0 # 낚시 제어 시간 초기값 반환
        except Exception as e:
            print(e)
    
    def castnetFishing(self, perfectTemplateImage, screenWidth, screenHeight): # 투망 낚시 함수
        try:
            myMacro.keyboardInput(self.castnetKey) # 투망 낚시 스킬 키 입력
            time.sleep(5) # 투망 낚시 미니게임이 시작될 때까지 대기
            spaceMax = 5 # 스페이스 키를 연속해서 입력 가능한 최대 횟수
            spaceWaitTime = 0.2 # 스페이스 키 입력 대기 시간
            perfect = False # PERFECT 이미지 탐지 여부
            spaceCount = 0 # 스페이스 키 입력 횟수
            castnetTime = time.time() # 투망 낚시 제어 시간 설정
            while True:
                if perfect == True: # PERFECT 이미지를 탐지한 상태일 경우
                    if spaceCount < spaceMax: # 스페이스 키 연속 입력 횟수가 4번 미만일 경우
                        myMacro.keyboardInput('space') # 스페이스 키 입력
                        time.sleep(spaceWaitTime) # 스페이스 키 입력 후 대기
                        spaceCount += 1 # 스페이스 키 입력 횟수 증가
                    else: # 스페이스 키 연속 입력 횟수가 4번 이상일 경우
                        perfect = False # PERFECT 이미지 탐지 여부 변경
                        spaceCount = 0 # 스페이스 키 입력 횟수 초기화
                if perfect == False and self.templateMatching(perfectTemplateImage, self.transformGreyFrame(0, 0, int(screenWidth / 2), int(screenHeight / 2)), 4)[0] == True: # PERFECT 이미지를 탐지했을 경우
                    perfect = True # PERFECT 이미지 탐지 여부 변경
                if self.getTimeDifference(castnetTime) > 7: # 투망 낚시 미니게임 시작 후 7초가 지났을 경우
                    break
        except Exception as e:
            print(e)
    
    def templateMatching(self, templateImage, targetFrame, minCount): # 템플릿 매칭 함수
        try:
            methods = ['cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED'] # 템플릿 매칭 방법(비교 연산 방법으로 결과값의 최댓값을 취할지 최솟값을 취할지를 결정하는데 cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED는 최솟값을 그 이외는 최댓값을 취함)
            detectedCoords = [] # 템플릿 매칭 성공 좌표들이 저장될 리스트
            duplicationCoords = [] # 좌표 중복 여부 확인 변수들이 저장될 리스트
            for method in methods:
                method = eval(method) # 템플릿 매칭 방법 설정
                try:
                    res = cv2.matchTemplate(templateImage, targetFrame, method) # 템플릿 이미지와 템플릿 매칭 범위 프레임 비교
                    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(res) # 템플릿 매칭 성공 시 위치 최솟값 및 최댓값 저장
                except:
                    continue
                if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]: # 템플릿 매칭 방법이 cv2.TM_SQDIFF 또는 cv2.TM_SQDIFF_NORMED일 경우
                    upLeft = minLoc # 위치 최솟값을 좌측 상단으로 설정
                else: # 그 이외의 템플릿 매칭 방법일 경우
                    upLeft = maxLoc # 위치 최댓값을 좌측 상단으로 설정
                detectedCoords.append(upLeft) # 리스트에 좌측 상단 좌표 추가
            for i in range(len(detectedCoords)): # 매칭된 이미지의 좌측 상단 좌표 수만큼 반복
                duplicationCoords.append(detectedCoords.count(detectedCoords[i])) # 리스트에 중복된 좌표의 개수 추가
            try:
                if max(duplicationCoords) >= minCount: # 설정한 개수 이상의 템플릿 매칭 방법으로 같은 좌표를 탐지했을 경우
                    for i in range(len(detectedCoords)): # 매칭된 이미지의 좌측 상단 좌표 수만큼 반복
                        if max(duplicationCoords) == detectedCoords.count(detectedCoords[i]): # 현재 좌표가 가장 많이 중복된 좌표일 경우
                            return True, detectedCoords[i][0], detectedCoords[i][1] # 성공 여부 및 좌표 반환
                else:
                    return False, None, None # 실패 여부 반환
            except Exception as e:
                return False, None, None # 실패 여부 반환
        except Exception as e:
            print(e)

def main():
    try:
        app = QtGui.QApplication(sys.argv)
        dialog = QtGui.QDialog() # 다이얼로그 생성
        obj = MainClass(dialog) # 객체 생성
        dialog.show() # 윈도우 출력
        os.remove(os.getcwd() + '\\TempLostArkIcon.png') # 아이콘 이미지 파일 삭제
        sys.exit(app.exec_()) # 종료 이벤트 발생 시 프로그램 종료
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()