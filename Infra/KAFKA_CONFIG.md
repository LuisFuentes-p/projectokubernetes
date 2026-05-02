# Kafka Configuration

## Topics Overview

### 1. **transactions**
- **Partitions**: 12
- **Replication Factor**: 3
- **Cleanup Policy**: delete
- **Retention**: 7 days (604800000 ms)
- **Producer**: TransactionProducer
- **Consumers**: PricingService, TransactionProcessor
- **Key**: commodity (gold, silver, oil)
- **Rationale**: Full transaction history; partitioned by commodity for locality

### 2. **prices**
- **Partitions**: 6
- **Replication Factor**: 3
- **Cleanup Policy**: compact
- **Min Cleanable Dirty Ratio**: 0.1
- **Producer**: PricingService
- **Consumers**: TransactionProcessor, PricingConsumer
- **Key**: commodity
- **Rationale**: Stores only latest price state; compacted topics remove old values

### 3. **transactions_processed**
- **Partitions**: 12
- **Replication Factor**: 3
- **Cleanup Policy**: delete
- **Retention**: 7 days (604800000 ms)
- **Producer**: TransactionProcessor
- **Consumers**: Consumer (stores in PostgreSQL)
- **Key**: commodity
- **Rationale**: Full history of processed transactions with enriched pricing data

### 4. **transactions_dlq** (Dead Letter Queue)
- **Partitions**: 6
- **Replication Factor**: 3
- **Cleanup Policy**: delete
- **Retention**: 14 days (1209600000 ms)
- **Key**: commodity
- **Rationale**: For debugging failed transactions; longer retention for investigation

## Partition Key Strategy

**Key**: `commodity`

All messages are keyed by commodity (gold, silver, oil) to ensure:
- Messages for the same commodity are routed to the same partition
- Maintains ordering within each commodity stream
- Enables efficient state management in processors

## Data Flow

```
TransactionProducer
    ↓ (commodity key)
[transactions topic]
    ├→ PricingService (aggregates demand)
    │   ↓ (commodity key)
    │  [prices topic]
    │
    └→ TransactionProcessor
        (joins with prices via poll)
            ↓ (commodity key)
        [transactions_processed topic]
            ↓
        Consumer (stores in PostgreSQL)
```

## Integration Notes

1. **Docker Initialization**: Kafka topics are created automatically when `docker-compose up` runs via the `kafka-topics-init` service
2. **Partition Keys**: All producers now use `commodity` as the partition key
3. **Consumer Groups**:
   - `pricing-service`: PricingService
   - `transaction-processor`: TransactionProcessor (transactions)
   - `transaction-processor-prices`: TransactionProcessor (prices)
   - `db-consumer-group`: TransactionConsumer
   - `price-db-consumer`: PricingConsumer

## Running the Cluster

```bash
cd Infra
docker-compose up -d
```

The `kafka-topics-init` service will automatically create all topics with the proper configuration.

## Verifying Topics

To manually verify topics (inside the kafka container):

```bash
# List all topics
kafka-topics.sh --list --bootstrap-server kafka:9092

# Describe a specific topic
kafka-topics.sh --describe --bootstrap-server kafka:9092 --topic transactions

# Check topic config
kafka-configs.sh --bootstrap-server kafka:9092 --describe --entity-type topic --entity-name transactions
```

## Cleanup Policy Details

- **delete**: Old messages are deleted based on retention time
- **compact**: Only the latest value for each key is retained, older values are removed
