package com.shobkaj.app.config;

import com.shobkaj.app.model.*;
import com.shobkaj.app.repository.ReviewRepository;
import com.shobkaj.app.repository.UserRepository;
import com.shobkaj.app.repository.WorkerProfileRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;

/**
 * Data initializer that seeds the database with dummy data on application
 * startup.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {

        private final UserRepository userRepository;
        private final WorkerProfileRepository workerProfileRepository;
        private final ReviewRepository reviewRepository;

        @Override
        @Transactional
        public void run(String... args) {
                // Skip if data already exists
                if (userRepository.count() > 0) {
                        log.info("Database already initialized, skipping seed data...");
                        return;
                }

                log.info("Initializing ShobKaj database with dummy data...");

                // ===== Worker 1: Rahim (Plumber) =====
                User rahimUser = new User("Rahim", "password123", Role.WORKER);
                rahimUser = userRepository.save(rahimUser);

                WorkerProfile rahimProfile = new WorkerProfile(
                                rahimUser,
                                Skill.PLUMBER,
                                new BigDecimal("400.00"),
                                "Experienced plumber with 10+ years of expertise in residential and commercial plumbing. Available for emergency repairs.");
                rahimProfile = workerProfileRepository.save(rahimProfile);

                Review rahimReview1 = new Review(rahimProfile, 5, "Great job! Fixed my leaky faucet in no time.",
                                "Ahmed");
                reviewRepository.save(rahimReview1);

                log.info("Created worker: Rahim (Plumber, 400tk/hr) with 1 review");

                // ===== Worker 2: Sumana (Maid) =====
                User sumanaUser = new User("Sumana", "password123", Role.WORKER);
                sumanaUser = userRepository.save(sumanaUser);

                WorkerProfile sumanaProfile = new WorkerProfile(
                                sumanaUser,
                                Skill.MAID,
                                new BigDecimal("150.00"),
                                "Professional house cleaner with attention to detail. Expert in deep cleaning and organization.");
                sumanaProfile = workerProfileRepository.save(sumanaProfile);

                Review sumanaReview1 = new Review(sumanaProfile, 5, "Clean work! My house is spotless.", "Fatima");
                reviewRepository.save(sumanaReview1);

                Review sumanaReview2 = new Review(sumanaProfile, 4, "Late arrival but did a good job overall.",
                                "Karim");
                reviewRepository.save(sumanaReview2);

                log.info("Created worker: Sumana (Maid, 150tk/hr) with 2 reviews");

                // ===== Worker 3: Fatema (Babysitter) =====
                User fatemaUser = new User("Fatema", "password123", Role.WORKER);
                fatemaUser = userRepository.save(fatemaUser);

                WorkerProfile fatemaProfile = new WorkerProfile(
                                fatemaUser,
                                Skill.BABYSITTER,
                                new BigDecimal("250.00"),
                                "Loving and experienced babysitter with 5+ years of childcare experience. CPR certified, patient, and great with kids of all ages.");
                workerProfileRepository.save(fatemaProfile);

                log.info("Created worker: Fatema (Babysitter, 250tk/hr) with no reviews");

                // ===== Create a sample customer =====
                User customerUser = new User("customer1", "password123", Role.CUSTOMER);
                userRepository.save(customerUser);

                log.info("Created sample customer: customer1");

                log.info("===========================================");
                log.info("ShobKaj database initialized successfully!");
                log.info("Total workers: 3");
                log.info("Total reviews: 3");
                log.info("===========================================");
                log.info("API Endpoints available:");
                log.info("  GET  http://localhost:8080/api/workers");
                log.info("  GET  http://localhost:8080/api/workers/{id}");
                log.info("  POST http://localhost:8080/api/reviews");
                log.info("  H2 Console: http://localhost:8080/h2-console");
                log.info("===========================================");
        }
}
