Test ID: RT-BACK-08
Title: Verify API response under network partition scenarios (New)
Preconditions: Simulate a network partition between the API and dependent services
Steps:
Disconnect the network to one or more dependent services.
Send a valid search request.
Expected Result: The API continues to serve partial responses with a clear error or warning about degraded functionality.

Test ID: RT-BACK-09
Title: Verify API's handling of stale cache scenarios (New)
Preconditions: Introduce stale or corrupted cache data for API responses
Steps:
Trigger a cached query by sending a previously searched term.
Monitor if the API detects and refreshes stale cache data.
Expected Result: The system refreshes or invalidates stale cache entries, ensuring accurate responses.

Test ID: RT-BACK-10
Title: Test response when dependent services return incorrect data (New)
Preconditions: Simulate incorrect or unexpected data from a dependent service (e.g., malformed suggestions).
Steps:
Send a search query dependent on the failing service.
Observe API behavior and logs.
Expected Result: The API filters out invalid data, logging the anomaly while maintaining functional responses.