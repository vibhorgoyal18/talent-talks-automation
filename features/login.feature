Feature: Login functionality
  As a site visitor
  I want to login
  So that I can access protected areas

  @ui @smoke
  Scenario Outline: Attempt to login with different credentials
    Given I open the login page
    When I sign in with "<scenario>"
    Then I should see "<expected_state>"

    Examples:
      | scenario      | expected_state |
      | valid_login   | success        |
      | invalid_login | error          |
