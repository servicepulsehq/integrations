data "http" "tracked_vendors" {
  url = "${trim(var.base_url, "/")}/api/v1/tracked-vendors"
  request_headers = {
    Authorization = "Bearer ${var.api_token}"
    Accept        = "application/json"
  }
}

locals {
  parsed = try(jsondecode(data.http.tracked_vendors.response_body), {})
  rows   = try(local.parsed.vendors, [])
  by_slug = {
    for row in local.rows :
    lower(trimspace(try(row.vendor.slug, ""))) => try(row.vendor, {})
    if try(row.vendor.slug, "") != ""
  }
  slugs_to_check = length(var.vendor_slugs) > 0 ? [for s in var.vendor_slugs : lower(trimspace(s))] : sort(keys(local.by_slug))
  default_bad = toset([
    "degraded_performance",
    "partial_outage",
    "major_outage",
    "maintenance",
  ])
  bad = var.allow_maintenance ? setsubtract(local.default_bad, toset(["maintenance"])) : local.default_bad
  missing = [for slug in local.slugs_to_check : slug if !contains(keys(local.by_slug), slug)]
  norm = {
    for slug in local.slugs_to_check :
    slug => contains(keys(local.by_slug), slug) ? coalesce(trimspace(try(local.by_slug[slug].currentStatus, "")), "unknown") : "missing"
  }
  unhealthy = [
    for slug in local.slugs_to_check :
    slug
    if contains(keys(local.by_slug), slug) && (
      (local.norm[slug] == "unknown" && !var.allow_unknown) ||
      setcontains(local.bad, local.norm[slug])
    )
  ]
}

check "servicepulse_stack_healthy" {
  assert {
    condition     = length(local.missing) == 0 && length(local.unhealthy) == 0
    error_message = "ServicePulse stack check failed: missing=${join(",", local.missing)} unhealthy=${join(",", local.unhealthy)}"
  }
}
