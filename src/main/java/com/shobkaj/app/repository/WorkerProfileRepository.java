package com.shobkaj.app.repository;

import com.shobkaj.app.model.Skill;
import com.shobkaj.app.model.WorkerProfile;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository interface for WorkerProfile entity.
 */
@Repository
public interface WorkerProfileRepository extends JpaRepository<WorkerProfile, Long> {

    List<WorkerProfile> findBySkill(Skill skill);

    @Query("SELECT wp FROM WorkerProfile wp JOIN FETCH wp.user")
    List<WorkerProfile> findAllWithUser();

    @Query("SELECT wp FROM WorkerProfile wp JOIN FETCH wp.user LEFT JOIN FETCH wp.reviews WHERE wp.id = :id")
    Optional<WorkerProfile> findByIdWithUserAndReviews(Long id);

    Optional<WorkerProfile> findByUserId(Long userId);
}
