import aiohttp
import asyncio
import uvicorn
from fastai import *
from fastai.vision import *
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse
from starlette.staticfiles import StaticFiles
import os
import ssl
import aiohttp

# 모델 파일 경로
model_file_path = './app/models/DogCatClassifier.pkl'

# 전체 품종 리스트
classes = ['Abyssinian', 'Bengal', 'Birman', 'Bombay', 'British_Shorthair', 'Egyptian_Mau', 'Maine_Coon', 'Persian', 'Ragdoll', 'Russian_Blue', 'Siamese', 'Sphynx', 'american_bulldog', 'american_pit_bull_terrier', 'basset_hound', 'beagle', 'boxer', 'chihuahua', 'english_cocker_spaniel', 'english_setter', 'german_shorthaired', 'great_pyrenees', 'havanese', 'japanese_chin', 'keeshond', 'leonberger', 'miniature_pinscher', 'newfoundland', 'pomeranian', 'pug', 'saint_bernard', 'samoyed', 'scottish_terrier', 'shiba_inu', 'staffordshire_bull_terrier', 'wheaten_terrier', 'yorkshire_terrier']

# 강아지와 고양이 품종 리스트 분리
dog_classes = [
    'american_bulldog', 'american_pit_bull_terrier', 'basset_hound', 'beagle', 'boxer',
    'chihuahua', 'english_cocker_spaniel', 'english_setter', 'german_shorthaired',
    'great_pyrenees', 'havanese', 'japanese_chin', 'keeshond', 'leonberger',
    'miniature_pinscher', 'newfoundland', 'pomeranian', 'pug', 'saint_bernard',
    'samoyed', 'scottish_terrier', 'shiba_inu', 'staffordshire_bull_terrier',
    'wheaten_terrier', 'yorkshire_terrier'
]
cat_classes = [
    'Abyssinian', 'Bengal', 'Birman', 'Bombay', 'British_Shorthair', 'Egyptian_Mau',
    'Maine_Coon', 'Persian', 'Ragdoll', 'Russian_Blue', 'Siamese', 'Sphynx'
]

path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))

async def setup_learner():
    try:
        # 사전 다운로드된 모델을 로드
        learn = load_learner(Path(model_file_path).parent, Path(model_file_path).name)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise

loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()

@app.route('/test-page')
async def homepage(request):
    try:
        html_file = path / 'view' / 'index.html'
        return HTMLResponse(html_file.open().read())
    except FileNotFoundError:
        return PlainTextResponse("Test page not found.", status_code=404)

@app.route('/breeds', methods=['POST'])
async def analyze(request):
    query_params = request.query_params
    source_type = query_params.get('source', 'file')  # 기본값은 파일

    if source_type == 'url':
        # URL로부터 이미지 가져오기
        try:
            img_url = await request.form()
            img_url = img_url.get('url', None)  # 폼 데이터에서 'url' 값을 가져옵니다.
            if not img_url:
                return JSONResponse({'error': 'URL parameter is required for source=url'}, status_code=400)

            # SSL 인증서 검증 비활성화 상태       
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                async with session.get(img_url) as response:
                    if response.status != 200:
                        return JSONResponse({'error': 'Failed to fetch image from URL'}, status_code=400)

                    img_bytes = await response.read()
        except Exception as e:
            return JSONResponse({'error': f'Error fetching image from URL: {str(e)}'}, status_code=500)

    elif source_type == 'file':
        # 폼 데이터로부터 이미지 파일 읽기
        try:
            img_data = await request.form()
            img_bytes = await (img_data['file'].read())
        except Exception as e:
            return JSONResponse({'error': f'Error reading image file: {str(e)}'}, status_code=400)

    else:
        return JSONResponse({'error': 'Invalid source type. Use "file" or "url".'}, status_code=400)

    try:
        img = open_image(BytesIO(img_bytes))
        prediction, _, probs = learn.predict(img)

        # 쿼리 파라미터 확인 (type)
        filter_type = query_params.get('type', None)  # None이면 모든 품종 반환

        # 필터링 로직
        if filter_type == 'dog':
            dog_probs = {dog: probs[classes.index(dog)].item() for dog in dog_classes}
            best_dog = max(dog_probs, key=dog_probs.get)
            return JSONResponse({'result': best_dog})
        elif filter_type == 'cat':
            cat_probs = {cat: probs[classes.index(cat)].item() for cat in cat_classes}
            best_cat = max(cat_probs, key=cat_probs.get)
            return JSONResponse({'result': best_cat})

        return JSONResponse({'result': str(prediction)})

    except Exception as e:
        return JSONResponse({'error': f'Error processing image: {str(e)}'}, status_code=500)


@app.route('/health', methods=['GET'])
async def health_check(request):
    return JSONResponse({'status': 'healthy'})

if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
