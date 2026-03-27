# Recipe: Go client

Add a `replace` in your `go.mod` pointing at [`libraries/servicepulse-client-go`](../libraries/servicepulse-client-go/), or vendor the folder.

```go
import sp "github.com/servicepulsehq/integrations/libraries/servicepulse-client-go"

c, err := sp.NewClient(os.Getenv("SERVICEPULSE_API_TOKEN"), "")
if err != nil { log.Fatal(err) }
if err := c.AssertStackHealthy([]string{"stripe"}, sp.AssertOptions{}); err != nil {
    log.Fatal(err)
}
```

Run tests in that module with `go test ./...`.
