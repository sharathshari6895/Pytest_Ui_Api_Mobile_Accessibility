import os
import json
import requests
import configparser
import pytest
import logging

from axe_selenium_python import Axe
from selenium import webdriver
from typing import Dict, Any
from appium.webdriver.appium_service import AppiumService
from appium.options.common import AppiumOptions
from MobilePages.bigoven_favorite_recipes import BigOvenFavoriteRecipe
from MobilePages.bigoven_adding_new_recipe import BigOvenRecipeManager
from UI_Pages.cartPage import CartPage
from UI_Pages.checkoutPage import CheckoutPage
from UI_Pages.loginPage import LoginPage

current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, '..', 'Config', 'config.ini')
ui_data_path = os.path.join(current_dir, '..', 'Data', 'ui_data.json')
mobile_data_path = os.path.join(current_dir, '..', 'Data', 'mobile_data.json')
assertion_data_path = os.path.join(current_dir, '..', 'Data', 'asseration_data.json')
api_data_path = os.path.join(current_dir, '..', 'Data', 'api_data.json')


# Fixture to initialize a WebDriver instance based on the test parameter
@pytest.fixture(params=["chrome"], scope="function")
def init_driver(request):
    if request.param == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument('--log-level=3')  # Setting Chrome log level to 3 (info)
        driver = webdriver.Chrome(options=options)
        config = read_config()
        if not config or 'base_url' not in config:
            raise ValueError("BASE_URL not found in the config file.")
        base_url = config['base_url']
        driver.maximize_window()
        driver.get(base_url)
        yield driver
        driver.quit()


# Fixture to read configuration data from a UI config file
def read_config(ui_path=config_path, section='UI'):
    parser = configparser.ConfigParser()
    parser.read(ui_path, encoding='utf-8')
    if parser.has_section(section):
        config = dict(parser.items(section))
    else:
        raise ValueError(f"Section '{section}' not found in the config file.")
    return config


# Fixture to provide login data to test functions
@pytest.fixture
def ui_data():
    with open(ui_data_path, "r") as file:
        data = json.load(file)
    return data


# Fixture to provide assertion data to test functions
@pytest.fixture
def assertion_data():
    with open(assertion_data_path, "r") as file:
        assertionData = json.load(file)
    return assertionData


# Fixture to read API configuration data from an INI file
@pytest.fixture(scope='function')
def api_config_from_ini():
    return read_config_api(config_path)


# Fixture to read API configuration data from an INI file
def read_config_api(api_path):
    parser = configparser.ConfigParser()
    parser.read(api_path, encoding='utf-8')
    if parser.has_section('API'):
        config = dict(parser.items('API'))
    else:
        raise ValueError("Section 'API' not found in the config file.")
    return config


# Fixture to obtain an authentication token for API requests
@pytest.fixture(scope='function')
def auth_token(api_data_fixture, api_config_from_ini):
    api_config = api_config_from_ini
    response = requests.post(api_config['api_url'] + api_config['auth_end_point'],
                             json=api_data_fixture.get('auth_payload', {}))
    return response.json()["token"]


# Fixture to obtain a booking ID created through API requests
@pytest.fixture(scope='function')
def created_booking_id(api_data_fixture, auth_token, api_config_from_ini):
    api_config = api_config_from_ini
    response = requests.post(api_config['api_url'] + api_config['booking_base_end_point'],
                             json=api_data_fixture.get("booking_data", {}), headers={'Cookie': 'token=' + auth_token})
    assert response.status_code == 200, f"Failed to create booking. Status code: {response.status_code}"
    return response.json().get("bookingid", '')


# Fixture to provide API data to test functions
@pytest.fixture(scope='function')
def api_data_fixture():
    with open(api_data_path) as f:
        api_data = json.load(f)
    return api_data


#
# # Fixture to set up logging configuration before each test
@pytest.fixture(scope='function', autouse=True)
def logger_setup(request):
    # Configuring root logger
    logger_name = "root"
    root_logger = logging.getLogger(logger_name)
    root_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(name)s : %(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S %p')
    # Adding console handler for displaying logs in the console
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    root_logger.addHandler(ch)
    # Creating log folder and file
    fh = None
    log_folder = os.path.abspath(
        os.path.join(current_dir, '..', 'Log'))
    try:
        os.makedirs(log_folder, exist_ok=True)
        log_file = os.path.join(log_folder, 'test_logs.log')
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        root_logger.addHandler(fh)
    except Exception as e:
        print(f"Error creating log folder or file: {e}")
    root_logger.setLevel(logging.INFO)
    urllib3_logger = logging.getLogger('urllib3')
    urllib3_logger.setLevel(logging.ERROR)
    ch.setLevel(logging.ERROR)
    yield
    # Cleaning up log handlers to avoid duplicate log entries
    root_logger.removeHandler(ch)
    if fh:
        root_logger.removeHandler(fh)
        fh.close()


# Fixture to read configuration data from a Mobile config file
def read_config_mobile():
    config = configparser.ConfigParser()
    config.read(config_path)
    if 'Mobile' in config:
        mobile_config = config['Mobile']
        return mobile_config
    else:
        raise Exception("Mobile section not found in config.ini")


# Fixture to set up the Appium driver
@pytest.fixture(scope="function")
def appium_driver_setup():
    mobile_config = read_config_mobile()
    appium_service = AppiumService()
    appium_service.start()
    cap: Dict[str, Any] = {
        "deviceName": mobile_config['deviceName'],
        "platformName": mobile_config['platformName'],
        "automationName": mobile_config['automationName'],
        "appActivity": mobile_config['appActivity'],
        "appPackage": mobile_config['appPackage'],
        "auto_accept_alerts": mobile_config['auto_accept_alerts'],
        "unhandled_prompt_behavior": mobile_config['unhandled_prompt_behavior'],
        "timeout": mobile_config['timeout'],
        "noReset": mobile_config['noReset']
    }
    driver = webdriver.Remote(mobile_config['appium_server_url'], options=AppiumOptions().load_capabilities(cap))
    yield driver
    driver.quit()
    appium_service.stop()


# Fixture to provide Mobile data to test functions
@pytest.fixture
def mobile_data():
    with open(mobile_data_path, "r") as file:
        data = json.load(file)
        return data


# Fixture to initialize Appium pages for testing
@pytest.fixture(scope="function")
def setup_appium_pages(appium_driver_setup):
    appium_driver = appium_driver_setup
    big_oven_favoritePage = BigOvenFavoriteRecipe(appium_driver)
    big_oven_new_recipe = BigOvenRecipeManager(appium_driver)
    return appium_driver, big_oven_favoritePage, big_oven_new_recipe


# Fixture to set up pages for each test function
@pytest.fixture(scope="function")
def setup_pages(init_driver):
    driver = init_driver
    login_page = LoginPage(driver)
    cart_page = CartPage(driver)
    checkout_page = CheckoutPage(driver)
    return driver, login_page, cart_page, checkout_page


@pytest.fixture
def accessibility_driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


@pytest.fixture
def run_accessibility_test(accessibility_driver):
    def _run_accessibility_test(url):
        accessibility_driver.get(url)
        axe = Axe(accessibility_driver)
        axe.inject()
        results = axe.run()
        return results

    return _run_accessibility_test

@pytest.fixture
def read_config_accessibility():
    def _read_config_accessibility(custom_config_path):
        config = configparser.ConfigParser()
        config.read(custom_config_path)
        if 'Accessibility' in config:
            accessibility_config = config['Accessibility']
            return accessibility_config
        else:
            raise Exception("Accessibility section not found in config.ini")
    return _read_config_accessibility