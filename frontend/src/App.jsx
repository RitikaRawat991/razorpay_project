import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeNav, setActiveNav] = useState("dashboard");

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_URL}/api/analytics/dashboard`
      );

      if (!response.ok) {
        throw new Error(
          `Backend returned ${response.status}`
        );
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

  const scrollToSection = (id) => {
    const element = document.getElementById(id);

    if (element) {
      element.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }

    setActiveNav(id);
  };

  const formatAmount = (amount) => {
    return `₹${Number(amount || 0).toLocaleString("en-IN")}`;
  };

  const summary = dashboard?.summary || {};

  const funnel = dashboard?.funnel || {};

  const recentRecoveries =
    dashboard?.recent_recoveries || [];

  const customerLearning =
    dashboard?.customer_learning || [];

  const maxFunnelValue = Math.max(
    funnel.failed_payments || 0,
    funnel.recovery_opportunities || 0,
    funnel.recovery_actions || 0,
    funnel.successful_recoveries || 0,
    1
  );

  if (loading) {
    return (
      <div className="loading">
        <div>
          <strong>RecoverIQ</strong>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">

      {/* ================================================== */}
      {/* SIDEBAR */}
      {/* ================================================== */}

      <aside className="sidebar">

        <div className="sidebar-brand">
          <div className="brand-mark">
            R
          </div>

          <div>
            <div className="brand-name">
              RecoverIQ
            </div>

            <div className="brand-subtitle">
              AI Revenue Recovery
            </div>
          </div>
        </div>

        <nav className="nav">

          <button
            className={`nav-item ${
              activeNav === "dashboard"
                ? "active"
                : ""
            }`}
            onClick={() =>
              scrollToSection("dashboard")
            }
          >
            <span className="nav-icon">▦</span>
            <span>Dashboard</span>
          </button>

          <button
            className={`nav-item ${
              activeNav === "payments"
                ? "active"
                : ""
            }`}
            onClick={() =>
              scrollToSection("payments")
            }
          >
            <span className="nav-icon">◉</span>
            <span>Payments</span>
          </button>

          <button
            className={`nav-item ${
              activeNav === "recoveries"
                ? "active"
                : ""
            }`}
            onClick={() =>
              scrollToSection("recoveries")
            }
          >
            <span className="nav-icon">↻</span>
            <span>Recoveries</span>
          </button>

          <button
            className={`nav-item ${
              activeNav === "ai-intelligence"
                ? "active"
                : ""
            }`}
            onClick={() =>
              scrollToSection("ai-intelligence")
            }
          >
            <span className="nav-icon">◈</span>
            <span>AI Intelligence</span>
          </button>

          <button
            className={`nav-item ${
              activeNav === "customers"
                ? "active"
                : ""
            }`}
            onClick={() =>
              scrollToSection("customers")
            }
          >
            <span className="nav-icon">◎</span>
            <span>Customers</span>
          </button>

          <button
            className={`nav-item ${
              activeNav === "analytics"
                ? "active"
                : ""
            }`}
            onClick={() =>
              scrollToSection("analytics")
            }
          >
            <span className="nav-icon">▤</span>
            <span>Analytics</span>
          </button>

        </nav>

        <div className="sidebar-footer">
          <div className="status-dot"></div>
          <span>System Operational</span>
        </div>

      </aside>


      {/* ================================================== */}
      {/* MAIN */}
      {/* ================================================== */}

      <main className="main" id="dashboard">

        {/* HEADER */}

        <header className="topbar">

          <div>
            <h1>Revenue Recovery Dashboard</h1>

            <p>
              AI-powered payment recovery and
              revenue intelligence
            </p>
          </div>

          <button
            className="refresh-btn"
            onClick={fetchDashboard}
          >
            ↻ Refresh
          </button>

        </header>


        {/* ERROR */}

        {error && (
          <div className="error">
            <strong>RecoverIQ</strong>

            <div>
              {error}
            </div>

            <button
              className="refresh-btn"
              onClick={fetchDashboard}
            >
              Retry
            </button>
          </div>
        )}


        {/* ================================================== */}
        {/* SUMMARY CARDS */}
        {/* ================================================== */}

        <section className="stats-grid">

          <div className="stat-card">

            <div className="stat-label">
              Total Payments
            </div>

            <div className="stat-value">
              {summary.total_payments || 0}
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
              {summary.failed_payments || 0}
            </div>

            <div className="stat-sub">
              Payments requiring recovery
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-label">
              Recovery Opportunities
            </div>

            <div className="stat-value">
              {summary.recovery_opportunities || 0}
            </div>

            <div className="stat-sub">
              AI identified opportunities
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-label">
              Recovered Revenue
            </div>

            <div className="stat-value">
              {formatAmount(
                summary.recovered_amount
              )}
            </div>

            <div className="stat-sub">
              Successfully recovered
            </div>

          </div>

        </section>


        {/* ================================================== */}
        {/* SECONDARY STATS */}
        {/* ================================================== */}

        <section className="stats-grid">

          <div className="stat-card">

            <div className="stat-label">
              Recovery Actions
            </div>

            <div className="stat-value">
              {summary.recovery_actions || 0}
            </div>

            <div className="stat-sub">
              Actions executed
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-label">
              Successful Recoveries
            </div>

            <div className="stat-value">
              {summary.successful_recoveries || 0}
            </div>

            <div className="stat-sub">
              Verified successful outcomes
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-label">
              Recovery Rate
            </div>

            <div className="stat-value">
              {summary.recovery_rate || 0}%
            </div>

            <div className="stat-sub">
              Actions converted to recovery
            </div>

          </div>


          <div className="stat-card">

            <div className="stat-label">
              Failed Payment Recovery
            </div>

            <div className="stat-value">
              {summary.failed_payment_recovery_rate ||
                0}
              %
            </div>

            <div className="stat-sub">
              Failed payments recovered
            </div>

          </div>

        </section>


        {/* ================================================== */}
        {/* PAYMENTS + ANALYTICS */}
        {/* ================================================== */}

        <div
          className="dashboard-grid"
          id="analytics"
        >

          {/* FUNNEL */}

          <section className="panel">

            <h2>
              Recovery Funnel
            </h2>

            <p className="panel-description">
              Payment recovery pipeline from failure
              to successful recovery
            </p>

            <div className="funnel">

              <div className="funnel-row">

                <div className="funnel-label">
                  Failed Payments
                </div>

                <div className="funnel-bar">
                  <div
                    className="funnel-fill"
                    style={{
                      width: `${
                        ((funnel.failed_payments ||
                          0) /
                          maxFunnelValue) *
                        100
                      }%`,
                    }}
                  />
                </div>

                <div className="funnel-value">
                  {funnel.failed_payments || 0}
                </div>

              </div>


              <div className="funnel-row">

                <div className="funnel-label">
                  Recovery Opportunities
                </div>

                <div className="funnel-bar">
                  <div
                    className="funnel-fill"
                    style={{
                      width: `${
                        ((funnel.recovery_opportunities ||
                          0) /
                          maxFunnelValue) *
                        100
                      }%`,
                    }}
                  />
                </div>

                <div className="funnel-value">
                  {funnel.recovery_opportunities ||
                    0}
                </div>

              </div>


              <div className="funnel-row">

                <div className="funnel-label">
                  Recovery Actions
                </div>

                <div className="funnel-bar">
                  <div
                    className="funnel-fill"
                    style={{
                      width: `${
                        ((funnel.recovery_actions ||
                          0) /
                          maxFunnelValue) *
                        100
                      }%`,
                    }}
                  />
                </div>

                <div className="funnel-value">
                  {funnel.recovery_actions || 0}
                </div>

              </div>


              <div className="funnel-row">

                <div className="funnel-label">
                  Successful Recoveries
                </div>

                <div className="funnel-bar">
                  <div
                    className="funnel-fill"
                    style={{
                      width: `${
                        ((funnel.successful_recoveries ||
                          0) /
                          maxFunnelValue) *
                        100
                      }%`,
                    }}
                  />
                </div>

                <div className="funnel-value">
                  {funnel.successful_recoveries ||
                    0}
                </div>

              </div>

            </div>

          </section>


          {/* PERFORMANCE */}

          <section className="panel">

            <h2>
              Recovery Performance
            </h2>

            <p className="panel-description">
              Current revenue recovery performance
            </p>

            <div className="learning-list">

              <div className="learning-item">

                <div className="learning-main">

                  <span className="learning-customer">
                    Recovery Rate
                  </span>

                  <span className="learning-cause">
                    Successful actions
                  </span>

                </div>

                <span className="badge recovered">
                  {summary.recovery_rate || 0}%
                </span>

              </div>


              <div className="learning-item">

                <div className="learning-main">

                  <span className="learning-customer">
                    Failed Recoveries
                  </span>

                  <span className="learning-cause">
                    Recovery attempts that failed
                  </span>

                </div>

                <span className="badge failed">
                  {summary.failed_recoveries || 0}
                </span>

              </div>


              <div className="learning-item">

                <div className="learning-main">

                  <span className="learning-customer">
                    Recovered Revenue
                  </span>

                  <span className="learning-cause">
                    Verified recovered amount
                  </span>

                </div>

                <span className="badge recovered">
                  {formatAmount(
                    summary.recovered_amount
                  )}
                </span>

              </div>


              <div className="learning-item">

                <div className="learning-main">

                  <span className="learning-customer">
                    Recovery Actions
                  </span>

                  <span className="learning-cause">
                    AI recovery interventions
                  </span>

                </div>

                <span className="badge pending">
                  {summary.recovery_actions || 0}
                </span>

              </div>

            </div>

          </section>

        </div>


        {/* ================================================== */}
        {/* PAYMENTS */}
        {/* ================================================== */}

        <section
          className="panel recoveries-panel"
          id="payments"
        >

          <h2>
            Payment Recovery Activity
          </h2>

          <p className="panel-description">
            Latest payment recovery outcomes
          </p>

          <div className="table-wrapper">

            <table>

              <thead>

                <tr>
                  <th>Payment</th>
                  <th>Customer</th>
                  <th>Root Cause</th>
                  <th>Action</th>
                  <th>Status</th>
                  <th>Amount</th>
                </tr>

              </thead>

              <tbody>

                {recentRecoveries.length === 0 ? (

                  <tr>
                    <td colSpan="6">
                      No recovery activity found.
                    </td>
                  </tr>

                ) : (

                  recentRecoveries.map(
                    (recovery) => (

                      <tr
                        key={
                          recovery.outcome_id
                        }
                      >

                        <td>
                          {recovery.razorpay_payment_id ||
                            recovery.payment_id ||
                            "-"}
                        </td>

                        <td>
                          Customer #
                          {recovery.customer_id}
                        </td>

                        <td>
                          {recovery.root_cause ||
                            "-"}
                        </td>

                        <td>
                          <span className="action">
                            {recovery.action ||
                              "-"}
                          </span>
                        </td>

                        <td>

                          <span
                            className={`badge ${
                              recovery.outcome ===
                              "recovered"
                                ? "recovered"
                                : recovery.outcome ===
                                  "failed"
                                ? "failed"
                                : "pending"
                            }`}
                          >
                            {recovery.outcome ||
                              "pending"}
                          </span>

                        </td>

                        <td className="amount">
                          {formatAmount(
                            recovery.recovered_amount
                          )}
                        </td>

                      </tr>

                    )
                  )

                )}

              </tbody>

            </table>

          </div>

        </section>


        {/* ================================================== */}
        {/* RECOVERIES */}
        {/* ================================================== */}

        <section
          className="panel recoveries-panel"
          id="recoveries"
        >

          <h2>
            Recent Recoveries
          </h2>

          <p className="panel-description">
            Successfully recovered payments
          </p>

          <div className="table-wrapper">

            <table>

              <thead>

                <tr>
                  <th>Payment</th>
                  <th>Customer</th>
                  <th>Cause</th>
                  <th>Recovery Action</th>
                  <th>Recovered Amount</th>
                </tr>

              </thead>

              <tbody>

                {recentRecoveries
                  .filter(
                    (item) =>
                      item.outcome ===
                      "recovered"
                  )
                  .map((recovery) => (

                    <tr
                      key={`recovery-${recovery.outcome_id}`}
                    >

                      <td>
                        {recovery.razorpay_payment_id ||
                          recovery.payment_id ||
                          "-"}
                      </td>

                      <td>
                        Customer #
                        {recovery.customer_id}
                      </td>

                      <td>
                        {recovery.root_cause ||
                          "-"}
                      </td>

                      <td>
                        <span className="action">
                          {recovery.action ||
                            "-"}
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


        {/* ================================================== */}
        {/* AI INTELLIGENCE */}
        {/* ================================================== */}

        <section
          className="panel recoveries-panel"
          id="ai-intelligence"
        >

          <h2>
            AI Recovery Pipeline
          </h2>

          <p className="panel-description">
            RecoverIQ closed-loop intelligence:
            Detect → Diagnose → Predict → Guard →
            Act → Verify → Learn
          </p>

          <div className="learning-list">

            <div className="learning-item">

              <div className="learning-main">

                <span className="learning-customer">
                  01 · Detect
                </span>

                <span className="learning-cause">
                  Identifies failed and risky
                  payment events
                </span>

              </div>

              <span className="badge pending">
                ACTIVE
              </span>

            </div>


            <div className="learning-item">

              <div className="learning-main">

                <span className="learning-customer">
                  02 · Diagnose
                </span>

                <span className="learning-cause">
                  Determines the root cause of
                  payment failure
                </span>

              </div>

              <span className="badge recovered">
                ACTIVE
              </span>

            </div>


            <div className="learning-item">

              <div className="learning-main">

                <span className="learning-customer">
                  03 · Predict
                </span>

                <span className="learning-cause">
                  Estimates recovery probability
                  and expected recovery
                </span>

              </div>

              <span className="badge recovered">
                ACTIVE
              </span>

            </div>


            <div className="learning-item">

              <div className="learning-main">

                <span className="learning-customer">
                  04 · Guard
                </span>

                <span className="learning-cause">
                  Validates recovery action using
                  safety rules
                </span>

              </div>

              <span className="badge recovered">
                ACTIVE
              </span>

            </div>


            <div className="learning-item">

              <div className="learning-main">

                <span className="learning-customer">
                  05 · Act
                </span>

                <span className="learning-cause">
                  Executes the recommended recovery
                  intervention
                </span>

              </div>

              <span className="badge recovered">
                ACTIVE
              </span>

            </div>


            <div className="learning-item">

              <div className="learning-main">

                <span className="learning-customer">
                  06 · Verify
                </span>

                <span className="learning-cause">
                  Confirms whether revenue was
                  actually recovered
                </span>

              </div>

              <span className="badge recovered">
                ACTIVE
              </span>

            </div>


            <div className="learning-item">

              <div className="learning-main">

                <span className="learning-customer">
                  07 · Learn
                </span>

                <span className="learning-cause">
                  Stores customer and merchant
                  recovery patterns
                </span>

              </div>

              <span className="badge recovered">
                ACTIVE
              </span>

            </div>

          </div>

        </section>


        {/* ================================================== */}
        {/* CUSTOMERS */}
        {/* ================================================== */}

        <section
          className="panel recoveries-panel"
          id="customers"
        >

          <h2>
            Customer Recovery Memory
          </h2>

          <p className="panel-description">
            Historical recovery behavior used for
            future decisions
          </p>

          <div className="table-wrapper">

            <table>

              <thead>

                <tr>
                  <th>Customer</th>
                  <th>Payment</th>
                  <th>Root Cause</th>
                  <th>Attempts</th>
                  <th>Status</th>
                </tr>

              </thead>

              <tbody>

                {customerLearning.length ===
                0 ? (

                  <tr>
                    <td colSpan="5">
                      No customer learning data
                      available.
                    </td>
                  </tr>

                ) : (

                  customerLearning.map(
                    (memory, index) => (

                      <tr
                        key={`${memory.payment_id}-${index}`}
                      >

                        <td>
                          Customer #
                          {memory.customer_id}
                        </td>

                        <td>
                          {memory.payment_id}
                        </td>

                        <td>
                          {memory.root_cause ||
                            "-"}
                        </td>

                        <td>
                          {memory.attempts || 0}
                        </td>

                        <td>

                          <span
                            className={`badge ${
                              memory.status ===
                              "recovered"
                                ? "recovered"
                                : memory.status ===
                                  "failed"
                                ? "failed"
                                : "pending"
                            }`}
                          >
                            {memory.status ||
                              "pending"}
                          </span>

                        </td>

                      </tr>

                    )
                  )

                )}

              </tbody>

            </table>

          </div>

        </section>


        {/* ================================================== */}
        {/* ANALYTICS */}
        {/* ================================================== */}

        <section
          className="panel recoveries-panel"
        >

          <h2>
            Analytics & Business Impact
          </h2>

          <p className="panel-description">
            Revenue recovery metrics generated by
            RecoverIQ
          </p>

          <div className="stats-grid">

            <div className="stat-card">

              <div className="stat-label">
                Recovered Revenue
              </div>

              <div className="stat-value">
                {formatAmount(
                  summary.recovered_amount
                )}
              </div>

            </div>


            <div className="stat-card">

              <div className="stat-label">
                Successful Recoveries
              </div>

              <div className="stat-value">
                {summary.successful_recoveries ||
                  0}
              </div>

            </div>


            <div className="stat-card">

              <div className="stat-label">
                Recovery Rate
              </div>

              <div className="stat-value">
                {summary.recovery_rate || 0}%
              </div>

            </div>


            <div className="stat-card">

              <div className="stat-label">
                Opportunities
              </div>

              <div className="stat-value">
                {summary.recovery_opportunities ||
                  0}
              </div>

            </div>

          </div>

        </section>


        {/* ================================================== */}
        {/* FOOTER */}
        {/* ================================================== */}

        <footer className="dashboard-footer">

          <span>
            RecoverIQ · AI Revenue Recovery
            Orchestrator
          </span>

          <span>
            Backend: FastAPI · Frontend: React
          </span>

        </footer>

      </main>

    </div>
  );
}

export default App;