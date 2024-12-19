# load_env_vars.py

# Import the required modules
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Access the environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Now you can use these keys in your code
print(OPENAI_API_KEY)  # For testing purposes (Make sure to avoid printing sensitive keys in production)
print(GITHUB_TOKEN)
