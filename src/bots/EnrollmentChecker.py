#------------------------------ imports --------------------------------

# standard modules
import traceback

# intra-project modules
from splinterbot.bot import Bot, LoginManager
from splinterbot.plugins import Gmail as GmailPlugin
from sites.myred import MyRedBrowser

# external libraries
from splinter.exceptions import ElementDoesNotExist

#-----------------------------------------------------------------------


class EnrollmentChecker(Bot):

    def __init__(self):
        self.logins = LoginManager()

    def run(self):
        """Checks MyRED to see if classes in the shopping cart for next
        semester are open or closed."""

        # get login details from terminal
        self.logins['myred'] = LoginManager.ask('NUID',
                                                'MyRED Password')

        # set up gmail for notifications
        self.logins['gmail'] = LoginManager.ask('Gmail Address',
                                                'Gmail Password')
        self.attach_plugin(GmailPlugin(*self.logins['gmail']))

        # Send a non-error email to verify it's working
        #self.plugins['gmail'].send_email(
        #    'EnrollmentChecker process has started.')

        strikes = 0  # three webdriver exception's and we'll shut down
        while True:

            # get the open/closed status of the shopping cart classes
            try:
                cart = self.check_shopping_cart()
                self.print_cart(cart)

            # handle exceptions
            except ElementDoesNotExist as e:
                strikes += 1
                if strikes >= 3:
                    self.handle_exception(e)
            except Exception as e:
                self.handle_exception(e)
            else:
                strikes = 0

            # wait until the next run
            self.wait(60 * 5)

    def handle_exception(self, e):
        traceback.print_exc()
        msg = '{0} - {1}'.format(type(e).__name__, e)
        self.plugins['gmail'].send_email(msg)
        exit()

    @staticmethod
    def print_cart(cart):
        print('----')
        printBuffer = ['{0}: {1}'.format(cartClass[0], cartClass[1])
                       for cartClass in cart]
        print('\n'.join(printBuffer))
        print('----')

    def notify_of_status(self, cart):
        for course in cart:
            if course[1] != 'Closed':
                self.plugins['gmail'].send_email('{0}: {1}'.format(course[0],
                                                                   course[1]))

    def check_shopping_cart(self):
        # create a driver for Wells Fargo
        with MyRedBrowser() as browser:

            # go to wellsfargo.com and login
            browser.nav_home()
            browser.login(*self.logins['myred'])

            browser.nav_to_enrollment_planner()

            with browser.get_panel_browser() as panelBrowser:
                panelBrowser.nav_to_shopping_cart()
                panelBrowser.choose_semester(1)

                return panelBrowser.parse_shopping_cart()


if __name__ == "__main__":
    EnrollmentChecker().run()
