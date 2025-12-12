package com.shobkaj.app.dto;

import com.shobkaj.app.model.Role;
import com.shobkaj.app.model.User;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO for authentication response.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AuthResponse {

    private Long userId;
    private String username;
    private String email;
    private Role role;
    private Long workerProfileId;
    private String message;

    public static AuthResponse fromUser(User user, String message) {
        AuthResponse response = new AuthResponse();
        response.setUserId(user.getId());
        response.setUsername(user.getUsername());
        response.setEmail(user.getEmail());
        response.setRole(user.getRole());
        if (user.getWorkerProfile() != null) {
            response.setWorkerProfileId(user.getWorkerProfile().getId());
        }
        response.setMessage(message);
        return response;
    }
}
