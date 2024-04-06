from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import time
import re
import pandas as pd

#firefox profile directory containing cookies of web.whatsapp.com
firefox_profile = r"your-directory-goes-here"
#name of the chat to scrape
chat_name = "name-goes-here"
#scrape until this message text
stop_scrape = "message-text-goes-here"



url = r"https://web.whatsapp.com/"
df = pd.DataFrame(columns=["Date","Time","User","Message"])


options=Options()
options.add_argument("-profile")
options.add_argument(firefox_profile)
driver = webdriver.Firefox(options=options)

driver.get(url)

#waiting until page is loaded
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME,'_ak8l'))
    )
except:
    print("Error: page not loaded or class name not found")
    driver.quit()

element = driver.find_element(By.XPATH,"//*[contains(text(), '{}')]".format(chat_name))
element.click()
time.sleep(2)

#scrolling until "stop_scrape" is loaded
while True:
    time.sleep(1)
    try:
        element = driver.find_element(By.XPATH,"//*[contains(text(), '{}')]".format(stop_scrape))
        break
    except:
        driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div[4]/div/div[3]/div/div[2]').send_keys(Keys.PAGE_UP)   

#collecting messages
messages = driver.find_elements(By.XPATH,"//*[contains(@class, 'selectable-text copyable-text')]/span")
user_date = ""
message_text = ""
for x in messages:
    #extracting username and date
    try:
        user_date = str(x.find_element(By.XPATH,"../../../..//*[contains(@data-pre-plain-text, ' ')]").get_attribute('data-pre-plain-text'))
    except:
        pass
    #extracting message text
    try:
        message_text = str(x.get_attribute('innerHTML'))
    except:
        pass

    #cleaning up
    if user_date != "" and message_text != "":
        l = re.split(']|,',user_date)
        l[0]=l[0].replace("[","").strip()
        l[1]=l[1].strip()
        l[2]=l[2].replace(":","").strip()

        #adding a row to the dataframe
        new_row = {"Date":l[1],"Time":l[0],"User":l[2],"Message":str(message_text)}
        df.loc[len(df)] = new_row

    
    user_date = ""
    message_text = ""

#saving dataframe to csv
df.to_csv("Results.csv")

driver.quit()
exit(1)

