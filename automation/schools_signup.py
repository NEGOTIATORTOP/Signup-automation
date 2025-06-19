import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from .gmail_code_reader import get_latest_verification_code
from .captcha_solver import solve_captcha, solve_captcha_2captcha

PASSWORD = "asdf@000"
CAPTCHA_API_KEY = ""  # Optionally set your 2captcha API key

def get_chrome_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

async def automate_signup(creds):
    results_success = []
    results_failed = []
    for cred in creds:
        email = cred["email"]
        password = cred["password"]
        driver = None
        try:
            driver = get_chrome_driver()
            driver.set_page_load_timeout(40)
            driver.get("https://schools.myp2e.org/")
            time.sleep(2)
            # Click SIGN IN
            driver.find_element(By.XPATH, "//button[contains(.,'SIGN IN')]").click()
            time.sleep(2)
            # Click Sign up now
            driver.find_element(By.LINK_TEXT, "Sign up now").click()
            time.sleep(2)
            # Fill email and send code
            email_box = driver.find_element(By.NAME, "email")
            email_box.clear()
            email_box.send_keys(email)
            driver.find_element(By.XPATH, "//button[contains(.,'Send verification code')]").click()
            time.sleep(7)
            # Get verification code from Gmail
            code = get_latest_verification_code(email, password)
            if not code:
                results_failed.append(email)
                driver.quit()
                continue
            code_box = driver.find_element(By.NAME, "code")
            code_box.clear()
            code_box.send_keys(code)
            driver.find_element(By.XPATH, "//button[contains(.,'Verify code')]").click()
            time.sleep(2)
            # Password boxes
            driver.find_element(By.NAME, "newPassword").send_keys(PASSWORD)
            driver.find_element(By.NAME, "confirmPassword").send_keys(PASSWORD)
            # Check for captcha
            captcha_elements = driver.find_elements(By.CSS_SELECTOR, "img[alt*='captcha'], img[src*='captcha']")
            if captcha_elements:
                captcha_img = captcha_elements[0]
                captcha_img.screenshot("captcha.png")
                captcha_code = solve_captcha("captcha.png")
                if not captcha_code and CAPTCHA_API_KEY:
                    captcha_code = solve_captcha_2captcha("captcha.png", CAPTCHA_API_KEY)
                if captcha_code:
                    try:
                        captcha_input = driver.find_element(By.NAME, "captcha")
                        captcha_input.clear()
                        captcha_input.send_keys(captcha_code)
                    except Exception:
                        pass
                try:
                    os.remove("captcha.png")
                except Exception:
                    pass
            # Click Sign Up
            driver.find_element(By.XPATH, "//button[contains(.,'Sign Up')]").click()
            time.sleep(3)
            results_success.append(email)
        except Exception as ex:
            print(f"Signup failed for {email}: {ex}")
            results_failed.append(email)
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
        await asyncio.sleep(1)  # polite delay
    return results_success, results_failed
