package main

import (
	"encoding/json"
	"net/http"
	"sync"
	"os"
	"io"
	"fmt"
	"os/signal"
	"syscall"
	"bytes"
	"log"
	"flag"
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
    TTS_Port string `json:"port"`
	API_Port string `json:"api_port"`
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
	UserID      string                 `json:"user_id"`
	Script      map[string]interface{} `json:"script"`
	PodcastName string                 `json:"podcast_name"`
}

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


	config, err := loadConfig()
	if err != nil {
		logger.Error("Failed to load configuration: %v", err)
		return
	}

	// Define the payload
	payload := map[string]interface{}{
		"user_id":      body.UserID,
		"podcast_name": body.PodcastName,
		"script":       body.Script,
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

	out, err := os.Create("audio.wav")
	if err != nil {
		logger.Error("Unable to create file: %v", err)
		return
	}
	defer out.Close()

	_, err = io.Copy(out, resp.Body)
	if err != nil {
		logger.Error("Unable to write file: %v", err)
		return
	}

	logger.Info("Audio saved successfully")
}