# -*- coding:utf-8 -*-
import os
import struct
import zlib

# -------------------------------------------------------------------------
# get_hwp_recoard(val)
# 입력된 4Byte 값을 HWP 레코드 구조에 맞게 변환하여 추출한다.
# 입력값 : val - DWORD
# 리턴값 : tag_id, level, size
# -------------------------------------------------------------------------
def get_hwp_recoard(val): # 레코드 헤더에서 각종 정보를 추출하는 함수
    b = 0b1111111111
    c = 0b111111111111
    tag_id = (val & b)
    level = ((val >> 10) & b)
    size = (val >> 20) & c
    return tag_id, level, size

# -------------------------------------------------------------------------
# scan_hwp_recoard(buf, lenbuf)
# 주어진 버퍼를 HWP 레코드 구조로 해석한다.
# 입력값 : buf    - 버퍼
#         lenbuf - 버퍼 크기
# 리턴값 : True or False (HWP 레코드 추적 성공 여부)
# -------------------------------------------------------------------------
def scan_hwp_recoard(buf, lenbuf): # BodyText/Section 버퍼 전체에 대해 레코드를 추적해서 결과를 반환하는 함수
    pos = 0
    while pos < lenbuf:
        extra_size = 4
        val = struct.unpack('<L', buf[pos:pos+4])[0]
        tagid, level, size = get_hwp_recoard(val)
        if size == 0xfff:
            extra_size = 8
            size = struct.unpack('<L', buf[pos+4:pos+4+4])[0]
        pos += (size + extra_size)
    if pos == lenbuf:
        return True
    return False

class KavMain:
    # ---------------------------------------------------------------------
    # init(self, plugins_path)
    # 플러그인 엔진을 초기화 한다.
    # 입력값 : plugins_path - 플러그인 엔진의 위치
    # 리턴값 : 0 - 성공, 0 이외의 값 - 실패
    # ---------------------------------------------------------------------
    def init(self, plugins_path):
        self.virus_name = 'Exploit.HWP.Generic' # 진단/치료하는 악성코드 이름
        return 0 # 플러그인 엔진 초기화 성공

    # ---------------------------------------------------------------------
    # listvirus(self)
    # 진단/치료 가능한 악성코드의 리스트를 알려준다.
    # 리턴값 : 악성코드 리스트
    # ---------------------------------------------------------------------   
    def listvirus(self):
        vlist = list()
        vlist.append(self.virus_name) # 진단/치료하는 악성코드 이름 등록
        return vlist

    # ---------------------------------------------------------------------
    # scan(self, filehandle, filename, fileformat, filename_ex)
    # 악성코드를 검사한다.
    # 입력값 : filehandle  - 파일 핸들
    #         filename    - 파일 이름
    #         fileformat  - 파일 포맷
    #         filename_ex - 파일 이름 (압축 내부 파일 이름)
    # 리턴값 : 악성코드 발견 여부, 악성코드 이름, 악성코드 ID
    # ---------------------------------------------------------------------
    def scan(self, filehandle, filename, fileformat, filename_ex):
        mm = filehandle
        if filename_ex.lower().find('bodytext/section') >= 0: # 악성코드 검사 대상이 BodyText/Section 일 경우
            buf = mm[:]
            try:
                buf = zlib.decompress(buf, -15) # 압축 해제
            except zlib.error:
                pass
            if scan_hwp_recoard(buf, len(buf)) is False: # 압축 해제된 버퍼에 대해 레코드 추적에 실패했을 경우
                return True, self.virus_name, 0 # 악성코드를 발견했음을 반환
        return False, '', -1 # 악성코드를 발견하지 못했음을 반환

    # ---------------------------------------------------------------------
    # disinfect(self, filename, malware_id)
    # 악성코드를 치료한다.
    # 입력값 : filename   - 파일 이름
    #         malware_id - 치료할 악성코드 ID
    # 리턴값 : 악성코드 치료 여부
    # ---------------------------------------------------------------------
    def disinfect(self, filename, malware_id):
        try:
            if malware_id == 0: # 악성코드 진단 결과에서 받은 ID 값이 0일 경우
                os.remove(filename) # 파일 삭제
                return True # 치료 완료 반환
        except IOError:
            pass
        return False # 치료 실패 반환

    # ---------------------------------------------------------------------
    # getinfo(self)
    # 플러그인 엔진의 주요 정보를 알려준다. (제작자, 버전, ...)
    # 리턴값 : 플러그인 엔진 정보
    # ---------------------------------------------------------------------
    def getinfo(self):
        info = dict()
        info['author'] = 'MINE' # 제작자
        info['version'] = '1.0' # 버전
        info['title'] = 'HWP Engine' # 엔진 설명
        info['kmd_name'] = 'hwp' # 엔진 파일 이름
        info['sig_num'] = 1 # 진단/치료 가능한 악성코드 수
        return info

    # ---------------------------------------------------------------------
    # uninit(self)
    # 플러그인 엔진을 종료한다.
    # 리턴값 : 0 - 성공, 0 이외의 값 - 실패
    # ---------------------------------------------------------------------
    def uninit(self):
        return 0 # 플러그인 엔진 종료 성공
