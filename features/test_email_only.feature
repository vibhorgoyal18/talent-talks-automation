Feature: Email Verification for Interview Invite
  As an interviewer
  I want to verify the interview invitation email
  So that candidates receive the correct interview link

  @email @test
  Scenario: Verify interview email can be fetched
    Given I have Gmail credentials configured
    When I search for the latest interview invitation email
    Then I should find the email in inbox or spam
    And I should be able to extract the interview URL
