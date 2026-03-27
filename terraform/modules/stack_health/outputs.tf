output "checked_slugs" {
  value       = local.slugs_to_check
  description = "Slugs that were evaluated."
}

output "unhealthy_slugs" {
  value       = local.unhealthy
  description = "Slugs in a blocking status (empty when check passes)."
}

output "missing_slugs" {
  value       = local.missing
  description = "Requested slugs not present on your tracked stack."
}
