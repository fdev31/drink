Feature: Login

Scenario: Basic authentication
    Given I connect to /login
    Then I expect HTML
    When I select login_form form
    When I set login_name = admin
    When I set login_password = admin
    When I submit
    Then I expect HTML
