package com.wardlog.gateway.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

import java.util.List;

@ConfigurationProperties(prefix = "security")
public record SecurityRoutesProperties(List<String> publicPaths) {
}
