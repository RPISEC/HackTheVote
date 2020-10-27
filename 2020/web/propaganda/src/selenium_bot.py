import traceback
import signal

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait

timeout = 20

class SigHandler:
    kill = False
    def __init__(self):
        signal.signal(signal.SIGALRM, self._handle_timeout)

    def _handle_timeout(self, signum, frame):
        self.kill = True
        raise TimeoutError

def visit_webpage(url):
    sighandler = SigHandler()
    options = webdriver.ChromeOptions()
    options.add_argument('--js-flags="--jitless"')
    options.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=options)
    browser.set_page_load_timeout(timeout)
    # add cookie for domains the challenge is reachable on
    browser.get('http://propaganda.hackthe.vote:8000/thispagedoesnotexist')
    browser.add_cookie({"name": "flag", "value": "flag{unst0pp4ble_r3direct_m33ts_imm0v4ble_br0wser}", "httpOnly": False, "path": '/challenge'})
    browser.get('http://127.0.0.1:8000/thispagedoesnotexist')
    browser.add_cookie({"name": "flag", "value": "flag{unst0pp4ble_r3direct_m33ts_imm0v4ble_br0wser}", "httpOnly": False, "path": '/challenge'})
    # webdriverwait checks every 500ms
    try:
        browser.get(url)
        WebDriverWait(browser, 2.5).until(lambda x: False) # this just waits for the js timeout to end. I'm sure there's a better way but yeah
    except (WebDriverException, TimeoutException):
        pass
    except:
        if sighandler.kill:
            return 'Timed out :('
        print(traceback.format_exc())
        return 'Something unexpected happened, contact admin'
    finally:
        browser.quit()
    return 'Thank you for your submission, we will get back to you in 1-2 business years.'
