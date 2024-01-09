from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, WebDriverException, NoSuchElementException

import tkinter as tk
import time
from bs4 import BeautifulSoup

def OpenBrowser():
    browser_options = webdriver.ChromeOptions()
    browser_options.headless = True
    driver = Chrome(options=browser_options)

    return driver

def login(driver, url, username, password):
    driver.get(url)
    time.sleep(1)
    se_connecter = driver.find_element(By.LINK_TEXT, "SE CONNECTER")
    se_connecter.click()
    time.sleep(2)
    username_field = driver.find_element(By.NAME, "username")
    username_field.send_keys(username)

    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(password)
    time.sleep(1)
    login_button = driver.find_element(By.NAME, "login")
    login_button.click()
    time.sleep(3)

def GetData(driver, url, keywords, location) -> list:
    
    driver.get(url)

    keywords_field = driver.find_element(By.CSS_SELECTOR, "#mots")
    keywords_field.send_keys(keywords)

    wait = WebDriverWait(driver, 10)
    dropdown_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ui-multiselect")))
    dropdown_button.click()

    # Now, wait for the dropdown menu to appear and be visible
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ui-multiselect-menu")))

    # Replace 'OPTION_TEXT' with the text of the option you want to click
    option_to_select = wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), '{location}')]")))
    option_to_select.click()

    search_button = driver.find_element(By.CSS_SELECTOR, "button > h2")
    search_button.click()
    time.sleep(3)
   
    results = driver.find_element(By.CSS_SELECTOR, "#dmp-result")
    pages_numbers = None
    pages = None
    try:
        pages = results.find_element(By.CLASS_NAME, "pages")
        pages_numbers = pages.find_elements(By.CSS_SELECTOR, "a")
    except NoSuchElementException:
        print("Element with class 'pages' not found on the page.")
    
    number_of_pages = -1
    data = []

    if pages_numbers != None :
        try:
            pages_numbers = pages.find_elements(By.CSS_SELECTOR, "span")
        except NoSuchElementException:
            print("Element with class 'pages' not found on the page.")

        print("Only one page!")
        if len(pages_numbers) < 1:
            print("No results!")
            return data
        else:
            number_of_pages = 1


        
    # print("the latest page is: ", (pages_numbers[-2]).text)
    if number_of_pages < 0 :
        number_of_pages = 0

    for i in range(number_of_pages):
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        desired_text = str(i + 1)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//span[@class='current' and contains(text(), '{desired_text}')]"))
            )
        except TimeoutException:
            print("Timed out waiting for page to load")
        except WebDriverException as e:
            print("Error during navigation:", e)

        offers_list = soup.find_all(class_='rhover')

        for offer in offers_list:
            # Extract basic information using Beautiful Soup
            title = offer.find(class_='textbleu11bold')
            city = offer.find(class_='textgrisfonce9')
            description = offer.find(class_='textnoir9')
            details = offer.find(class_='ligdethover')

            offer_item = {
                "title": title.text if title else '',
                "city": city.text if city else '',
                "description": description.text if description else '',
                "details": details.text if details else ''
            }
            
            unique_identifier = offer.get('id')  # for example, use the 'id' attribute

            if unique_identifier:
                # Locate the corresponding Selenium WebElement
                try:
                    trigger_element = driver.find_element(By.ID, unique_identifier)
                    trigger_element.click()
                    WebDriverWait(driver, 1).until(EC.visibility_of_element_located((By.ID, "ui-dialog")))
                    # Extract the information from the pop-up
                    noselect_element = driver.find_element(By.ID, "noselect")
                    popup_text = noselect_element.text
                    offer_item["popup_text"] = popup_text
                    # except TimeoutException:
                    #     print("Timed out waiting for the pop-up to appear.")
                except NoSuchElementException:
                    print(f"Element with ID '{unique_identifier}' not found.")
                except WebDriverException as e:
                    print("Error during clicking on the element:", e)

            # Wait for the pop-up to appear
            try:
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-dialog")))
                # Extract the information from the pop-up
                noselect_element = driver.find_element(By.ID, "noselect")
                popup_text = noselect_element.text
                offer_item["popup_text"] = popup_text
            except TimeoutException:
                print("Timed out waiting for the pop-up to appear.")
            except NoSuchElementException:
                print("Pop-up element not found.")

            # Add to the data list
            data.append(offer_item)

            # Close the pop-up if necessary (adjust the selector or action as needed)
            close_button = driver.find_element(By.CSS_SELECTOR, ".ui-dialog-titlebar-close")
            close_button.click()

            # Additional wait to ensure the pop-up is closed before proceeding
            time.sleep(1)

        # Go to the next page
        desired_text = str(i + 2)
        if int(desired_text) <= number_of_pages:
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, desired_text)))
                attempts = 0
                max_attempts = 3
                while attempts < max_attempts:
                    try:
                        link_to_click = driver.find_element(By.LINK_TEXT, desired_text)
                        link_to_click.click()
                        break
                    except StaleElementReferenceException:
                        attempts += 1
                        time.sleep(1)
            except:
                print("failed to click on: ", desired_text)
        time.sleep(2)
    return data