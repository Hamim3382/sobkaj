package com.shobkaj.app.service;

import com.shobkaj.app.dto.ReviewRequest;
import com.shobkaj.app.dto.ReviewResponse;
import com.shobkaj.app.dto.WorkerProfileResponse;
import com.shobkaj.app.model.Review;
import com.shobkaj.app.model.Skill;
import com.shobkaj.app.model.WorkerProfile;
import com.shobkaj.app.repository.ReviewRepository;
import com.shobkaj.app.repository.WorkerProfileRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

/**
 * Service for handling worker-related operations.
 */
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class WorkerService {

    private final WorkerProfileRepository workerProfileRepository;
    private final ReviewRepository reviewRepository;

    /**
     * Get all workers with basic profile information.
     */
    public List<WorkerProfileResponse> getAllWorkers() {
        return workerProfileRepository.findAllWithUser().stream()
                .map(WorkerProfileResponse::fromEntitySimple)
                .collect(Collectors.toList());
    }

    /**
     * Get workers filtered by skill.
     */
    public List<WorkerProfileResponse> getWorkersBySkill(Skill skill) {
        return workerProfileRepository.findBySkill(skill).stream()
                .map(WorkerProfileResponse::fromEntitySimple)
                .collect(Collectors.toList());
    }

    /**
     * Get worker profile with all reviews.
     */
    public WorkerProfileResponse getWorkerById(Long id) {
        WorkerProfile profile = workerProfileRepository.findByIdWithUserAndReviews(id)
                .orElseThrow(() -> new EntityNotFoundException("Worker profile not found with id: " + id));
        return WorkerProfileResponse.fromEntity(profile);
    }

    /**
     * Add a review for a worker.
     */
    @Transactional
    public ReviewResponse addReview(ReviewRequest request) {
        Long workerProfileId = request.getWorkerProfileId();
        if (workerProfileId == null) {
            throw new IllegalArgumentException("Worker profile ID cannot be null");
        }
        WorkerProfile profile = workerProfileRepository.findById(workerProfileId)
                .orElseThrow(() -> new EntityNotFoundException(
                        "Worker profile not found with id: " + workerProfileId));

        Review review = new Review(
                profile,
                request.getRating(),
                request.getComment(),
                request.getReviewerName());

        Review savedReview = reviewRepository.save(review);
        return ReviewResponse.fromEntity(savedReview);
    }

    /**
     * Get all reviews for a worker.
     */
    public List<ReviewResponse> getReviewsByWorkerId(Long workerProfileId) {
        return reviewRepository.findByWorkerProfileIdOrderByCreatedAtDesc(workerProfileId).stream()
                .map(ReviewResponse::fromEntity)
                .collect(Collectors.toList());
    }
}
