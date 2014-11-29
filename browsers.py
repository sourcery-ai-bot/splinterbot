#------------------------------ imports --------------------------------

# standard modules
# N/A

# intra-project modules
# N/A

# external libraries
from splinter.driver.webdriver.firefox import WebDriver as FirefoxWebDriver

#-----------------------------------------------------------------------


class WFBrowser(FirefoxWebDriver):

    def login(self, username, password):
        self.fill('userid', username)
        self.fill('password', password)

        btnSignon = self.find_by_id('btnSignon')
        btnSignon.click()
