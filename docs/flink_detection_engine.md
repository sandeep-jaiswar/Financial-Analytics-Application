flowchart TB
 subgraph src["Data Sources"]
        trades[("Kafka Topic: Trades")]
        market[("Kafka Topic: MarketData")]
        fx[("Kafka Topic: FXRates")]
        iceberg[("Iceberg Tables - Historical Trades, Reference Data")]
  end
 subgraph input["Data Stream Preparation"]
        unify["Data Unifier(Join Trades + Market + FX)"]
        enrich["Data Enricher(Lookup Reference Data from Iceberg)"]
        validator["Schema Validator(Ensure consistency & completeness)"]
  end
 subgraph rules["Detection Pipelines"]
        ruleDetect["Rule-based Engine(Regulatory / Business Rules)"]
        anomalyDetect["Anomaly Detection(Z-score, Isolation Forest)"]
        patternDetect["Pattern Detector(Temporal event sequence)"]
        contextEnrich["Context Builder(Account / Trader / Desk Context)"]
  end
 subgraph output["Alert Generation"]
        alertGen["Alert Aggregator(Merge & deduplicate alerts)"]
        riskScore["Risk Scorer(Assign severity & confidence)"]
        formatter["Alert Formatter(JSON / Avro for downstream)"]
  end
 subgraph fde["Flink Detection Engine"]
    direction TB
        input
        rules
        output
  end
 subgraph sink["Downstream Outputs"]
        alertTopic[("Kafka Topic: ComplianceAlerts")]
        audit[("Iceberg Table: AlertAudit")]
        notif["Alert Dashboard / API Gateway"]
  end
    trades --> unify
    market --> unify
    fx --> unify
    iceberg --> enrich
    unify --> enrich
    enrich --> validator
    validator --> ruleDetect & anomalyDetect & patternDetect
    ruleDetect --> contextEnrich
    anomalyDetect --> contextEnrich
    patternDetect --> contextEnrich
    contextEnrich --> alertGen
    alertGen --> riskScore
    riskScore --> formatter
    formatter --> alertTopic & audit & notif

     trades:::source
     market:::source
     fx:::source
     iceberg:::source
     alertTopic:::alert
     audit:::alert
     notif:::alert
    classDef source fill:#2980b9,stroke:#fff,color:#fff
    classDef process fill:#8e44ad,stroke:#fff,color:#fff
    classDef store fill:#f39c12,stroke:#fff,color:#fff
    classDef api fill:#27ae60,stroke:#fff,color:#fff
    classDef alert fill:#e74c3c,stroke:#fff,color:#fff
    classDef external fill:#9b59b6,stroke:#fff,color:#fff


