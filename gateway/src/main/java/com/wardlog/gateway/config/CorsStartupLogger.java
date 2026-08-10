package com.wardlog.gateway.config;

import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;
import org.springframework.web.cors.CorsConfiguration;

import java.util.Map;

@Component
@RequiredArgsConstructor
public class CorsStartupLogger implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(CorsStartupLogger.class);

    private final GlobalCorsProperties corsProperties;

    @Override
    public void run(ApplicationArguments args) {
        for (Map.Entry<String, CorsConfiguration> entry : corsProperties.corsConfigurations().entrySet()) {
            log.info("CORS allowed origins for {}: {}", entry.getKey(), entry.getValue().getAllowedOrigins());
        }
    }
}
