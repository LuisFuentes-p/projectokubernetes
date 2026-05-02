#!/bin/bash

REPLICATION_FACTOR="${KAFKA_REPLICATION_FACTOR:-1}"

if [ "$REPLICATION_FACTOR" -gt 1 ]; then
  echo "Requested replication factor $REPLICATION_FACTOR requires a multi-broker Kafka cluster."
  echo "This compose stack runs a single Kafka broker, so topic creation will use replication factor 1."
  REPLICATION_FACTOR=1
fi

# Topic: transactions
# Policy: delete, retention: 7 days
kafka-topics.sh --create \
  --bootstrap-server kafka:9092 \
  --topic transactions \
  --if-not-exists \
  --partitions 12 \
  --replication-factor "$REPLICATION_FACTOR" \
  --config retention.ms=604800000 \
  --config cleanup.policy=delete

# Topic: prices
# Policy: compact (latest state only)
kafka-topics.sh --create \
  --bootstrap-server kafka:9092 \
  --topic prices \
  --if-not-exists \
  --partitions 6 \
  --replication-factor "$REPLICATION_FACTOR" \
  --config cleanup.policy=compact \
  --config min.cleanable.dirty.ratio=0.1

# Topic: transactions_processed
# Policy: delete, retention: 7 days
kafka-topics.sh --create \
  --bootstrap-server kafka:9092 \
  --topic transactions_processed \
  --if-not-exists \
  --partitions 12 \
  --replication-factor "$REPLICATION_FACTOR" \
  --config retention.ms=604800000 \
  --config cleanup.policy=delete

# Topic: transactions_dlq (Dead Letter Queue)
# Policy: delete, retention: 14 days
kafka-topics.sh --create \
  --bootstrap-server kafka:9092 \
  --topic transactions_dlq \
  --if-not-exists \
  --partitions 6 \
  --replication-factor "$REPLICATION_FACTOR" \
  --config retention.ms=1209600000 \
  --config cleanup.policy=delete

echo "Kafka topics initialized successfully!"
