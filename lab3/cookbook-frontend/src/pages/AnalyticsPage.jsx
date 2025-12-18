import { useMemo, useState } from "react";
import { useAuth } from "../auth/AuthContext";

const API_BASE = "http://127.0.0.1:8000/api";

const TASKS = [
  {
    key: "top-favorites",
    title: "1) Top recipes by favorites",
    endpoint: "/analytics/top-recipes-by-favorites/",
    params: [{ name: "limit", label: "Limit", type: "number", defaultValue: 10 }],
  },
  {
    key: "ratings",
    title: "2) Recipe ratings (avg rating + comments count)",
    endpoint: "/analytics/recipe-ratings/",
    params: [
      { name: "min_comments", label: "Min comments", type: "number", defaultValue: 1 },
      { name: "min_avg_rating", label: "Min avg rating", type: "number", defaultValue: 0 },
    ],
  },
  {
    key: "ingredient-usage",
    title: "3) Ingredient usage (in how many recipes)",
    endpoint: "/analytics/ingredient-usage/",
    params: [{ name: "min_recipes", label: "Min recipes", type: "number", defaultValue: 1 }],
  },
  {
    key: "recipes-by-items",
    title: "4) Recipes by ingredient count (complexity proxy)",
    endpoint: "/analytics/recipes-by-ingredient-count/",
    params: [{ name: "min_items", label: "Min ingredients", type: "number", defaultValue: 1 }],
  },
  {
    key: "comments-trend",
    title: "5) Comments by month (trend)",
    endpoint: "/analytics/comments-by-month/",
    params: [{ name: "months", label: "Months", type: "number", defaultValue: 12 }],
  },
  {
    key: "unit-usage",
    title: "6) Unit usage (count + avg quantity)",
    endpoint: "/analytics/unit-usage/",
    params: [{ name: "min_items", label: "Min items", type: "number", defaultValue: 1 }],
  },
];

function buildQuery(paramsObj) {
  const sp = new URLSearchParams();
  Object.entries(paramsObj).forEach(([k, v]) => {
    if (v !== "" && v !== null && v !== undefined) sp.set(k, v);
  });
  const qs = sp.toString();
  return qs ? `?${qs}` : "";
}

export default function AnalyticsPage() {
  const { token, logout } = useAuth();

  const [selectedKey, setSelectedKey] = useState(TASKS[0].key);
  const selectedTask = useMemo(
    () => TASKS.find((t) => t.key === selectedKey),
    [selectedKey]
  );

  const [params, setParams] = useState(() => {
    const init = {};
    TASKS.forEach((t) => {
      t.params?.forEach((p) => (init[`${t.key}.${p.name}`] = p.defaultValue ?? ""));
    });
    return init;
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const currentParamsObj = useMemo(() => {
    const obj = {};
    selectedTask.params?.forEach((p) => {
      obj[p.name] = params[`${selectedTask.key}.${p.name}`];
    });
    return obj;
  }, [params, selectedTask]);

  async function runTask() {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const url = `${API_BASE}${selectedTask.endpoint}${buildQuery(currentParamsObj)}`;
      const res = await fetch(url, {
        headers: { Authorization: `Token ${token}` },
      });

      if (res.status === 401) {
        logout();
        throw new Error("Session expired. Please log in again.");
      }
      if (!res.ok) throw new Error("Failed to load analytics");

      const data = await res.json();
      setResult({ url, ...data });
    } catch (e) {
      setError(e.message || "Error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h2>Analytics (Lab 3)</h2>
        <p className="muted">
          Click any task → it calls the Django REST endpoint that returns a pandas DataFrame
          as JSON (rows + columns + basic stats).
        </p>

        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <a className="btn btn-secondary" href="http://127.0.0.1:8000/dashboard/analytics/" target="_blank" rel="noreferrer">
            Open Django Plotly Dashboard (v1)
          </a>
          <a className="btn btn-secondary" href="http://127.0.0.1:8000/dashboard/analytics/v2/" target="_blank" rel="noreferrer">
            Open Django Bokeh Dashboard (v2)
          </a>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3>Tasks</h3>
          <div className="list">
            {TASKS.map((t) => (
              <button
                key={t.key}
                className={"task-btn " + (t.key === selectedKey ? "task-btn-active" : "")}
                onClick={() => setSelectedKey(t.key)}
                type="button"
              >
                {t.title}
              </button>
            ))}
          </div>
        </div>

        <div className="card">
          <h3>Run</h3>

          <div className="form-grid">
            {selectedTask.params?.map((p) => (
              <label key={p.name} className="form-field">
                <span className="label">{p.label}</span>
                <input
                  type={p.type || "text"}
                  value={params[`${selectedTask.key}.${p.name}`]}
                  onChange={(e) =>
                    setParams((prev) => ({
                      ...prev,
                      [`${selectedTask.key}.${p.name}`]: e.target.value,
                    }))
                  }
                />
              </label>
            ))}
          </div>

          <button className="btn btn-primary" onClick={runTask} disabled={loading}>
            {loading ? "Loading..." : "Fetch DataFrame"}
          </button>

          {error && <p className="error">{error}</p>}

          {result && (
            <>
              <p className="muted" style={{ marginTop: 10 }}>
                Endpoint: <code>{result.url}</code>
              </p>

              <h4>Stats</h4>
              <pre className="code">
                {JSON.stringify(result.stats, null, 2)}
              </pre>

              <h4>Rows</h4>
              <div className="table-wrap">
                <table className="table">
                  <thead>
                    <tr>
                      {result.columns?.map((c) => (
                        <th key={c}>{c}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(result.rows || []).slice(0, 50).map((r, idx) => (
                      <tr key={idx}>
                        {result.columns?.map((c) => (
                          <td key={c}>{String(r[c] ?? "")}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {(result.rows || []).length > 50 && (
                <p className="muted">Showing first 50 rows.</p>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
