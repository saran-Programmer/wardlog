package com.wardlog.userservice.service;

import com.wardlog.userservice.dto.AuthResponse;
import com.wardlog.userservice.dto.AuthTokens;
import com.wardlog.userservice.dto.UserResponse;
import com.wardlog.userservice.dto.LoginRequest;
import com.wardlog.userservice.dto.RegisterRequest;
import com.wardlog.userservice.entity.User;
import com.wardlog.userservice.exception.UserNotFoundException;
import com.wardlog.userservice.exception.EmailAlreadyExistsException;
import com.wardlog.userservice.exception.InvalidCredentialsException;
import com.wardlog.userservice.repository.UserRepository;
import com.wardlog.userservice.security.JwtService;
import io.jsonwebtoken.Claims;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseCookie;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AuthService {

    private static final String INVALID_CREDENTIALS_MESSAGE = "Invalid email or password";
    private static final String REFRESH_COOKIE_NAME = "refreshToken";
    private static final String REFRESH_COOKIE_PATH = "/api/v1/auth";

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    @Value("${jwt.refresh-token-days}")
    private long refreshTokenDays;

    public ResponseEntity<AuthResponse> register(RegisterRequest request) {
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new EmailAlreadyExistsException("An account with this email already exists");
        }

        User user = User.builder()
                .email(request.getEmail())
                .passwordHash(passwordEncoder.encode(request.getPassword()))
                .name(request.getName())
                .age(request.getAge())
                .sex(request.getSex())
                .speciality(request.getSpeciality())
                .tone(request.getTone())
                .assistantName(request.getAssistantName() != null ? request.getAssistantName() : "wardlog")
                .build();

        User saved = userRepository.save(user);
        return withRefreshCookie(buildAuthTokens(saved), HttpStatus.CREATED);
    }

    public ResponseEntity<AuthResponse> login(LoginRequest request) {
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new InvalidCredentialsException(INVALID_CREDENTIALS_MESSAGE));

        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
            throw new InvalidCredentialsException(INVALID_CREDENTIALS_MESSAGE);
        }

        return withRefreshCookie(buildAuthTokens(user), HttpStatus.OK);
    }

    public ResponseEntity<AuthResponse> refresh(String refreshToken) {
        if (refreshToken == null) {
            throw new InvalidCredentialsException("Missing refresh token");
        }

        Claims claims = jwtService.parseToken(refreshToken);

        if (!jwtService.isRefreshToken(claims)) {
            throw new InvalidCredentialsException("Token is not a refresh token");
        }

        UUID userId = UUID.fromString(claims.getSubject());
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("User not found: " + userId));

        AuthResponse body = AuthResponse.builder()
                .accessToken(jwtService.generateAccessToken(user))
                .user(toUserResponse(user))
                .build();

        return ResponseEntity.ok(body);
    }

    public ResponseEntity<Void> logout() {
        ResponseCookie expiredCookie = ResponseCookie.from(REFRESH_COOKIE_NAME, "")
                .httpOnly(true)
                .secure(true)
                .sameSite("None")
                .path(REFRESH_COOKIE_PATH)
                .maxAge(0)
                .build();

        return ResponseEntity.noContent()
                .header(HttpHeaders.SET_COOKIE, expiredCookie.toString())
                .build();
    }

    private ResponseEntity<AuthResponse> withRefreshCookie(AuthTokens tokens, HttpStatus status) {
        ResponseCookie refreshCookie = ResponseCookie.from(REFRESH_COOKIE_NAME, tokens.getRefreshToken())
                .httpOnly(true)
                .secure(true)
                .sameSite("None")
                .path(REFRESH_COOKIE_PATH)
                .maxAge(Duration.ofDays(refreshTokenDays))
                .build();

        AuthResponse body = AuthResponse.builder()
                .accessToken(tokens.getAccessToken())
                .user(tokens.getUser())
                .build();

        return ResponseEntity.status(status)
                .header(HttpHeaders.SET_COOKIE, refreshCookie.toString())
                .body(body);
    }

    private AuthTokens buildAuthTokens(User user) {
        return AuthTokens.builder()
                .accessToken(jwtService.generateAccessToken(user))
                .refreshToken(jwtService.generateRefreshToken(user))
                .user(toUserResponse(user))
                .build();
    }

    private UserResponse toUserResponse(User user) {
        return UserResponse.builder()
                .id(user.getId())
                .email(user.getEmail())
                .name(user.getName())
                .age(user.getAge())
                .sex(user.getSex())
                .speciality(user.getSpeciality())
                .tone(user.getTone() != null ? user.getTone().getLabel() : null)
                .assistantName(user.getAssistantName())
                .build();
    }
}
