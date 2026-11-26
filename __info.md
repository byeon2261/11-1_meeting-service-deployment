# 서비스 배포 및 자동화 운영

## 5. 서비스 이미지 제작
...

### 공통 빌드 범위와 제외 규칙
...

### API 이미지 빌드와 캐시

이미지 생성: docker build -t 이미지:태그 빌드컨텍스트

backend 이미지 생성
```bash
docker build -f backend/Dockerfile -t meeting-api:v1 .
```

### React 빌드와 웹 Dockerfile
같은 프로젝트 루트에서 웹 이미지를 만든다.

```bash
docker build -f frontend/Dockerfile -t meeting-web:v1 .
```

**확인할 결과** · 로그에서 `npm ci` → `npm run build` → `COPY --from=build`를 찾는다. 화면 빌드가 성공하고 최종 Nginx 이미지에 결과 파일이 전달되어야 한다.

만들어진 웹 이미지를 목록에서 확인한다.

## 6. 컨테이너 네트워크와 서비스 실행

### 실행 환경변수와 외부 연결

![설명](https://img.notionusercontent.com/s3/prod-files-secure%2F2ed584e0-2b03-4eac-8d4b-4490d601f1ba%2F032ec9d1-1147-4da7-ac20-af6d6f37e048%2Fconfiguration-boundaries.png/size/w=2000?tok=eyJhbGciOiJFUzI1NiIsImtpZCI6IlI3dzVrRnREIiwidHlwIjoiSldUIn0.eyJzcGFjZUlkIjoiMmVkNTg0ZTAtMmIwMy00ZWFjLThkNGItNDQ5MGQ2MDFmMWJhIiwiZmlsZUlkIjoiMDMyZWM5ZDEtMTE0Ny00ZGE3LWFjMjAtYWY2ZDZmMzdlMDQ4IiwiYWN0b3IiOiJub3Rpb25fdXNlcjozZGJkODcyYi01OTRjLTgxN2ItOTg1MS0wMDAyMGY1NmY1ZWIiLCJyZWNvcmQiOiJibG9jazo0MjMyZmRiMS00MTQ4LTgwMGMtYThhMC1lN2FhZDA1N2RhODciLCJleHAiOjE3OTU2NTgyMDV9.Fxm4ICdJzdsahJZYi45cKOdiuofJbGYCWwzBKNKQaFRGQWdqBmLtkVwihQM3fHZA56oQYikK8hW9dTayndD-jw&imgBuildSrc=createSecureFileAccessTokenImageUrl&mtd=com)

### 네트워크와 API 실행

### 공유 네트워크

Docker 네트워크는 컨테이너를 연결하는 방식을 정한다. **Docker 호스트**는 컨테이너를 실행하는 Docker Engine 쪽 환경을 뜻한다. 대표적인 세 방식은 다음과 같다.

| 방식 | 연결 방식 |
| --- | --- |
| **bridge** | 컨테이너별 네트워크 공간을 유지하면서 같은 Docker 호스트의 컨테이너들을 가상 네트워크로 연결한다. |
| **host** | 컨테이너가 Docker 호스트의 네트워크 공간을 공유한다. |
| **none** | 외부 네트워크 연결 없이 실행한다. |

웹과 API는 **각자의 네트워크 공간을 유지하면서 서로 통신**해야 한다. 같은 Docker 실행 환경 안의 두 컨테이너를 연결하므로 **bridge**를 사용한다.

`docker network create`에서 네트워크 종류를 정하는 `--driver`를 생략하면 기본값인 **bridge**가 선택된다. 따라서 아래 명령은 `meeting-local`이라는 bridge 네트워크를 만든다. Docker의 네트워크 종류

프로젝트 루트에서 두 컨테이너가 함께 사용할 네트워크를 만든다.

```bash
docker network create meeting-local
```

**확인할 결과** · 네트워크 ID가 출력된다. 아직 API나 웹을 시작한 것은 아니며, 이 네트워크에 연결할 컨테이너를 이어서 만든다.

### API 컨테이너

준비한 `.env`의 값을 전달하고, API를 방금 만든 공유 네트워크에 연결해 실행한다.

```bash
docker run -d --name meeting-api --network meeting-local --network-alias api --env-file .env -p 127.0.0.1:8000:8000 meeting-api:v1
```
```
-d: 백그라운드 실행
--network-alias: 네트워크 별칭. 호출할때 해당 별칭을 사용하면 된다.
```

## 7. !! 11-2.... 레포에 작성.
### 믿기시지 않겠지만 11-2_compose-lab 레포에서 내용 참조


## 8. 일정 조정 서비스의 Compose 관리

<aside>
💡

**Compose로 일정 조정 서비스의 실행 조건과 준비 상태를 관리한다.**
수동 실행의 이미지·환경변수·포트·네트워크를 Compose 설정에 대응시킨다.
기존 이미지로 업무를 먼저 확인한 뒤, 빌드·준비 조건·프로세스 관리와 서비스별 변경을 연결한다.

</aside>

### 일정 조정 서비스와 실행 구성

먼저 API v1·웹 v2 이미지로 기존 업무가 이어지는지 확인한다. 이후 같은 파일에 빌드·준비 검사·프로세스 관리 조건을 더한다.

<aside>
💭

**수동 실행에서 지정한 값들은 Compose 파일의 어느 항목으로 옮겨질까?**
이미지·환경변수·웹의 중계 주소·게시 포트·공유 네트워크를 기존 명령과 대응시킨다.

</aside>

### 기존 이미지로 실행하는 기본 구성

루트의 `compose.yaml`을 다음 전체 내용으로 만든다. **첫 구성의 목적은 이미 만든 API v1·웹 v2를 수동 실행에서 Compose로 옮겨 동작을 확인하는 것**이다.

```yaml
name: meeting-service

services:
  api:
    image: meeting-api:v1
    env_file:
      - .env
    environment:
      SERVICE_HOST: 0.0.0.0
      SERVICE_PORT: "8000"
    expose:
      - "8000"
    networks:
      - service

  web:
    image: meeting-web:v2
    environment:
      API_UPSTREAM: http://api:8000
    ports:
      - "127.0.0.1:8080:8080"
    networks:
      - service

networks:
  service:
    driver: bridge
```