# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

# Imports from default library
import re
import time
from random import randint
from operator import attrgetter


SELENIUM_PATH = "/path/to/selenium"

### GLOBAL VARIABLES ###
PAGE_WAIT_TIME = 2.5 # global wait for page to load time
ACTION_WAIT_TIME = 0.07 # global wait-for-action-before-another time


## CONTAINER 
OBJ_LIST = [] # Array for all Item objects.
ITEMS_LIST = [] # Array with items available to be bought in in-game store.

PRICE_RE = r"\d+"

# Default titles of items, costs and yelds as I could not find a way to scrape them all on the fly, as some are unavailable 
ITEMS_COSTS = [
    {'title': 'Rubber Stamp', 'price': 9, 'yield': 2},
    {'title': 'Accountant', 'price': 32, 'yield': 7},
    {'title': 'Money Press', 'price': 920, 'yield': 213 },
    {'title': 'Bribe', 'price': 5000, 'yield': 1190},
    {'title': 'Mint', 'price': 86000, 'yield': 20975 },
    {'title': 'Espionage', 'price': 395000, 'yield': 98750 },
    {'title': 'Black Op', 'price': 2860000, 'yield': 733333 },
    {'title': 'Propaganda Campaign', 'price': 79100000, 'yield': 20815789 },
    {'title': 'Insurance Fraud', 'price': 911000000, 'yield': 246216216 },
    {'title': 'Russian Oligarch', 'price': 9800000000, 'yield': 2722222222 },
    {'title': 'Invade North Korea', 'price': 16500000000, 'yield': 4714285714 },
    {'title': 'Invade Cuba', 'price': 87000000000, 'yield': 25588235294 },
    {'title': 'Commercial Bank', 'price': 372000000000, 'yield': 112727272727 },
    {'title': 'Invade Iran', 'price': 439000000000, 'yield': 137187500000 },
    {'title': 'Tech Company', 'price': 963000000000, 'yield': 321000000000 }
]

# CSS selectors for some specific elements
class CSS_SELECTORS:
    HELP_BUTTON = 'div.modal-footer button[type="submit"]'
    PRINT_BUTTON = 'button[title="Print 1 dollar"]'
    MONEY_TICKER = 'div.MoneyTicker_root__3zEPt > span.h1'
    # Used by get_items_list()
    ITEMS_SELECTOR_1 = 'div.Card_root__2V-y5.mb-4.border-0.card' 
    ITEMS_SELECTOR_2 = 'div.list-group.list-group-flush'
    BOUGHT_ITEMS_CONTAINER = 'div.Card_root__2V-y5.mb-4.border-0.card'
    BOUGHT_ITEMS_INCOME = 'div.mb-2.small'

'''
Item class. Self contained are:
* item's title
* item's buy price
* item's CSS selector
* item's yield value
* if item is avaiable to be bought
'''
class Item:
    # price_re = r"\d+"

    def __init__(self, title: str, buy_price: int, css_selector, yield_value: int, enabled: bool):
        self.css_selector = css_selector 
        self.title = title # Title of item
        self.buy_price = buy_price #  Price of item
        self.yield_value = yield_value #  How much cash it yields?
        self.enabled = enabled # Can item be bought?

    def __repr__(self):
        return 'Title: {} \n Buy price: {} \n Enabled: {}'.format(self.title, self.buy_price, self.enabled)

    # Return price-to-yield ratio of current price and yield.
    @property
    def price_to_yield_ratio(self):
        return self.buy_price / self.yield_value


    # Call it to buy selected item. 
    # Function sends "click" action to selected button which "aria-label" value
    # Matches title of item.
    def buy(self):
        click_button('button[aria-label="{}"]'.format(self.title), action='send_key')

    # Update current buy price after buying
    def update_buy_price(self):
        _buy_price_string = self.css_selector.find_element(By.CSS_SELECTOR, 'span[aria-label="price"]').text
        _buy_price_int = re.findall(PRICE_RE, _buy_price_string)
        self.buy_price = int("".join(_buy_price_int))

