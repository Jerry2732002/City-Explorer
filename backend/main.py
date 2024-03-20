from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import recommendation,authentication

app = FastAPI()

#SET UP CORS HERE

# origin = ['your front end url here']
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origin,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
   
# )

@app.get('/')
def read_root():
    return {"message": "Welcome to City Explorer"}


app.include_router(recommendation.route,prefix="/api/weather")
app.include_router(authentication.route,prefix="/api/authentication")