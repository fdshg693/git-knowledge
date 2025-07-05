// Package main demonstrates go-swagger annotations with a simple user API
// This example shows how to structure code for go-swagger generation
// without external dependencies for demonstration purposes.
//
//	Schemes: http, https
//	Host: localhost:8080
//	BasePath: /api/v1
//	Version: 1.0.0
//	Title: User Management API
//	Description: A simple example of go-swagger usage
//
//	Consumes:
//	- application/json
//
//	Produces:
//	- application/json
//
// swagger:meta
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"
)

// User represents a user in the system
// swagger:model
type User struct {
	// The user's unique identifier
	// required: true
	// minimum: 1
	// example: 123
	ID int64 `json:"id"`

	// The user's full name
	// required: true
	// min length: 1
	// max length: 100
	// example: John Doe
	Name string `json:"name"`

	// The user's email address
	// format: email
	// example: john.doe@example.com
	Email string `json:"email,omitempty"`

	// The user's status
	// enum: active,inactive,pending
	// example: active
	Status string `json:"status"`

	// The user's creation timestamp
	// read only: true
	CreatedAt time.Time `json:"created_at,omitempty"`

	// The user's last update timestamp
	// read only: true
	UpdatedAt time.Time `json:"updated_at,omitempty"`
}

// UserService provides user management operations
type UserService struct {
	users  map[int64]*User
	nextID int64
	mutex  sync.RWMutex
}

// NewUserService creates a new user service with sample data
func NewUserService() *UserService {
	service := &UserService{
		users:  make(map[int64]*User),
		nextID: 1,
	}

	// Add sample users
	sampleUsers := []*User{
		{ID: 1, Name: "Alice Johnson", Email: "alice@example.com", Status: "active", CreatedAt: time.Now()},
		{ID: 2, Name: "Bob Smith", Email: "bob@example.com", Status: "active", CreatedAt: time.Now()},
		{ID: 3, Name: "Charlie Brown", Email: "charlie@example.com", Status: "inactive", CreatedAt: time.Now()},
	}

	for _, user := range sampleUsers {
		service.users[user.ID] = user
		if user.ID >= service.nextID {
			service.nextID = user.ID + 1
		}
	}

	return service
}

// Utility function to parse URL paths
func extractIDFromPath(path string) (int64, error) {
	parts := strings.Split(strings.Trim(path, "/"), "/")
	if len(parts) < 3 {
		return 0, fmt.Errorf("invalid path")
	}
	return strconv.ParseInt(parts[len(parts)-1], 10, 64)
}

// swagger:route GET /users users listUsers
//
// # Lists all users
//
// Returns a list of users in the system with optional filtering and pagination.
//
//	Produces:
//	- application/json
//
//	Parameters:
//	  + name: limit
//	    in: query
//	    description: Maximum number of users to return
//	    type: integer
//	    default: 10
//	    maximum: 100
//	  + name: offset
//	    in: query
//	    description: Number of users to skip
//	    type: integer
//	    default: 0
//	  + name: status
//	    in: query
//	    description: Filter users by status
//	    type: string
//	    enum: [active, inactive, pending]
//
//	Responses:
//	  200: usersResponse
//	  400: errorResponse
//	  500: errorResponse
func (s *UserService) listUsersHandler(w http.ResponseWriter, r *http.Request) {
	// Parse query parameters
	limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
	if limit <= 0 || limit > 100 {
		limit = 10
	}

	offset, _ := strconv.Atoi(r.URL.Query().Get("offset"))
	if offset < 0 {
		offset = 0
	}

	status := r.URL.Query().Get("status")

	// Get users
	users := s.listUsers(limit, offset, status)

	// Return response
	w.Header().Set("Content-Type", "application/json")
	response := map[string]interface{}{
		"users": users,
		"meta": map[string]interface{}{
			"limit":  limit,
			"offset": offset,
			"count":  len(users),
		},
	}
	json.NewEncoder(w).Encode(response)
}

