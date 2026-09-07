import { pct, bandColor, bandTint } from '../lib/format.js'

export default function RiskHeadline({ result }) {
  const { probability, band, band_label, uncertainty_band } = result
  return (
    <div
      className="card"
      style={{ background: bandTint(band), borderColor: bandColor(band) + '55' }}
    >
      <div className="headline">
        <div className="risk-num" style={{ color: bandColor(band) }}>
          {pct(probability)}
        </div>
        <div>
          <span className="band-pill" style={{ background: bandColor(band) }}>
            {band} risk
          </span>
          <div className="verdict" style={{ marginTop: 6 }}>
            {band_label}
          </div>
        </div>
      </div>

      {uncertainty_band && (
        <div className="uncertainty">
          If the questions you skipped had gone the other way, this estimate could sit
          anywhere from <strong>{pct(uncertainty_band[0])}</strong> to{' '}
          <strong>{pct(uncertainty_band[1])}</strong>.
        </div>
      )}

      <div className="uncertainty">
        This is a screening aid, not a diagnosis. Only a clinician can confirm diabetes.
      </div>
    </div>
  )
}
