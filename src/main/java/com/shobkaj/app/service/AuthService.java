package com.shobkaj.app.service;

import com.shobkaj.app.dto.AuthResponse;
import com.shobkaj.app.dto.LoginRequest;
import com.shobkaj.app.dto.SignupRequest;
import com.shobkaj.app.model.*;
import com.shobkaj.app.repository.UserRepository;
import com.shobkaj.app.repository.WorkerProfileRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;

/**
 * Service for handling authentication operations.
 */
@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final WorkerProfileRepository workerProfileRepository;

    /**
     * Register a new user.
     */
    @Transactional
    public AuthResponse signup(SignupRequest request) {
        // Check if username already exists
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new IllegalArgumentException("Username already exists");
        }

        // Create user
        User user = new User(
                request.getUsername(),
                request.getPassword(), // In production, hash this!
                request.getRole());
        user.setEmail(request.getEmail());
        user = userRepository.save(user);

        // If worker, create worker profile
        if (request.getRole() == Role.WORKER) {
            Skill skill = Skill.PLUMBER; // Default
            if (request.getSkill() != null && !request.getSkill().isEmpty()) {
                try {
                    skill = Skill.valueOf(request.getSkill().toUpperCase());
                } catch (IllegalArgumentException e) {
                    // Use default skill
                }
            }

            BigDecimal hourlyRate = new BigDecimal("200.00"); // Default 200tk
            if (request.getHourlyRate() != null && request.getHourlyRate() > 0) {
                hourlyRate = BigDecimal.valueOf(request.getHourlyRate());
            }

            String description = request.getDescription();
            if (description == null || description.isEmpty()) {
                description = "Experienced " + skill.name().toLowerCase() + " ready to help you.";
            }

            WorkerProfile profile = new WorkerProfile(user, skill, hourlyRate, description);
            profile = workerProfileRepository.save(profile);
            user.setWorkerProfile(profile);
        }

        return AuthResponse.fromUser(user, "Registration successful! Welcome to ShobKaj.");
    }

    /**
     * Authenticate a user.
     */
    @Transactional(readOnly = true)
    public AuthResponse login(LoginRequest request) {
        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> new IllegalArgumentException("Invalid username or password"));

        // Simple password check (In production, use BCrypt!)
        if (!user.getPassword().equals(request.getPassword())) {
            throw new IllegalArgumentException("Invalid username or password");
        }

        return AuthResponse.fromUser(user, "Login successful!");
    }

    /**
     * Get user by ID.
     */
    @Transactional(readOnly = true)
    public AuthResponse getUserById(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("User not found"));
        return AuthResponse.fromUser(user, "User found");
    }
}
