#-*- coding: utf-8 -*-
import os
import sys
import time
import win32api
import win32con
import win32gui
import threading
from ctypes import windll
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import myMacro
import icoBinary

sem = threading.Semaphore(1) # 세마포어 설정
exit_var = False # 스레드 종료 변수

class MacroClass(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.actives = [] # 설정 파일의 내용이 저장될 리스트
        self.start = False # 시작 버튼 눌림 여부
        self.pause = 'F12' # 중지 키(디폴트 F12)
        self.size_x = 470 # 프로그램의 가로 크기
        self.size_y = 400 # 프로그램의 세로 크기
        self.pos_x = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)/2 - self.size_x/2 # 처음 프로그램이 나타나는 x좌표(중앙으로 설정)
        self.pos_y = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)/2 - self.size_y/2 # 처음 프로그램이 나타나는 y좌표(중앙으로 설정)
        self.setupWindow() # 윈도우 설정
        self.setupButton() # 버튼 설정
        self.setupLabel() # 레이블 설정
        self.setupEdit() # 에디트 설정
        self.setupStatusBar() # 상태바 설정
        self.setFixedSize(self.size_x, self.size_y) # 화면 크기 변경 금지
    
    def setupWindow(self): # 윈도우 특성 설정 함수
        title = 'TERA Macro Program' # 타이틀
        self.setWindowTitle(title) # 윈도우 타이클 설정
        self.setGeometry(self.pos_x, self.pos_y, self.size_x, self.size_y) # 윈도우 위치,크기 설정
        ico_binary = icoBinary.title_ico_binary_tera # 타이틀 아이콘 바이너리
        fp = open(os.getcwd() + '\\tmp_title.ico', 'wb') # 임시 아이콘 파일 생성
        fp.write(ico_binary)
        fp.close()
        self.setWindowIcon(QIcon(os.getcwd() + '\\tmp_title.ico')) # 타이틀 아이콘 설정
        
    def setupButton(self): # 버튼 설정 함수
        btnFile = QPushButton('File Open', self) # 설정 파일 오픈 버튼
        btnFile.resize(btnFile.sizeHint() * 1.25) # 버튼 크기
        btnFile.move(10, self.size_y - 60) # 버튼 위치
        btnFile.clicked.connect(self.setup_file) # 설정 파일에서 설정 정보 가져오는 함수
        btnStart = QPushButton('Start', self) # 매크로 시작 버튼
        btnStart.resize(btnStart.sizeHint() * 1.25)
        btnStart.move(self.size_x/3.7, self.size_y - 60)
        btnStart.clicked.connect(self.start_thread) # 매크로 동작 함수
        btnPause = QPushButton('Pause', self) # 매크로 중지 버튼
        btnPause.resize(btnPause.sizeHint() * 1.25)
        btnPause.move(self.size_x/1.9, self.size_y - 60)
        btnPause.clicked.connect(self.pause_thread) # 매크로 중지 함수
        btnExit = QPushButton('Exit', self) # 매크로 종료 버튼
        btnExit.resize(btnExit.sizeHint() * 1.25)
        btnExit.move(self.size_x - 105, self.size_y - 60)
        btnExit.clicked.connect(QCoreApplication.instance().quit) # 종료

    def setupLabel(self): # 레이블 설정 함수
        title = 'TERA Macro  ver 1.0 by.KHW' # 제목
        self.label = QLabel(title, self) # 제목 설정
        self.label.move(self.size_x/3, 10) # 레이블 위치
        self.label.resize(170, 15) # 레이블 크기
        content = unicode('[동작 종류]\n1. 키보드 입력 : 단순 입력, 지속 입력\nex) f1 입력 -> f1\nex) w 5.5초간 입력 -> w^5.5\n\n2. 마우스 입력 : 좌클릭, 우클릭, 휠클릭, 지속 클릭, 화면 이동\nex) 좌클릭 -> leftclick, 우클릭 -> rightclick, 휠클릭 -> wheelclick\nex) 5초간 좌클릭 -> leftclick^5\nex) 500 픽셀만큼 오른쪽으로 화면 이동 -> move^500,0\nex) 300 픽셀만큼 왼쪽으로 화면 이동 -> move^-300,0\nex) 100 픽셀만큼 아래로 화면 이동 -> move^0,100\nex) 200 픽셀만큼 위로 화면 이동 -> move^0,-200\nex) x,y 픽셀만큼 화면 이동 -> move^x,y\n\n[파일 구성 방법]\n1. 각 동작들은 한 줄에 입력\n2. 각 줄의 맨 앞은 핫키로 지정(핫키 구분자는 :(콜론))\n3. 동작 종류 입력 후 딜레이 시간(초)를 입력하되 공백으로 구분\n4. 딜레이 시간 입력을 생략하면 안되므로 딜레이 시간이 불필요할 경우 0으로 입력\nex) a 입력되고 0.5초 후에 b 입력하는 동작을 핫키 f1로 설정 -> f1: a 0.5 b\nex) 1 입력 후에 딜레이 없이 2 입력하는 동작을 핫키 shift로 설정  -> shift: 1 0 2\n', 'utf-8') # 내용
        self.label = QLabel(content, self) # 내용 설정
        self.label.move(10, 35)
        self.label.resize(450, 310)

    def setupEdit(self): # 에디트 설정 함수
        lineEditLabel = QLabel('Pause : ', self) # 중지 키 설정 레이블
        lineEditLabel.move(self.size_x - 120, 35)
        lineEditLabel.resize(50, 15)
        self.lineEdit = QLineEdit(self.pause, self) # 에디트 설정(초기 내용 입력)
        self.lineEdit.move(self.size_x - 65, 32) # 에디트 위치
        self.lineEdit.resize(50, 20) # 에디트 크기

    def setupStatusBar(self): # 상태표시줄 설정 함수
        self.statusBar = QStatusBar(self) # 상태 표시줄 설정
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('Not Set') # 초기 상태 표시줄 내용

    def setup_file(self): # 설정 파일에서 설정 정보 가져오는 함수
        if self.start: # 매크로가 동작중인 경우
            return
        fname = QFileDialog.getOpenFileName(self) # 설정 파일 오픈
        content = '' # 설정 파일 내용이 저장될 변수
        tmp_line_hotkey = [] # 핫키가 있는 첫번째 위치의 내용이 저장될 리스트(핫키 중복 예방)
        duplication = False # 중복 여부
        fp = open(fname)
        active = fp.readlines() # 설정 파일 한 라인씩 저장
        fp.close()
        self.actives = [] # 설정 파일의 내용이 저장될 리스트 초기화
        for line in active: # 설정 파일 한 라인씩 반복
            line_hotkey = line.split(' ')[0] # 해당 라인을 공백으로 구분 후 핫키가 있는 첫번째 위치 저장
            if line == '': # 해당 라인이 공백일 경우(설정된 내용이 없을 경우)
                continue
            if ':' not in line_hotkey: # 핫키가 있는 첫번째 위치에 핫키 구분자(콜론)가 없을 경우
                continue
            for hotkey in tmp_line_hotkey: # 중복된 핫키가 있는지 확인
                if line_hotkey == hotkey: # 중복된 핫키가 있을 경우
                    duplication = True # 중복 여부 값 변경
                    break
            if duplication: # 핫키가 중복됐을 경우
                duplication = False # 중복 여부 값 초기화
                continue
            self.actives.append(line.lower().strip()) # 설정 파일의 내용이 저장될 리스트에 해당 라인 추가
            content += line # 설정 파일 내용 추가
            tmp_line_hotkey.append(line_hotkey) # 임시 리스트에 핫키가 있는 첫번째 위치 추가
        self.label.clear() # 레이블 클리어
        self.label.move(10, 35)
        self.label.resize(450, 300)
        self.label.setText('Setup File Contents\n\n' + content) # 설정 파일 내용으로 레이블 갱신
        self.statusBar.showMessage('Set') # 상태 표시줄 내용 갱신

    def pause_thread(self): # 매크로 중지 함수
        global exit_var
        if self.start: # 매크로가 동작중인 경우
            exit_var = True # 스레드 종료 변수 값 설정
            self.start = False # 시작 버튼 눌림 여부 값 변경
            self.statusBar.showMessage('Pause') # 상태 표시줄 내용 갱신
        else: # 매크로가 동작하기 전이거나, 이미 매크로가 중지된 경우
            self.statusBar.showMessage('Already Pause') # 상태 표시줄 내용 갱신

    def start_thread(self): # 매크로 동작 함수
        global exit_var
        if len(self.actives) == 0: # 아직 설정되지 않은 상태일 경우
            self.statusBar.showMessage('Need Set') # 상태 표시줄 내용 갱신
            return
        if self.start: # 이미 매크로가 동작중인 경우
            self.statusBar.showMessage('Already Start') # 상태 표시줄 내용 갱신
            return
        if exit_var: # 스레드 종료 변수 값이 설정된 경우(중지 후 다시 시작했을 경우)
            exit_var = False # 스레드 종료 변수 값 초기화
        self.pause = str(self.lineEdit.text()) # 설정한 중지 키 저장
        self.pause = self.pause.lower() # 설정한 중지 키 소문자 변환
        duplication = False # 핫키와 중지 키 중복 여부
        for active in self.actives:
            hotkey = active.split(' ')[0] # 공백으로 구분 후 핫키가 있는 첫번째 위치 저장
            hotkey = hotkey[:-1].lower() # 핫키 구분자(콜론) 제거해서 순수히 핫키만 저장, 핫키 소문자 변환
            if self.pause == hotkey: # 핫키와 설정한 중지 키가 같을 경우(겹치면 안됨)
                duplication = True # 중복 여부 값 변경
            for vk in myMacro.virtual_key:
                if hotkey == vk[0]: # 설정한 핫키일 경우
                    key_state = win32api.GetKeyState(vk[1]) # 핫키 초기 입력 상태
                    th = threading.Thread(target=self.detect_key_state_thread, args=(hotkey, active, vk, key_state,)) # 핫키 입력 감지 스레드 설정
                    th.start() # 스레드 생성
        if duplication: # 핫키 중에서 설정한 중지 키와 같은 키가 있을 경우(겹치면 안됨)
            self.pause = 'None' # 중지 키 비활성화
            self.lineEdit.clear() # 에디트 클리어
            self.lineEdit.setText(self.pause) # 에디트 비활성화 상태로 설정
        else: # 핫키 중에서 설정한 중지 키와 같은 키가 없을 경우(안겹치므로 설정한 중지 키 입력 감지 스레드 구성)
            for vk in myMacro.virtual_key:
                if self.pause == vk[0]: # 설정한 중지 키일 경우
                    key_state_pause = win32api.GetKeyState(vk[1]) # 설정한 중지 키 초기 입력 상태
                    th_pause = threading.Thread(target=self.detect_key_state_thread, args=(self.pause, active, vk, key_state_pause,)) # 설정한 중지 키 입력 감지 스레드 설정
                    th_pause.start() # 스레드 생성
        self.start = True # 시작 버튼 눌림 여부 값 변경
        self.statusBar.showMessage('Start') # 상태 표시줄 내용 갱신
    
    def detect_key_state_thread(self, key, active, vk, key_state): # 키보드 입력 감지 스레드
        global exit_var
        while True:
            sem.acquire() # 임계영역 생성
            if exit_var: # 스레드 종료 변수 값이 설정됐을 경우
                sem.release() # 임계영역 해제
                return # 스레드 종료
            cur_key_state = win32api.GetKeyState(vk[1]) # 현재 키보드 입력 상태
            if cur_key_state != key_state: # 키보드 입력 상태가 변경됐을 경우
                key_state = cur_key_state # 키보드 입력 상태 갱신
                if key_state == -127 or key_state == -128: # 두번 실행 방지
                    act = active.split(' ') # 설정 파일 내용 저장
                    if key == self.pause: # 입력한 키가 설정한 중지 키일 경우
                        exit_var = True # 스레드 종료 변수 값 설정
                        self.start = False # 시작 버튼 눌림 여부 값 변경
                        self.statusBar.showMessage('Pause') # 상태 표시줄 내용 갱신
                        sem.release() # 임계영역 해제
                        return # 스레드 종료
                    for i in range(0, len(act)): # 설정 파일
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
                                if '^' in act[i]: # 지속 입력 및 클릭일 경우
                                    continue_time = act[i].split('^')[1] # 지속 시간 저장
                                    if 'leftclick' in act[i]: # 마우스 지속 좌클릭일 경우
                                        myMacro.click_mouse_down_left() # 마우스 좌클릭 상태 유지
                                        time.sleep(float(continue_time)) # 지속 시간만큼 대기
                                        myMacro.click_mouse_up_left() # 마우스 좌클릭 상태 해제
                                    elif 'rightclick' in act[i]: # 마우스 지속 우클릭일 경우
                                        myMacro.click_mouse_down_right() # 마우스 우클릭 상태 유지
                                        time.sleep(float(continue_time)) # 지속 시간만큼 대기
                                        myMacro.click_mouse_up_right() # 마우스 우클릭 상태 해제
                                    elif 'wheelclick' in act[i]: # 마우스 지속 휠클릭일 경우
                                        myMacro.click_mouse_down_wheel() # 마우스 휠클릭 상태 유지
                                        time.sleep(float(continue_time)) # 지속 시간만큼 대기
                                        myMacro.click_mouse_up_wheel() # 마우스 휠클릭 상태 해제
                                    else: # 키보드 지속 입력일 경우
                                        input_key = act[i].split('^')[0] # 입력 키 저장
                                        myMacro.input_down_keyboard(input_key) # 입력 키 눌림 상태 유지
                                        time.sleep(float(continue_time)) # 지속 시간만큼 대기
                                        myMacro.input_up_keyboard(input_key)# 입력 키 눌림 상태 해제
                                else: # 지속 입력 및 클릭이 아닐 경우
                                    if 'leftclick' in act[i]: # 마우스 좌클릭일 경우
                                        myMacro.click_mouse_left(0,0) # 마우스 좌클릭
                                    elif 'rightclick' in act[i]: # 마우스 우클릭일 경우
                                        myMacro.click_mouse_right(0,0) # 마우스 우클릭
                                    elif 'wheelclick' in act[i]: # 마우스 휠클릭일 경우
                                        myMacro.click_mouse_wheel() # 마우스 휠클릭
                                    else: # 키보드 입력일 경우
                                        myMacro.input_keyboard(act[i]) # 키보드 입력
            sem.release() # 임계영역 해제

def main():
    app = QApplication(sys.argv)
    gui = MacroClass() # 객체 생성
    gui.show() # 윈도우 화면에 표시
    os.remove(os.getcwd() + '\\tmp_title.ico') # 임시 아이콘 파일 삭제
    sys.exit(app.exec_()) # 종료 이벤트 발생 시 프로그램 종료
 
if __name__ == '__main__':
    main()
