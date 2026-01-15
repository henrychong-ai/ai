// Package example demonstrates Go testing patterns.
// This is a template file showing idiomatic Go test structure.
package example

import (
	"context"
	"errors"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Example domain types for demonstration
type User struct {
	ID        string
	Name      string
	Email     string
	CreatedAt time.Time
}

// Example service interface
type UserService interface {
	GetByID(ctx context.Context, id string) (*User, error)
	Create(ctx context.Context, name, email string) (*User, error)
}

// Example errors
var (
	ErrNotFound = errors.New("user not found")
	ErrInvalid  = errors.New("invalid input")
)

// =============================================================================
// Table-Driven Test Example
// =============================================================================

func TestValidateEmail(t *testing.T) {
	tests := []struct {
		name    string
		email   string
		wantErr bool
	}{
		{
			name:    "valid email",
			email:   "user@example.com",
			wantErr: false,
		},
		{
			name:    "empty email",
			email:   "",
			wantErr: true,
		},
		{
			name:    "missing @ symbol",
			email:   "userexample.com",
			wantErr: true,
		},
		{
			name:    "missing domain",
			email:   "user@",
			wantErr: true,
		},
		{
			name:    "valid with subdomain",
			email:   "user@mail.example.com",
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := validateEmail(tt.email)

			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}

// validateEmail is an example function to test
func validateEmail(email string) error {
	if email == "" {
		return ErrInvalid
	}
	// Simple validation for demo
	for i, c := range email {
		if c == '@' && i > 0 && i < len(email)-1 {
			return nil
		}
	}
	return ErrInvalid
}

// =============================================================================
// Test with Setup and Cleanup
// =============================================================================

func TestWithSetupAndCleanup(t *testing.T) {
	// Setup
	tempData := setupTestData(t)

	// Cleanup runs even if test fails
	t.Cleanup(func() {
		cleanupTestData(tempData)
	})

	// Test code
	assert.NotNil(t, tempData)
}

func setupTestData(t *testing.T) *User {
	t.Helper()
	return &User{
		ID:        "test-123",
		Name:      "Test User",
		Email:     "test@example.com",
		CreatedAt: time.Now(),
	}
}

func cleanupTestData(_ *User) {
	// Cleanup logic here
}

// =============================================================================
// Subtest Example
// =============================================================================

func TestUser(t *testing.T) {
	t.Run("creation", func(t *testing.T) {
		user := &User{Name: "Alice", Email: "alice@example.com"}
		assert.Equal(t, "Alice", user.Name)
		assert.Equal(t, "alice@example.com", user.Email)
	})

	t.Run("validation", func(t *testing.T) {
		t.Run("empty name fails", func(t *testing.T) {
			err := validateUser(&User{Name: "", Email: "test@example.com"})
			assert.Error(t, err)
		})

		t.Run("empty email fails", func(t *testing.T) {
			err := validateUser(&User{Name: "Test", Email: ""})
			assert.Error(t, err)
		})

		t.Run("valid user passes", func(t *testing.T) {
			err := validateUser(&User{Name: "Test", Email: "test@example.com"})
			assert.NoError(t, err)
		})
	})
}

func validateUser(u *User) error {
	if u.Name == "" {
		return errors.New("name required")
	}
	if u.Email == "" {
		return errors.New("email required")
	}
	return nil
}

// =============================================================================
// Parallel Tests Example
// =============================================================================

func TestParallel(t *testing.T) {
	tests := []struct {
		name  string
		input int
		want  int
	}{
		{"zero", 0, 0},
		{"positive", 5, 25},
		{"negative", -3, 9},
		{"large", 100, 10000},
	}

	for _, tt := range tests {
		tt := tt // Capture range variable for parallel execution
		t.Run(tt.name, func(t *testing.T) {
			t.Parallel() // Run in parallel

			got := square(tt.input)
			assert.Equal(t, tt.want, got)
		})
	}
}

func square(n int) int {
	return n * n
}

// =============================================================================
// Test with Context Example
// =============================================================================

func TestWithContext(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
	defer cancel()

	// Use context in test
	done := make(chan bool)

	go func() {
		// Simulate work that respects context
		select {
		case <-ctx.Done():
			return
		case <-time.After(10 * time.Millisecond):
			done <- true
		}
	}()

	select {
	case <-done:
		// Success
	case <-ctx.Done():
		t.Fatal("context cancelled before completion")
	}
}

// =============================================================================
// Error Checking Examples
// =============================================================================

func TestErrorHandling(t *testing.T) {
	t.Run("error is returned", func(t *testing.T) {
		_, err := getUserByID("")
		assert.Error(t, err)
	})

	t.Run("specific error type", func(t *testing.T) {
		_, err := getUserByID("nonexistent")
		assert.ErrorIs(t, err, ErrNotFound)
	})

	t.Run("no error on success", func(t *testing.T) {
		user, err := getUserByID("valid-id")
		require.NoError(t, err)
		assert.NotNil(t, user)
	})
}

func getUserByID(id string) (*User, error) {
	if id == "" {
		return nil, ErrInvalid
	}
	if id == "nonexistent" {
		return nil, ErrNotFound
	}
	return &User{ID: id, Name: "Test"}, nil
}

// =============================================================================
// Benchmark Example
// =============================================================================

func BenchmarkSquare(b *testing.B) {
	for i := 0; i < b.N; i++ {
		square(100)
	}
}

func BenchmarkValidateEmail(b *testing.B) {
	emails := []string{
		"user@example.com",
		"test@mail.example.org",
		"invalid-email",
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		validateEmail(emails[i%len(emails)])
	}
}
