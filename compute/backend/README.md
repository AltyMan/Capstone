# Purpose
Backend of Habit Tracking System
https://testdriven.io/blog/flask-pytest/#code-coverage

## To Implement
- [x] SQlite Database for Habits
- [ ] Better REST API Endpoints
- [ ] Streaks/Analytic Systems
- [ ] Documentation
- [x] Design proper schema for SQlite
- [ ] Testing client for Flask .test_client()
- [ ] Heatmaps
- [ ] CPM for deciding task times
- [ ] Chat ML Guidance?
    - predict habit completion probability
    - detect habit decay
    - recommend optimal reminder times
    - classify self-reported vs device habits
- ActivityWatch data format (https://docs.activitywatch.net/en/latest/buckets-and-events.html)
- [ ] pydantic/pytest?

# HabitRepository
purpose is to segment responsibilites, Habit should not be a scheduler, datastore, and logger.
https://github.com/vklap/py_ddd_framework