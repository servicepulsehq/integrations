# servicepulse-client-go

Go **Personal API** client: **`GET /api/v1/tracked-vendors`** and **`AssertStackHealthy`**, aligned with [`servicepulse-client`](../../servicepulse-client/) (Python) and [`@servicepulsehq/client`](../servicepulse-client-js/) (Node).

## Use in your module

From the same checkout:

```go
// go.mod
replace github.com/servicepulsehq/integrations/libraries/servicepulse-client-go => ../path/to/integrations/libraries/servicepulse-client-go
```

```go
import servicepulse "github.com/servicepulsehq/integrations/libraries/servicepulse-client-go"

c, err := servicepulse.NewClient(os.Getenv("SERVICEPULSE_API_TOKEN"), "")
if err != nil { log.Fatal(err) }
if err := c.AssertStackHealthy([]string{"stripe", "snowflake"}, servicepulse.AssertOptions{}); err != nil {
	log.Fatal(err)
}
```

Or clone [servicepulsehq/integrations](https://github.com/servicepulsehq/integrations) and point `replace` at `libraries/servicepulse-client-go`.

## Test

```bash
go test ./...
```

## License

[MIT](../../LICENSE)
