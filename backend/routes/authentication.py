from fastapi import APIRouter,HTTPException
from datetime import datetime, timedelta
from models.user import UserLogin,UserSignup
from database.user import login,signup
import jwt 
import bcrypt

route = APIRouter()

TOKEN_EXPIRE_MINUTES = 60
SALT = bcrypt.gensalt(10)
SECRET_KEY = "g5iv0jd5hi4hkf5iu8"
ALGORITHM = "HS256"

### API for user login

@route.post("/user_login", response_model= dict)
async def candidate_login(user: UserLogin) -> dict:
    try:
        login_info = await login(user.useremail)
        stored_password_hash = login_info["password"].encode()
        entered_password = user.password.encode()

        if not bcrypt.checkpw(entered_password, stored_password_hash):
            raise HTTPException(status_code=401, detail="Incorrect password")
        else:
            access_token = create_access_token(data={"email": user.email})
            return {"access_token": access_token, "token_type": "bearer"}

    except KeyError:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



## API for user signup 

@route.post("/user_signup", response_model= dict)
async def candidate_signup(user: UserSignup) -> dict:
    try:
        byte_password = bcrypt.hashpw(user.password.encode(), SALT)
        hashed_password = byte_password.decode()
        result = await signup(user.useremail, hashed_password,user.preferences)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")