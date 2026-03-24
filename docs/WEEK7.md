# Week 7: Backend Development - User Models and Authentication

## Completed Tasks

### User Models
- Created User model with extended fields
- Extended Django AbstractUser with custom fields
- Added profile fields: phone, location, bio, current_position, current_company
- Added social links: LinkedIn, GitHub, portfolio_url

### Authentication System
- Implemented JWT authentication
- JWT token generation and validation
- User registration endpoint with validation
- User login endpoint with token response
- Password change functionality
- Account deletion capability

### API Endpoints
- Added user registration and login endpoints
- Created user profile serializers and views
- Wrote unit tests for user models
- POST /api/auth/register/ - User registration
- POST /api/auth/login/ - User login
- POST /api/auth/logout/ - User logout
- GET /api/users/profile/ - Get current user profile
- PUT /api/users/update_profile/ - Update user profile
- POST /api/users/change_password/ - Password change