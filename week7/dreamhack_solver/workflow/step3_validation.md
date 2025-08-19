# Step 3: 플래그 검증 및 최종 처리

## 목표
획득한 문자열이 실제 플래그인지 검증하고 최종 결과 보고

## 플래그 검증 프로세스

### 3.1 형식 검증

```python
def validate_flag_format(potential_flag):
    """플래그 형식 확인"""
    
    import re
    
    # 표준 플래그 패턴들
    flag_patterns = [
        r'^flag\{[A-Za-z0-9_\-!@#$%^&*()+=]{8,64}\}$',
        r'^FLAG\{[A-Za-z0-9_\-!@#$%^&*()+=]{8,64}\}$',
        r'^DH\{[A-Za-z0-9_\-!@#$%^&*()+=]{8,64}\}$',
        r'^CTF\{[A-Za-z0-9_\-!@#$%^&*()+=]{8,64}\}$',
        r'^[A-Z]{2,10}\{[A-Za-z0-9_\-!@#$%^&*()+=]{8,64}\}$'  # 일반 패턴
    ]
    
    for pattern in flag_patterns:
        if re.match(pattern, potential_flag):
            return True, pattern
    
    # 형식은 맞지 않지만 플래그일 가능성
    if '{' in potential_flag and '}' in potential_flag:
        return "POSSIBLE", "Non-standard format"
    
    return False, None
```

### 3.2 플래그 추출 및 정제

```python
def extract_and_clean_flag(response_text):
    """응답에서 플래그 추출 및 정제"""
    
    import re
    
    # 다양한 형태로 플래그 찾기
    patterns = [
        r'(flag\{[^}]+\})',
        r'(FLAG\{[^}]+\})',
        r'(DH\{[^}]+\})',
        r'(CTF\{[^}]+\})',
        r'([A-Z]{2,10}\{[^}]+\})'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, response_text, re.IGNORECASE)
        if matches:
            # 가장 긴 매치 선택 (더 완전할 가능성)
            flag = max(matches, key=len)
            
            # 정제
            flag = flag.strip()
            flag = flag.replace('\\n', '')
            flag = flag.replace('\\r', '')
            
            return flag
    
    return None
```

### 3.3 인코딩 처리

```python
def handle_encoded_flags(potential_flag):
    """인코딩된 플래그 처리"""
    
    decoders = {
        'base64': lambda x: base64.b64decode(x).decode(),
        'hex': lambda x: bytes.fromhex(x).decode(),
        'url': lambda x: urllib.parse.unquote(x),
        'html': lambda x: html.unescape(x)
    }
    
    for encoding_type, decoder in decoders.items():
        try:
            decoded = decoder(potential_flag)
            if 'flag{' in decoded.lower():
                return decoded
        except:
            continue
    
    return potential_flag
```

### 3.4 부분 플래그 조합

```python
def combine_partial_flags(partial_results):
    """여러 부분으로 나뉜 플래그 조합"""
    
    # 부분 플래그 수집
    parts = {}
    
    for result in partial_results:
        # Part 1, Part 2 형식
        if 'part' in result.lower():
            part_num = extract_part_number(result)
            parts[part_num] = extract_flag_content(result)
        
        # 순차적 발견
        elif result.startswith('flag{') and not result.endswith('}'):
            parts['start'] = result
        elif not result.startswith('flag{') and result.endswith('}'):
            parts['end'] = result
        elif not result.startswith('flag{') and not result.endswith('}'):
            parts['middle'] = result
    
    # 조합 시도
    if len(parts) > 1:
        # 번호 순서대로
        if all(isinstance(k, int) for k in parts.keys()):
            combined = ''.join([parts[i] for i in sorted(parts.keys())])
        # 시작-중간-끝
        else:
            combined = parts.get('start', '') + parts.get('middle', '') + parts.get('end', '')
        
        return combined
    
    return None
```

## 최종 보고서 생성

### 3.5 성공 보고서

```python
def generate_success_report(flag, context):
    """성공 시 상세 보고서 생성"""
    
    return {
        "workflow_status": "COMPLETED_SUCCESS",
        "flag": flag,
        "validation": {
            "format_valid": True,
            "confidence": "HIGH"
        },
        "solving_methodology": {
            "vulnerability_exploited": context.successful_vector,
            "attack_vector": context.attack_method,
            "key_payload": context.winning_payload,
            "critical_discovery": context.key_insight
        },
        "execution_metrics": {
            "total_time_seconds": context.elapsed_time,
            "total_attempts": context.attempt_count,
            "successful_step": context.successful_step,
            "tools_used": list(context.tools_used)
        },
        "reproduction_steps": [
            f"1. {step}" for step in context.reproduction_steps
        ],
        "learning_points": [
            "취약점 발견 과정: " + context.discovery_process,
            "핵심 통찰: " + context.key_insight,
            "우회 기법: " + context.bypass_technique if context.bypass_technique else "N/A"
        ]
    }
```

