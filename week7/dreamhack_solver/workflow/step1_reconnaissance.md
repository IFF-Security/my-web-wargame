# Step 1: 종합 정찰 및 분석

## 목표
모든 가능한 공격 벡터를 파악하고 우선순위화된 공격 계획 수립

## 입력
- **target_url**: 공격 대상 URL
- **project_path**: 문제 파일이 있는 로컬 경로

## 실행 프로세스

### 1.1 의존성 취약점 스캔

#### 실행
```bash
dreamhack_solver:trivy(path="{project_path}")
```

#### CVE 발견 시 상세 분석
```python
def analyze_cve_details(cve_list):
    """CVE 설명을 정독하고 핵심 정보 추출"""
    for cve in cve_list:
        print(f"[분석] {cve.id}")
        print(f"  설명: {cve.description}")
        print(f"  영향: {cve.affected_component}")
        print(f"  버전: {cve.affected_versions}")
        
        # 핵심: CVE 설명에서 취약 함수/옵션 식별
        vulnerable_function = extract_function(cve.description)
        attack_condition = extract_condition(cve.description)
        
    return prioritized_cves
```

#### 결과 처리
- CVE 발견: 상세 정보를 attack_vectors에 추가
- CVE 없음: 다른 공격 벡터에 집중
- 경로 오류: 원격 전용 모드로 전환

### 1.2 파일 구조 및 코드 분석

#### 프로젝트 구조 파악
```bash
# 한 번에 필요한 정보 모두 수집 (효율성)
dreamhack_solver:execute_command(
    command="""
    echo "=== 프로젝트 구조 ===" && \
    find {project_path} -type f \( -name "*.js" -o -name "*.py" -o -name "*.php" \) | head -20 && \
    echo "=== 패키지 정보 ===" && \
    cat {project_path}/package.json 2>/dev/null || cat {project_path}/requirements.txt 2>/dev/null && \
    echo "=== 라우팅 정보 ===" && \
    grep -r "app\.\(get\|post\|put\|delete\)\|router\." {project_path} --include="*.js" | head -20 && \
    echo "=== 플래그 힌트 ===" && \
    grep -r "flag\|FLAG\|secret\|SECRET" {project_path} --include="*.js" --include="*.py" 2>/dev/null | head -10
    """
)
```

#### 핵심 코드 분석
```python
# CVE와 코드 연결 (중요!)
def verify_cve_in_code(cve_info, project_path):
    """CVE 설명에서 추출한 취약 함수/옵션이 실제 코드에 있는지 확인"""
    
    # CVE 설명에서 취약한 부분 추출
    vulnerable_keywords = extract_keywords_from_cve(cve_info.description)
    # 예: "res.render", "template option", 특정 함수명 등
    
    for keyword in vulnerable_keywords:
        # 해당 키워드가 실제로 사용되는지 확인
        result = dreamhack_solver:execute_command(
            command=f"grep -r '{keyword}' {project_path} --include='*.js' --include='*.py'"
        )
        if result:
            print(f"[확인] CVE 관련 코드 발견: {keyword}")
            analyze_usage_context(result)
    
    return findings
```

### 1.3 원격 시스템 정찰

#### 초기 응답 패턴 수집 (관찰 우선)
```python
# 기본 응답 수집
responses = {}
responses['root'] = dreamhack_solver:curl(target_url, method="GET")
responses['404'] = dreamhack_solver:curl(f"{target_url}/nonexistent", method="GET")

# 응답 패턴 분석
tech_stack = identify_technology(responses)
error_format = analyze_error_format(responses['404'])
```

#### 엔드포인트 매핑
```python
# 소스 코드에서 발견한 엔드포인트 확인
discovered_endpoints = extract_from_source()
for endpoint in discovered_endpoints:
    response = dreamhack_solver:curl(f"{target_url}{endpoint}", method="GET")
    analyze_endpoint(endpoint, response)
```

### 1.4 공격 벡터 우선순위 결정