"""
Basic util wrapper to evaluate time neededd to run function.
"""
def evaluate_time(function):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = function(*args, **kwargs)
        t2 = time.time() - t1
        print("{} ran in {} s".format(function.__name__, t2))
        return result
    return wrapper


"""
Click button function.
Can send either normal, left-mouse click or enter because it seems some buttons need that.
"""
# @evaluate_time
def click_button(css_selector, action='click'):
    button = driver.find_element_by_css_selector(css_selector)
    if button:
        if action == 'click':
            button.click()
            pass
        elif action == 'send_key':
            button.send_keys('\n')
            pass

# Create chairman function. Simply inputs needed info on start screen, then rusches through by sending tabs and enters.
# @evaluate_time
def create_chairman(first_lastname):
    x = 0

    def _pass_click(value):
        actions.send_keys(value)
        actions.send_keys(Keys.TAB)
        actions.pause(ACTION_WAIT_TIME)

    
    click_button('button[type="button"]')
    actions = ActionChains(driver)
    input_fields = driver.find_elements_by_css_selector('input')
    for each in input_fields:
        if each.get_attribute('type') == 'text':
            _pass_click(first_lastname[x])
            x=+1
        elif each.get_attribute('type') == 'number':
            _pass_click(randint(10_000, 1_000_000))


    actions.send_keys(Keys.ENTER)
    actions.send_keys(Keys.TAB)
    actions.send_keys(Keys.ENTER)
    actions.perform()


# Return array of in-game store elements
# @evaluate_time
def get_items_list():
    _buy_list = driver.find_element_by_css_selector(CSS_SELECTORS.ITEMS_SELECTOR_1)
    # Each list item
    items_list = _buy_list.find_elements_by_css_selector(CSS_SELECTORS.ITEMS_SELECTOR_2)
    return items_list



# @evaluate_time
def assign_classes():
    # price_re = r"\d+"

    for item in ITEMS_LIST:
        # In each of in-game items element find button element, then get it's aria-label to get title of item 
        buy_button = item.find_elements_by_css_selector('button')[0]
        button_title = buy_button.get_attribute('aria-label')

        # If item is locked, we can't do anything with it!
        if button_title != 'Locked item':
            
            # If Item object already exists for given store item, skip it
            in_list = any(item.title == button_title for item in OBJ_LIST)
            
            if not in_list:
                _buy_price_string = buy_button.find_element(By.CSS_SELECTOR, 'span[aria-label="price"]').text
                _buy_price_int = re.findall(PRICE_RE, _buy_price_string)
                buy_price_int = int("".join(_buy_price_int))
                is_enabled = ('disabled' in buy_button.get_attribute('class').split(' '))
                if not is_enabled and not in_list:
                    OBJ_LIST.append(
                        Item(title=button_title, buy_price=buy_price_int, css_selector=buy_button,
                             yield_value=[each['yield'] for each in ITEMS_COSTS if each['title'] == button_title][0],
                             enabled=False))
                    print(f'Item added ({button_title})')
                elif is_enabled and not in_list:
                    OBJ_LIST.append(
                        Item(title=button_title, buy_price=buy_price_int, css_selector=buy_button,
                             yield_value=[each['yield'] for each in ITEMS_COSTS if each['title'] == button_title][0],
                             enabled=True))
                    print(f'Item added ({button_title})')


# Get current balance of player. 
# Either return string on actual float value.
# @evaluate_time
def get_current_balance(print_only=False):
    current_balance_str = CURRENT_BALANCE_OBJ.text
    _current_balance_clean = current_balance_str.replace(',', '')
    current_balance_float = float(_current_balance_clean.split('$')[-1])
    if print_only:
        return f'Balance: {current_balance_str}'
    return current_balance_float


