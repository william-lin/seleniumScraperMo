from selenium import webdriver
from scraperMoConstants import CHROME_DRIVER_FILE
from bs4 import BeautifulSoup
from time import sleep
import os


class BasicBrowser():
    ''' Basic class that wraps most common methods of the selenium driver.
    url -> url to open when first starting browser;
    chromePath -> assume chrome browser file is in cwd unless otherwise specified;
    delay -> some websites require manual input before starting automation, use delay=True in that case.
    '''

    def __init__(self, url="about:blank", chromePath=None, delay=False):
        if not chromePath:
            chromePath = os.path.join(os.getcwd(), CHROME_DRIVER_FILE)        
        self.driver = self._driver_launch(chromePath)
        self.driver.get(url)
        if _delay:
            self._delay()
        self.home_tab = self.driver.window_handles[0] #This is the tab you opened with.
        

    def _driver_launch(self, chromePath):
        driver = webdriver.Chrome(chromePath)
        if driver:
            return driver
        else:
            raise BadChromePathException

        
    def _delay(self, message='Hit "Return" to continue...'):
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

    def get_url(self):
        return self.driver.current_url    
    
    def refresh(self, sleep_time=0):
        self.driver.refresh()
        sleep(sleep_time)
        
    def get_source(self, elem=None):
        ''' (Self Defined) Return the Page Source of the driver or the given element (using innerHTML)
        '''
        
        if elem:
            return elem.get_attribute('innerHTML')
        return self.driver.page_source

    def soupify(self, source=None):
        '''(Self Defined) Return a BeautifulSoup of the page source or of the given source.
        source can be a string of html or an element.
        '''
        
        if not source:
            soup = BeautifulSoup(self.driver.page_source)
        else:
            try:
                soup = BeautifulSoup(source)
            except TypeError:
                try:
                    soup = self.get_source(elem=source)
                except BadSourceException: 
                    return None
        return soup    

        
class BadChromePathException(Exception):
    pass

class BadSourceException(Exception):
    pass


if __name__ == '__main__':
    browser = BasicBrowser("http://google.com")
    browser.refresh(sleep_time=1)
    