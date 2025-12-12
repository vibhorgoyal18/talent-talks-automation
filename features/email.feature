Feature: Email inbox verification
  As a tester
  I want to read emails from Gmail inbox
  So that I can verify email notifications are received

  @email
  Scenario: Fetch latest emails from inbox
    Given I connect to Gmail inbox
    When I fetch the latest "5" emails
    Then I should see the email list

  @email
  Scenario: Search for specific email
    Given I connect to Gmail inbox
    When I search for emails with subject "TalentTalks"
    Then I should see matching emails
