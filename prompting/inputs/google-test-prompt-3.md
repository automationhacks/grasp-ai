# MISSION

- Generate test cases to test google homepage
- Please cover the following areas
  - Functional cases for the web (desktop and tablet), mobile (responsive and native), and backend services.
  - Test input variations like valid inputs, invalid inputs, edge cases

# INPUT

1. Google home page is an app that takes the following inputs:

* `Search box`
*  User can either click on `Google search button` or `I'm feeling lucky button`

# STEPS

You can follow below examples while preparing the test case in csv format

- Test ID: FT-WEB-01
- Title: Test google search for valid search params
- Preconditions
  - Given google search page is loaded
- Steps:
  - When user types a valid search query in the search box
  - And clicks search button
- Expected Result
  - Then google search results page should show relevant results

# RESPONSE FORMAT

- CSV with columns as `Test ID`, `Title`, `Preconditions`, `Steps`, `Expected Result`
- If there are multiple steps ensure there is proper line break between them