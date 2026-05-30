# Load Testing

Locust was used to test the deployed `/predict` endpoint with multipart image uploads.

Final run:

```text
Users: 10
Spawn rate: 2 users/second
Duration: 60 seconds
Total requests: 52
Failures: 0
Average response time: 9096.11 ms
95th percentile: 12000 ms
Conclusion: STABLE
```

The required assignment report is in `bscs23020_lt_mlops.txt`.
