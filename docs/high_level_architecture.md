---
config:
  layout: elk
---
flowchart LR
 subgraph ext["External Data Sources"]
        trades[("Trade Events")]
        market[("Market Data")]
        ref[("Reference Data")]
  end
 subgraph kafka["Kafka Ingestion Layer"]
        topics{{"Kafka Topics"}}
        reg[("Schema Registry")]
  end
 subgraph tableflow["StreamTableSync (Table Abstraction Layer)"]
        schemaWatcher["Schema Watcher"]
        materializer["Materializer KafkaToIceberg"]
        compactor["Compactor"]
        metaDB[("Metadata Store")]
        api["Control Plane API"]
  end
 subgraph flink["Flink Real-Time Processing Layer"]
        rules["Rule-Based Processing"]
        anomaly["Anomaly Detection CEP/ML"]
        alertsTopic{{"alerts_topic"}}
  end
 subgraph iceberg["Apache Iceberg Storage & Query Layer"]
        tables[("Trade & Audit Tables")]
        compHist[("Compaction History")]
  end
 subgraph viz["Alerting & Visualization"]
        dash["Compliance Dashboards"]
        notif["Alert Manager and Workflow - Slack and Email"]
  end
    trades --> topics
    market --> topics
    ref --> topics
    topics --> schemaWatcher & rules
    schemaWatcher --> materializer
    materializer --> tables & metaDB
    compactor --> tables
    metaDB --> api
    api --> materializer
    tables --> rules & dash
    rules --> anomaly
    anomaly --> alertsTopic
    alertsTopic --> dash & notif
    compHist --> dash
     trades:::external
     market:::external
     ref:::external
     topics:::kafka
     reg:::kafka
     schemaWatcher:::tableflow
     materializer:::tableflow
     compactor:::tableflow
     metaDB:::tableflow
     api:::tableflow
     rules:::flink
     anomaly:::flink
     alertsTopic:::flink
     tables:::iceberg
     compHist:::iceberg
     dash:::viz
     notif:::viz
    classDef kafka fill:#9b59b6,stroke:#fff,color:#fff
    classDef tableflow fill:#2980b9,stroke:#fff,color:#fff
    classDef flink fill:#27ae60,stroke:#fff,color:#fff
    classDef iceberg fill:#f39c12,stroke:#fff,color:#fff
    classDef viz fill:#e74c3c,stroke:#fff,color:#fff
    classDef external fill:#7f8c8d,stroke:#fff,color:#fff
