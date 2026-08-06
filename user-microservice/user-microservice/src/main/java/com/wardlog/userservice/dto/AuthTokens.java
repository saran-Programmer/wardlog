package com.wardlog.userservice.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

/**
 * Internal carrier for both tokens. Never serialized directly as a response body —
 * the controller splits it into the AuthResponse body and the refresh cookie.
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AuthTokens {

    private String accessToken;

    private String refreshToken;

    private UserResponse user;
}
