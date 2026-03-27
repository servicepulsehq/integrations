/**
 * ServicePulse → your server: verify HMAC on raw JSON body.
 * Production sends header X-Signature: <hex HMAC-SHA256 of body UTF-8>.
 */
import crypto from "crypto";
import express from "express";

const PORT = Number(process.env.PORT ?? 3000);
const SECRET = process.env.SERVICEPULSE_WEBHOOK_SECRET ?? "";

function expectedSignature(rawBody, secret) {
  return crypto.createHmac("sha256", secret).update(rawBody).digest("hex");
}

function signaturesMatch(provided, expected) {
  try {
    const a = Buffer.from(provided, "utf8");
    const b = Buffer.from(expected, "utf8");
    if (a.length !== b.length) return false;
    return crypto.timingSafeEqual(a, b);
  } catch {
    return false;
  }
}

function extractSignature(req) {
  const direct = req.get("x-signature");
  if (direct) return direct.trim();
  const legacy = req.get("x-servicepulse-signature");
  if (!legacy) return "";
  const m = /^sha256=(.+)$/i.exec(legacy.trim());
  return m ? m[1].trim() : legacy.trim();
}

const app = express();

app.post(
  "/webhooks/servicepulse",
  express.raw({ type: "application/json" }),
  (req, res) => {
    if (!SECRET) {
      console.error("Set SERVICEPULSE_WEBHOOK_SECRET");
      return res.status(500).send("Server misconfigured");
    }
    const raw = req.body instanceof Buffer ? req.body : Buffer.from([]);
    const sig = extractSignature(req);
    const expected = expectedSignature(raw, SECRET);
    if (!sig || !signaturesMatch(sig, expected)) {
      return res.status(401).send("Invalid signature");
    }

    let payload;
    try {
      payload = JSON.parse(raw.toString("utf8"));
    } catch {
      return res.status(400).send("Invalid JSON");
    }

    console.log("Verified ServicePulse webhook:", payload.trigger, payload.vendor?.slug);
    res.status(204).end();
  }
);

app.get("/health", (_req, res) => res.send("ok"));

app.listen(PORT, () => {
  console.log(`Listening on :${PORT} POST /webhooks/servicepulse`);
});
