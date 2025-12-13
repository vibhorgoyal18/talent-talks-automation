Feature: Create Job Opening
  As an HR manager
  I want to create new job openings
  So that I can start the recruitment process for positions

  @ui @job @smoke @e2e
  Scenario Outline: Create job opening and verify it appears in the list
    Given I am logged in as a valid user
    And I navigate to the Create Job Opening page
    When I create a job opening with "<scenario>" data
    Then the job opening should be created successfully
    When I navigate to View Job Openings page
    Then I should see the job opening "<job_name>" in the list
    And the job opening "<job_name>" should have status "Active"
    When I schedule an interview for the job opening with "<scenario>" candidate data
    Then the interview should be scheduled successfully
    And the interview invitation email should be sent to "vibhorgoyal.talenttalks@gmail.com"

    Examples:
      | scenario           | job_name           |
      | python_developer   | Python Developer   |
      | java_developer     | Java Developer     |
      | frontend_developer | Frontend Developer |
