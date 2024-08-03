from dotenv import load_dotenv
import os

load_dotenv() 

class Config:
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
