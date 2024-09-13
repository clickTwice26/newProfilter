from datetime import datetime
from wsgiref.util import request_uri

from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse

from fastapi import FastAPI, Depends, HTTPException, Request
from starlette.exceptions import HTTPException as StarletteHTTPException

# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from prof.validators import *
import prof.schemas as SCHEMAS
from prof.program import *
import prof.handler as HANDLER

# app = FastAPI(
#     title="profiler - abusive word detector",
#     docs_url=True, redoc_url=True
# )
app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")
SQLALCHEMY_DATABASE_URL = "sqlite:///./database/test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class WordsStorage(Base):
    __tablename__ = "wordsStorage"
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, index=True)  # Ensure this column is created

class APIStatus(Base):
    __tablename__ = "apiStatus"
    id = Column(Integer, primary_key=True, index=True)
    authKey = Column(String, index=True, unique=True)
    queryCount = Column(Integer, index=True, default=0)
    limitCount = Column(Integer, default=500)
    username = Column(String, index=True)

class UserData(Base):
    __tablename__ = "userData"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), index=True, unique=True)
    password = Column(String(200))
    email = Column(String(200), index=True, unique=True, nullable=False)
    creditBalance = Column(Float, default=100)
    creationTime = Column(DateTime, default=datetime.now)
    # oneTimeToken = Column(String(200), unique=True, nullable=False)
class AllRequests(Base):
    __tablename__ = "allRequests"
    id = Column(Integer, primary_key=True, index=True)
    authKey = Column(String, index=True)
    message = Column(String)
    response = Column(String)
class SystemEconomy(Base):
    __tablename__ = "systemEconomy"
    id = Column(Integer, primary_key=True, index=True)
    totalIssuedCredit = Column(Integer)
    totalDilutedCredit = Column(Integer)
    productVersion = Column(String(20), index=True, nullable=False)
    perRequestPrice = Column(Float, default=0.35)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.exception_handler(StarletteHTTPException)
async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return PlainTextResponse("nothing found", status_code=404)
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)
@app.get("/")
async def root():
    return SCHEMAS.WelcomeMessage()
@app.post("/profCheck")
async def profCheck(checkBox : SCHEMAS.ProfanityCheck, db: Session = Depends(get_db)):
    allWords = db.query(WordsStorage).all()
    words = [word.word for word in allWords]
    keyList = db.query(APIStatus).all()
    keys = [key.authKey for key in keyList]

    if checkBox.authKey in keys:
        apiLog = db.query(APIStatus).filter_by(authKey=checkBox.authKey).first()
        # print(apiLog.queryCount)
        if apiLog != None:
            if apiLog.queryCount >= apiLog.limitCount:

                checkedResponse = SCHEMAS.ProfanityCheckResponse(response="null", auth=True, error="request limit exceeded")

            else:
                found, zlist, severity = HANDLER.search(checkBox.message, words)  # Passing list of words
                apiLog.queryCount += 1
                db.commit()
                checkedResponse = SCHEMAS.ProfanityCheckResponse(response="ok", auth=True, found=found, badWords=zlist, severity=severity)

        else:
            checkedResponse = SCHEMAS.ProfanityCheckResponse(response="null", auth=False, error="authkey not found")

    else:
        checkedResponse = SCHEMAS.ProfanityCheckResponse(response="ok", auth=False)

    return checkedResponse.model_dump()
# @app.post("/wordAdd")
# # async def addWord(wordsAdd : SCHEMAS.WordsAddingTemplate, db: Session = Depends(get_db)):
# async  def addword(db : Session = Depends(get_db)):
#     wordsAdd = open("env/vulgar.txt", "r").read().splitlines()
#     # wordsAdd = wordsAdd.wordsList.splitlines()
#     failed = 0
#     success = 0
#     for i in wordsAdd:
#         i = i.strip()
#         try:
#             newWord = WordsStorage(word=i)
#             db.add(newWord)
#             db.commit()
#
#             success = success + 1
#         except Exception as error:
#                 print(error)
#                 failed+=1
#     db.close()
#     return {"success": success, "failed": failed}


@app.post("/createUser")
async def get_token(userInfo : SCHEMAS.createUserTemplate, db : Session = Depends(get_db)):
    checkExist = db.query(UserData).filter(UserData.email == userInfo.email).first()
    creationResponse = SCHEMAS.createUserResponse()
    if checkExist is not None:
        creationResponse.response = "null"
        creationResponse.userCreation = "failed - already exists user. try with another email"
        return creationResponse
    else:
        try:
            selectedUsername = generateUsername(userInfo.email)
            newUser = UserData(
                username= selectedUsername,
                password=userInfo.password,
                email=userInfo.email,
                creditBalance=100
            )
            db.add(newUser)
            db.commit()
            creationResponse.response = "ok"
            creationResponse.username = selectedUsername
            creationResponse.creditBalance = 100
            return creationResponse
        except Exception as error:
            creationResponse.userCreation = f"failed - user creation failed {error}"
            db.rollback()
        finally:
            db.close()
        return creationResponse

@app.post("/generateToken")
async def generateToken(userCredentials : SCHEMAS.demandTokenTemplate, db : Session = Depends(get_db)):
    fetchedUserDetails = db.query(UserData).filter(UserData.email == userCredentials.email).first()
    productPrice = 0.35 #temporarily
    requestAmount = userCredentials.requestAmount
    response = SCHEMAS.tokenGenerationResponse()
    if fetchedUserDetails is None or fetchedUserDetails.email != userCredentials.email:
        response.response = "null"
        response.status = "authentication error"
        return response
    ableToby = productBuyingAbility(productPrice=0.35, requestAmount=requestAmount, balance=fetchedUserDetails.creditBalance)
    if ableToby != True:
        response.response = "null"
        response.status = "insufficient funds"
        return response
    requestedToken = getProductToken()
    newApi = APIStatus(
        authKey = requestedToken,
        queryCount = 0,
        username = fetchedUserDetails.username,
        limitCount = requestAmount,

    )

    try:
        fetchedUserDetails.creditBalance -= productPrice * requestAmount

        db.add(newApi)
        db.commit()
        response.response = "ok"
        response.status = "new token generated"
        response.token = requestedToken
        response.issuedBy = fetchedUserDetails.username
        response.requestLimit = requestAmount
        return response
    except Exception as error:
        print(error)
        response.response = "null"
        response.status = "error"
        return response