#### 우선순위 매트릭스
```python
def prioritize_attack_vectors(recon_data):
    vectors = []
    
    # 1순위: CVE with RCE
    if recon_data.cve_list:
        for cve in recon_data.cve_list:
            if 'RCE' in cve.impact or 'command' in cve.description.lower():
                vectors.append({
                    'type': 'CVE',
                    'id': cve.id,
                    'priority': 1,
                    'confidence': 'HIGH'
                })
    
    # 2순위: 인증/인가 우회
    if 'login' in recon_data.endpoints or 'admin' in recon_data.endpoints:
        vectors.append({
            'type': 'AUTH_BYPASS',
            'target': identified_auth_endpoints,
            'priority': 2,
            'confidence': 'MEDIUM'
        })
    
    # 3순위: 일반 웹 취약점
    for endpoint in recon_data.endpoints:
        if has_parameters(endpoint):
            vectors.append({
                'type': 'WEB_VULNS',
                'target': endpoint,
                'priority': 3,
                'tests': ['SQLi', 'CMDi', 'LFI', 'SSTI']
            })
    
    return sorted(vectors, key=lambda x: x['priority'])
```

### 1.5 Step1 완료 보고

#### 성공 시 출력
```json
{
  "step": "1_reconnaissance",
  "status": "SUCCESS",
  "summary": {
    "cve_found": true,
    "cve_count": 3,
    "endpoints_discovered": 12,
    "technologies": ["Node.js", "Express", "Pug"],
    "interesting_findings": [
      "Admin panel at /admin",
      "File upload at /upload",
      "Pretty parameter in render"
    ]
  },
  "attack_plan": [
    {
      "priority": 1,
      "vector": "CVE-2021-21353",
      "target": "/render endpoint with pretty option",
      "confidence": "HIGH"
    },
    {
      "priority": 2,
      "vector": "Unicode normalization bypass",
      "target": "/login",
      "confidence": "MEDIUM"
    }
  ],
  "context_forward": {
    "key_parameters": ["pretty", "title", "content"],
    "session_required": false,
    "auth_mechanism": "username/password"
  },
  "next_action": "Step2_Exploitation"
}
```

## 중요 원칙

### 효율성 극대화
1. **배치 명령**: 여러 명령을 하나로 결합
2. **정보 저장**: 모든 결과를 변수에 저장
3. **중복 방지**: 이미 수집한 정보 재요청 금지

### 분석 깊이
1. **CVE 정독**: 설명을 한 줄씩 읽고 이해
2. **코드 연결**: CVE와 실제 코드 매칭
3. **패턴 인식**: 응답에서 기술 스택 파악

### 우선순위 원칙
1. **RCE 최우선**: Remote Code Execution 가능성
2. **인증 우회**: 관리자 권한 획득 가능성
3. **정보 유출**: 추가 공격 정보 획득

## 체크리스트

### 필수 완료 항목
- [ ] Trivy 스캔 실행 (또는 스킵 사유 명확)
- [ ] 프로젝트 파일 구조 분석
- [ ] 사용된 라이브러리/프레임워크 식별
- [ ] 엔드포인트 목록 작성
- [ ] 파라미터 및 입력점 매핑
- [ ] CVE와 코드 연결 확인 (CVE 발견 시)
- [ ] 기본 응답 패턴 수집
- [ ] 에러 메시지 형식 파악
- [ ] 공격 우선순위 결정
- [ ] attack_plan 생성 완료

### 정보 수집 체크리스트
- [ ] 기술 스택 확인 (언어, 프레임워크, 라이브러리)
- [ ] 인증 메커니즘 파악
- [ ] 세션 관리 방식 확인
- [ ] 입력 검증 수준 평가
- [ ] 특이사항 및 힌트 기록

### 효율성 체크리스트
- [ ] 중복 요청 없이 진행
- [ ] 모든 수집 정보 변수 저장
- [ ] 배치 명령 활용
- [ ] 캐싱 시스템 활용