// swagger:route POST /users users createUser
//
// # Create a new user
//
// Adds a new user to the system with the provided information.
//
//	Consumes:
//	- application/json
//
//	Produces:
//	- application/json
//
//	Parameters:
//	  + name: user
//	    in: body
//	    description: User data
//	    required: true
//	    schema:
//	      $ref: "#/definitions/User"
//
//	Responses:
//	  201: userResponse
//	  400: errorResponse
//	  500: errorResponse
func (s *UserService) createUserHandler(w http.ResponseWriter, r *http.Request) {
	var user User
	if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
		http.Error(w, `{"error": "Invalid JSON"}`, http.StatusBadRequest)
		return
	}

	// Validate required fields
	if user.Name == "" {
		http.Error(w, `{"error": "Name is required"}`, http.StatusBadRequest)
		return
	}

	// Set default status if not provided
	if user.Status == "" {
		user.Status = "active"
	}

	// Create user
	createdUser := s.createUser(&user)

	// Return response
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(createdUser)
}

// swagger:route GET /users/{id} users getUserByID
//
// # Get user by ID
//
// Returns a single user identified by their unique ID.
//
//	Produces:
//	- application/json
//
//	Parameters:
//	  + name: id
//	    in: path
//	    description: User ID
//	    required: true
//	    type: integer
//	    format: int64
//
//	Responses:
//	  200: userResponse
//	  404: errorResponse
//	  500: errorResponse
func (s *UserService) getUserByIDHandler(w http.ResponseWriter, r *http.Request) {
	id, err := extractIDFromPath(r.URL.Path)
	if err != nil {
		http.Error(w, `{"error": "Invalid user ID"}`, http.StatusBadRequest)
		return
	}

	user, exists := s.getUser(id)
	if !exists {
		http.Error(w, `{"error": "User not found"}`, http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

// Business logic methods

func (s *UserService) createUser(user *User) *User {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	user.ID = s.nextID
	s.nextID++
	user.CreatedAt = time.Now()
	user.UpdatedAt = time.Now()

	s.users[user.ID] = user
	return user
}

func (s *UserService) getUser(id int64) (*User, bool) {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	user, exists := s.users[id]
	return user, exists
}

func (s *UserService) listUsers(limit, offset int, status string) []*User {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	var result []*User
	count := 0

	for _, user := range s.users {
		// Apply status filter if provided
		if status != "" && user.Status != status {
			continue
		}

		// Apply offset
		if count < offset {
			count++
			continue
		}

		// Apply limit
		if len(result) >= limit {
			break
		}

		result = append(result, user)
		count++
	}

	return result
}

// Response Models for swagger documentation

// A list of users response
// swagger:response usersResponse
type usersResponseWrapper struct {
	// The users list with metadata
	// in: body
	Body struct {
		Users []User `json:"users"`
		Meta  struct {
			Limit  int `json:"limit"`
			Offset int `json:"offset"`
			Count  int `json:"count"`
		} `json:"meta"`
	} `json:"body"`
}

// A single user response
// swagger:response userResponse
type userResponseWrapper struct {
	// The user data
	// in: body
	Body User `json:"body"`
}

// Error response
// swagger:response errorResponse
type errorResponseWrapper struct {
	// The error message
	// in: body
	Body struct {
		Error string `json:"error"`
	} `json:"body"`
}

// Simple router implementation
type Router struct {
	userService *UserService
}

func NewRouter(userService *UserService) *Router {
	return &Router{userService: userService}
}

func (router *Router) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	// Add CORS headers
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	// Log request
	log.Printf("%s %s", r.Method, r.URL.Path)

	// Route requests
	path := strings.TrimPrefix(r.URL.Path, "/api/v1")

	switch {
	case path == "/users" && r.Method == "GET":
		router.userService.listUsersHandler(w, r)
	case path == "/users" && r.Method == "POST":
		router.userService.createUserHandler(w, r)
	case strings.HasPrefix(path, "/users/") && r.Method == "GET":
		router.userService.getUserByIDHandler(w, r)
	default:
		http.Error(w, `{"error": "Not found"}`, http.StatusNotFound)
	}
}

// Main server setup
func main() {
	userService := NewUserService()
	router := NewRouter(userService)

	// Setup server
	mux := http.NewServeMux()
	mux.Handle("/api/v1/", router)

	// Health check endpoint
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
	})

	fmt.Println("Server starting on :8080")
	fmt.Println("API available at: http://localhost:8080/api/v1/users")
	fmt.Println("Health check at: http://localhost:8080/health")
	fmt.Println()
	fmt.Println("Example requests:")
	fmt.Println("  GET  http://localhost:8080/api/v1/users")
	fmt.Println("  GET  http://localhost:8080/api/v1/users/1")
	fmt.Println("  POST http://localhost:8080/api/v1/users")

	log.Fatal(http.ListenAndServe(":8080", mux))
}
