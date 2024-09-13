from pydantic import BaseModel


class ProfanityCheck(BaseModel):
    message : str
    authKey : str

class ProfanityCheckResponse(BaseModel):
    response : str = "null"
    error : str = "null"
    auth : bool = False
    found : bool = False
    badWords : list = []
    severity : float = 0.0
class WordsAddingTemplate(BaseModel):
    wordsList : str

class SessionData(BaseModel):
    username : str
class WelcomeMessage(BaseModel):
    greeting : str = "welcome to our product"
    productName : str = "profilter"

class createUserTemplate(BaseModel):
    email : str
    password : str
class createUserResponse(BaseModel):
    response : str = "null"
    userCreation : str = "success"
    username : str = "could not get generated"

    creditBalance : float = 0.0
    creationDate : str = "null"
class demandTokenTemplate(BaseModel):
    password : str
    email : str
    productVersion : str | None = "beta"
    requestAmount : int
class tokenGenerationResponse(BaseModel):
    response : str = "null"
    status : str = "null"
    token : str = "null"
    requestLimit : int = 0
    issuedBy : str = "null"






