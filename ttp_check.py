import sys
import os
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import subprocess

chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--headless")
chrome_options.binary_location = "/usr/bin/google-chrome"
driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"), options=chrome_options)

driver.get("https://ttp.cbp.dhs.gov/schedulerui/schedule-interview/location?lang=en&vo=true&service=UP")
time.sleep(2)

airports = {
    'SFO': 'US34',
    'BOS': 'US190',
    'ANC': 'US10',
}
center_id_prefix = "centerDetails"

def check_loc(loc):
    res = None
    while True:
        try:
            driver.find_element(by=By.ID, value=center_id_prefix + loc).click()
            time.sleep(1)
            res = driver.find_element(by=By.CLASS_NAME, value="nextAppointment").text
            break
        except Exception as e:
            print(f"page load error, retry: {e}")
            time.sleep(1)
            continue

    if 'No appointments available for this location' == res:
        return None
    elif res.startswith('Next Available Appointment'):
        return res
    else:
        raise Exception("Unexpected formatting")

import argparse

parser = argparse.ArgumentParser("Global Entry")
parser.add_argument(
    "--airport_list",
    nargs="+",
    help="List of airport codes",
    required=True,
)
parser.add_argument(
    "--email_list",
    nargs="+",
    help="List of emails",
    required=True,
)
args = parser.parse_args()

airport_keys = airports.keys()
avail = {k: None for k in airport_keys}

found = False
for code in args.airport_list:
    result = check_loc(airports[code])
    avail[code] = result
    found = (not found) and (result != None)

if found:
    print("sending email")
    out_str = ""
    for code in args.airport_list:
        out_str += f"{code}:\n{avail[code]}\n\n"
    email_str = ', '.join(args.email_list)
    subprocess.run(f'echo "{out_str}" | mutt -s "Global Entry Appointment" -- {email_str}', shell=True)

driver.quit()
