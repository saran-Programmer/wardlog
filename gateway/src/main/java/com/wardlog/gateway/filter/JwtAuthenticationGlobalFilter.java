package com.wardlog.gateway.filter;

import com.wardlog.gateway.config.SecurityRoutesProperties;
import com.wardlog.gateway.security.JwtService;
import io.jsonwebtoken.JwtException;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.util.AntPathMatcher;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

@Component
public class JwtAuthenticationGlobalFilter implements GlobalFilter, Ordered {

    private static final String AUTHORIZATION_HEADER = "Authorization";
    private static final String BEARER_PREFIX = "Bearer ";
    private static final String DOCTOR_ID_HEADER = "X-Doctor-Id";

    private final JwtService jwtService;
    private final SecurityRoutesProperties securityRoutesProperties;
    private final AntPathMatcher pathMatcher = new AntPathMatcher();

    public JwtAuthenticationGlobalFilter(JwtService jwtService, SecurityRoutesProperties securityRoutesProperties) {
        this.jwtService = jwtService;
        this.securityRoutesProperties = securityRoutesProperties;
    }

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {

        if (exchange.getRequest().getMethod() == HttpMethod.OPTIONS) {
            return chain.filter(exchange);
        }

        // Strip any client-supplied X-Doctor-Id so it can't be spoofed downstream.
        ServerHttpRequest sanitizedRequest = exchange.getRequest().mutate()
                .headers(headers -> headers.remove(DOCTOR_ID_HEADER))
                .build();

        String path = sanitizedRequest.getURI().getPath();
        if (isPublicPath(path)) {
            return chain.filter(exchange.mutate().request(sanitizedRequest).build());
        }

        String authHeader = sanitizedRequest.getHeaders().getFirst(AUTHORIZATION_HEADER);
        if (authHeader == null || !authHeader.startsWith(BEARER_PREFIX)) {
            return reject(exchange);
        }

        String token = authHeader.substring(BEARER_PREFIX.length()).trim();
        if (token.isEmpty()) {
            return reject(exchange);
        }

        String doctorId;
        try {
            doctorId = jwtService.extractDoctorId(token);
        } catch (JwtException | IllegalArgumentException e) {
            return reject(exchange);
        }

        ServerHttpRequest authenticatedRequest = sanitizedRequest.mutate()
                .header(DOCTOR_ID_HEADER, doctorId)
                .build();

        return chain.filter(exchange.mutate().request(authenticatedRequest).build());
    }

    private boolean isPublicPath(String path) {
        return securityRoutesProperties.publicPaths().stream()
                .anyMatch(pattern -> pathMatcher.match(pattern, path));
    }

    private Mono<Void> reject(ServerWebExchange exchange) {
        exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
        return exchange.getResponse().setComplete();
    }

    @Override
    public int getOrder() {
        return Ordered.HIGHEST_PRECEDENCE;
    }
}
