// Package example demonstrates testify suite patterns.
// This is a template file showing test suite structure with setup/teardown.
package example

import (
	"context"
	"database/sql"
	"testing"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"
)

// =============================================================================
// Mock Definitions
// =============================================================================

// MockUserRepository is a mock implementation of UserRepository
type MockUserRepository struct {
	mock.Mock
}

func (m *MockUserRepository) GetByID(ctx context.Context, id string) (*User, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*User), args.Error(1)
}

func (m *MockUserRepository) Create(ctx context.Context, user *User) error {
	args := m.Called(ctx, user)
	return args.Error(0)
}

func (m *MockUserRepository) Update(ctx context.Context, user *User) error {
	args := m.Called(ctx, user)
	return args.Error(0)
}

func (m *MockUserRepository) Delete(ctx context.Context, id string) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

// =============================================================================
// Test Suite Definition
// =============================================================================

// UserServiceSuite is a test suite for UserService
type UserServiceSuite struct {
	suite.Suite
	mockRepo *MockUserRepository
	service  *userService
	ctx      context.Context
}

// userService is an example service for demonstration
type userService struct {
	repo UserRepository
}

// UserRepository interface for demonstration
type UserRepository interface {
	GetByID(ctx context.Context, id string) (*User, error)
	Create(ctx context.Context, user *User) error
	Update(ctx context.Context, user *User) error
	Delete(ctx context.Context, id string) error
}

func newUserService(repo UserRepository) *userService {
	return &userService{repo: repo}
}

func (s *userService) GetUser(ctx context.Context, id string) (*User, error) {
	return s.repo.GetByID(ctx, id)
}

func (s *userService) CreateUser(ctx context.Context, name, email string) (*User, error) {
	user := &User{Name: name, Email: email}
	if err := s.repo.Create(ctx, user); err != nil {
		return nil, err
	}
	return user, nil
}

// =============================================================================
// Suite Setup and Teardown
// =============================================================================

// SetupSuite runs once before all tests in the suite
func (s *UserServiceSuite) SetupSuite() {
	// Initialize shared resources (e.g., test database connection)
	s.ctx = context.Background()
}

// TearDownSuite runs once after all tests in the suite
func (s *UserServiceSuite) TearDownSuite() {
	// Cleanup shared resources
}

// SetupTest runs before each test
func (s *UserServiceSuite) SetupTest() {
	// Create fresh mock for each test
	s.mockRepo = new(MockUserRepository)
	s.service = newUserService(s.mockRepo)
}

// TearDownTest runs after each test
func (s *UserServiceSuite) TearDownTest() {
	// Verify mock expectations
	s.mockRepo.AssertExpectations(s.T())
}

// =============================================================================
// Test Methods
// =============================================================================

func (s *UserServiceSuite) TestGetUser_Success() {
	// Arrange
	expectedUser := &User{
		ID:    "123",
		Name:  "Alice",
		Email: "alice@example.com",
	}

	s.mockRepo.On("GetByID", mock.Anything, "123").
		Return(expectedUser, nil)

	// Act
	user, err := s.service.GetUser(s.ctx, "123")

	// Assert
	s.NoError(err)
	s.NotNil(user)
	s.Equal("Alice", user.Name)
	s.Equal("alice@example.com", user.Email)
}

func (s *UserServiceSuite) TestGetUser_NotFound() {
	// Arrange
	s.mockRepo.On("GetByID", mock.Anything, "nonexistent").
		Return(nil, ErrNotFound)

	// Act
	user, err := s.service.GetUser(s.ctx, "nonexistent")

	// Assert
	s.ErrorIs(err, ErrNotFound)
	s.Nil(user)
}

func (s *UserServiceSuite) TestCreateUser_Success() {
	// Arrange
	s.mockRepo.On("Create", mock.Anything, mock.AnythingOfType("*example.User")).
		Return(nil)

	// Act
	user, err := s.service.CreateUser(s.ctx, "Bob", "bob@example.com")

	// Assert
	s.NoError(err)
	s.NotNil(user)
	s.Equal("Bob", user.Name)
	s.Equal("bob@example.com", user.Email)
}

func (s *UserServiceSuite) TestCreateUser_RepoError() {
	// Arrange
	repoErr := errors.New("database error")
	s.mockRepo.On("Create", mock.Anything, mock.AnythingOfType("*example.User")).
		Return(repoErr)

	// Act
	user, err := s.service.CreateUser(s.ctx, "Bob", "bob@example.com")

	// Assert
	s.Error(err)
	s.Nil(user)
}

// =============================================================================
// Run the Suite
// =============================================================================

func TestUserServiceSuite(t *testing.T) {
	suite.Run(t, new(UserServiceSuite))
}

// =============================================================================
// Integration Test Suite Example
// =============================================================================

// IntegrationSuite demonstrates a suite with real database
type IntegrationSuite struct {
	suite.Suite
	db *sql.DB
}

func (s *IntegrationSuite) SetupSuite() {
	// Skip if no test database
	dsn := "postgres://test:test@localhost:5432/test?sslmode=disable"
	db, err := sql.Open("postgres", dsn)
	if err != nil {
		s.T().Skip("Test database not available")
	}
	s.db = db
}

func (s *IntegrationSuite) TearDownSuite() {
	if s.db != nil {
		s.db.Close()
	}
}

func (s *IntegrationSuite) SetupTest() {
	// Clean tables before each test
	if s.db != nil {
		_, _ = s.db.Exec("TRUNCATE users CASCADE")
	}
}

func (s *IntegrationSuite) TestDatabaseIntegration() {
	if s.db == nil {
		s.T().Skip("Database not available")
	}

	// Integration test code here
	s.NotNil(s.db)
}

func TestIntegrationSuite(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping integration tests in short mode")
	}
	suite.Run(t, new(IntegrationSuite))
}

// errors import for demonstration
import "errors"
