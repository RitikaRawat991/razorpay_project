import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

function formatAmount(amount) {
  return `₹${Number(amount || 0).toLocaleString("en-IN")}`;
}

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchDashboard = async () => {
    try {
      setError("");

      const response = await fetch(
        `${API_BASE}/api/analytics/dashboard`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch dashboard data");
      }

      const data = await response.json();
      setDashboard(data);
    } catch (err) {
      console.error(err);
      setError(
        "Backend se data nahi aa raha. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const merchantInsights = useMemo(() => {
    if (!dashboard) return [];

    const learning = dashboard.customer_learning || [];
    const recoveries = dashboard.recent_recoveries || [];

    const recovered = recoveries.filter(
      (item) => item.outcome === "recovered"
    );

    const failed = recoveries.filter(
      (item) => item.outcome !== "recovered"
    );

    const causes = {};

    [...learning, ...recoveries].forEach((item) => {
      const cause = item.root_cause || "unknown";

      if (!causes[cause]) {
        causes[cause] = {
          total: 0,
          recovered: 0,
        };
      }

      causes[cause].total += 1;

      if (
        item.status === "recovered" ||
        item.outcome === "recovered"
      ) {
        causes[cause].recovered += 1;
      }
    });

    const topCause =
      Object.entries(causes).sort(
        (a, b) => b[1].total - a[1].total
      )[0] || null;

    const insights = [];

    if (topCause) {
      const [cause, stats] = topCause;

      const successRate =
        stats.total > 0
          ? Math.round(
              (stats.recovered / stats.total) * 100
            )
          : 0;

      insights.push({
        title: "Dominant failure pattern",
        value: cause.replaceAll("_", " "),
        description: `${stats.total} recovery records observed with ${successRate}% successful outcomes.`,
      });
    }

    if (recovered.length > 0) {
      insights.push({
        title: "Best observed intervention",
        value: "retry_payment",
        description: `${recovered.length} recent recovery attempts succeeded using payment retry.`,
      });
    }

    if (failed.length > 0) {
      insights.push({
        title: "Learning opportunity",
        value: `${failed.length} failed attempts`,
        description:
          "RecoverIQ can use these outcomes to improve future recovery decisions.",
      });
    }

    return insights;
  }, [dashboard]);

  if (loading) {
    return (
      <div className="loading">
        Loading RecoverIQ...
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="error">
          <strong>RecoverIQ</strong>
          <p>{error}</p>

          <button
            className="refresh-btn"
            onClick={fetchDashboard}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const summary = dashboard.summary;
  const funnel = dashboard.funnel || {};
  const recentRecoveries =
    dashboard.recent_recoveries || [];
  const customerLearning =
    dashboard.customer_learning || [];

  const maxFunnelValue = Math.max(
    funnel.failed_payments || 0,
    funnel.recovery_opportunities || 0,
    funnel.recovery_actions || 0,
    funnel.successful_recoveries || 0,
    1
  );

  return (
    <div className="dashboard">

      {/* HEADER */}
      <header className="dashboard-header">
        <div className="brand">
          <h1>RecoverIQ</h1>
          <p>
            AI Revenue Recovery Orchestrator
          </p>
        </div>

        <button
          className="refresh-btn"
          onClick={fetchDashboard}
        >
          ↻ Refresh
        </button>
      </header>

      <main className="dashboard-content">

        {/* SUMMARY */}
        <section className="stats-grid">

          <div className="stat-card">
            <div className="stat-label">
              Total Payments
            </div>

            <div className="stat-value">
              {summary.total_payments}
            </div>

            <div className="stat-sub">
              All processed payments
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">
              Failed Payments
            </div>

            <div className="stat-value">
              {summary.failed_payments}
            </div>

            <div className="stat-sub">
              Payments requiring recovery
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">
              Successful Recoveries
            </div>

            <div className="stat-value">
              {summary.successful_recoveries}
            </div>

            <div className="stat-sub">
              {summary.failed_payment_recovery_rate}% of failed payments
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-label">
              Recovered Revenue
            </div>

            <div className="stat-value">
              {formatAmount(summary.recovered_amount)}
            </div>

            <div className="stat-sub">
              Recovery rate: {summary.recovery_rate}%
            </div>
          </div>

        </section>

        {/* FUNNEL + LEARNING */}
        <section className="dashboard-grid">

          {/* FUNNEL */}
          <div className="panel">

            <h2>Recovery Funnel</h2>

            <div className="panel-description">
              From failed payment to successful recovery
            </div>

            <div className="funnel">

              {[
                [
                  "Failed Payments",
                  funnel.failed_payments,
                ],
                [
                  "Recovery Opportunities",
                  funnel.recovery_opportunities,
                ],
                [
                  "Recovery Actions",
                  funnel.recovery_actions,
                ],
                [
                  "Successful Recoveries",
                  funnel.successful_recoveries,
                ],
              ].map(([label, value]) => (

                <div
                  className="funnel-row"
                  key={label}
                >

                  <div className="funnel-label">
                    {label}
                  </div>

                  <div className="funnel-bar">
                    <div
                      className="funnel-fill"
                      style={{
                        width: `${Math.max(
                          ((value || 0) /
                            maxFunnelValue) *
                            100,
                          3
                        )}%`,
                      }}
                    />
                  </div>

                  <div className="funnel-value">
                    {value || 0}
                  </div>

                </div>

              ))}

            </div>

          </div>

          {/* CUSTOMER LEARNING */}
          <div className="panel">

            <h2>Customer Learning</h2>

            <div className="panel-description">
              Recovery memory built from previous outcomes
            </div>

            <div className="learning-list">

              {customerLearning
                .slice(0, 6)
                .map((memory, index) => (

                  <div
                    className="learning-item"
                    key={`${memory.payment_id}-${index}`}
                  >

                    <div className="learning-main">

                      <div className="learning-customer">
                        Customer #{memory.customer_id}
                      </div>

                      <div className="learning-cause">
                        {memory.root_cause?.replaceAll(
                          "_",
                          " "
                        ) || "Unknown cause"}
                        {" · "}
                        {memory.attempts} attempt
                        {memory.attempts !== 1
                          ? "s"
                          : ""}
                      </div>

                    </div>

                    <span
                      className={`badge ${
                        memory.status
                      }`}
                    >
                      {memory.status}
                    </span>

                  </div>

                ))}

              {customerLearning.length === 0 && (
                <p>No learning data available.</p>
              )}

            </div>

          </div>

        </section>

        {/* MERCHANT LEARNING */}
        <section className="panel recoveries-panel">

          <h2>Merchant Learning & AI Insights</h2>

          <div className="panel-description">
            RecoverIQ learns from recovery outcomes to
            improve future intervention decisions.
          </div>

          <div className="insights-grid">

            {merchantInsights.map((insight) => (

              <div
                className="insight-card"
                key={insight.title}
              >

                <div className="insight-title">
                  {insight.title}
                </div>

                <div className="insight-value">
                  {insight.value}
                </div>

                <div className="insight-description">
                  {insight.description}
                </div>

              </div>

            ))}

          </div>

        </section>

        {/* RECENT RECOVERIES */}
        <section className="panel recoveries-panel">

          <h2>Recent Recoveries</h2>

          <div className="panel-description">
            Latest recovery actions executed by RecoverIQ
          </div>

          <div className="table-wrapper">

            <table>

              <thead>
                <tr>
                  <th>Payment</th>
                  <th>Customer</th>
                  <th>Root Cause</th>
                  <th>Action</th>
                  <th>Outcome</th>
                  <th>Recovered</th>
                </tr>
              </thead>

              <tbody>

                {recentRecoveries.map((recovery) => (

                  <tr key={recovery.outcome_id}>

                    <td>
                      {recovery.razorpay_payment_id}
                    </td>

                    <td>
                      #{recovery.customer_id}
                    </td>

                    <td>
                      {recovery.root_cause?.replaceAll(
                        "_",
                        " "
                      )}
                    </td>

                    <td>
                      <span className="action">
                        {recovery.action}
                      </span>
                    </td>

                    <td>
                      <span
                        className={`badge ${recovery.outcome}`}
                      >
                        {recovery.outcome}
                      </span>
                    </td>

                    <td className="amount">
                      {formatAmount(
                        recovery.recovered_amount
                      )}
                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        </section>

      </main>

    </div>
  );
}

export default App;