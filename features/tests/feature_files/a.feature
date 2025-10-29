@regression
Feature: validate a feature

  Background: common setup
    Given a common step

  @bvt
  Scenario: validate a scenario
    When I perform an action
    Then I should see the result

  Scenario: validate another scenario
    When I perform another action
    Then I should see a different result
