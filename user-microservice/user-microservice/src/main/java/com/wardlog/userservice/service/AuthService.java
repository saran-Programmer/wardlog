package com.wardlog.userservice.service;

import com.wardlog.userservice.dto.AuthResponse;
import com.wardlog.userservice.dto.UserResponse;
import com.wardlog.userservice.dto.LoginRequest;
import com.wardlog.userservice.dto.RefreshRequest;
import com.wardlog.userservice.dto.RegisterRequest;
import com.wardlog.userservice.entity.User;
import com.wardlog.userservice.exception.UserNotFoundException;
import com.wardlog.userservice.exception.EmailAlreadyExistsException;
import com.wardlog.userservice.exception.InvalidCredentialsException;
import com.wardlog.userservice.repository.UserRepository;
import com.wardlog.userservice.security.JwtService;
import io.jsonwebtoken.Claims;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AuthService {

    private static final String INVALID_CREDENTIALS_MESSAGE = "Invalid email or password";

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthResponse register(RegisterRequest request) {
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
        return buildAuthResponse(saved);
    }

    public AuthResponse login(LoginRequest request) {
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new InvalidCredentialsException(INVALID_CREDENTIALS_MESSAGE));

        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
            throw new InvalidCredentialsException(INVALID_CREDENTIALS_MESSAGE);
        }

        return buildAuthResponse(user);
    }

    public AuthResponse refresh(RefreshRequest request) {
        Claims claims = jwtService.parseToken(request.getRefreshToken());

        if (!jwtService.isRefreshToken(claims)) {
            throw new InvalidCredentialsException("Token is not a refresh token");
        }

        UUID userId = UUID.fromString(claims.getSubject());
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("User not found: " + userId));

        String accessToken = jwtService.generateAccessToken(user);

        return AuthResponse.builder()
                .accessToken(accessToken)
                .refreshToken(request.getRefreshToken())
                .user(toUserResponse(user))
                .build();
    }

    private AuthResponse buildAuthResponse(User user) {
        return AuthResponse.builder()
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
