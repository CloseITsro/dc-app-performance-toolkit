import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from util.conf import JIRA_SETTINGS
from util.api.jira_clients import JiraRestClient


def subtasks_navigation_plugin(webdriver, datasets):
    page = BasePage(webdriver)

    # finding a random subtask
    jira_api = JiraRestClient(JIRA_SETTINGS.server_url, JIRA_SETTINGS.admin_login, JIRA_SETTINGS.admin_password)
    subtasks = jira_api.issues_search(jql="issuetype = Sub-task", max_results=1, fields=['parent'])
    if not subtasks:
        raise Exception('No sub-task found in the test data. Please create a sub-task to test the Subtasks Navigation plugin.')
    subtask_key = subtasks[0]['key']

    @print_timing("subtasks_navigation_plugin")
    def measure():

        @print_timing("subtasks_navigation_plugin:elements_visible")
        def sub_measure():
            page.go_to_url(f"{JIRA_SETTINGS.server_url}/browse/{subtask_key}")
            page.wait_until_visible((By.ID, "summary-val"))  # Wait for summary field visible
            page.wait_until_visible((By.ID, "subtasks-navigation-panel"))  # Wait for you app-specific UI element by ID selector
            page.wait_until_visible((By.CLASS_NAME, "snp-progressbar-div"))
            page.wait_until_visible((By.ID, "issuetable"))
        sub_measure()

        @print_timing("subtasks_navigation_plugin:number_of_subtasks")
        # The number of sub-tasks visible in the table is equal to the number of the total number of sub-tasks of the parent issue.
        def sub_measure():
            subtask_parent_key = subtasks[0]['fields']['parent']['key']
            parent = jira_api.issues_search(jql=f"key = {subtask_parent_key}", max_results=1, fields=['subtasks'])[0]
            parent_subtasks_count = len(parent['fields']['subtasks'])
            page.go_to_url(f"{JIRA_SETTINGS.server_url}/browse/{subtask_key}")
            page.wait_until_visible((By.ID, "issuetable"))
            issue_table_rows_count = len(page.get_elements((By.CLASS_NAME, "issuerow")))
            assert issue_table_rows_count == parent_subtasks_count, "The number of issuerow elements is not equal to the number of issue subtasks."
        sub_measure()
    measure()
