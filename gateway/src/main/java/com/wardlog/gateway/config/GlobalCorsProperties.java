package com.wardlog.gateway.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.web.cors.CorsConfiguration;

import java.util.Map;

@ConfigurationProperties(prefix = "spring.cloud.gateway.server.webflux.globalcors")
public record GlobalCorsProperties(Map<String, CorsConfiguration> corsConfigurations) {
}
