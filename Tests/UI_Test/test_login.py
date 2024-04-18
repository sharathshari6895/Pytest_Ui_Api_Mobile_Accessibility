import pytest
from Tests.UI_Test.BaseTest import BaseTest
from Tests.configtest import init_driver, ui_data, assertion_data
import allure
from Tests.configtest import logger_setup, setup_pages
import logging


class TestLogin(BaseTest):

    # Test scenario for logging into the application with invalid credentials
    @pytest.mark.run(order=1)
    @allure.severity(allure.severity_level.NORMAL)
    def test_invalid_sign_in(self, setup_pages, ui_data, assertion_data, init_driver, logger_setup):
        logging.getLogger("root").info("Starting test_invalid_signin")
        allure.attach('Starting test_invalid_signin', attachment_type=allure.attachment_type.TEXT)
        driver, login_page, _, _ = setup_pages
        try:
            login_page.click_login(ui_data['userName'], ui_data['INVALID PASSWORD'])
            expected_url = assertion_data.get('expected_url')
            if expected_url is not None:
                assert driver.current_url == expected_url
            else:
                raise KeyError("Key 'expected_url' not found in assertion_data")
        except AssertionError as assertion_error:
            logging.getLogger('root').error(f"Assertion Error occurred: {assertion_error}")
            allure.attach(driver.get_screenshot_as_png(), name="Screenshot", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            logging.getLogger('root').error(f"Exception occurred: {e}")
            allure.attach(driver.get_screenshot_as_png(), name="Screenshot", attachment_type=allure.attachment_type.PNG)
            pytest.fail(f"Exception occurred: {e}")
        finally:
            logging.getLogger("root").info("Ending test_invalid_signin")
            allure.attach('Ending test_invalid_signin', attachment_type=allure.attachment_type.TEXT)

    # Test scenario for logging into the application with valid credentials
    @pytest.mark.run(order=2)
    def test_valid_sign_in(self, setup_pages, ui_data, assertion_data, logger_setup, init_driver):
        logging.getLogger("root").info("Starting test_valid_signin")
        allure.attach('Starting test_valid_signin', attachment_type=allure.attachment_type.TEXT)
        driver, login_page, _, _ = setup_pages
        logging.getLogger("root").info("Logging with valid credentials")
        allure.attach('Logging with valid credentials', attachment_type=allure.attachment_type.TEXT)
        self.login_and_assert(login_page, driver, ui_data, assertion_data)
        logging.getLogger("root").info("Ending test_valid_signin")
        allure.attach('Ending test_valid_signin', attachment_type=allure.attachment_type.TEXT)
