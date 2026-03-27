export declare class ServicePulseError extends Error {
    constructor(message: string);
}
export type UnhealthyVendor = {
    slug: string;
    name?: string;
    currentStatus: string;
};
export declare class StackNotHealthyError extends ServicePulseError {
    readonly unhealthy: UnhealthyVendor[];
    readonly missingSlugs: string[];
    constructor(message: string, unhealthy: UnhealthyVendor[], missingSlugs: string[]);
}
export type TrackedVendorsResponse = {
    vendors?: Array<{
        vendor?: Record<string, unknown>;
    }>;
};
export type AssertStackHealthyOptions = {
    allowMaintenance?: boolean;
    allowUnknown?: boolean;
    extraBadStatuses?: Iterable<string>;
};
export declare class ServicePulseClient {
    private readonly timeoutMs;
    private readonly base;
    private readonly headers;
    constructor(apiToken: string, baseUrl?: string, timeoutMs?: number);
    getTrackedVendors(): Promise<TrackedVendorsResponse>;
    assertStackHealthy(vendorSlugs?: string[] | null, options?: AssertStackHealthyOptions): Promise<void>;
}
//# sourceMappingURL=client.d.ts.map