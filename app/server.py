import aiohttp
import asyncio
import uvicorn
from fastai import *
from fastai.vision import *
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
import os

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
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())

@app.route('/breeds', methods=['POST'])
async def analyze(request):
    img_data = await request.form()
    img_bytes = await (img_data['file'].read())
    img = open_image(BytesIO(img_bytes))
    prediction, _, probs = learn.predict(img)
    
    # 쿼리 파라미터 확인 (type)
    query_params = request.query_params
    filter_type = query_params.get('type', None)  # None이면 모든 품종 반환
    
    # 필터링 로직
    if filter_type == 'dog':
        # 강아지 품종 중 가장 높은 확률을 가진 품종 반환
        dog_probs = {dog: probs[classes.index(dog)].item() for dog in dog_classes}
        best_dog = max(dog_probs, key=dog_probs.get)
        return JSONResponse({'result': best_dog})
    elif filter_type == 'cat':
        # 고양이 품종 중 가장 높은 확률을 가진 품종 반환
        cat_probs = {cat: probs[classes.index(cat)].item() for cat in cat_classes}
        best_cat = max(cat_probs, key=cat_probs.get)
        return JSONResponse({'result': best_cat})
    
    # 기본 동작: 모든 품종 중 가장 높은 확률의 품종 반환
    return JSONResponse({'result': str(prediction)})

@app.route('/health', methods=['GET'])
async def health_check(request):
    return JSONResponse({'status': 'healthy'})

if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
