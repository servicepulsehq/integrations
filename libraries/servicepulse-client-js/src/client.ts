const DEFAULT_BASE_URL = "https://servicepulse.dev";

const DEFAULT_BAD = new Set([
  "degraded_performance",
  "partial_outage",
  "major_outage",
  "maintenance",
]);

export class ServicePulseError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ServicePulseError";
  }
}

export type UnhealthyVendor = { slug: string; name?: string; currentStatus: string };

export class StackNotHealthyError extends ServicePulseError {
  readonly unhealthy: UnhealthyVendor[];
  readonly missingSlugs: string[];

  constructor(message: string, unhealthy: UnhealthyVendor[], missingSlugs: string[]) {
    super(message);
    this.name = "StackNotHealthyError";
    this.unhealthy = unhealthy;
    this.missingSlugs = missingSlugs;
  }
}

export type TrackedVendorsResponse = {
  vendors?: Array<{ vendor?: Record<string, unknown> }>;
};

export type AssertStackHealthyOptions = {
  allowMaintenance?: boolean;
  allowUnknown?: boolean;
  extraBadStatuses?: Iterable<string>;
};

export class ServicePulseClient {
  private readonly base: string;
  private readonly headers: Headers;

  constructor(
    apiToken: string,
    baseUrl: string = DEFAULT_BASE_URL,
    private readonly timeoutMs: number = 30_000
  ) {
    const token = (apiToken ?? "").trim();
    if (!token) throw new Error("apiToken is required");
    this.base = baseUrl.replace(/\/$/, "");
    this.headers = new Headers({
      Authorization: `Bearer ${token}`,
      Accept: "application/json",
    });
  }

  async getTrackedVendors(): Promise<TrackedVendorsResponse> {
    const url = `${this.base}/api/v1/tracked-vendors`;
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), this.timeoutMs);
    try {
      const r = await fetch(url, { headers: this.headers, signal: ctrl.signal });
      const text = await r.text();
      if (!r.ok) {
        throw new ServicePulseError(
          `ServicePulse API error ${r.status}: ${text.slice(0, 500)}`
        );
      }
      return JSON.parse(text) as TrackedVendorsResponse;
    } catch (e) {
      if (e instanceof ServicePulseError) throw e;
      if (e instanceof Error && e.name === "AbortError") {
        throw new ServicePulseError(`ServicePulse request timed out after ${this.timeoutMs}ms`);
      }
      throw new ServicePulseError(
        `ServicePulse request failed: ${e instanceof Error ? e.message : String(e)}`
      );
    } finally {
      clearTimeout(t);
    }
  }

  async assertStackHealthy(
    vendorSlugs?: string[] | null,
    options: AssertStackHealthyOptions = {}
  ): Promise<void> {
    const bad = new Set(DEFAULT_BAD);
    if (options.allowMaintenance) bad.delete("maintenance");
    if (options.extraBadStatuses) {
      for (const s of options.extraBadStatuses) bad.add(s);
    }

    const data = await this.getTrackedVendors();
    const rows = data.vendors ?? [];
    const bySlug = new Map<string, Record<string, unknown>>();
    for (const row of rows) {
      const v = row.vendor;
      if (!v || typeof v !== "object") continue;
      const slug = String(v.slug ?? "")
        .trim()
        .toLowerCase();
      if (slug) bySlug.set(slug, v);
    }

    const slugsToCheck =
      vendorSlugs != null && vendorSlugs.length > 0
        ? vendorSlugs.map((s) => s.trim().toLowerCase()).filter(Boolean)
        : [...bySlug.keys()].sort();

    const unhealthy: UnhealthyVendor[] = [];
    const missingSlugs: string[] = [];

    for (const slug of slugsToCheck) {
      const v = bySlug.get(slug);
      if (!v) {
        missingSlugs.push(slug);
        continue;
      }
      const status = String(v.currentStatus ?? "").trim() || "unknown";
      if (status === "unknown" && !options.allowUnknown) {
        unhealthy.push({
          slug,
          name: v.name != null ? String(v.name) : undefined,
          currentStatus: status,
        });
        continue;
      }
      if (bad.has(status)) {
        unhealthy.push({
          slug,
          name: v.name != null ? String(v.name) : undefined,
          currentStatus: status,
        });
      }
    }

    const parts: string[] = [];
    if (unhealthy.length) {
      parts.push(
        `Unhealthy vendors: ${unhealthy.map((u) => `${u.slug}=${u.currentStatus}`).join(", ")}`
      );
    }
    if (missingSlugs.length) {
      parts.push(`Slugs not in tracked stack: ${[...new Set(missingSlugs)].sort().join(", ")}`);
    }
    if (parts.length) {
      throw new StackNotHealthyError(parts.join("; "), unhealthy, [...new Set(missingSlugs)].sort());
    }
  }
}
