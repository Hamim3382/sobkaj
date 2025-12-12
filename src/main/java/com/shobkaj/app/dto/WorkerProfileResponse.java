package com.shobkaj.app.dto;

import com.shobkaj.app.model.Review;
import com.shobkaj.app.model.Skill;
import com.shobkaj.app.model.WorkerProfile;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;
import java.util.stream.Collectors;

/**
 * DTO for worker profile response with reviews.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class WorkerProfileResponse {

    private Long id;
    private String workerName;
    private Skill skill;
    private BigDecimal hourlyRate;
    private String description;
    private Double averageRating;
    private List<ReviewResponse> reviews;

    /**
     * Create response from entity.
     */
    public static WorkerProfileResponse fromEntity(WorkerProfile profile) {
        WorkerProfileResponse response = new WorkerProfileResponse();
        response.setId(profile.getId());
        response.setWorkerName(profile.getWorkerName());
        response.setSkill(profile.getSkill());
        response.setHourlyRate(profile.getHourlyRate());
        response.setDescription(profile.getDescription());

        List<Review> reviews = profile.getReviews();
        if (reviews != null && !reviews.isEmpty()) {
            response.setReviews(reviews.stream()
                    .map(ReviewResponse::fromEntity)
                    .collect(Collectors.toList()));
            double avg = reviews.stream()
                    .mapToInt(Review::getRating)
                    .average()
                    .orElse(0.0);
            response.averageRating = avg;
        } else {
            response.setReviews(List.of());
            response.averageRating = null;
        }

        return response;
    }

    /**
     * Create simple response from entity (without loading reviews).
     */
    public static WorkerProfileResponse fromEntitySimple(WorkerProfile profile) {
        WorkerProfileResponse response = new WorkerProfileResponse();
        response.setId(profile.getId());
        response.setWorkerName(profile.getWorkerName());
        response.setSkill(profile.getSkill());
        response.setHourlyRate(profile.getHourlyRate());
        response.setDescription(profile.getDescription());
        response.setReviews(null);
        response.averageRating = null;
        return response;
    }
}
