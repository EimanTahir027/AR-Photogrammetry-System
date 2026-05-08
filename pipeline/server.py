from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()
app.mount('/static', StaticFiles(directory='models/glb'), name='static')

@app.get('/')
def viewer():
    return FileResponse('ar_web_viewer/index.html')
