package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"sync"
	"syscall"
)

// Global variables
var Env string

////////////////////// LOGS

type ColorLogger struct {
	debugLogger *log.Logger
    infoLogger  *log.Logger
    warnLogger  *log.Logger
    errorLogger *log.Logger
}

func NewColorLogger() *ColorLogger {
	return &ColorLogger{
		debugLogger: log.New(os.Stdout, "\033[1;36mDEBUG \033[0m", log.Ldate|log.Ltime),
		infoLogger:  log.New(os.Stdout, "\033[1;34mINFO  \033[0m", log.Ldate|log.Ltime),
		warnLogger:  log.New(os.Stdout, "\033[1;33mWARN  \033[0m", log.Ldate|log.Ltime),
		errorLogger: log.New(os.Stderr, "\033[1;31mERROR \033[0m", log.Ldate|log.Ltime),
	}
}

func (l *ColorLogger) Debug(format string, v ...interface{}) {
	l.debugLogger.Output(2, fmt.Sprintf(format, v...))
}

func (l *ColorLogger) Info(format string, v ...interface{}) {
    l.infoLogger.Output(2, fmt.Sprintf(format, v...))
}

func (l *ColorLogger) Warn(format string, v ...interface{}) {
    l.warnLogger.Output(2, fmt.Sprintf(format, v...))
}

func (l *ColorLogger) Error(format string, v ...interface{}) {
    l.errorLogger.Output(2, fmt.Sprintf(format, v...))
}

//////////////////////


type Item struct {
	ID    string  `json:"id"`
	Name  string  `json:"name"`
	Price float64 `json:"price"`
}

var (
	items = []Item{}
	mux   = sync.Mutex{}
)


type Config struct {
    TTS_IP   string `json:"ip"`
    TTS_Port string `json:"tts_port"`
	API_Port string `json:"api_port"`
	GEMINI_Port string `json:"gemini_port"`
}

func loadConfig() (*Config, error) {
    var config Config

    file, err := os.Open(fmt.Sprintf("config/%s.json", Env))
    if err != nil {
        return nil, err
    }
    defer file.Close()

    decoder := json.NewDecoder(file)
    if err := decoder.Decode(&config); err != nil {
        return nil, err
    }

    return &config, nil
}

func main() {
	logger := NewColorLogger()
    logger.Info("Logger initialized")

    flag.StringVar(&Env, "env", "dev", "environment")
    flag.Parse()


    config, err := loadConfig()
    if err != nil {
        log.Fatalf("Failed to load configuration: %v", err)
    }

	http.HandleFunc("/api/items", itemsHandler)
	http.HandleFunc("/api/audio", getAudio)
	http.HandleFunc("/api/generate_script", generateScriptHandler)
	http.HandleFunc("/api/scripts", scriptsHandler)


	go func() {
		if err := http.ListenAndServe(":"+config.API_Port, nil); err != nil {
			log.Fatalf("Failed to start server: %v", err)
		}
	}()
	logger.Info("Server started on port " + config.API_Port)


	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt, syscall.SIGTERM)
	<-quit

	fmt.Println("Server is shutting down...")
	os.Exit(0)
}

func itemsHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case "GET":
		getItems(w, r)
	case "POST":
		createItem(w, r)
	default:
		http.Error(w, "Invalid method", 405)
	}
}

func getItems(w http.ResponseWriter, r *http.Request) {
	mux.Lock()
	defer mux.Unlock()

	json.NewEncoder(w).Encode(items)
}

func createItem(w http.ResponseWriter, r *http.Request) {
	mux.Lock()
	defer mux.Unlock()

	var item Item
	_ = json.NewDecoder(r.Body).Decode(&item)
	items = append(items, item)

	json.NewEncoder(w).Encode(item)
}


type RequestBody struct {
	UserID     string `json:"user_id"`
	PodcastId  string `json:"podcast_id"`
}

