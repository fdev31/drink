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

Scenario Outline: Misc connection success
    Given I'm logged-in as admin
    When I connect to <url>
    Then I expect JSON

    Examples:
    | url |
    | /users/struct |
    | /groups/struct |
    | /pages/struct |

    | /users/actions |
    | /groups/actions |
    | /pages/actions |


Scenario Outline: "struct" connection failures
    Given I'm logged-out
    When I connect to <url>
    Then I expect JSON error

    Examples:
    | url |
    | /users/struct |
    | /groups/struct |

Scenario Outline: Misc anonymous user limitations checks
    Given I'm logged-out
    When I connect to <url>
    Then I expect empty content

    Examples:
    | url |
    | /pages/title |
    | /groups/title |
    | /groups/description |
    | /pages/title |
    | /pages/help/content |
    | /groups/users/title |
