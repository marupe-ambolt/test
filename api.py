
import uvicorn
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from argparse import ArgumentParser

from utilities.utilities import get_uptime
from utilities.logging.config import initialize_logging, initialize_logging_middleware

from ml.emily import Emily
from static.render import render
from starlette.responses import HTMLResponse


emily = Emily()

# --- Welcome to your Emily API! --- #
# See the README for guides on how to test it.

# Your API endpoints under http://yourdomain/api/...
# are accessible from any origin by default.
# Make sure to restrict access below to origins you
# trust before deploying your API to production.

parser = ArgumentParser()
parser.add_argument('-e', '--env', default='.env',
                    help='sets the environment file')
args = parser.parse_args()
dotenv_file = args.env
load_dotenv(dotenv_file)

app = FastAPI()

initialize_logging()
initialize_logging_middleware(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TrainItem(BaseModel):
    dataset_path: str
    save_path: str


@app.post('/api/train')
def train(item: TrainItem):
    return {'result': emily.train(item)}


class EvaluateItem(BaseModel):
    dataset_path: str
    model_path: str


@app.post('/api/evaluate')
def evaluate(item: EvaluateItem):
    return {'result': emily.evaluate(item)}


class PredictItem(BaseModel):
    sample: str
    model_path: str


@app.post('/api/predict')
def predict(item: PredictItem):
    return {'result': emily.predict(item)}


@app.get('/api')
def hello():
    return {
        "service": os.environ.get('COMPOSE_PROJECT_NAME'),
        "uptime": get_uptime()
    }


@app.get('/')
def index():
    return HTMLResponse(
        render(
            'static/index.html',
            host=os.environ.get('HOST_IP'),
            port=os.environ.get('CONTAINER_PORT')
        )
    )


if __name__ == '__main__':

    uvicorn.run(
        'api:app',
        host=os.environ.get('HOST_IP'),
        port=int(os.environ.get('CONTAINER_PORT'))
    )

