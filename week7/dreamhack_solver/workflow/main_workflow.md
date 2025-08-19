# CTF 자동화 메인 워크플로우 v2.0

## 초기 제공 정보
- **target_url**: 공격 대상 웹 서비스 URL
- **project_path**: 문제 파일이 있는 로컬 경로

## 전역 제약사항
- 최대 실행 시간: 90분
- 최대 재시도: 단계별 제한 (Step1: 5회, Step2: 30회, Step3: 3회)
- 플래그 파일 직접 읽기 금지 (flag.txt, answer.txt 등)
- 플래그는 반드시 원격 익스플로잇으로만 획득

## 사용 가능한 도구
1. **dreamhack_solver:trivy** - CVE 취약점 스캔
2. **dreamhack_solver:curl** - HTTP 요청
3. **dreamhack_solver:execute_command** - 시스템 명령 실행

## 필수 행동 규칙
1. **관찰 우선**: 공격 전 시스템 동작 패턴 파악
2. **실패 분석**: 각 실패 후 에러 메시지 분석 및 학습
3. **한 번에 한 가지**: 변수는 한 번에 하나씩만 변경
4. **정보 재사용**: 한 번 얻은 정보는 변수에 저장하여 재사용
5. **조기 중단**: 동일 에러 3회 반복 시 해당 방법 포기

## 워크플로우 실행 순서

```mermaid
graph TD
    Start[사용자 입력 수신] --> Step1[Step 1: 종합 정찰] 시작 대기
    Step1 --> Step2[Step 2: 통합 익스플로잇] 시작 대기
    
    Step2 --> Module_Decision{모듈 선택}
    Module_Decision -->|CVE 발견| Step2a[2a: CVE 익스플로잇]
    Module_Decision -->|웹앱 확인| Step2b[2b: 웹 공격]
    Module_Decision -->|실패 누적| Step2c[2c: 고급 기법]
    
    Step2a --> Step3[Step 3: 검증]
    Step2b --> Step3
    Step2c --> Step3
    
    Step3 -->|플래그 확인| Success[성공 보고]
    Step3 -->|검증 실패| Failure[실패 보고]
```

## 컨텍스트 관리 시스템

### 정보 누적 구조
```python
class CTFContext:
    def __init__(self):
        self.recon_data = {}        # Step1 수집 정보
        self.tested_payloads = {}   # 시도한 페이로드
        self.successful_patterns = [] # 성공 패턴
        self.failed_attempts = []    # 실패 기록
        self.discovered_info = {
            'endpoints': [],
            'parameters': [],
            'technologies': [],
            'vulnerabilities': []
        }
    
    def carry_forward(self, step):
        """다음 단계로 핵심 정보 전달"""
        return self.get_essential_for_step(step)
```

## 단계별 체크포인트

### Step 1 (정찰) 완료 조건
- [ ] Trivy 스캔 완료 또는 스킵 결정
- [ ] 파일 구조 분석 완료
- [ ] 엔드포인트 매핑 완료
- [ ] 공격 우선순위 결정
- [ ] attack_plan 생성

### Step 2 (익스플로잇) 완료 조건
- [ ] 우선순위별 공격 시도
- [ ] 각 실패 분석 및 학습
- [ ] 성공 또는 모든 벡터 소진
- [ ] 플래그 획득 또는 최종 실패 확정

### Step 3 (검증) 완료 조건
- [ ] 플래그 형식 검증
- [ ] 최종 보고서 생성
- [ ] 클린업 완료

## 상태 코드 정의
- **SUCCESS**: 플래그 획득 성공
- **FAILURE**: 명확한 실패
- **IN_PROGRESS**: 진행 중
- **PARTIAL**: 부분적 성공 (추가 작업 필요)

## 출력 형식

### 각 단계 출력
```json
{
  "step": "current_step_number",
  "status": "STATUS_CODE",
  "action_taken": "실행한 구체적 행동",
  "result": "결과 요약",
  "learned": "실패에서 배운 점",
  "next_action": "다음 계획"
}
```

### Step 간 정보 전달
```json
{
  "from_step": "1_reconnaissance",
  "to_step": "2_exploitation",
  "essential_data": {
    "attack_vectors": [...],
    "priority_order": [...],
    "key_findings": {...}
  }
}
```

### 최종 성공 출력
```json
{
  "workflow_status": "COMPLETED_SUCCESS",
  "flag": "flag{...}",
  "summary": {
    "vulnerability": "exploited_vulnerability_type",
    "method": "attack_method_used",
    "key_insight": "critical_discovery",
    "attempts": "total_attempts_count"
  }
}
```

### 최종 실패 출력
```json
{
  "workflow_status": "COMPLETED_FAILURE",
  "reason": "주요 실패 원인",
  "attempts_summary": ["시도한 방법들"],
  "partial_successes": ["부분 성공 내역"],
  "recommendations": ["추가 시도 제안"]
}
```

## 효율성 원칙

### 도구 사용 최적화
```python
# 파일 읽기 캐싱
file_cache = {}
def read_file(path):
    if path not in file_cache:
        file_cache[path] = execute_command(f"cat {path}")
    return file_cache[path]

# curl 세션 재사용
session_cookies = {}
def curl_with_session(url, **kwargs):
    if 'cookies' not in kwargs:
        kwargs['cookies'] = session_cookies.get(url, {})
    response = curl(url, **kwargs)
    # 쿠키 업데이트 로직
    return response
```

### 실패 패턴 인식
```python
failure_patterns = {}
def should_stop_trying(method, error):
    if method not in failure_patterns:
        failure_patterns[method] = []
    
    failure_patterns[method].append(error)
    
    # 동일 에러 3회 반복
    if failure_patterns[method][-3:].count(error) >= 3:
        return True
    
    # 명확한 실패 신호
    if any(signal in error for signal in STOP_SIGNALS):
        return True
    
    return False
```

## 핵심 원칙

1. **자동 실행**: 입력 받으면 즉시 Step1 시작
2. **적응적 진행**: 각 단계 결과에 따라 경로 조정
3. **학습 기반**: 실패에서 배우고 다음 시도 개선
4. **투명성**: 모든 과정과 사고를 기록
5. **효율성**: 중복 제거, 캐싱 활용

## 비상 탈출 조건

다음 상황 발생 시 즉시 종료:
- 플래그 발견 및 검증 완료
- 90분 시간 초과
- 사용자의 명시적 중단 요청
- 모든 공격 벡터 소진

## 디버깅 모드

문제 발생 시 다음 정보 수집:
- 마지막 성공한 명령
- 현재 단계와 상태
- 수집된 모든 정보
- 시도한 모든 페이로드
- 에러 패턴 분석

## 사용 예시

```bash
# 사용자 입력
target_url: http://ctf.example.com:8080
project_path: /home/user/ctf_challenge

# 자동 실행 시작
→ Step 1: 종합 정찰 시작...
→ Step 2: 익스플로잇 전략 선택...
→ Step 3: 플래그 검증...
→ 최종 결과 출력
```
