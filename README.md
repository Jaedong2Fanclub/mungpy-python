# Dog & Cat Breed Classifier

이 프로젝트는 이미지 기반으로 강아지와 고양이 품종을 분류하는 API 서버입니다. FastAPI와 Fastai를 사용하여 학습된 모델을 로드하고, 주어진 이미지를 바탕으로 품종을 예측합니다.

## 서버 동작 방법

### 1. 도커(Docker) 환경에서 실행
이 프로젝트는 Docker를 사용하여 실행할 수 있습니다.

#### 1.1. Docker 이미지 빌드
프로젝트 루트 디렉토리에서 Docker 이미지를 빌드합니다.

```bash
docker build -t dog-cat-classifier .
```

#### 1.2. Docker 컨테이너 실행
Docker 컨테이너를 실행합니다. 아래 명령어는 서버를 5000 포트에서 실행합니다.

```bash
docker run -d -p 5000:5000 dog-cat-classifier
```

서버는 `http://localhost:5000`에서 실행됩니다.

## 헬스체크
서버가 정상적으로 동작하는지 확인하려면 `/health` 엔드포인트를 통해 헬스체크를 할 수 있습니다.

```bash
curl http://localhost:5000/health
```

정상 응답 예시:

```json
{
  "status": "healthy"
}
```
## API 엔드포인트

### 1. `/breeds` - 품종 예측
이미지 업로드를 통해 품종을 예측할 수 있습니다. POST 요청을 /breeds 엔드포인트로 보내면 됩니다.

#### 요청예시

```bash
curl -X 'POST' \
  'http://localhost:5000/breeds?type=dog' \
  -F 'file=@<image_path>'
```

#### 응답예시(강아지 품종 예측)
```bash
{
  "result": "beagle"
}
```

#### 응답 예시 (고양이 품종 예측)
```bash
{
  "result": "Siamese"
}
```

#### 응답 예시 (모든 품종 예측)
```bash
{
  "result": "pug"
}
```

#### 파라미터

- `file`: 예측할 이미지 파일 (필수)
- `type`: 품종 필터링을 위한 파라미터 (선택적)
    - `dog`: 강아지 품종 예측
    - `cat`: 고양이 품종 예측
    - `생략`: 모든 품종 예측

### 2. `/health` - 헬스체크

서버가 정상적으로 동작하는지 확인하는 엔드포인트입니다. GET 요청을 보내면 서버 상태를 확인할 수 있습니다.

#### 요청 예시

```bash
curl http://localhost:5000/health
```

#### 응답 예시

```bash
{
  "status": "healthy"
}
```
## 구분 가능한 품종 목록

### 1. 고양이 품종 (Cat Breeds)
- Abyssinian
- Bengal
- Birman
- Bombay
- British_Shorthair
- Egyptian_Mau
- Maine_Coon
- Persian
- Ragdoll
- Russian_Blue
- Siamese
- Sphynx

### 2. 강아지 품종 (Dog Breeds)
- american_bulldog
- american_pit_bull_terrier
- basset_hound
- beagle
- boxer
- chihuahua
- english_cocker_spaniel
- english_setter
- german_shorthaired
- great_pyrenees
- havanese
- japanese_chin
- keeshond
- leonberger
- miniature_pinscher
- newfoundland
- pomeranian
- pug
- saint_bernard
- samoyed
- scottish_terrier
- shiba_inu
- staffordshire_bull_terrier
- wheaten_terrier
- yorkshire_terrier
