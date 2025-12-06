# ☁️ AWS EC2 배포 가이드 (Antz)

이 가이드는 **Antz** 프로젝트를 AWS EC2(Elastic Compute Cloud) 인스턴스에 배포하는 전체 과정을 단계별로 설명합니다.

---

## 1. AWS EC2 인스턴스 생성

### 1.1. 인스턴스 시작
1.  [AWS Management Console](https://console.aws.amazon.com/)에 로그인합니다.
2.  우측 상단 리전이 **Seoul (ap-northeast-2)**인지 확인합니다.
3.  검색창에 **EC2**를 입력하고 선택합니다.
4.  **[인스턴스 시작]** (Launch Instances) 버튼을 클릭합니다.

### 1.2. 인스턴스 설정
다음 설정값들을 입력/선택합니다:

*   **이름 및 태그**: `Antz` (원하는 이름)
*   **애플리케이션 및 OS 이미지**: `Ubuntu` 선택
    *   Amazon Machine Image (AMI): **Ubuntu Server 22.04 LTS** (프리 티어 사용 가능)
*   **인스턴스 유형**: `t2.micro` (프리 티어 사용 가능)
*   **키 페어(로그인)**:
    *   **[새 키 페어 생성]** 클릭
    *   이름: `smart-feeder-key` (원하는 이름)
    *   유형: `RSA`
    *   형식: `.pem`
    *   **[키 페어 생성]** 클릭 -> **파일이 다운로드됩니다. 절대 잃어버리지 마세요!**

### 1.3. 네트워크 설정 (중요!)
*   **네트워크 설정** 섹션에서 **[편집]** 클릭.
*   **보안 그룹 생성** 선택.
*   **인바운드 보안 그룹 규칙** (방화벽 설정):
    1.  **SSH (TCP 22)**:
        *   소스 유형: **내 IP** (보안을 위해 권장) 또는 위치 무관(0.0.0.0/0)
    2.  **사용자 지정 TCP (TCP 3000)**: (웹 서버 포트)
        *   포트 범위: `3000`
        *   소스 유형: **위치 무관 (0.0.0.0/0)** (누구나 접속 가능하게 하려면)

### 1.4. 스토리지 구성
*   `30` GiB gp3 (프리 티어는 최대 30GB까지 무료입니다).

**[인스턴스 시작]** 버튼을 클릭하여 서버를 생성합니다.

---

## 2. 서버 접속 (SSH)

터미널(Mac/Linux) 또는 PowerShell(Windows)을 엽니다.

### 2.1. 키 파일 권한 설정 (Mac/Linux 필수)
다운로드 받은 키 파일(`smart-feeder-key.pem`)이 있는 폴더로 이동 후 실행합니다.
```bash
chmod 400 smart-feeder-key.pem
```

### 2.2. 접속하기
AWS 콘솔의 인스턴스 목록에서 생성한 인스턴스의 **퍼블릭 IPv4 주소**를 확인하세요. (예: `12.34.56.78`)

```bash
# 형식: ssh -i "키파일경로" ubuntu@퍼블릭IP
ssh -i "smart-feeder-key.pem" ubuntu@12.34.56.78
```
`Are you sure you want to continue connecting?` 질문이 나오면 `yes` 입력 후 엔터.

---

## 3. 환경 구축 (Docker 설치)

서버에 접속했다면, 다음 명령어들을 순서대로 실행하여 Docker를 설치합니다.

```bash
# 1. 시스템 업데이트
sudo apt-get update

# 2. Docker 설치 스크립트 다운로드 및 실행
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. 현재 사용자(ubuntu)에게 Docker 권한 부여
sudo usermod -aG docker $USER

# 4. Docker Compose 설치 (최신 버전)
sudo apt-get install -y docker-compose-plugin
```

**중요**: 권한 적용을 위해 **로그아웃 후 다시 접속**해야 합니다.
```bash
exit
# 다시 ssh 명령어로 접속하세요!
```

---

## 4. 프로젝트 배포

### 4.1. 코드 다운로드
```bash
git clone https://github.com/byulsi/Smart-Data-Feeder.git
cd Smart-Data-Feeder
```

### 4.2. 환경 변수 설정
OpenDART API 키 설정을 위해 `.env` 파일을 생성합니다.

```bash
# 예제 파일 복사
cp .env.example .env

# 파일 편집
nano .env
```
편집기에서 `DART_API_KEY=...` 부분을 찾아 실제 키를 입력하세요.
(저장하고 나가기: `Ctrl + O` -> `Enter` -> `Ctrl + X`)

### 4.3. 서비스 실행
Docker Compose를 사용하여 백엔드와 프론트엔드를 한 번에 실행합니다.

```bash
docker compose up -d --build
```
*   `-d`: 백그라운드 실행
*   `--build`: 이미지 새로 빌드

---

## 5. 접속 확인

브라우저를 열고 주소를 입력합니다:
`http://[퍼블릭IP]:3000`

(예: `http://12.34.56.78:3000`)

화면이 정상적으로 보인다면 배포 성공입니다! 🎉

---

## 6. 유지 보수

### 로그 확인
```bash
docker compose logs -f
```

### 서비스 중지
```bash
docker compose down
```

### 최신 코드 업데이트
```bash
git pull origin main
docker compose up -d --build
```
