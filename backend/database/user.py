from fastapi import HTTPException 
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from models.user import UserSignup


MONGODB_URI="mongodb+srv://jerrysebastian:jerrymongodb@cluster0.qdwqg8q.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGODB_URI)
db = client.cityexplorer
collection = db.user

async def login(email: str) -> dict:
    user_data = await collection.find_one({"useremail": email})

    if user_data:
        return user_data
    else:
        raise HTTPException(status_code=404, detail="User not found")    



async def signup(useremail: str, password: str, preferences: str) -> dict:
    user_data = UserSignup(
        useremail=useremail,
        password=password,
        preferences=preferences
    )
    result = await collection.insert_one(user_data.dict())

    if result.inserted_id:
        return {"message" : "User sign up successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to sign up user")
    
    
async def get_preferences(email: str) -> dict:
    user_data = await collection.find_one({"useremail": email})

    if user_data:    
        preferences = user_data.get("preferences")
        if preferences is not None:
            return preferences
        else:
            raise HTTPException(status_code=404, detail="Preferences not found for the user")
    else:
        raise HTTPException(status_code=404, detail="User not found")