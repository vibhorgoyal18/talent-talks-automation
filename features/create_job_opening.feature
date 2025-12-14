Feature: Create Job Opening
  As an HR manager
  I want to create new job openings
  So that I can start the recruitment process for positions

  @ui @job @smoke @e2e
  Scenario Outline: Create job opening and verify it appears in the list
    Given I am logged in as a valid user
    And I navigate to the Create Job Opening page
    
    # Create Job Opening - Granular Steps
    When I load job opening data for "<scenario>"
    And I fill in "Job Opening Name" with value from scenario "job_name"
    And I fill in "Enter or paste job description" with value from scenario "job_description"
    And I set "Interview Duration (minutes)" to 30
    And I check the "Enable Resume Evaluation" checkbox
    And I set "Resume Evaluation Percentage" to 100
    And I click the "Create Job Opening" button
    And I wait for 2 seconds
    
    # Verify Job Opening in List
    When I navigate to View Job Openings page
    Then I should see the item stored as "created_job_name" in the list
    And the item stored as "created_job_name" should have status "Active"
    
    # Schedule Interview - Granular Steps
    When I load candidate data for "<scenario>"
    And I navigate to "/interviews/new" page
    And I select from "Select Job Opening" the value stored as "created_job_name"
    And I fill in "Candidate Name" with value from scenario "candidate_name"
    And I fill in "Candidate Email" with value from scenario "candidate_email"
    And I fill in "Interview Date" with tomorrow's date
    And I fill in "Interview Time" with "10:00"
    And I upload the file from "cv_file" to "Select CV File"
    And I click the "Schedule Interview" button
    And I wait for 2 seconds
    Then the interview invitation email should be sent to "vibhorgoyal.talenttalks@gmail.com"

    Examples:
      | scenario           | job_name           |
      | python_developer   | Python Developer   |
