# 3_Express & PP Test

이 프로젝트는 Docker를 통한 express 프로젝트의 배포와 PP 공격 기법을 테스트해보는 프로젝트입니다.

## Docker 사용법
1. Dockerfile 파일 생성
2. docker image build
    - `docker build --tag {tag} .`
3. docker image deploy
    - `docker run -d -p {port} --name {name} {tag}`
    - port는 프로젝트에서 사용한 port 번호를 사용해야 함
    - name은 tag와 동일할 필요 없음
    - tag는 build에서 사용한 tag를 사용
4. port 확인
    - `docker ps | grep {name}` 명령을 통해 deploy한 image 정보 확인
    - 어떤 포트가 할당되었는지 확인
        - `0.0.0.0:{real}->{port}` 형식으로 표시됨
        - port는 프로젝트에서 사용한 내부 port 번호임
        - real이 실제 네트워크에 연결된 port 번호임
5. 연결 확인
    - 브라우저를 열고, `localhost:{real}`로 접속이 가능한지 확인

## Dockerfile의 주요 Instruction
- `FROM` : 기반이 되는 이미지 설정
    - node 프로젝트는 주로 `node:24-alpine` 이미지를 사용
    - node 경량 이미지중 최신 버전
- `WORKDIR` : Docker Instruction의 실행 기준 위치 지정
    - 이후 실행되는 명령어는 전부 `WORKDIR`의 위치에서 실행됨
- `COPY` : Build Context에 있는 지정된 로컬 파일들을 Build Container로 복사
    - src는 로컬의 dockerfile 위치 기준
    - dst는 위에서 설정한 WORKDIR 기준
- `RUN` : 빌드 과정에서 주어진 명령어를 수행함
- `CMD` : 빌드된 이미지를 배포할 때 수행할 명령어를 지정
    - 가장 마지막으로 사용된 CMD 명령만 적용됨
