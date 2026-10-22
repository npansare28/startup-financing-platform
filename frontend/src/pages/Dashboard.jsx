import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import Sidebar from "../components/Sidebar";

function Dashboard() {
    const navigate = useNavigate();
    const { user } = useAuth();

    const [stats, setStats] = useState({
        profileViews: 0,
        connections: 0,
        matches: 0,
        notifications: 0,
    });

    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const [
                    profileViewsRes,
                    connRes,
                    matchRes,
                    notifRes,
                ] = await Promise.allSettled([
                    api.get("/profile-views"),
                    api.get("/connections"),
                    api.get("/matches"),
                    api.get("/notifications"),
                ]);

                setStats({
                    profileViews:
                        profileViewsRes.status === "fulfilled"
                            ? profileViewsRes.value.data?.count || 0
                            : 0,

                    connections:
                        connRes.status === "fulfilled"
                            ? connRes.value.data?.count || 0
                            : 0,

                    matches:
                        matchRes.status === "fulfilled"
                            ? matchRes.value.data?.count || 0
                            : 0,

                    notifications:
                        notifRes.status === "fulfilled"
                            ? notifRes.value.data?.unread_count || 0
                            : 0,
                });

            } catch (error) {
                console.error("Dashboard stats error:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    const displayRole =
        user?.role === "PITCHER"
            ? "Founder"
            : user?.role === "INVESTOR"
                ? "Investor"
                : user?.role || "Member";

    return (
        <div className="dashboard-page">

            <Sidebar />

            <main className="dashboard-main">

                {/* Top Bar */}
                <header className="dashboard-header">

                    <div>
                        <h1>Dashboard</h1>

                        <p>
                            Welcome back,{" "}
                            <strong>
                                {user?.email || "User"}
                            </strong>
                        </p>
                    </div>

                    <div className="user-badge">
                        {displayRole}
                    </div>

                </header>


                {/* Welcome Card */}
                <section className="welcome-card">

                    <div>

                        <span className="welcome-label">
                            YOUR STARTUP JOURNEY
                        </span>

                        <h2>
                            Build connections.
                            <br />
                            Find opportunities.
                        </h2>

                        <p>
                            Discover investors, connect with
                            founders and find the right financing
                            opportunities for your startup.
                        </p>

                        <button
                            className="primary-button"
                            onClick={() => navigate("/search")}
                        >
                            Explore Opportunities →
                        </button>

                    </div>

                </section>


                {/* Stats */}
                <section className="stats-grid">

                    {/* Profile Views */}
                    <div className="stat-card">

                        <div className="stat-icon">
                            👀
                        </div>

                        <div>

                            <span>
                                Profile Views
                            </span>

                            <strong>
                                {loading
                                    ? "—"
                                    : stats.profileViews}
                            </strong>

                        </div>

                    </div>


                    {/* Connections */}
                    <div className="stat-card">

                        <div className="stat-icon">
                            🤝
                        </div>

                        <div>

                            <span>
                                Connections
                            </span>

                            <strong>
                                {loading
                                    ? "—"
                                    : stats.connections}
                            </strong>

                        </div>

                    </div>


                    {/* Matches */}
                    <div className="stat-card">

                        <div className="stat-icon">
                            💫
                        </div>

                        <div>

                            <span>
                                Matches
                            </span>

                            <strong>
                                {loading
                                    ? "—"
                                    : stats.matches}
                            </strong>

                        </div>

                    </div>


                    {/* Notifications */}
                    <div className="stat-card">

                        <div className="stat-icon">
                            🔔
                        </div>

                        <div>

                            <span>
                                Unread Alerts
                            </span>

                            <strong>
                                {loading
                                    ? "—"
                                    : stats.notifications}
                            </strong>

                        </div>

                    </div>

                </section>


                {/* Quick Actions */}
                <section className="dashboard-section">

                    <div className="section-header">

                        <div>

                            <h2>
                                Quick Actions
                            </h2>

                            <p>
                                Get started with the platform
                            </p>

                        </div>

                    </div>


                    <div className="actions-grid">

                        {/* Profile */}
                        <button
                            className="action-card"
                            onClick={() =>
                                navigate("/profile")
                            }
                        >

                            <span className="action-icon">
                                👤
                            </span>

                            <div>

                                <h3>
                                    Complete Profile
                                </h3>

                                <p>
                                    Add your information and
                                    preferences.
                                </p>

                            </div>

                            <span className="arrow">
                                →
                            </span>

                        </button>


                        {/* Recommendations */}
                        <button
                            className="action-card"
                            onClick={() =>
                                navigate("/recommendations")
                            }
                        >

                            <span className="action-icon">
                                ⭐
                            </span>

                            <div>

                                <h3>
                                    View Recommendations
                                </h3>

                                <p>
                                    Swipe on people that match
                                    your goals.
                                </p>

                            </div>

                            <span className="arrow">
                                →
                            </span>

                        </button>


                        {/* Search */}
                        <button
                            className="action-card"
                            onClick={() =>
                                navigate("/search")
                            }
                        >

                            <span className="action-icon">
                                🔎
                            </span>

                            <div>

                                <h3>
                                    {user?.role === "PITCHER"
                                        ? "Find Investors"
                                        : "Find Startups"}
                                </h3>

                                <p>
                                    Discover potential financing
                                    partners.
                                </p>

                            </div>

                            <span className="arrow">
                                →
                            </span>

                        </button>

                    </div>

                </section>

            </main>

        </div>
    );
}

export default Dashboard;