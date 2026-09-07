import type { ListingInput, PredictionResponse } from "../types";

/** Million VND -> "X.XX tỷ VNĐ" (or "X triệu VNĐ" below one tỷ). */
export function toBillion(millionVnd: number): string {
  const billion = millionVnd / 1000;
  if (billion >= 1) return `${billion.toLocaleString("vi-VN", { maximumFractionDigits: 2 })} tỷ VNĐ`;
  return `${millionVnd.toLocaleString("vi-VN", { maximumFractionDigits: 1 })} triệu VNĐ`;
}

/** Compact million-VND number, e.g. 10627 -> "10,627". */
export function toMillion(millionVnd: number): string {
  return millionVnd.toLocaleString("en-US", { maximumFractionDigits: 0 });
}

/**
 * A rough low–high band around a point estimate. The model is not calibrated for
 * intervals, so this is a presentation aid: ±spread widened for sparse inputs.
 */
export function estimateRange(
  predicted: number,
  input: ListingInput,
): { low: number; high: number; spreadPct: number } {
  const filled = [
    input.Width, input.Length, input.Bedrooms, input.Bathrooms, input.Floors,
    input["Property Type"], input.Province, input.district,
  ].filter((v) => v !== undefined && v !== "").length;
  // 8 optional signals: full inputs -> ±18%, area-only -> ±35%
  const spreadPct = 0.35 - (filled / 8) * 0.17;
  return {
    low: predicted * (1 - spreadPct),
    high: predicted * (1 + spreadPct),
    spreadPct,
  };
}

/** Fallback interpretation when the API does not return one. */
export function localInterpretation(result: PredictionResponse, input: ListingInput): string {
  const loc = [input.district, input.Province].filter(Boolean).join(", ") || "the selected area";
  const perM2 = result.price_per_m2
    ? ` (${result.price_per_m2.toLocaleString("en-US", { maximumFractionDigits: 1 })} million VND/m²)`
    : "";
  const type = input["Property Type"] ? `${input["Property Type"]} ` : "property ";
  return `Estimated market value ≈ ${toBillion(result.predicted_price)}${perM2} for a ${
    input.Area
  } m² ${type}in ${loc}.`;
}
