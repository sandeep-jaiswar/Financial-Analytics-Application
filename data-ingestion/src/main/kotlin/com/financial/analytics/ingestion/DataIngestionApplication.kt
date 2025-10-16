package com.financial.analytics.ingestion

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class DataIngestionApplication

fun main(args: Array<String>) {
    runApplication<DataIngestionApplication>(*args)
}