### 3.6 실패 보고서

```python
def generate_failure_report(context):
    """실패 시 상세 분석 보고서"""
    
    return {
        "workflow_status": "COMPLETED_FAILURE",
        "failure_analysis": {
            "primary_reason": identify_main_failure_reason(context),
            "attempted_vectors": context.all_attempts,
            "promising_leads": context.partial_successes,
            "blockers_identified": context.protection_mechanisms
        },
        "partial_findings": {
            "confirmed_technologies": context.tech_stack,
            "discovered_endpoints": context.endpoints,
            "interesting_behaviors": context.anomalies,
            "potential_vulnerabilities": context.unconfirmed_vulns
        },
        "execution_metrics": {
            "total_time_seconds": context.elapsed_time,
            "total_attempts": context.attempt_count,
            "modules_used": context.modules_loaded,
            "unique_payloads": len(context.unique_payloads)
        },
        "recommendations": generate_recommendations(context),
        "next_steps": [
            "수동 분석 권장 영역: " + identify_manual_areas(context),
            "추가 도구 필요: " + suggest_additional_tools(context),
            "다른 접근법: " + suggest_alternative_approaches(context)
        ]
    }
```

### 3.7 불확실한 경우

```python
def handle_uncertain_flag(potential_flag, context):
    """플래그 불확실 시 처리"""
    
    return {
        "workflow_status": "COMPLETED_UNCERTAIN",
        "potential_flag": potential_flag,
        "validation": {
            "format_valid": False,
            "issue": "Non-standard format or incomplete",
            "confidence": "LOW"
        },
        "evidence": {
            "where_found": context.source_location,
            "why_suspicious": context.flag_indicators,
            "similar_patterns": context.similar_findings
        },
        "suggestion": "Manual verification recommended",
        "alternative_interpretations": [
            "Could be encoded: Try base64/hex decode",
            "Might be partial: Look for other parts",
            "Custom format: Check CTF rules"
        ]
    }
```

## 클린업 작업

### 3.8 환경 정리

```python
def cleanup_environment():
    """임시 파일 및 리소스 정리"""
    
    # 생성된 임시 파일 삭제
    dreamhack_solver:execute_command(
        command="rm -f /tmp/exploit_* /tmp/test_* /tmp/*.py 2>/dev/null"
    )
    
    # 프로세스 정리
    dreamhack_solver:execute_command(
        command="pkill -f 'python.*exploit' 2>/dev/null || true"
    )
    
    print("[클린업] 임시 파일 및 프로세스 정리 완료")
```

## 체크리스트

### 검증 완료 확인
- [ ] 플래그 형식 검증
- [ ] 중복 제거 (여러 플래그 발견 시)
- [ ] 인코딩 확인 및 디코딩
- [ ] 부분 플래그 조합 시도
- [ ] 재현 가능성 확인

### 보고서 완성도
- [ ] 취약점 명확히 명시
- [ ] 재현 단계 상세 기록
- [ ] 실행 메트릭 정확성
- [ ] 학습 포인트 도출
- [ ] 실패 시 원인 분석

### 최종 확인
- [ ] 플래그 완전성 (시작과 끝 확인)
- [ ] 특수문자 처리 정확성
- [ ] 대소문자 구분 확인
- [ ] 공백 및 개행 제거
- [ ] 최종 클린업 완료

## 빠른 검증 함수

```python
def quick_validate(text):
    """빠른 플래그 검증 및 추출"""
    
    # 즉시 플래그 패턴 확인
    import re
    flag_pattern = r'((?:flag|FLAG|DH|CTF)\{[^}]+\})'
    match = re.search(flag_pattern, text)
    
    if match:
        flag = match.group(1)
        return {
            "found": True,
            "flag": flag,
            "confidence": "HIGH" if flag.startswith(('flag{', 'FLAG{', 'DH{')) else "MEDIUM"
        }
    
    return {"found": False}
```

## 핵심 원칙

1. **정확성**: 플래그 한 글자도 놓치지 않기
2. **완전성**: 부분 플래그는 조합 시도
3. **검증**: 형식과 내용 모두 확인
4. **문서화**: 모든 과정 상세 기록
5. **청결**: 환경 정리로 마무리
