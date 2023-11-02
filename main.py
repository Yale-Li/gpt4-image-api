import os
import requests
import time
import json

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc


load_dotenv()


options = uc.ChromeOptions()
options.headless = False
driver = uc.Chrome(options=options)
app = FastAPI()


class Payload(BaseModel):
    attachment: str
    prompt: str


@app.get("/start")
async def start_session():
    driver.get("https://chat.openai.com/")
    time.sleep(3)
    login_button = driver.find_element(By.XPATH, '//div[text()="Log in"]')
    login_button.click()
    time.sleep(3)

    # find email field
    email = driver.find_element(By.XPATH, '//input[@id="username"]')
    email.send_keys(os.getenv("EMAIL"))
    
    # Find Continuew button
    cont = driver.find_element(By.XPATH, '//button[text()="Continue"]')
    cont.click()
    time.sleep(1)

    # Find password field
    password = driver.find_element(By.XPATH, '//input[@name="password"]')
    password.send_keys(os.getenv("PASSWORD"))
    password.send_keys(Keys.ENTER)
    time.sleep(5)

    # Find the Okay, let’s go button
    okay_button = driver.find_element(By.XPATH, '//div[text()="Okay, let’s go"]')
    okay_button.click()

    SESSION_NAME = os.getenv("SESSION_TITLE")
    time.sleep(3)
    if SESSION_NAME:
        session_name = driver.find_element(By.XPATH, f'//div[text()="{SESSION_NAME}"]')
        session_name.click()
    else:
        gpt4_button = driver.find_element(By.XPATH, '//span[text()="GPT-4"]')
        gpt4_button.click()

    # Setup OK
    return {"status": "Success", "result": "Selenium session started!"}


@app.post("/action")
async def perform_action(payload: Payload):
    try:
        image_filename = os.path.join("images", os.path.basename(payload.attachment))
        if payload.attachment.startswith('http'):
        
            # Download the image from the provided URL
            response = requests.get(payload.attachment, stream=True)
            response.raise_for_status()

            # Extract image filename and save inside 'images' folder
            with open(image_filename, "wb") as image_file:
                for chunk in response.iter_content(chunk_size=8192):
                    image_file.write(chunk)

        # open new chat
        # driver.get("https://chat.openai.com/?model=gpt-4")
        # time.sleep(5)

        # Make the input file element visible
        driver.execute_script(
            'document.querySelector(\'input[type="file"]\').style.display = "block";'
        )

        # Send the local path of the downloaded image to the file input element
        upload = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
        upload.send_keys(os.path.abspath(image_filename))

        # Find prompt text area
        prompt = driver.find_element(By.XPATH, '//textarea[@id="prompt-textarea"]')
        prompt.send_keys(payload.prompt)

        # Find the submit button data-testid="send-button
        submit_button = driver.find_element(By.XPATH, '//button[@data-testid="send-button"]')
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(submit_button))
        prompt.send_keys(Keys.ENTER)

        # Wait the result
        time.sleep(5)
        regen_btn = (By.XPATH, "//div[contains(text(), 'Regenerate')]")
        WebDriverWait(driver, 120).until(EC.presence_of_element_located(regen_btn))

        # Get response
        code_elements = driver.find_elements(By.TAG_NAME, "code")
        answer = code_elements[-1].text.strip() if code_elements else None
        if not answer:
            answer_elements = driver.find_elements(
                By.CSS_SELECTOR, ".markdown.prose.w-full.break-words"
            )
            answer = answer_elements[-1].text.strip()

        final_resp = {"status": "Success", "result": {}}
        if answer:
            final_resp["result"] = answer

        # Cleanup
        # os.remove(os.path.abspath(image_filename))

        return final_resp

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/stop")
async def stop_session():
    driver.quit()
    return {"status": "Success", "result": "Selenium session closed!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000)
