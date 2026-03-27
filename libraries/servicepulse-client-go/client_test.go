package servicepulse

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestClient_AssertStackHealthy_OK(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/api/v1/tracked-vendors" {
			t.Fatalf("path %s", r.URL.Path)
		}
		_ = json.NewEncoder(w).Encode(map[string]any{
			"vendors": []map[string]any{
				{"vendor": map[string]any{"slug": "stripe", "name": "Stripe", "currentStatus": "operational"}},
			},
		})
	}))
	defer ts.Close()

	c, err := NewClient("sp_test", ts.URL)
	if err != nil {
		t.Fatal(err)
	}
	if err := c.AssertStackHealthy([]string{"stripe"}, AssertOptions{}); err != nil {
		t.Fatal(err)
	}
}

func TestClient_AssertStackHealthy_Blocks(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = json.NewEncoder(w).Encode(map[string]any{
			"vendors": []map[string]any{
				{"vendor": map[string]any{"slug": "stripe", "currentStatus": "major_outage"}},
			},
		})
	}))
	defer ts.Close()

	c, _ := NewClient("sp_test", ts.URL)
	err := c.AssertStackHealthy([]string{"stripe"}, AssertOptions{})
	se, ok := err.(*StackNotHealthyError)
	if !ok || len(se.Unhealthy) != 1 {
		t.Fatalf("expected StackNotHealthyError, got %v", err)
	}
}
