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
