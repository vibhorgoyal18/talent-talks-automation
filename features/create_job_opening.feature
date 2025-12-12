Feature: Create Job Opening
  As an HR manager
  I want to create new job openings
  So that I can start the recruitment process for positions

  Background:
    Given I am logged in as a valid user
    And I navigate to the Create Job Opening page

  @ui @job
  Scenario Outline: Create a new job opening with different configurations
    When I create a job opening with "<scenario>" data
    Then the job opening should be created successfully

    Examples:
      | scenario           |
      | python_developer   |
      | java_developer     |
      | frontend_developer |

  @ui @job @smoke
  Scenario: Create a simple job opening
    When I enter job name "QA Engineer"
    And I enter job description "Looking for a QA Engineer with automation experience"
    And I set interview duration to 30 minutes
    And I enable resume evaluation with 50 percent
    And I add technology "Selenium"
    And I add technology "Python"
    And I add technology "Pytest"
    Then the Create Job Opening button should be enabled

  @ui @job @smoke
  Scenario: Verify newly created job opening appears in job openings list
    When I create a job opening with "python_developer" data
    Then the job opening should be created successfully
    When I navigate to View Job Openings page
    Then I should see the job opening "Python Developer" in the list
    And the job opening "Python Developer" should have status "Active"