// Get audio from generated script
func getAudio(w http.ResponseWriter, r *http.Request) {
	logger := NewColorLogger()
	logger.Info("Getting audio")

	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var body RequestBody

	err := json.NewDecoder(r.Body).Decode(&body)
	if err != nil {
		logger.Error("Failed to decode request body: %v", err)
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	// Read the names.json file
	dataPath := os.Getenv("DATA_PATH")
	namesFile, err := os.Open(fmt.Sprintf("%s/names.json", dataPath))
	if err != nil {
		logger.Error("Unable to open names file: %v", err)
		return
	}

	var names map[string]string
	err = json.NewDecoder(namesFile).Decode(&names)
	if err != nil {
		logger.Error("Unable to decode names: %v", err)
		return
	}

	// Get the name of the podcast
	podcastName, ok := names[body.PodcastId]
	if !ok {
		logger.Error("Name not found for podcast ID: %s", body.PodcastId)
		return
	}

	config, err := loadConfig()
	if err != nil {
		logger.Error("Failed to load configuration: %v", err)
		return
	}

	// Define the payload
	payload := map[string]interface{}{
		"user_id":      body.UserID,
		"podcast_name": podcastName,
		"podcast_id":   body.PodcastId,
	}

	payloadBytes, err := json.Marshal(payload)
	if err != nil {
		logger.Error("Unable to marshal JSON: %v", err)
		return
	}

	reader := bytes.NewReader(payloadBytes)

	// Send the POST request using config
	req, err := http.NewRequest("POST", "http://"+config.TTS_IP+":"+config.TTS_Port+"/api/audio", reader)
	if err != nil {
		logger.Error("Unable to create request: %v", err)
		return
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		logger.Error("Unable to get audio: %v", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK {
		logger.Info("OK")
	} else {
		logger.Error("Received non-OK response: %v", resp.Status)
	}
}

type GenerateScriptRequest struct {
	UserID      string `json:"user_id"`
	Subject     string `json:"subject"`
	PodcastName string `json:"podcast_name"`
}

// Generate script
func generateScriptHandler(w http.ResponseWriter, r *http.Request) {
	logger := NewColorLogger()
	logger.Info("Generating script")

	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var body GenerateScriptRequest

	err := json.NewDecoder(r.Body).Decode(&body)
	if err != nil {
		logger.Error("Failed to decode request body: %v", err)
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	if body.PodcastName == "" {
		body.PodcastName = body.Subject
	}

	config, err := loadConfig()
	if err != nil {
		logger.Error("Failed to load configuration: %v", err)
		return
	}

	// Define the payload
	payload := map[string]string{
		"user_id":  body.UserID,
		"subject": body.Subject,
	}

	payloadBytes, err := json.Marshal(payload)
	if err != nil {
		logger.Error("Unable to marshal JSON: %v", err)
		return
	}

	reader := bytes.NewReader(payloadBytes)

	// Send the POST request using config
	req, err := http.NewRequest("POST", "http://"+config.TTS_IP+":"+config.GEMINI_Port+"/generate_script", reader)
	if err != nil {
		logger.Error("Unable to create request: %v", err)
		return
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		logger.Error("Unable to generate script: %v", err)
		return
	}
	defer resp.Body.Close()

	// Get the data_path from the DATA_PATH environment variable
	data_path := os.Getenv("DATA_PATH")

	// Check if DATA_PATH is set
	if data_path == "" {
		logger.Error("DATA_PATH environment variable is not set")
		return
	}

	// Save the script in a JSON file
	scriptPath := fmt.Sprintf("%s/names.json", data_path)

	// Open the file
	file, err := os.OpenFile(scriptPath, os.O_RDWR|os.O_CREATE, 0755)
	if err != nil {
		logger.Error("Unable to open file: %v", err)
		return
	}
	defer file.Close()

	// Read the existing data
	var existingData map[string]string
	err = json.NewDecoder(file).Decode(&existingData)
	if err != nil && err != io.EOF {
		logger.Error("Unable to decode existing data: %v", err)
		return
	}

	// Get the script_id from the response
	var respBody map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&respBody)
	if err != nil {
		logger.Error("Unable to decode response body: %v", err)
		return
	}
	script_id, ok := respBody["script_id"].(string)
	if !ok {
		logger.Error("script_id not found in response")
		return
	}

	// Append the new data
	existingData[script_id] = body.PodcastName

	// Write the data back to the file
	file.Seek(0, 0)
	file.Truncate(0)
	err = json.NewEncoder(file).Encode(existingData)
	if err != nil {
		logger.Error("Unable to write to file: %v", err)
		return
	}

	logger.Info("Script generated successfully")
}

func scriptsHandler(w http.ResponseWriter, r *http.Request) {
	logger := NewColorLogger()
	logger.Info("Getting scripts")

	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var body struct {
		UserID string `json:"user_id"`
	}

	err := json.NewDecoder(r.Body).Decode(&body)
	if err != nil {
		logger.Error("Failed to decode request body: %v", err)
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	// Get all scripts of the given user_id
	dataPath := os.Getenv("DATA_PATH")
	scriptsPath := fmt.Sprintf("%s/%s/scripts/", dataPath, body.UserID)
	entries, err := os.ReadDir(scriptsPath)
	if err != nil {
		logger.Error("Unable to read directory: %v", err)
		http.Error(w, "Unable to read directory", http.StatusInternalServerError)
		return
	}
	scripts := make([]map[string]string, 0, len(entries))
	for _, entry := range entries {
		if entry.IsDir() {
			continue
		}

		// Remove the 'script_' prefix and '.json' suffix from the file name to get the podcast ID
		podcastID := strings.TrimSuffix(strings.TrimPrefix(entry.Name(), "script_"), ".json")

		// Read the names.json file
		namesFile, err := os.Open(fmt.Sprintf("%s/names.json", dataPath))
		if err != nil {
			logger.Error("Unable to open names file: %v", err)
			continue
		}

		var names map[string]string
		err = json.NewDecoder(namesFile).Decode(&names)
		if err != nil {
			logger.Error("Unable to decode names: %v", err)
			continue
		}

		// Get the name of the podcast
		podcastName, ok := names[podcastID]
		if !ok {
			logger.Error("Name not found for podcast ID: %s", podcastID)
			continue
		}

		// Add the podcast to the scripts
		scripts = append(scripts, map[string]string{
			"id":   podcastID,
			"name": podcastName,
		})
	}

	json.NewEncoder(w).Encode(scripts)
}