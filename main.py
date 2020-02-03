"""
Automatic logger for trackable items on Geocaching website using Selenium and ChromeDriver.
Based on the version of your Chrome browser download and unzip the ChromeDriver: https://chromedriver.chromium.org/downloads.
Change the path self.selenium_path to where chromedriver is located.
Write your trackable codes each on one line.
Logger will check these 4 possible cases:
    1) TB does not exist
    2) TB is locked
    3) TB has been already logged
    4) TB has not been logged yet
"""

from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

from myCal import Datepicker

class Root(Tk):
    def __init__(self):
        self.selenium_path = 'C:/SeleniumDrivers/chromedriver'
        super(Root, self).__init__()
        self.title("Trackables loging by MasovyKnedlicek")
        self.geometry("650x400+1000+200")
        self.resizable(False, False)
        self.configure(background='#404040')

        # ----- LABELS -----
        self.styleLabel = ttk.Style()
        self.styleLabel.configure("BW.TLabel", foreground="white", background="#404040", font=("Helvetica 10 bold"))

        self.labelName = ttk.Label(self, text="Name: ", style="BW.TLabel")
        self.labelName.place(x=10, y=10)

        self.labelPassword = ttk.Label(self, text="Password: ", style="BW.TLabel")
        self.labelPassword.place(x=10, y=40)

        self.labelTrackables = ttk.Label(self, text="Trackables: ", style="BW.TLabel")
        self.labelTrackables.place(x=10, y=70)

        self.labelLog = ttk.Label(self, text="Log: ", style="BW.TLabel")
        self.labelLog.place(x=330, y=10)

        self.labelDate = ttk.Label(self, text="Date: ", style="BW.TLabel")
        self.labelDate.place(x=330, y=70)

        # ----- TEXTBOXES -----
        self.styleTextBox = ttk.Style()
        self.styleTextBox.configure("BW.TEntry", font=("Helvetica 10"))

        self.textBoxName = ttk.Entry(self, style="BW.TEntry", width=35)
        self.textBoxName.place(x=90, y=10)

        self.textBoxPassword = ttk.Entry(self, style="BW.TEntry", width=35, show="*")
        self.textBoxPassword.place(x=90, y=40)

        self.textBoxLog = Text(self, width=35, height=3, font='helvetica 10')
        self.textBoxLog.place(x=372, y=10)

        # ----- SCROLLEDTEXTS -----
        self.scrolledTrackables = ScrolledText(self, width=28, height=17, font=("Helvetica 10"))
        self.scrolledTrackables.place(x=90, y=70)

        self.scrolledInfoPrint = ScrolledText(self, width=38, height=15, font=("Helvetica 10"), bg="#d1e0e0")
        self.scrolledInfoPrint.place(x=335, y=140)

        # ----- BUTTONS -----
        self.styleButton = ttk.Style()
        self.styleButton.configure('C.TButton',
                  background='#ff6666',
                  font=('Helvetica', 12, 'bold'))

        self.buttonExecute = ttk.Button(self, text="Execute", style="C.TButton", underline=0, command=self.execute, width=10)
        self.buttonExecute.place(x=90, y=355)

        self.buttonExit = ttk.Button(self, text="Exit", style="C.TButton", underline=1, command=self.exit_window, width=10)
        self.buttonExit.place(x=205, y=355)

        # ----- CALENDAR -----
        self.mycalendar = Datepicker(self, entrywidth=12, entrystyle="BW.TEntry")
        self.mycalendar.place(x=372, y=70)

        # ----- CHECKBOX -----
        self.styleCheckBox = ttk.Style()
        self.styleCheckBox.configure("C.TCheckbutton", foreground="white", background="#404040", font=("Helvetica 10 bold"))

        self.checkShowBrowser = ttk.Checkbutton(self, text="Open Chrome", style="C.TCheckbutton", underline=0, variable=False)
        self.checkShowBrowser.invoke()
        self.checkShowBrowser.place(x=370, y=100)

    # ----- FUNCTIONS -----
    def execute(self):
        # --- TB list ---
        self.TBid = []
        self.trackable_list(self.TBid)

        # --- browser visibility ---
        if self.checkShowBrowser.instate(['selected']):
            self.BrowserVisible = True
        else:
            self.BrowserVisible = False

        # --- logging info ---
        self.User = self.textBoxName.get()
        self.Password = self.textBoxPassword.get()
        self.URL = 'https://www.geocaching.com/account/signin'

        if self.textBoxLog.index("end-1c") == '1.0':
            self.Log = 'Discovered. Thanks for sharing.'
        else:
            self.Log = self.textBoxLog.get("1.0", END)

        self.callBrowser()

    def callBrowser(self):
        # Selenium driver
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chromeOptions.add_experimental_option("prefs", prefs)
        if not self.BrowserVisible:
            chromeOptions.add_argument('headless')
        chromeOptions.add_argument("--disable-extensions")

        self.driver = webdriver.Chrome(self.selenium_path, options=chromeOptions)
        self.driver.get(self.URL)

        self.driver.find_element_by_id('UsernameOrEmail').send_keys(self.User)
        self.driver.find_element_by_id('Password').send_keys(self.Password)
        self.driver.find_element_by_id('SignIn').click()

        self.TBcount = 1
        self.TBLoggedCount = 0

        for TB in self.TBid:
            self.driver.get('https://www.geocaching.com/track/details.aspx?tracker=' + TB)

            if self.trackable_exists('Warning'):
                if self.driver.find_elements_by_xpath("//*[contains(text(), 'Found it? Log it! (locked)')]"):
                    self.result = ('{0}/{1} ... {2} locked'.format(self.TBcount, len(self.TBid), TB))
                else:
                    if self.trackable_not_logged('ctl00_ContentBody_InteractionLogLink'):
                        element = self.driver.find_element_by_id('ctl00_ContentBody_trLogIt')
                        div = self.driver.find_element_by_id('ctl00_ContentBody_LogLink')
                        # logging
                        TBlogLink = div.get_attribute('href')
                        self.driver.get(TBlogLink)
                        select = Select(self.driver.find_element_by_id('ctl00_ContentBody_LogBookPanel1_ddLogType'))
                        select.select_by_visible_text('Discovered It')
                        # Date
                        element = self.driver.find_element_by_id(
                            'ctl00_ContentBody_LogBookPanel1_uxDateFormatHint')  # date format
                        self.adjust_date(element.text, self.mycalendar.get())
                        self.driver.find_element_by_id('uxDateVisited').clear()
                        self.driver.find_element_by_id('uxDateVisited').send_keys(self.datum)
                        # TB code
                        self.driver.find_element_by_id('ctl00_ContentBody_LogBookPanel1_tbCode').clear()
                        self.driver.find_element_by_id('ctl00_ContentBody_LogBookPanel1_tbCode').send_keys(TB)
                        # Log
                        self.driver.find_element_by_id('ctl00_ContentBody_LogBookPanel1_uxLogInfo').send_keys(self.Log)
                        # Click
                        self.driver.find_element_by_id('ctl00_ContentBody_LogBookPanel1_btnSubmitLog').click()
                        # Count
                        self.result = ('{0}/{1} ... {2}   LOGGED'.format(self.TBcount, len(self.TBid), TB))
                        self.TBLoggedCount += 1
                    else:
                        element = self.driver.find_element_by_id('ctl00_ContentBody_InteractionLogLink')
                        if 'Logged on' in element.text:
                            self.result = ('{0}/{1} ... {2} logged already ({3})'.format(self.TBcount, len(self.TBid), TB,
                                                                                   element.text.split('Logged on')[
                                                                                       1].strip()))
                        else:
                            self.result = ('{0}/{1} ... {2} logged already'.format(self.TBcount, len(self.TBid), TB))
            else:
                self.result = ('%s does not exist!' % TB)

            self.TBcount += 1

            # Status
            self.scrolledInfoPrint.insert(END, self.result + "\n")
            self.scrolledInfoPrint.update()
            self.scrolledInfoPrint.see(END)

        self.scrolledInfoPrint.insert(END, "==========================\n")
        self.scrolledInfoPrint.insert(END, 'Logged in total: %s TB.\n' % (self.TBLoggedCount))
        self.driver.quit()



    def adjust_date(self, format, datum):
        fs = format[1:-1].split('.') #d.m.yyyy
        ds = datum.split('-') #24-12-2019

        if fs[0] == 'd':
            if ds[0][0] == '0':
                day = ds[0][1]
            else:
                day = ds[0]
        else:
            if ds[0][0] == '0':
                month = ds[0][1]
            else:
                month = ds[0]

        if fs[1].lower() == 'm':
            if ds[1][0] == '0':
                month = ds[1][1]
            else:
                month = ds[1]
        else:
            if ds[1][0] == '0':
                day = ds[1][1]
            else:
                day = ds[1]

        datum = ('{0}.{1}.{2}'.format(day, month, ds[2]))
        self.datum = datum

    def trackable_exists(self, Trida):
        try:
            element = self.driver.find_element_by_class_name(Trida)
            return False
        except NoSuchElementException:
            return True

    def trackable_not_logged(self, ID):
        try:
            element = self.driver.find_element_by_id(ID)
            return False
        except NoSuchElementException:
            return True

    def trackable_list(self, TBid):
        self.pocet = self.scrolledTrackables.index("end-1c")
        if self.pocet == '1.0':
            TBid = []
        else:
            for i in range(1, int(float(self.pocet))+1, 1):
                TBid.append(self.scrolledTrackables.get(0.0 + i, 0.6 + i)) # TB has only 6 characters
        TBid = [x for x in TBid if x != '']
        self.TBid = TBid

    def exit_window(self):
        self.destroy()
        #self.quit()



root = Root()

if __name__ == '__main__':
    root.mainloop()