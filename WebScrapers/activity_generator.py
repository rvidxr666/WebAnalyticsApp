from driver import ScrapingBrowser
from time import sleep
import random
import names
import randominfo
import sys
from randominfo import Person
import sqlite3


def activity_on_the_website(browser):
    n = 0
    while n != 5:
        n = random.randint(0, 10)

        if n == 5:
            break

        if n % 2 == 0:
            house_prices_link = browser.driver.find_element_by_xpath(
                '//a[contains(text(), "House-Prices")]').get_attribute("href")
            browser.driver.get(house_prices_link)
            sleep(3)
            answers = [1, 2, 3, "yes", "yes", "yes", "yes", "yes", 3, "no"]

            elems = browser.driver.find_elements_by_xpath('//input[contains(@class, "form-control")]')

            for i in range(len(elems)):
                elems[i].send_keys(answers[i])

            submit_button = browser.driver.find_element_by_xpath('//button[contains(text(), "Submit")]')
            browser.scroll_to_the_element(submit_button)
            submit_button.click()
        else:
            celebrity = browser.driver.find_element_by_xpath(
                '//a[contains(text(), "Identify the Celebrity")]').get_attribute("href")
            browser.driver.get(celebrity)

            amount_to_wait = random.randint(0, 10)
            sleep(amount_to_wait)

            send_picture_button = browser.driver.find_element_by_xpath('//input[contains(@name, "filename")]')
            send_picture_button.send_keys(r"C:\Users\maksi\Desktop\Python\Diploma\WebScrapers\static\rihanna.jpg")

            browser.driver.find_element_by_xpath('//button[contains(@type, "submit")]').click()

    logout_path = browser.driver.find_element_by_xpath('//a[contains(text(), "Logout")]').get_attribute("href")
    browser.driver.get(logout_path)
    return


def generating_properties(n):
    if n == 0:
        string_name = names.get_full_name(gender="m")
        gender = "m"
    else:
        string_name = names.get_full_name(gender="f")
        gender = "f"

    first_name, last_name = string_name.split(" ")
    email = randominfo.get_email()
    password = randominfo.random_password()

    return first_name, last_name, email, password, gender


def registering_activity(browser):
    browser.driver.get("http://localhost:5000/register")
    n = random.randint(0, 1)

    first_name, last_name, email, password, gender = generating_properties(n)

    elements = browser.driver.find_elements_by_xpath('//input[contains(@class, "form-control")]')
    for elem in elements:
        prprty = elem.get_attribute("id")

        if prprty == "name":
            elem.send_keys(first_name)

        if prprty == "surname":
            elem.send_keys(last_name)

        if prprty == "email":
            elem.send_keys(email)

        if prprty == "password":
            elem.send_keys(password)

        if prprty == "gender":
            elem.send_keys(gender)

    register_button = browser.driver.find_element_by_xpath('//button[contains(@type, "submit")]')
    register_button.click()
    logging_in(password, email, browser)

    activity_on_the_website(browser)


def logging_in(password, email, browser):
    elements = browser.driver.find_elements_by_xpath('//input[contains(@class, "form-control")]')
    for elem in elements:
        prprty = elem.get_attribute("id")

        if prprty == "email":
            elem.send_keys(email)

        if prprty == "password":
            elem.send_keys(password)

    login_button = browser.driver.find_element_by_xpath('//button[contains(@type, "submit")]')
    login_button.click()


def connect_to_db_retrieve_credentials():
    con = sqlite3.connect("../SourceApp/DBs/user.db")
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM user")
    amount_of_users = cur.fetchall()[0][0]

    n = random.randint(0, amount_of_users)

    cur.execute(f"SELECT email, password FROM user WHERE id = {n}")
    credentials = cur.fetchall()[0]
    email = credentials[0]
    password = credentials[1]

    return email, password


def login_activity(browser):
    email, password = connect_to_db_retrieve_credentials()
    logging_in(password, email, browser)
    activity_on_the_website(browser)


def main():
    browser = ScrapingBrowser("http://localhost:5000/login")
    n = random.randint(0, 4)
    print(n)

    if n == 0:
        registering_activity(browser)
    else:
        login_activity(browser)


if __name__ == "__main__":
    main()
