package main

import (
	"log"
	"net/http"

	"github.com/meshy/backend/internal/handler"
)

func cors(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "http://localhost:3000")
		w.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}

		next.ServeHTTP(w, r)
	})
}

func main() {
	mux := http.NewServeMux()
	mux.Handle("/api/track", handler.NewTrackHandler())

	server := &http.Server{
		Addr:    ":8080",
		Handler: cors(mux),
	}

	log.Println("[Server] listening on :8080")
	if err := server.ListenAndServe(); err != nil {
		log.Fatal(err)
	}
}
