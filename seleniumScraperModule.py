from seleniumScraperBasic import BasicBrowser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os
from selenium.common.exceptions import *
#NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementNotInteractableException, ElementClickInterceptedException


class Browser(BasicBrowser):
    ''' Using the BasicBrowser to further enhance the browser, including tab management.
    ''' 
    
    
    def get_links(self, elem=None):
        ''' Return a list of urls that appear as links in the node'''
        
        if not elem:
            elem = self.driver
        return [x.get_attribute('href') for x in elem.find_elements_by_tag_name('a')]

    def writeSoup(self, filename, extension="htm", source=""):
        ''' Save the webpage (or the given source) with the given filename in cwd.
        '''
        
        if source:
            soup = self.soupify(source)
        else:
            soup = self.soupify()
        
        fullname = filename + "." + extension
        if fullname in os.listdir(os.getcwd()):
            i = 1
            while 1:
                fullname = filename + "_" + str(i).rjust(3, "0") + "." + extension
                if fullname in os.listdir(os.getcwd()):
                    i += 1
                else:
                    
                    with open(fullname, 'w') as writer:
                        writer.write(soup.prettify())
                    print('Written: ' + '"' + fullname + '"')
                    return
        else:
            with open(fullname, 'w') as writer:
                writer.write(soup.prettify())
            print('Written: ' + '"' + fullname + '"')
            return          
    
        
    def act(self, elem_identifier, mode, timeout=3, retry=3, refresh=0, click=False, send_keys="", sleep_time=0):
        '''
        Giant wrapper for the find_elements_by_xxx included in the selenium driver, with wait build-in to prevent
        errors caused by long loading times.
        
        mode is one of ['CLASS_NAME', 'CSS_SELECTOR', 'SELECTOR', 'ID', 'LINK_TEXT', 'NAME', 'PARTIAL_LINK_TEXT', 'TAG_NAME', 'XPATH']
        elem_identifier is the xpath; css_selector...etc
        click: whether to click the element or not
        send_keys: what keys to send to the element
        
        See https://selenium-python.readthedocs.io/waits.html
        and https://stackoverflow.com/questions/26566799/wait-until-page-is-loaded-with-selenium-webdriver-for-python
        '''
        
        to_return = self._act(elem_identifier, mode, timeout=timeout, retry=retry, refresh=refresh, click=click, send_keys=send_keys)
        sleep(sleep_time)
        return to_return
    
    
    def _act(self, elem_identifier, mode, timeout=3, retry=3, refresh=0, click=False, send_keys=""):
        '''
        Sleepless helper function
        '''
        if mode == 'SELECTOR':
            mode = 'CSS_SELECTOR' #shorthand conversion
            
        element = None
        while retry > 0:
            try:
                element = WebDriverWait(self.driver, timeout).until(\
                    EC.presence_of_element_located((getattr(By, mode), elem_identifier)))
            except TimeoutException:
                if retry:
                    retry -= 1
                else:
                    message = "Error Processing (Max retry reached): " + elem_identifier + ": " + mode + "  (Hit 'Return'...)"
                    self.delay(message)
                    return None
            else:
                try:
                    if send_keys:
                        element.clear()
                        element.send_keys(send_keys)
                    if click:
                        try:
                            element.click()
                        except ElementClickInterceptedException: #special workaround for clicking events in the following:
                            if mode != 'CSS_SELECTOR' or mode != 'SELECTOR':
                                message = "Click intercepted: Try using CSS Selector!  (Hit 'Return'...)"
                                self.delay(message)
                            else:
                                # Courtesy: https://blog.csdn.net/WanYu_Lss/article/details/84137519 
                                # (scrapy解决selenium中无法点击Element：ElementClickInterceptedException_Python_WanYu_Lss的博客-CSDN博客)
                                elem = self.driver.find_elements_by_css_selector(elem_identifier)
                                self.driver.execute_script("arguments[0].click();", element)
                except ElementNotInteractableException:
                    message = "Cannot sendkeys/click!: Element Is Not Interactable!  (Hit 'Return'...)"
                    self.delay(message)
                else:
                    return element
            
            # Refresh and then retry once
            if refresh > 0:
                retry += 1
                refresh -= 1
                self.driver.refresh()
                sleep(2)
                
            else:
                return None