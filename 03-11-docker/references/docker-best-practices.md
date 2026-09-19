# Dockerfile 최적화 가이드라인

## 1. 베이스 이미지 선택

| 상황 | 선택 | 이유 |
| :--- | :--- | :--- |
| 일반적인 Node.js / Python 서비스 | `-slim` | glibc 기반이라 호환성 문제가 없고 충분히 작음 |
| 네이티브 모듈이 없고 크기가 최우선 | `-alpine` | 가장 작지만 musl libc라 네이티브 모듈 빌드가 실패할 수 있음 |
| 정적 바이너리(Go, Rust) | `distroless/static` 또는 `scratch` | 셸조차 없어 공격 표면이 가장 작음 |

태그는 `node:22-slim`처럼 메이저 버전까지 고정합니다. 재현성이 중요하면 다이제스트(`@sha256:...`)로 고정합니다.

## 2. 캐시 최적화

변경이 적은 의존성 목록(`package.json`과 락 파일, `requirements.txt`)을 먼저 COPY하고 설치한 뒤, 소스 코드를 나중에 COPY합니다. 소스만 바뀌면 설치 레이어는 캐시에서 재사용됩니다.

## 3. 멀티 스테이지 빌드

```dockerfile
FROM node:22-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-slim
ENV NODE_ENV=production
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force
COPY --from=build /app/dist ./dist
USER node
CMD ["node", "dist/server.js"]
```

- 빌드 스테이지에는 개발 의존성과 컴파일러가 있어도 됩니다. 최종 스테이지로 넘어가지 않습니다.
- 빌드 단계가 없는 프로젝트라면 스테이지를 나누지 않고 `npm ci --omit=dev`만으로 충분합니다. 의미 없는 멀티 스테이지를 만들지 않습니다.

## 4. 보안

- `USER node`(Node 공식 이미지에 내장) 또는 직접 만든 비-루트 사용자로 실행합니다.
- `.env`, 키 파일을 이미지에 넣지 않습니다. 실행 시점에 환경 변수나 시크릿 마운트로 주입합니다.
- 빌드 중 필요한 토큰은 `RUN --mount=type=secret`을 사용합니다. `ARG`로 넘긴 값은 이미지 히스토리에 남습니다.

## 5. .dockerignore 기본값

```
node_modules
.git
.env*
dist
coverage
*.log
Dockerfile
.dockerignore
```

## 6. 시작 명령

`CMD ["npm", "start"]` 대신 `CMD ["node", "dist/server.js"]`처럼 런타임을 직접 실행합니다. npm을 거치면 종료 시그널(SIGTERM)이 앱에 전달되지 않아 컨테이너가 강제 종료될 때까지 기다리게 됩니다.
