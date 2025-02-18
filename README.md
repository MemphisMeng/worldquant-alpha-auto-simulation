build:
```
sam build --profile worldquant -u
```

deploy:
```
sam deploy --stack-name worldquant --no-fail-on-empty-changeset --capabilities CAPABILITY_NAMED_IAM --resolve-s3 --profile worldquant
```