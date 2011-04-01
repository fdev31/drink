Feature: Simple navigation

Scenario: First-level click on folder
    Given I'm logged-in as admin
    When I connect to /pages
    Then I expect HTML

Scenario Outline: Misc connection success
    Given I'm logged-in as admin
    When I connect to <url>
    Then I expect HTML

    Examples:
    | url |
    | /search |
    | /users |
    | /groups |
    | /pages |
