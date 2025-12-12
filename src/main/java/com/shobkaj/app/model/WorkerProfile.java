package com.shobkaj.app.model;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * Entity representing a worker's profile with skills and rates.
 */
@Entity
@Table(name = "worker_profiles")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class WorkerProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "user_id", nullable = false)
    @JsonIgnore
    private User user;

    @NotNull(message = "Skill is required")
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Skill skill;

    @NotNull(message = "Hourly rate is required")
    @Positive(message = "Hourly rate must be positive")
    @Column(nullable = false)
    private BigDecimal hourlyRate;

    @Column(length = 1000)
    private String description;

    @OneToMany(mappedBy = "workerProfile", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Review> reviews = new ArrayList<>();

    // Helper method to get username from linked user
    public String getWorkerName() {
        return user != null ? user.getUsername() : null;
    }

    // Constructor for easy creation
    public WorkerProfile(User user, Skill skill, BigDecimal hourlyRate, String description) {
        this.user = user;
        this.skill = skill;
        this.hourlyRate = hourlyRate;
        this.description = description;
    }
}
