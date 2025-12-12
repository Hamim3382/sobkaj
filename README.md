# ShobKaj - Blue-Collar Job Marketplace

A Spring Boot application for connecting customers with physical labor workers (plumbers, maids, daycare providers, etc.).

## Features

- **Worker Profiles**: Browse workers with skills, hourly rates, and descriptions
- **Reviews System**: Customers can leave reviews for workers (1-5 star rating)
- **H2 In-Memory Database**: No external database setup required
- **RESTful API**: Clean REST endpoints for all operations

## Tech Stack

- Java 17
- Spring Boot 3.2.0
- Spring Data JPA
- H2 Database
- Lombok
- Jakarta Validation

## Getting Started

### Prerequisites

- Java 17 or higher installed
- Maven (or use the included Maven wrapper)

### Running the Application

**Using Maven Wrapper (Recommended):**

```bash
# Windows
./mvnw.cmd spring-boot:run

# Linux/Mac
./mvnw spring-boot:run
```

**Using Maven:**

```bash
mvn spring-boot:run
```

The application will start on `http://localhost:8080`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/workers` | List all workers |
| GET | `/api/workers?skill=PLUMBER` | Filter workers by skill |
| GET | `/api/workers/{id}` | Get worker profile with reviews |
| GET | `/api/workers/{id}/reviews` | Get reviews for a worker |
| POST | `/api/reviews` | Add a review for a worker |

### Example Requests

**List all workers:**
```bash
curl http://localhost:8080/api/workers
```

**Get worker with reviews:**
```bash
curl http://localhost:8080/api/workers/1
```

**Add a review:**
```bash
curl -X POST http://localhost:8080/api/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "workerProfileId": 1,
    "rating": 5,
    "comment": "Excellent work!",
    "reviewerName": "John"
  }'
```

## Seed Data

The application comes with pre-loaded data:

| Worker | Skill | Rate | Reviews |
|--------|-------|------|---------|
| Rahim | Plumber | 400tk/hr | 1 review (5 stars) |
| Sumana | Maid | 150tk/hr | 2 reviews (5 & 4 stars) |
| Fatema | Babysitter | 250tk/hr | No reviews |

## H2 Console

Access the H2 database console at: `http://localhost:8080/h2-console`

- **JDBC URL**: `jdbc:h2:mem:shobkajdb`
- **Username**: `sa`
- **Password**: *(leave empty)*

## Project Structure

```
src/main/java/com/shobkaj/app/
├── ShobKajApplication.java     # Main entry point
├── config/
│   └── DataInitializer.java    # Seed data loader
├── controller/
│   └── WorkerController.java   # REST endpoints
├── dto/
│   ├── ReviewRequest.java      # Review creation DTO
│   ├── ReviewResponse.java     # Review response DTO
│   └── WorkerProfileResponse.java
├── exception/
│   └── GlobalExceptionHandler.java
├── model/
│   ├── Role.java               # CUSTOMER, WORKER enum
│   ├── Skill.java              # Job skills enum
│   ├── User.java               # User entity
│   ├── WorkerProfile.java      # Worker profile entity
│   └── Review.java             # Review entity
├── repository/
│   ├── UserRepository.java
│   ├── WorkerProfileRepository.java
│   └── ReviewRepository.java
└── service/
    └── WorkerService.java      # Business logic
```

## License

MIT License
