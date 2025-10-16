object Versions {
    const val kotlin = "1.9.22"
    const val springBoot = "3.2.2"
    const val springDependencyManagement = "1.1.4"
    const val kotlinLogging = "3.0.5"
    const val clickhouseJdbc = "0.6.0"
    const val kotlinxCoroutines = "1.7.3"
    const val commonsMath = "3.6.1"
    const val junit = "5.10.1"
}

object Libs {
    // Kotlin
    const val kotlinStdlib = "org.jetbrains.kotlin:kotlin-stdlib"
    const val kotlinReflect = "org.jetbrains.kotlin:kotlin-reflect"
    const val kotlinLogging = "io.github.microutils:kotlin-logging-jvm:${Versions.kotlinLogging}"
    
    // Coroutines
    const val kotlinxCoroutinesCore = "org.jetbrains.kotlinx:kotlinx-coroutines-core:${Versions.kotlinxCoroutines}"
    const val kotlinxCoroutinesTest = "org.jetbrains.kotlinx:kotlinx-coroutines-test:${Versions.kotlinxCoroutines}"
    
    // Spring Boot
    const val springBootStarterWeb = "org.springframework.boot:spring-boot-starter-web"
    const val springBootStarterValidation = "org.springframework.boot:spring-boot-starter-validation"
    const val springBootStarterDataJdbc = "org.springframework.boot:spring-boot-starter-data-jdbc"
    const val springBootStarterThymeleaf = "org.springframework.boot:spring-boot-starter-thymeleaf"
    const val springBootStarterTest = "org.springframework.boot:spring-boot-starter-test"
    
    // Jackson
    const val jacksonModuleKotlin = "com.fasterxml.jackson.module:jackson-module-kotlin"
    
    // Database
    const val clickhouseJdbc = "com.clickhouse:clickhouse-jdbc:${Versions.clickhouseJdbc}"
    
    // Math & Analytics
    const val commonsMath = "org.apache.commons:commons-math3:${Versions.commonsMath}"
    
    // Testing
    const val junitJupiter = "org.junit.jupiter:junit-jupiter:${Versions.junit}"
    const val kotlinTest = "org.jetbrains.kotlin:kotlin-test"
}
