from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from bs4 import BeautifulSoup
import os
import re
import pandas as pd
from time import sleep
from lxml import html


class ScrapingBrowser:
    path_to_the_browser = os.path.join('C:\Program Files (x86)', 'chromedriver.exe')

    def __init__(self, addr):
        self.driver = webdriver.Chrome(self.path_to_the_browser)
        self.driver.get(addr)

    def show_html(self):
        html_source = self.driver.page_source
        soup = BeautifulSoup(html_source, "html.parser")
        return soup

    def scroll_down(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)

    def scroll_to_the_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        sleep(1)

    def get_tree(self):
        source_page = self.driver.page_source
        tree = html.fromstring(source_page)
        return tree


