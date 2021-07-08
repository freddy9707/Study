# -*- coding: utf-8 -*-

INF = 9876543210
totalCount, partyCount = 16, 4 # 공격대원 수, 공격대에 존재할 수 있는 파티 수
fireteam = {'워로드':0, # 슈샤이어
            '버서커':1,
      '디스트로이어':0,
        '홀리나이트':2,
              '바드':2, # 로헨델
            '서머너':1,
          '아르카나':0,
          '호크아이':1, # 아르데타인
          '데빌헌터':1,
          '블래스터':0,
          '스카우터':1,
            '기공사':1, # 애니츠
        '배틀마스터':2,
          '인파이터':0,
            '창술사':0,
          '블레이드':3, # 페이튼
            '데모닉':1
    }
synergy = [['바드','홀리나이트','워로드'], # 서포터
           ['버서커','데모닉','호크아이','인파이터'], # 받는피해증가
           ['데빌헌터','아르카나'], # 치명타적중률증가
           ['워로드','블래스터','서머너','디스트로이어'], # 방어력감소
           ['기공사','스카우터'], # 공격력증가
           ['블레이드','워로드'], # 백어택증가
           ['창술사','배틀마스터'], # 치명타저항감소
           ['인파이터','블래스터','디스트로이어'] # 무력화증가
    ] # 시너지가 여러개인 직업이 존재함. 이 경우 같은 파티에 같은 시너지 클래스군이 배정될 수 있음

def networkflow(start, end):
    answer = 0
    while True:
        queue, path = [start], [-1]*v # 다음에 방문할 정점들, 방문 경로
        while queue:
            present = queue[0] # 현재 정점
            del queue[0]
            if present not in path:
                for _next in adj[present]:
                    # 흐를 수 있고, 다음 정점이 방문하지 않은 정점일 경우
                    if capacity[present][_next] - flow[present][_next] > 0 and path[_next] == -1:
                        queue.append(_next)
                        path[_next] = present
                        if _next == end: # 다음 방문할 정점이 도착지일 경우
                            break
        if path[end] == -1: # 가능한 모든 경로를 찾았을 경우
            break
        # print('\n', path) # 디버깅 코드
        flowRate = INF # 현재 경로에서의 최소 유량
        present = end
        while present != start:
            previous = path[present]
            flowRate = min(flowRate, capacity[previous][present] - flow[previous][present])
            present = path[present]
        present = end
        p, c = None, None # 파티, 클래스
        while present != start:
            previous = path[present]
            # print(previous, present) # 디버깅 코드
            if p == None:
                p = previous
            c = present
            flow[previous][present] += flowRate
            flow[present][previous] -= flowRate # 음의 유량
            present = path[present]
        # print(p, c) # 디버깅 코드
        party[p-(n+m+1)].append(fireteamList[c-1]) # 파티에 공격대원 배치
        # show() # 디버깅 코드
        fireteam[fireteamList[c-1]] -= 1 # 배치가 끝난 공격대원 수 감소
        answer += flowRate
    return answer

def show():
    for i in range(partyCount):
        print(str(i+1) + '파티:', party[i])
    print()

'''
# 공격대원 랜덤으로 구성 후 테스트
def test():
    import random
    a = 0
    while a != 16:
        for k, v in fireteam.items():
            if random.random() > 0.5:
                fireteam[k] += 1
                a += 1
                if a == 16:
                    break
test() # 디버깅 코드
'''

party = [[] for _ in range(partyCount)] # 공격대에 존재하는 파티
count = 0
for k, v in fireteam.items():
    count += v
if count < totalCount:
    print('공격대인원부족')
elif count > totalCount:
    print('공격대인원초과')
