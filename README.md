# GPT4 Image Recognition API
Small tool using selenium to get a temporary API endpoint for the ChatGPT Image Input / image recognition feature.  
Very quickly made, you should not rely on this on prod.  
Should be deprecated as soon as we have access to official OpenAI endpoints.  
Works with google authentification. If you use a different login method, please modify the code for your usecase.  

# Installation
- Create venv, then clone the repo  
- Install requirements:  
`pip install -r requirements.txt`
- Define a `.env` file
> EMAIL=
> 
> PASSWORD=
> 
> SESSION_NAME=

# Usage
- Run FastAPI server: `python main.py`

## GET
`http://localhost:8000/start`  
Start a new session. Complete manually the login steps and press enter when asked.  
Wait for the OpenAI popup to display before pressing enter.  

`http://localhost:8000/stop`  
Stop the current session.  

`http://localhost:8000/action`  
Post an image file or URL with a prompt. Example:  
```
Request:
{
    "image": "https://www.reuters.com/resizer/NLk9k89J1tfmH-B7XKd598-6j_Y=/960x0/filters:quality(80)/cloudfront-us-east-2.images.arcpublishing.com/reuters/AHF2FYISNJO55J6N35YJBZ2JYY.jpg",
    "prompt": "Describe this image precisely."
}

Response:
{
    "status": "Success",
    "result": {
        "answer": "A night view of the Eiffel Tower illuminated, with its reflection visible in calm water in the foreground. The sky is dark blue, and there are two streetlights on either side of the scene."
    }
}
```


## Todo List:
1. recognize image formats
2. handle GPT error responses