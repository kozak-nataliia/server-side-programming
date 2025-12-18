export default function AnalyticsPage() {
  return (
    <div className="page">
      <div className="page-header">
        <h2>Analytics</h2>
        <p className="muted">Admins only. Choose a dashboard:</p>

        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <a
            className="btn btn-secondary"
            href="http://127.0.0.1:8000/dashboard/analytics/"
            target="_blank"
            rel="noreferrer"
          >
            Open Plotly Dashboard (v1)
          </a>

          <a
            className="btn btn-secondary"
            href="http://127.0.0.1:8000/dashboard/analytics/v2/"
            target="_blank"
            rel="noreferrer"
          >
            Open Bokeh Dashboard (v2)
          </a>
        </div>
      </div>
    </div>
  );
}
