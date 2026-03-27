package servicepulse

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"slices"
	"strings"
	"time"
)

const DefaultBaseURL = "https://servicepulse.dev"

var defaultBad = map[string]struct{}{
	"degraded_performance": {},
	"partial_outage":     {},
	"major_outage":       {},
	"maintenance":        {},
}

type ServicePulseError struct {
	Msg string
}

func (e *ServicePulseError) Error() string { return e.Msg }

type UnhealthyVendor struct {
	Slug           string `json:"slug"`
	Name           string `json:"name,omitempty"`
	CurrentStatus  string `json:"currentStatus"`
}

type StackNotHealthyError struct {
	Msg          string
	Unhealthy    []UnhealthyVendor
	MissingSlugs []string
}

func (e *StackNotHealthyError) Error() string { return e.Msg }

type Client struct {
	baseURL    string
	token      string
	httpClient *http.Client
}

func NewClient(apiToken string, baseURL string) (*Client, error) {
	t := strings.TrimSpace(apiToken)
	if t == "" {
		return nil, fmt.Errorf("apiToken is required")
	}
	if baseURL == "" {
		baseURL = DefaultBaseURL
	}
	baseURL = strings.TrimRight(baseURL, "/")
	return &Client{
		baseURL: baseURL,
		token:   t,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}, nil
}

type trackedVendorsResponse struct {
	Vendors []struct {
		Vendor json.RawMessage `json:"vendor"`
	} `json:"vendors"`
}

type vendorRow struct {
	Slug           string `json:"slug"`
	Name           string `json:"name"`
	CurrentStatus  string `json:"currentStatus"`
}

func (c *Client) GetTrackedVendors() (map[string]vendorRow, error) {
	req, err := http.NewRequest(http.MethodGet, c.baseURL+"/api/v1/tracked-vendors", nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Accept", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, &ServicePulseError{Msg: "ServicePulse request failed: " + err.Error()}
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		snippet := string(body)
		if len(snippet) > 500 {
			snippet = snippet[:500]
		}
		return nil, &ServicePulseError{Msg: fmt.Sprintf("ServicePulse API error %d: %s", resp.StatusCode, snippet)}
	}

	var data trackedVendorsResponse
	if err := json.Unmarshal(body, &data); err != nil {
		return nil, err
	}

	bySlug := make(map[string]vendorRow)
	for _, row := range data.Vendors {
		var v vendorRow
		if err := json.Unmarshal(row.Vendor, &v); err != nil {
			continue
		}
		slug := strings.ToLower(strings.TrimSpace(v.Slug))
		if slug != "" {
			bySlug[slug] = v
		}
	}
	return bySlug, nil
}

type AssertOptions struct {
	AllowMaintenance bool
	AllowUnknown     bool
	ExtraBadStatuses []string
}

func (c *Client) AssertStackHealthy(vendorSlugs []string, opt AssertOptions) error {
	bad := make(map[string]struct{})
	for k := range defaultBad {
		bad[k] = struct{}{}
	}
	if opt.AllowMaintenance {
		delete(bad, "maintenance")
	}
	for _, s := range opt.ExtraBadStatuses {
		bad[strings.TrimSpace(s)] = struct{}{}
	}

	bySlug, err := c.GetTrackedVendors()
	if err != nil {
		return err
	}

	var slugsToCheck []string
	if len(vendorSlugs) > 0 {
		for _, s := range vendorSlugs {
			s = strings.ToLower(strings.TrimSpace(s))
			if s != "" {
				slugsToCheck = append(slugsToCheck, s)
			}
		}
	} else {
		for s := range bySlug {
			slugsToCheck = append(slugsToCheck, s)
		}
		slices.Sort(slugsToCheck)
	}

	var unhealthy []UnhealthyVendor
	var missing []string

	for _, slug := range slugsToCheck {
		v, ok := bySlug[slug]
		if !ok {
			missing = append(missing, slug)
			continue
		}
		status := strings.TrimSpace(v.CurrentStatus)
		if status == "" {
			status = "unknown"
		}
		if status == "unknown" && !opt.AllowUnknown {
			unhealthy = append(unhealthy, UnhealthyVendor{Slug: slug, Name: v.Name, CurrentStatus: status})
			continue
		}
		if _, isBad := bad[status]; isBad {
			unhealthy = append(unhealthy, UnhealthyVendor{Slug: slug, Name: v.Name, CurrentStatus: status})
		}
	}

	slices.Sort(missing)
	missing = slices.Compact(missing)

	var parts []string
	if len(unhealthy) > 0 {
		var b bytes.Buffer
		b.WriteString("Unhealthy vendors: ")
		for i, u := range unhealthy {
			if i > 0 {
				b.WriteString(", ")
			}
			fmt.Fprintf(&b, "%s=%s", u.Slug, u.CurrentStatus)
		}
		parts = append(parts, b.String())
	}
	if len(missing) > 0 {
		parts = append(parts, "Slugs not in tracked stack: "+strings.Join(missing, ", "))
	}
	if len(parts) == 0 {
		return nil
	}
	return &StackNotHealthyError{
		Msg:          strings.Join(parts, "; "),
		Unhealthy:    unhealthy,
		MissingSlugs: missing,
	}
}
