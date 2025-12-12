package com.shobkaj.app.controller;

import com.shobkaj.app.dto.ReviewRequest;
import com.shobkaj.app.dto.ReviewResponse;
import com.shobkaj.app.dto.WorkerProfileResponse;
import com.shobkaj.app.model.Skill;
import com.shobkaj.app.service.WorkerService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST Controller for worker-related endpoints.
 */
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class WorkerController {

    private final WorkerService workerService;

    /**
     * GET /api/workers - List all workers.
     * Optional query param: skill (filter by skill type).
     */
    @GetMapping("/workers")
    public ResponseEntity<List<WorkerProfileResponse>> getAllWorkers(
            @RequestParam(required = false) Skill skill) {
        List<WorkerProfileResponse> workers;
        if (skill != null) {
            workers = workerService.getWorkersBySkill(skill);
        } else {
            workers = workerService.getAllWorkers();
        }
        return ResponseEntity.ok(workers);
    }

    /**
     * GET /api/workers/{id} - View worker profile with reviews.
     */
    @GetMapping("/workers/{id}")
    public ResponseEntity<WorkerProfileResponse> getWorkerById(@PathVariable Long id) {
        WorkerProfileResponse worker = workerService.getWorkerById(id);
        return ResponseEntity.ok(worker);
    }

    /**
     * POST /api/reviews - Add a review for a worker.
     */
    @PostMapping("/reviews")
    public ResponseEntity<ReviewResponse> addReview(@Valid @RequestBody ReviewRequest request) {
        ReviewResponse review = workerService.addReview(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(review);
    }

    /**
     * GET /api/workers/{id}/reviews - Get all reviews for a worker.
     */
    @GetMapping("/workers/{id}/reviews")
    public ResponseEntity<List<ReviewResponse>> getWorkerReviews(@PathVariable Long id) {
        List<ReviewResponse> reviews = workerService.getReviewsByWorkerId(id);
        return ResponseEntity.ok(reviews);
    }
}
