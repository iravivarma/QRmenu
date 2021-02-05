from fastapi import FastAPI
from main import menu_router
from security import security_router
import uvicorn
from sqlalchemy.orm import Session
import crud, models, schemas
import uvicorn, time
from database import SessionLocal, engine
from fastapi import Request, Depends
#import logging
from qr_logger import create_or_get_logger, log_warning
from fastapi.middleware.cors import CORSMiddleware#, SessionMiddleware
from starlette.middleware.gzip import GZipMiddleware


filename = "pilot.log"
logging = create_or_get_logger(filename)
logging.getLogger(__name__)
logging.debug('This will get logged to a file')


app = FastAPI(title='workpeer',
        description='workpeer API',
        version='1.0.0', redoc_url = None,)


def init_routers(app: FastAPI) -> None:
    #app.include_router(home_router)
    app.include_router(menu_router, prefix='', tags=['menu'])
    app.include_router(security_router, prefix='', tags=['Security'])


def create_app() -> FastAPI:
    # config = get_config()
    # app = FastAPI(
        
    # )
    init_routers(app=app)
    # init_listeners(app=app)
    # check_vertexes(app=app)
    #app.add_middleware(DBSessionMiddleware, db_url=config.DB_URL)

    return app


app = create_app()



origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#app.add_middleware(SessionMiddleware,)
#app.middleware(GZipMiddleware, minimum_size=100000000000)


@app.on_event("shutdown")
async def on_shutdown():
    log_warning(logging, "quitting the application now\n\n\n\n")
    logging.close()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



"""
to store all the metadata of a request in a table.
1. origins/same or different
2. request packet size - content length
3. response packet size
4. type of request
5. request_method
6. content type
7. origin
8. referrer
9. browser name
10. destination path
11. device name
12. device ip address
13. if such api is called again and already stored in table, increment the count
14. datetime the request is requested.
15. reponse time
16. response datapacket size.



same_origin_yn = Column(Boolean)
    request_size = Column(Integer)
    response_size = Column(Integer)
    request_type = Column(String)
    request_method = Column(String)
    content_type = Column(String)
    origin = Column(String)
    referrer = Column(String)
    browser_name = Column(String)
    destination_path = Column(String)
    device_name = Column(String)
    ip_address = Column(String)
    datetime = Column(DateTime)
    execution_time = Column(Integer)
"""

async def get_request_data(request, response, db: Session = Depends(get_db)):
    
    #db = get_db()
    db = SessionLocal()
    analysis_dict = {}
    print('Content-length' in request.headers)
    analysis_dict['same_origin_yn'] = True#request.scope['sec-fetch-site'] if 'sec-fetch-site' in request.scope else 'same'
    analysis_dict['request_size'] = request.headers['Content-length'] if 'Content-length' in request.headers else 0
    analysis_dict['response_size'] = response.headers['content-length']
    analysis_dict['request_type'] = request.scope['type']
    analysis_dict['request_method'] = request.scope['method']
    analysis_dict['content_type'] = request.headers['content_type'] if 'content_type' in request.headers else ""
    analysis_dict['origin'] = request.headers['origin'] if 'origin' in request.headers else ""
    analysis_dict['referer'] = request.headers['referer'] if 'referer' in request.headers else ""
    analysis_dict['browser'] = 'chrome'
    analysis_dict['destination_path'] = request.headers['sec-fetch-mode']
    analysis_dict['device_name'] = ''
    analysis_dict['ip_address'] = ''
    analysis_dict['datetime'] = time.time()*1000
    analysis_dict['execution_time'] = response.headers["x-Process-Time"]
    # print("printing the analysis dict")
    # print(analysis_dict)


    crud.insert_request_response_data(db, analysis_dict)
    db.close()



@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    a middleware to find the time required for an api to process the data and
    getting the route of the api which is being executed...
    @parameters:
    request: contains all the details of the api requested
    ex:
        {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.1'}, 'http_version': '1.1', 
        'server': ('127.0.0.1', 5000), 'client': ('127.0.0.1', 61833), 'scheme': 'http', 'method': 'POST',
        'root_path': '', 'path': '/users', 'raw_path': b'/users', 'query_string': b'', 
        'headers': [(b'host', b'127.0.0.1:5000'), (b'connection', b'keep-alive'), (b'content-length', b'58'), 
        (b'accept', b'application/json'), (b'user-agent', b'Mozilla/5.0 (Windows NT 10.0; Win64; x64) 
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'), (b'content-type',
        b'application/json'), (b'origin', b'http://127.0.0.1:5000'), (b'sec-fetch-site', b'same-origin'), 
        (b'sec-fetch-mode', b'cors'), (b'sec-fetch-dest', b'empty'), (b'referer', b'http://127.0.0.1:5000/docs'),
        (b'accept-encoding', b'gzip, deflate, br'), (b'accept-language', b'en-US,en;q=0.9')], 
        'fastapi_astack': <contextlib.AsyncExitStack object at 0x00000185C3501088>, 
        'app': <fastapi.applications.FastAPI object at 0x00000185C08C2908>,
        'router': <fastapi.routing.APIRouter object at 0x00000185C33E8D88>, 
        'endpoint': <function create_user at 0x00000185C33CDE58>, 'path_params': {}}
    call_next: call_next starts analysing the request and the entire process of repsonse.

    @returns:
    response: just returns the api response and its execution time appended
    """
    start_time = time.time()
    request.headers.set_name = "krishna's page"
    response = await call_next(request)
    # print(await request.body())
    # print(request.headers)
    # print("printing the scopes.......")
    # print(request.scope)
    #print("#######################################################")
    path = request.scope['path']#[route for route in request.scope['router'].routes if route.endpoint == request.scope['endpoint']][0].path
    #this path variable derives the route of the api that is being accessed currently
    process_time = time.time() - start_time
    #print(f'Path is: {path}\nexecution time is {process_time}')
    logging.warning(f'Path is: {path}\nexecution time is {process_time}')
    #print("###########################################################")
    #print(process_time)
    print(request.headers)

    response.headers["X-Process-Time"] = str(process_time)
    #await get_request_data(request, response)
    #adds the total execution time to the response
    # print(response)
    # print(response.__dict__)
    # print(response.body_iterator)
    # print(response.headers)
    return response



if __name__ == "__main__":
    uvicorn.run("pilot:app", host="127.0.0.1", port=8000, reload=True)