flowchart LR
 subgraph src["Incoming Alerts"]
        alertsTopic[("Kafka Topic: ComplianceAlerts")]
        auditTable[("Iceberg Table: AlertAudit")]
  end
 subgraph ams["Alert Management & Investigation"]
    direction TB
        ingest["Alert Ingest Service - Consume & Deduplicate"]
        enrichment["Alert Enrichment - Add trader, desk, account context"]
        triage["Alert Triage Engine - Severity & Priority"]
        workflow["Investigation Workflow Manager - Assign, Escalate, Resolve"]
        rulesEngine["Policy Engine - Regulatory / Internal Rules"]
        notifier["Notification Service - Email, Slack, Pager"]
        logging["Audit Logger - Immutable logs, Iceberg"]
  end
 subgraph uiLayer["Compliance Officer Interface"]
        dashboard["Web Dashboard - Filter, Search, Sort, Drill-down"]
        api["REST / GraphQL API"]
  end
 subgraph storeLayer["Datastores"]
        alertsDB[("Operational Alert DB")]
        history[("Iceberg: Resolved Alerts History")]
  end
    alertsTopic --> ingest
    auditTable --> ingest
    ingest --> enrichment
    enrichment --> triage
    triage --> workflow
    workflow --> notifier & alertsDB & history
    rulesEngine --> triage & workflow
    dashboard --> alertsDB
    api --> alertsDB & workflow

     alertsTopic:::kafka
     auditTable:::kafka
     ingest:::process
     enrichment:::process
     triage:::process
     workflow:::process
     rulesEngine:::process
     notifier:::process
     logging:::process
     dashboard:::ui
     api:::ui
     alertsDB:::store
     history:::store
    classDef kafka fill:#9b59b6,stroke:#fff,color:#fff
    classDef process fill:#8e44ad,stroke:#fff,color:#fff
    classDef store fill:#f39c12,stroke:#fff,color:#fff
    classDef ui fill:#27ae60,stroke:#fff,color:#fff
    classDef alert fill:#e74c3c,stroke:#fff,color:#fff


