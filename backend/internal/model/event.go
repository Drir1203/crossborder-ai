package model

import "time"

type TrackEvent struct {
	Event   string `json:"event"`
	Variant string `json:"variant"`
	Time    string `json:"time"`
}

func NewTrackEvent(event, variant string) TrackEvent {
	return TrackEvent{
		Event:   event,
		Variant: variant,
		Time:    time.Now().UTC().Format(time.RFC3339),
	}
}
