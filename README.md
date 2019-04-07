## Coins autoinvest

Autoconverts a set amount of Philippine Pesos to BTC every 15th and 30th of the month.

### Setup

1. Obtain your API key and secret from coins.ph
2. Create `.env.yaml` file at project root containing

```
COINS_API_KEY:
COINS_API_SECRET:
PHP_AMOUNT:
```

### Deployment

1. Deploy the cloud function

`gcloud functions deploy convert_PHP_to_BTC --runtime python37 --trigger-topic autoinvest_topic --env-vars-file .env.yaml`

2. Create a Cloud Scheduler job

* Frequency: `30 17 15,30 * *` (This executes every 15th and 30th of the month at 5:30PM.)
* Target: Pub/Sub
* Topic: autoinvest_topic
* Payload: type anything here it doesn't matter but it cannot be blank


