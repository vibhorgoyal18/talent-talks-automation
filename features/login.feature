Feature: Login functionality
  As a site visitor
  I want to login
  So that I can access protected areas

  @ui
  Scenario: Login with invalid credentials shows error
    Given I open the login page
    When I sign in with "invalid_login"
    Then I should see "error"

  @ui
  Scenario: Login with valid credentials redirects to dashboard
    Given I open the login page
    When I sign in with "valid_login"
    Then I should see "success"
