variable "api_token" {
  type        = string
  sensitive   = true
  description = "ServicePulse personal API token (sp_…)."
}

variable "base_url" {
  type        = string
  default     = "https://servicepulse.dev"
  description = "API origin (no trailing slash)."
}

variable "vendor_slugs" {
  type        = list(string)
  default     = []
  description = "Vendor slugs to evaluate. If empty, all tracked vendors are checked."
}

variable "allow_maintenance" {
  type        = bool
  default     = false
  description = "If true, maintenance is not treated as blocking."
}

variable "allow_unknown" {
  type        = bool
  default     = false
  description = "If false, unknown status blocks (recommended for automation)."
}
