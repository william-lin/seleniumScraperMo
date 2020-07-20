from seleniumScraperBasic import BasicBrowser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os
from selenium.common.exceptions import *
#NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementNotInteractableException, ElementClickInterceptedException


class Browser(BasicBrowser):
    ''' Using the BasicBrowser to further enhance the browser, including finding element and tab management.
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
        Sleepless helper function for self.act() where the action really takes place.
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


    def change_home_tab(self, handle):
        ''' (Tab management) Change home tab to handle
        '''
        
        self.home_tab = handle

    def get_window_handles(self ):
        ''' (Tab management) Return all open tabs (all windows handles) as a list
        '''
        
        return self.driver.window_handles

    def get_current_window_handle(self):
        ''' (Tab management) Return current active tab (window handle)
        '''        
        
        return self.driver.current_window_handle
    
    def openTab_JS(self, url, switch_tab=True, sleep_time=0.5):
        ''' (Tab management) Open url as a new tab
        '''
        
        if url == "":
            url = "about:blank"
        elif url[0:4] != 'http':
            url = "https://:" + url
        tab_already_open = self.get_window_handles()
        self.driver.execute_script('''window.open("''' + url + '''","_blank");''')
        updated_tab_list = self.get_window_handles()
        if len(updated_tab_list) - len(tab_already_open) == 1:
            new_tab = [x for x in updated_tab_list if x not in tab_already_open][0]
            if switch_tab:
                self.switchTab_JS(new_tab)
            return new_tab
        else:
            raise TabOpenException

    def closeTab_JS(self, handle=None, switch_back_home=True):   
        ''' (Tab management) Close current open tab, if not swith_back_home then let chrome decide 
        which tab to switch to.
        '''        
        
        #check for potential errors with hometab being closed
        if switch_back_home:
            if self.home_tab not in self.get_window_handles():
                raise NoSuchWindowException("Home tab DNE")
            elif self.home_tab == handle:
                raise TabCloseException("Can't switch back home when closing home: Do browser.change_home_tab() first")
            elif handle == None and self.get_current_window_handle() == self.home_tab:
                raise TabCloseException("Can't close current home tab and go back to it: Do browser.change_home_tab() first")
            
        #doing the actual closing
        if handle:
            if handle in self.get_window_handles():
                self.switchTab_JS(handle)
                self.driver.close()
            else:
                raise NoSuchWindowException("Tab to be close DNE")
            
        else:
            self.driver.close()
            
        #doing the actual switching
        if switch_back_home:
            self.switchTab_JS(self.home_tab)
        
    def closeAllOtherTabs_JS(self):
        ''' (Tab management) Close all open tabs except the current active tab in view; refine home to be the current
        active tab if home is closed.
        '''        
        if self.get_current_window_handle() != self.home_tab: #If not at home, change definition of home:
            self.change_home_tab(self.get_current_window_handle())
        handles_to_close = [x for x in self.get_window_handles() if x != self.home_tab]
        for handle in handles_to_close:
            self.closeTab_JS(handle)
            
    def closeAllExceptHome_JS(self):
        ''' (Tab management) Close all open tabs except the home tab.
        '''        
        if self.get_current_window_handle() != self.home_tab: #If not at home, go back home:
            self.switchTab_JS(self.home_tab)
        self.closeAllOtherTabs_JS()
        
        
    def switchTab_JS(self, handle):
        ''' (Tab management) Swich current tab view to the given handle.
        '''        
        self.driver.switch_to.window(handle)
        return handle


class TabOpenException(WebDriverException):
    pass

class TabCloseException(WebDriverException):
    pass

class TabSwitchException(WebDriverException):
    pass


if __name__ == '__main__':
    # Tab management test:
    yahoo, google,  bing= 'https://yahoo.com', 'https://google.com', 'https://bing.com'
    browser = Browser("about:blank")
    
    b = browser
    gg = b.openTab_JS(google)
    yy = b.openTab_JS(yahoo)
    bb = b.openTab_JS(bing)
    b.change_home_tab(bb)
    b.switchTab_JS(gg)
    input("Hit Return and only Bing will remain")
    b.closeAllExceptHome_JS()
    
    input("Hit Return Again to open three more tabs")
    gg = b.openTab_JS(google)
    yy = b.openTab_JS(yahoo)
    bb = b.openTab_JS(bing)
    b.change_home_tab(gg)   
    b.switchTab_JS(yy)
    input("Hit Return and only Yahoo will remain")
    b.closeAllOtherTabs_JS()