else:
    if fireteam['바드']+fireteam['홀리나이트'] >= partyCount: # 서폿의 수가 충분할 경우
        synergy[0].remove('워로드') # 워로드를 서폿에서 제외
    fireteamList = [] # 공격대원(클래스)을 나열한 리스트
    for k, v in fireteam.items():
        for _ in range(v):
            fireteamList.append(k)
    print('\n공격대 클래스 현황')
    for k, v in fireteam.items():
        if v != 0:
            print(k + ': ' + str(v))
    n, m, k = totalCount, len(synergy), partyCount # 공격대원 수, 시너지 수, 공격대에 존재할 수 있는 파티 수
    v = n+m+k+2 # 정점 수
    capacity = [[0]*v for _ in range(v)] # 용량
    flow = [[0]*v for _ in range(v)] # 유량
    adj = [[] for _ in range(v)] # 연결된 정점(source + 공격대원(16) + 시너지(8) + 파티(4) + sink)
    for _n in range(1, n+1): # source와 공격대원 매칭
        adj[0].append(_n)
        adj[_n].append(0)
        capacity[0][_n] = 1
    for _n in range(1, n+1): # 공격대원과 시너지 매칭
        for _m in range(n+1, n+m+1):
            if fireteamList[_n-1] in synergy[_m-(n+1)]:
                adj[_n].append(_m)
                adj[_m].append(_n)
                capacity[_n][_m] = 1
    for _m in range(n+1, n+m+1): # 시너지와 파티 매칭
        if adj[_m]:
            for _k in range(n+m+1, n+m+k+1):
                adj[_m].append(_k)
                adj[_k].append(_m)
                capacity[_m][_k] = 1
    for _k in range(n+m+1, v-1): # 파티와 sink 매칭
        adj[_k].append(v-1)
        adj[v-1].append(_k)
        capacity[_k][v-1] = totalCount
    print('\n겹치지 않는 시너지로 구성된 파티(시너지가 겹치는 클래스가 많거나 여러 시너지를 가진 클래스가 있을 경우 시너지 겹칠 수 있음)')
    max_flow = networkflow(0, v-1) # 최대 유량(파티에 배정된 클래스의 수)
    # print(max_flow) # 디버깅 코드
    show()
    print('시너지 겹침이 불가피한 경우 클래스는 겹치지 않게 구성된 파티')
    party.sort(key=len, reverse=True)
    while True:
        confirm = True
        for i in range(partyCount):
            if len(party[i]) > 4:
                for j in range(i+1, partyCount):
                    if len(party[j]) < 4:
                        for k in range(len(party[i])):
                            if party[i][k] == '바드' or party[i][k] == '홀리나이트' or (party[i][k] == '워로드' and '바드' not in party[i] and '홀리나이트' not in party[i]):
                                continue
                            if len(party[j]) == 0:
                                party[j].append(party[i][k])
                                party[i].remove(party[i][k])
                                confirm = False
                                break
                            else:
                                confirm2 = True
                                for li in synergy:
                                    if party[i][k] in li:
                                        for l in range(len(party[j])):
                                            if party[j][l] in li:
                                                confirm2 = False
                                                break
                                if confirm2:
                                    party[j].append(party[i][k])
                                    party[i].remove(party[i][k])
                                    confirm = False
                                    break
                        if not confirm:
                            break
                if not confirm:
                    break
        if confirm:
            break
    show()
    print('시너지와 클래스 겹침이 불가피한 경우의 파티')
    party.sort(key=len, reverse=True)
    while True:
        confirm = True
        for i in range(partyCount):
            if len(party[i]) > 4:
                for j in range(i+1, partyCount):
                    if len(party[j]) < 4:
                        for k in range(len(party[i])):
                            if party[i][k] == '바드' or party[i][k] == '홀리나이트' or (party[i][k] == '워로드' and '바드' not in party[i] and '홀리나이트' not in party[i]):
                                continue
                            party[j].append(party[i][k])
                            party[i].remove(party[i][k])
                            confirm = False
                            break
                        if not confirm:
                            break
                if not confirm:
                    break
        if confirm:
            break
    while sum([len(party[i]) for i in range(partyCount)]) != totalCount:
        for k, v in fireteam.items():
            if v != 0:
                for i in range(partyCount):
                    if len(party[i]) < 4:
                        party[i].append(k)
                        fireteam[k] -= 1
                        if fireteam[k] == 0:
                            break
    # show() # 디버깅 코드
    while True:
        confirm = True
        for i in range(partyCount):
            if len(set(party[i])) < 4:
                confirm = False
                idx = None
                for j in range(4):
                    if party[i].count(party[i][j]) > 1:
                        idx = j
                        break
                confirm2 = True
                for j in range(i+1, partyCount):
                    for k in range(len(party[j])):
                        for li in synergy:
                            if party[j][k] in li and party[i][idx] in li and party[j][k] not in party[i]:
                                party[j][k], party[i][idx] = party[i][idx], party[j][k]
                                confirm2 = False
                                break
                        if not confirm2:
                            break
                    if not confirm2:
                        break
                if not confirm2:
                    break
                for j in range(i-1, -1, -1):
                    for k in range(len(party[j])):
                        for li in synergy:
                            if party[j][k] in li and party[i][idx] in li and party[j][k] not in party[i]:
                                party[j][k], party[i][idx] = party[i][idx], party[j][k]
                                confirm2 = False
                                break
                        if not confirm2:
                            break
                    if not confirm2:
                        break
                break
        if confirm:
            break
    show()