# @evaluate_time
def evaluate_desired_item():

    # Calculate income per second of player
    def income_per_second(): # Income per second

        try:
            _bought_items_container = driver.find_elements_by_css_selector(CSS_SELECTORS.BOUGHT_ITEMS_CONTAINER)[1]
            bought_items_income = driver.find_element_by_css_selector(CSS_SELECTORS.BOUGHT_ITEMS_INCOME)
        except Exception:
            print('Failed to select yield.')
        else:
            try:
                income_text = bought_items_income.text
                # print(income_text)
                _text_slash = income_text.split('/')[0].split('$')[1]
                # _text_dollar = income_text.splip('/')[0].split('$')[1]
                income = int("".join(_text_slash.split(',')))
                return income
            except Exception:
                print('Failed to return yield as int.')
                
        
        print('Failed to get info from bought items container.')
        _balance_1 = get_current_balance()
        time.sleep(1)
        _balance_2 = get_current_balance()
        return _balance_2 - _balance_1 + 1



    # Temp desired item value.
    desired_item = {'title': None, 'score': None, 'buy_price': None}
    # Current income
    income = income_per_second()

    for item in OBJ_LIST:
        
        # For each item score is counted.
        # FIRST, difference between current buy price and balance is defined.
        # This difference is divided by calculated income.
        # This estimated how many seconds will it take to reach item.
        _seconds = (item.buy_price - get_current_balance()) / income
        

        # THEN score is calculated by dividing price-to-yield ratio of given item
        # (this is retrieved from Item's object) and divided by seconds needed
        # to pass to have enough funds for given item.
        # From items with simillar ration, the one which needs less seconds will win.
        _score = item.price_to_yield_ratio / _seconds + 1
        
        if desired_item['score'] == None or _score > desired_item['score']:
            desired_item['title'] = item.title
            desired_item['score'] = _score
            desired_item['buy_price'] = item.buy_price

    return desired_item

# Create chrome driver instance, pass chromedriver path, fetch the site
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--mute-audio")

first_lastname = input('Enter *space separated* first and last name to be used in game (leave blank to use default): ')
first_lastname = first_lastname.split(' ') if first_lastname != "" else ['Firstname', "Secondname"]

driver = webdriver.Chrome(executable_path=SELENIUM_PATH,
                          options=chrome_options)

with driver as driver:
    # global ITEMS_LIST
    global CURRENT_BALANCE_OBJ

    # Fetch the page, wait for it to load
    driver.get('https://thefed.app/')
    print(driver.current_url)
    time.sleep(PAGE_WAIT_TIME)

    # If URL is ok, create chairman, then wait a little.
    if driver.current_url == 'https://thefed.app/apply':
        create_chairman(first_lastname)
        time.sleep(PAGE_WAIT_TIME)

    # Again wait, dismiss info popup
    time.sleep(PAGE_WAIT_TIME-1)
    click_button(CSS_SELECTORS.HELP_BUTTON)

    # Fetch list of all items in shop
    ITEMS_LIST = get_items_list()
    
    CURRENT_BALANCE_OBJ = driver.find_element(By.CSS_SELECTOR, CSS_SELECTORS.MONEY_TICKER)

    # Run to the infinity
    while True:
        print(get_current_balance(print_only=True))
        assign_classes()

        # Evaluate desired item
        desired_item = evaluate_desired_item()
        print(f"Focusing on: {desired_item['title']}")

        # Until current balance is unmatched with current price of desired item, print money by clicking on "Print Money" button.
        while get_current_balance() < desired_item['buy_price'] + 2:
            
            click_button(CSS_SELECTORS.PRINT_BUTTON, action='send_key')
            
            # Have some sleep to not kill CPU.
            time.sleep(0.2)

        # This runs after player can afford item.
        # Loops through list of item elements, and if finds one where desired item's title and Item object title match, runs buy() method.
        for item in OBJ_LIST:
            if item.title == desired_item['title']:
                # Sleep to not kill CPU
                time.sleep(0.5)
                item.buy()
                print(f'Item bought: {desired_item["title"]}')
                # Update all prices
                item.update_buy_price()

                print(f'Updated buy price: {desired_item["buy_price"]}')
        # Wait to not kill CPU
        time.sleep(PAGE_WAIT_TIME-2)
