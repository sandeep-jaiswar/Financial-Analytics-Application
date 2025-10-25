flowchart LR
 subgraph ext["External Systems"]
        kafka[("Kafka Cluster")]
        registry[("Schema Registry")]
  end
 subgraph dataProc["Data Processing"]
        mat["Flink Materializer(Kafka→Iceberg sink)"]
        comp["Compactor(Optimize small files)"]
  end
 subgraph sts["StreamTableSync Service"]
    direction TB
        schemaWatcher["Schema Watcher(Detect schema updates)"]
        topicMapDB[("Topic↔Table Mapping DB")]
        metaStore["Metadata Store(Postgres / etcd)"]
        dataProc
        control["Control Plane API(REST/gRPC)"]
        audit["Audit Table(Iceberg)"]
        monitor["Monitoring & Metrics(Prometheus / Grafana)"]
  end
 subgraph iceberg["Apache Iceberg"]
        tables[("Managed Tables")]
        snapshots[("Snapshots / Versions")]
  end
    registry --> schemaWatcher
    kafka --> schemaWatcher & mat
    schemaWatcher --> topicMapDB & metaStore
    topicMapDB --> mat
    mat --> tables & audit & metaStore & monitor
    tables --> comp & snapshots
    comp --> tables & metaStore & monitor
    control --> schemaWatcher & mat & comp & metaStore & monitor
    audit --> snapshots

     kafka:::external
     registry:::external
     schemaWatcher:::service
     topicMapDB:::service
     metaStore:::service
     control:::service
     audit:::service
     monitor:::service
     tables:::store
     snapshots:::store
    classDef service fill:#2980b9,stroke:#fff,color:#fff
    classDef store fill:#f39c12,stroke:#fff,color:#fff
    classDef external fill:#9b59b6,stroke:#fff,color:#fff
    classDef api fill:#27ae60,stroke:#fff,color:#fff
    classDef process fill:#8e44ad,stroke:#fff,color:#fff
    classDef monitor fill:#e74c3c,stroke:#fff,color:#fff


