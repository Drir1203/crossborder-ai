package handler

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/meshy/backend/internal/model"
)

type TrackHandler struct{}

func NewTrackHandler() *TrackHandler {
	return &TrackHandler{}
}

func (h *TrackHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var event model.TrackEvent
	if err := json.NewDecoder(r.Body).Decode(&event); err != nil {
		http.Error(w, "invalid json", http.StatusBadRequest)
		return
	}

	event = model.NewTrackEvent(event.Event, event.Variant)

	log.Printf("[Track] event=%s variant=%s time=%s", event.Event, event.Variant, event.Time)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}
