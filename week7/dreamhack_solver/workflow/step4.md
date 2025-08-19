# Step 4: 플래그 검증 및 최종 처리

## 목표
획득한 문자열이 실제 플래그인지 검증하고 최종 결과 보고

## 플래그 검증 프로세스

### 4.1 형식 검증

#### 표준 플래그 패턴
```regex
^(flag|FLAG|CTF|DH)\{[A-Za-z0-9_\-!@#$%^&*()+=]{8,64}\}$
```

#### 검증 코드
```python
import re

def validate_flag(potential_flag):
    patterns = [
        r'^flag\{[A-Za-z0-9_\-!@#$%^&*()+=]{8,64}\}$',
        r'^FLAG\{[A-Za-z0-9_\-!@#$%^&*()+=]{8,64}\}$',
        r'^CTF\{[A-Za-z0-9_\-!@#$%^&*()+=]{8,64}\}$',
        r'^DH\{[A-Za-z0-9_\-!@#$%^&*()+=]{8,64}\}$'
    ]
    
    for pattern in patterns:
        if re.match(pattern, potential_flag):
            return True
    return False
```

### 4.2 플래그 추출 전략

#### 응답에서 플래그 찾기
```bash
# 다양한 플래그 형식 검색
dreamhack_solver:execute_command(
    command='''
    echo "{response_text}" | grep -oE "(flag|FLAG|CTF|DH)\{[A-Za-z0-9_\-!@#$%^&*()+=]{8,64}\}"
    '''
)
```

#### 부분 플래그 조합
```python
# 여러 조각으로 나뉜 플래그 처리
parts = []
if "flag_part1" in response:
    parts.append(extract_part(response, "part1"))
if "flag_part2" in response:
    parts.append(extract_part(response, "part2"))
    
complete_flag = "".join(parts)
```

### 4.3 엣지 케이스 처리

#### 인코딩된 플래그
```python
# Base64 디코딩
import base64
decoded = base64.b64decode(encoded_string)

# Hex 디코딩
decoded = bytes.fromhex(hex_string).decode()

# URL 디코딩
from urllib.parse import unquote
decoded = unquote(url_encoded)
```

#### 숨겨진 플래그
```bash
# HTML 주석 확인
dreamhack_solver:execute_command(
    command="echo '{html_response}' | grep '<!--.*flag.*-->'"
)

# JavaScript 변수 확인
dreamhack_solver:execute_command(
    command="echo '{js_code}' | grep 'var.*flag\\|const.*flag\\|let.*flag'"
)
```

## 최종 보고서 생성

### 성공 케이스
```json
{
  "workflow_status": "COMPLETED_SUCCESS",
  "flag": "flag{captured_flag_here}",
  "solving_methodology": {
    "vulnerability_exploited": "SQL Injection",
    "attack_vector": "/api/login endpoint",
    "key_payload": "' OR 1=1--",
    "steps_to_reproduce": [
      "1. Identified login endpoint from source code",
      "2. Tested SQL injection vulnerability",
      "3. Bypassed authentication",
      "4. Retrieved flag from admin panel"
    ]
  },
  "execution_metrics": {
    "total_time_seconds": 287,
    "attempts": 12,
    "tools_used": ["trivy", "curl", "execute_command"],
    "critical_discovery": "Unescaped user input in SQL query"
  },
  "learning_points": [
    "Always check for SQL injection in login forms",
    "Source code review reveals vulnerable endpoints"
  ]
}
```

### 실패 케이스
```json
{
  "workflow_status": "COMPLETED_FAILURE",
  "failure_analysis": {
    "primary_reason": "Unable to find exploitable vulnerability",
    "attempted_strategies": [
      "SQL Injection - All inputs properly sanitized",
      "Command Injection - Commands not executed",
      "Path Traversal - File access restricted",
      "SSTI - Template engine not vulnerable"
    ],
    "potential_blockers": [
      "WAF presence detected",
      "Strong input validation",
      "Updated dependencies without known CVEs"
    ]
  },
  "partial_findings": {
    "information_gathered": [
      "Server: Node.js Express",
      "Interesting endpoints: /api/*, /admin",
      "Potential username: 'ctfadmin'"
    ],
    "suspicious_behaviors": [
      "Unusual delay on /api/verify",
      "Different error message for admin user"
    ]
  },
  "recommendations": [
    "Try timing-based blind attacks",
    "Investigate authentication token generation",
    "Check for race conditions",
    "Review client-side JavaScript for hardcoded values"
  ],
  "execution_metrics": {
    "total_time_seconds": 1432,
    "total_attempts": 67,
    "endpoints_tested": 15,
    "payloads_tried": 45
  }
}
```

## 후처리 작업

### 클린업
```bash
# 생성된 임시 파일 정리
dreamhack_solver:execute_command(
    command="rm -f /tmp/exploit.* /tmp/response.*"
)
```

### 로그 정리
```python
# 중요 발견사항 요약
key_findings = {
    "vulnerable_endpoint": endpoint,
    "successful_payload": payload,
    "response_indicators": ["flag found", "admin access"],
    "timestamp": current_time
}
```

## 특수 상황 처리

### 플래그는 있지만 형식이 다른 경우
```json
{
  "workflow_status": "COMPLETED_UNCERTAIN",
  "potential_flag": "found_string_that_might_be_flag",
  "validation_failed_reason": "Does not match standard flag format",
  "confidence": "medium",
  "suggestion": "Manual review recommended"
}
```

### 다중 플래그 발견
```json
{
  "workflow_status": "COMPLETED_MULTIPLE",
  "flags_found": [
    "flag{primary_flag}",
    "flag{bonus_flag}"
  ],
  "context": {
    "primary": "Found via SQL injection",
    "bonus": "Found in HTML comment"
  }
}
```

## 체크리스트

### 최종 검증 사항
- [ ] 플래그 형식이 올바른가?
- [ ] 플래그가 완전한가? (일부만 획득하지 않았는가?)
- [ ] 재현 가능한 방법인가?
- [ ] 모든 시도가 문서화되었는가?
- [ ] 클린업이 완료되었는가?

## 중요 원칙

1. **절대 포기하지 않기**: 실패도 가치있는 정보
2. **투명한 보고**: 성공과 실패 모두 상세히 기록
3. **학습 지향**: 각 시도에서 배운 점 도출
4. **완전성**: 부분적 성공도 의미있게 보고
