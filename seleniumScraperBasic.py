from selenium import webdriver
from scraperMoConstants import CHROME_DRIVER_FILE
from time import sleep
import os


class BasicBrowser():
    ''' Basic class that wraps most common methods of the selenium driver.
    '''

    def __init__(self, url="about:blank", chromePath=None, delay=False):
        self.driver = self._driver_launch(chromePath)
        self.driver.get(url)
        if delay:
            self.delay()
        self.home_tab = self.driver.window_handles[0] #This is the tab you opened with.

    def _driver_launch(self, chromePath):
        driver = None
        if not chromePath:
            chromePath = os.path.join(os.getcwd(), CHROME_DRIVER_FILE)
        driver = webdriver.Chrome(os.path.join(chromePath))
        if driver:
            return driver

        
    def delay(self, message='Hit "Return" to continue...'):
        while 1:
            key = input(message)
            if key == '':
                break    
            
    def get(self, url, sleep_time=0):
        self.driver.get(url)
        sleep(sleep_time)
    
    def back(self, sleep_time=0):
        self.driver.back()
        sleep(sleep_time)
    
    def forward(self, sleep_time=0):
        self.driver.forward()
        sleep(sleep_time)
        
    def get_source(self, elem=None):
        if elem:
            return elem.get_attribute('innerHTML')
        return self.driver.page_source

    def get_url(self):
        return self.driver.current_url    
    
    def refresh(self, sleep_time=0):
        self.driver.refresh()
        sleep(sleep_time)



if __name__ == '__main__':
    browser = BasicBrowser("http://google.com")
    browser.refresh(sleep_time=1)
    