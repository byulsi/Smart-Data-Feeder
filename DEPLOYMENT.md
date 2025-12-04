# 🚀 Smart Data Feeder 배포 가이드 (초보자용)

이 가이드는 **Smart Data Feeder**를 여러분의 서버(또는 개인 PC)에 쉽고 안전하게 설치하는 방법을 설명합니다.
우리는 **Docker(도커)**라는 기술을 사용하여, 복잡한 설치 과정 없이 명령어 몇 줄로 프로그램을 실행할 것입니다.

---

## 1. 준비물 (Prerequisites)

시작하기 전에, 컴퓨터(또는 서버)에 다음 두 가지가 설치되어 있어야 합니다.

### 1) Git (깃)
코드를 다운로드받기 위해 필요합니다.
- **설치 확인**: 터미널에 `git --version`을 입력해보세요.

### 2) Docker (도커)
프로그램을 실행하는 가상 환경입니다.
- **설치 확인**: 터미널에 `docker --version`과 `docker-compose --version`을 입력해보세요.
- **설치 방법**:
    - **Windows/Mac**: [Docker Desktop](https://www.docker.com/products/docker-desktop/)을 다운로드하여 설치하세요.
    - **Linux (Ubuntu)**:
      ```bash
      # Docker 설치 스크립트 실행
      curl -fsSL https://get.docker.com -o get-docker.sh
      sudo sh get-docker.sh
      
      # 현재 사용자를 docker 그룹에 추가 (sudo 없이 실행하기 위해)
      sudo usermod -aG docker $USER
      # (로그아웃 후 다시 로그인해야 적용됩니다)
      ```

---

## 2. AWS EC2 빠른 시작 (AWS Quick Start) ☁️

AWS 프리 티어를 사용하여 무료로 서버를 구축하는 방법입니다.

### 1단계: 인스턴스 만들기
1.  **AWS 콘솔** 로그인 -> **EC2** 서비스 이동.
2.  **[인스턴스 시작]** 버튼 클릭.
3.  **이름**: `Smart-Data-Feeder` 입력.
4.  **OS**: `Ubuntu` 선택 (버전 22.04 LTS 권장).
5.  **인스턴스 유형**: `t2.micro` (프리 티어 사용 가능 라벨 확인).
6.  **키 페어**: [새 키 페어 생성] -> 이름 입력 -> 다운로드 (`.pem` 파일).
7.  **네트워크 설정**:
    -   [편집] 클릭.
    -   **보안 그룹**: [보안 그룹 생성] 선택.
    -   **인바운드 보안 그룹 규칙**:
        -   규칙 1: SSH (TCP 22) - 내 IP
        -   규칙 2: 사용자 지정 TCP (TCP 3000) - 위치 무관 (0.0.0.0/0) -> **웹 접속용**
8.  **스토리지 구성**: `30` GiB로 변경 (프리 티어 최대).
9.  **[인스턴스 시작]** 클릭.

### 2단계: 서버 접속하기
터미널(맥/리눅스) 또는 PowerShell(윈도우)을 켜고, 키 파일(`key.pem`)이 있는 폴더로 이동하세요.

```bash
# 1. 키 파일 권한 보호 (맥/리눅스 필수)
chmod 400 key.pem

# 2. 접속 (IP주소는 AWS 콘솔의 '퍼블릭 IPv4 주소' 확인)
ssh -i "key.pem" ubuntu@12.34.56.78
```

### 3단계: 설치 및 실행
서버에 접속했다면, 다음 명령어들을 한 줄씩 복사해서 붙여넣으세요. (Docker 설치부터 실행까지 한 번에 합니다)

```bash
# 1. Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 2. 로그아웃 후 다시 로그인 (권한 적용 위해)
exit
# (다시 ssh 접속 명령어로 접속하세요!)

# 3. 코드 다운로드 및 설정
git clone https://github.com/byulsi/Smart-Data-Feeder.git
cd Smart-Data-Feeder
cp .env.example .env
# (필요시 vi .env 로 API 키 수정)

# 4. 실행
docker-compose up -d --build
```

이제 브라우저 주소창에 `http://12.34.56.78:3000`을 입력하면 접속됩니다! 🎉

---

## 3. 로컬 설치 가이드 (Local Installation)

### 1단계: 코드 다운로드
```bash
git clone https://github.com/byulsi/Smart-Data-Feeder.git
cd Smart-Data-Feeder
```

### 2단계: 환경 설정 (.env 파일 만들기)
OpenDART API 키가 필요합니다.

1.  `.env` 파일을 생성합니다.
    ```bash
    # 리눅스/맥
    cp .env.example .env
    # 윈도우: 탐색기에서 .env.example 파일을 복사해서 이름을 .env로 바꾸세요.
    ```
2.  `.env` 파일을 열어 API 키를 입력합니다.
    ```text
    DART_API_KEY=your_api_key_here  <-- 여기에 실제 키를 붙여넣으세요
    ```

---

## 3. 실행하기 (Running)

이제 마법의 명령어 하나면 끝납니다! ✨

```bash
docker-compose up -d --build
```

- **`up`**: 실행하라
- **`-d`**: 백그라운드에서 (터미널을 꺼도 계속 돌게)
- **`--build`**: 최신 버전으로 새로 만들어서

처음 실행할 때는 이미지를 다운로드하고 빌드하느라 **몇 분 정도 걸릴 수 있습니다.**

---

## 4. 접속하기 (Access)

설치가 완료되면 브라우저를 켜고 다음 주소로 접속하세요.

- **내 컴퓨터에서 실행했다면**: `http://localhost:3000`
- **서버(AWS 등)에서 실행했다면**: `http://서버IP주소:3000`
    - (주의: AWS 보안 그룹 설정에서 **3000번 포트**를 열어주어야 합니다!)

---

## 5. 관리하기 (Maintenance)

### 프로그램 종료하기
```bash
docker-compose down
```

### 최신 버전으로 업데이트하기
개발자가 새로운 기능을 추가했다면, 다음 순서로 업데이트하세요.
```bash
# 1. 최신 코드 받기
git pull origin main

# 2. 다시 빌드하고 실행하기
docker-compose up -d --build
```

### 데이터 백업하기
수집된 데이터는 `data.db` 파일에 저장됩니다. 이 파일만 따로 복사해두면 언제든 데이터를 복구할 수 있습니다.

---

## ❓ 자주 묻는 질문 (FAQ) & 문제 해결

**Q. 서버를 껐다 켜도 데이터가 남아있나요?**
A. 네! `docker-compose.yml` 설정 덕분에 `data.db` 파일은 안전하게 보존됩니다.

**Q. "Permission denied" 에러가 떠요.**
A. 리눅스라면 명령어 앞에 `sudo`를 붙여보세요. (예: `sudo docker-compose up ...`)

**Q. 포트(3000)가 이미 사용 중이라는데요?**
A. `docker-compose.yml` 파일을 열어 포트를 변경하세요. (예: `"8080:3000"`으로 바꾸면 8080 포트로 접속됩니다.)

**Q. 실행이 잘 안되거나 에러가 발생해요.**
A. 로그를 확인해보면 원인을 알 수 있습니다. 다음 명령어를 입력해보세요:
```bash
docker-compose logs -f
```
(로그 확인을 멈추려면 `Ctrl + C`를 누르세요)

**Q. 코드를 수정했는데 반영이 안 돼요.**
A. 코드를 수정한 후에는 반드시 다시 빌드해야 합니다:
```bash
docker-compose up -d --build
```
