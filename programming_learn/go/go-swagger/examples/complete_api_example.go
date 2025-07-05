// Package main demonstrates a complete go-swagger implementation
// for a user management API
//
// This example shows how to define a RESTful API using go-swagger
// annotations and implement the generated handlers.
//
//	Schemes: http, https
//	Host: localhost:8080
//	BasePath: /api/v1
//	Version: 1.0.0
//	Title: User Management API
//	Description: A comprehensive example of go-swagger usage
//	Contact: Developer<developer@example.com>
//	License: MIT
//
//	Consumes:
//	- application/json
//
//	Produces:
//	- application/json
//
//	SecurityDefinitions:
//	bearer:
//	  type: apiKey
//	  name: Authorization
//	  in: header
//
// swagger:meta
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
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

// CreateUser adds a new user to the system
func (s *UserService) CreateUser(user *User) *User {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	user.ID = s.nextID
	s.nextID++
	user.CreatedAt = time.Now()
	user.UpdatedAt = time.Now()

	s.users[user.ID] = user
	return user
}

// GetUser retrieves a user by ID
func (s *UserService) GetUser(id int64) (*User, bool) {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	user, exists := s.users[id]
	return user, exists
}

// ListUsers returns a list of users with optional filtering
func (s *UserService) ListUsers(limit, offset int, status string) []*User {
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

// UpdateUser modifies an existing user
func (s *UserService) UpdateUser(id int64, updates *User) (*User, bool) {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	user, exists := s.users[id]
	if !exists {
		return nil, false
	}

	// Update fields
	if updates.Name != "" {
		user.Name = updates.Name
	}
	if updates.Email != "" {
		user.Email = updates.Email
	}
	if updates.Status != "" {
		user.Status = updates.Status
	}
	user.UpdatedAt = time.Now()

	return user, true
}

// DeleteUser removes a user from the system
func (s *UserService) DeleteUser(id int64) bool {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	_, exists := s.users[id]
	if !exists {
		return false
	}

	delete(s.users, id)
	return true
}

// HTTP Handlers with Swagger annotations

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
	users := s.ListUsers(limit, offset, status)

	// Return response
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"users": users,
		"meta": map[string]interface{}{
			"limit":  limit,
			"offset": offset,
			"count":  len(users),
		},
	})
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
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	// Validate required fields
	if user.Name == "" {
		http.Error(w, "Name is required", http.StatusBadRequest)
		return
	}

	// Set default status if not provided
	if user.Status == "" {
		user.Status = "active"
	}

	// Create user
	createdUser := s.CreateUser(&user)

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
	// Extract ID from URL path (simple parsing for /users/{id})
	pathParts := splitPath(r.URL.Path)
	if len(pathParts) < 3 {
		http.Error(w, "Invalid URL", http.StatusBadRequest)
		return
	}

	id, err := strconv.ParseInt(pathParts[2], 10, 64)
	if err != nil {
		http.Error(w, "Invalid user ID", http.StatusBadRequest)
		return
	}

	user, exists := s.GetUser(id)
	if !exists {
		http.Error(w, "User not found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

// swagger:route PUT /users/{id} users updateUser
//
// # Update user
//
// Updates an existing user with the provided information.
//
//	Consumes:
//	- application/json
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
//	  + name: user
//	    in: body
//	    description: Updated user data
//	    required: true
//	    schema:
//	      $ref: "#/definitions/User"
//
//	Responses:
//	  200: userResponse
//	  404: errorResponse
//	  400: errorResponse
//	  500: errorResponse
func (s *UserService) updateUserHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.ParseInt(vars["id"], 10, 64)
	if err != nil {
		http.Error(w, "Invalid user ID", http.StatusBadRequest)
		return
	}

	var updates User
	if err := json.NewDecoder(r.Body).Decode(&updates); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	user, exists := s.UpdateUser(id, &updates)
	if !exists {
		http.Error(w, "User not found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}

// swagger:route DELETE /users/{id} users deleteUser
//
// # Delete user
//
// Removes a user from the system.
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
//	  204: noContentResponse
//	  404: errorResponse
//	  500: errorResponse
func (s *UserService) deleteUserHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id, err := strconv.ParseInt(vars["id"], 10, 64)
	if err != nil {
		http.Error(w, "Invalid user ID", http.StatusBadRequest)
		return
	}

	if !s.DeleteUser(id) {
		http.Error(w, "User not found", http.StatusNotFound)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

// Response Models

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
		Message string `json:"message"`
		Code    int    `json:"code"`
	} `json:"body"`
}

// No content response
// swagger:response noContentResponse
type noContentResponseWrapper struct {
	// Empty response body
}

// Main server setup
func main() {
	userService := NewUserService()

	// Create router
	r := mux.NewRouter()
	api := r.PathPrefix("/api/v1").Subrouter()

	// Setup routes
	api.HandleFunc("/users", userService.listUsersHandler).Methods("GET")
	api.HandleFunc("/users", userService.createUserHandler).Methods("POST")
	api.HandleFunc("/users/{id}", userService.getUserByIDHandler).Methods("GET")
	api.HandleFunc("/users/{id}", userService.updateUserHandler).Methods("PUT")
	api.HandleFunc("/users/{id}", userService.deleteUserHandler).Methods("DELETE")

	// Add middleware for CORS and logging
	api.Use(corsMiddleware)
	api.Use(loggingMiddleware)

	// Serve swagger documentation
	opts := middleware.SwaggerUIOpts{SpecURL: "/swagger.yaml"}
	sh := middleware.SwaggerUI(opts, nil)
	api.Handle("/docs", sh)

	fmt.Println("Server starting on :8080")
	fmt.Println("API available at: http://localhost:8080/api/v1")
	fmt.Println("Documentation at: http://localhost:8080/api/v1/docs")

	log.Fatal(http.ListenAndServe(":8080", r))
}

// Middleware functions
func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}

func loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		next.ServeHTTP(w, r)
		log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
	})
}
