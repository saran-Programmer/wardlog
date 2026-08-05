package com.wardlog.userservice.service;

import com.wardlog.userservice.dto.UserResponse;
import com.wardlog.userservice.dto.UpdateProfileRequest;
import com.wardlog.userservice.entity.User;
import com.wardlog.userservice.exception.UserNotFoundException;
import com.wardlog.userservice.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;

    public UserResponse getProfile(UUID userId) {
        User user = findUserOrThrow(userId);
        return toResponse(user);
    }

    public UserResponse updateProfile(UUID userId, UpdateProfileRequest request) {
        User user = findUserOrThrow(userId);

        if (request.getName() != null) user.setName(request.getName());
        if (request.getAge() != null) user.setAge(request.getAge());
        if (request.getSex() != null) user.setSex(request.getSex());
        if (request.getSpeciality() != null) user.setSpeciality(request.getSpeciality());
        if (request.getTone() != null) user.setTone(request.getTone());
        if (request.getAssistantName() != null) user.setAssistantName(request.getAssistantName());

        User saved = userRepository.save(user);
        return toResponse(saved);
    }

    public void deleteUser(UUID userId) {
        User user = findUserOrThrow(userId);
        userRepository.delete(user);
    }

    private User findUserOrThrow(UUID userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("User not found: " + userId));
    }

    private UserResponse toResponse(User user) {
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
