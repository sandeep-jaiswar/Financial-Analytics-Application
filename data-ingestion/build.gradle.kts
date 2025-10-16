plugins {
    id("org.springframework.boot")
    id("io.spring.dependency-management")
    kotlin("plugin.spring")
    java
}

java {
    sourceCompatibility = JavaVersion.VERSION_21
    targetCompatibility = JavaVersion.VERSION_21
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter")
    implementation("org.springframework.boot:spring-boot-starter-data-jdbc")
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("com.clickhouse:clickhouse-jdbc:0.6.0")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin")
    implementation("com.fasterxml.jackson.datatype:jackson-datatype-jsr310")
    implementation("io.github.microutils:kotlin-logging-jvm:3.0.5")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    
    // Yahoo Finance API
    implementation("com.yahoofinance-api:YahooFinanceAPI:3.17.0")
    
    // Rate limiting
    implementation("io.github.resilience4j:resilience4j-ratelimiter:2.1.0")
    implementation("io.github.resilience4j:resilience4j-spring-boot3:2.1.0")
    
    // Logging
    implementation("org.slf4j:slf4j-api:2.0.9")
    
    // Scheduling
    implementation("org.springframework.boot:spring-boot-starter-actuator")
    
    // Retry mechanism
    implementation("org.springframework.retry:spring-retry:2.0.4")
    implementation("org.springframework:spring-aspects:6.1.3")
    
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.mockito:mockito-core:5.8.0")
    testImplementation("org.mockito:mockito-junit-jupiter:5.8.0")
    testImplementation("com.h2database:h2:2.2.224")
}

tasks.bootJar {
    enabled = true
}

tasks.jar {
    enabled = false
}
