# -*- coding: utf-8 -*-
import time
import ctypes
import myMacro

def	autoServerStart(first_wait_time, server_file, vmware_name, server_start_wait_time, tomcat8_service_restart, guacd_service_restart): # 서버 구동 함수
	time.sleep(first_wait_time) # 로그인 후 안정화 될 때가지 대기
	ctypes.windll.shell32.ShellExecuteA(0, 'open', server_file, None, None, 1) # vmware 실행
	while True:
		state, prog_pos_x, prog_pos_y, prog_size_x, prog_size_y = myMacro.get_program_pos_size_include_maximum(vmware_name) # vmware의 위치 및 크기 저장
		if state: # vmware의 위치 및 크기를 제대로 찾았을 경우
			myMacro.move_mouse(prog_pos_x + prog_size_x/2, prog_pos_y + prog_size_y/2) # vmware 화면 중앙으로 마우스 이동
			myMacro.click_mouse_left(0,0) # vmware 화면 중앙 좌클릭
			time.sleep(0.1)
			myMacro.keyboardInput_combination('ctrl', 'b') # 가상머신 구동 단축키 입력
			time.sleep(server_start_wait_time) # 서버 켜질 때까지 대기
			break
	while True:
		state, prog_pos_x, prog_pos_y, prog_size_x, prog_size_y = myMacro.get_program_pos_size_include_maximum(vmware_name) # vmware의 위치 및 크기 저장
		if state: # vmware의 위치 및 크기를 제대로 찾았을 경우
			myMacro.move_mouse(prog_pos_x + prog_size_x/2, prog_pos_y + prog_size_y/2) # vmware 화면 중앙으로 마우스 이동
			myMacro.click_mouse_left(0,0) # vmware 화면 중앙 좌클릭
			time.sleep(0.1)
			# 아이디 입력
			myMacro.keyboardInput('r')
			myMacro.keyboardInput('o')
			myMacro.keyboardInput('o')
			myMacro.keyboardInput('t')
			myMacro.keyboardInput('enter')
			time.sleep(1.5)
			# 패스워드 입력
			myMacro.keyboardInput('x')
			myMacro.keyboardInput('x')
			myMacro.keyboardInput('x')
			myMacro.keyboardInput('x')
			myMacro.keyboardInput('x')
			myMacro.keyboardInput('x')
			myMacro.keyboardInput('x')
			myMacro.keyboardInput_combination('shift', '2')
			myMacro.keyboardInput('enter')
			time.sleep(5)
			# 톰캣 서비스 재시작
			for c in tomcat8_service_restart:
				myMacro.keyboardInput(c)
			myMacro.keyboardInput('enter')
			time.sleep(10)
			# 과카몰리 서비스 재시작
			for c in guacd_service_restart:
				myMacro.keyboardInput(c)
			myMacro.keyboardInput('enter')
			return

def main():
	first_wait_time = 20 # 윈도우 로그인 후 처음 대기 시간
	server_file = 'D:\\Vmware\\Guacamole\\Guacamole.vmx' # vmware 파일
	vmware_name = 'Guacamole - VMware Workstation' # 가상머신 이름
	server_start_wait_time = 60 # 서버 켜질 때까지의 대기 시간
	tomcat8_service_restart = 'service tomcat8 restart' # 톰캣 서비스 재시작
	guacd_service_restart = 'service guacd restart' # 과카몰리 서비스 재시작
	autoServerStart(first_wait_time, server_file, vmware_name, server_start_wait_time, tomcat8_service_restart, guacd_service_restart) # 서버 구동 함수 실행

if __name__ == '__main__':
	main()