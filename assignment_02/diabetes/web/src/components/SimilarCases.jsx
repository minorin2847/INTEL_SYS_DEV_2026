export default function SimilarCases({ similar }) {
  if (!similar || !similar.available) {
    return (
      <div className="card">
        <h2>People like you in the survey</h2>
        <p className="muted small">Not available on this server.</p>
      </div>
    )
  }
  const { k, n_with_diabetes, neighbors } = similar
  return (
    <div className="card">
      <h2>People like you in the survey</h2>
      <p className="card-hint">
        The {k} survey respondents whose full answer pattern is closest to yours,
        found with the same random forest that made the estimate.
      </p>

      <div className="bigcount">
        <span className="n">
          {n_with_diabetes} of {k}
        </span>
        <span className="muted">had diabetes or pre-diabetes</span>
      </div>

      <div className="spacer" />
      {neighbors.map((nb, i) => (
        <div className="case" key={i}>
          <span className={'badge ' + (nb.outcome.startsWith('no') ? 'neg' : 'pos')}>
            {nb.outcome.startsWith('no') ? '–' : '+'}
          </span>
          <div>
            <div>{nb.profile}</div>
            <div className="prox">
              {nb.outcome} · similarity {(nb.proximity * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      ))}
      <p className="muted small" style={{ marginTop: 12 }}>
        Profiles are de-identified survey rows. A high count here is not a diagnosis -
        it reflects who else answered similarly.
      </p>
    </div>
  )
}
