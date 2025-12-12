package com.shobkaj.app.repository;

import com.shobkaj.app.model.Review;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repository interface for Review entity.
 */
@Repository
public interface ReviewRepository extends JpaRepository<Review, Long> {

    List<Review> findByWorkerProfileId(Long workerProfileId);

    List<Review> findByWorkerProfileIdOrderByCreatedAtDesc(Long workerProfileId);
}
