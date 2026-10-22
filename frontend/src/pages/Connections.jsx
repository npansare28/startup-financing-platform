import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import Sidebar from "../components/Sidebar";

function Connections() {
    const navigate = useNavigate();

    const [connections, setConnections] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const fetchConnections = async () => {
        try {
            setLoading(true);
            setError("");

            const response = await api.get("/connections");

            setConnections(response.data?.connections || []);
        } catch (err) {
            console.error("Connections fetch error:", err);

            setError(
                err.response?.data?.message ||
                "Failed to load connections"
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchConnections();
    }, []);

    return (
        <div className="dashboard-layout">
            <Sidebar />

            <div className="main-content">
                <header className="page-header">
                    <div>
                        <h1>My Connections</h1>
                        <p>
                            Your established network of founders and investors.
                        </p>
                    </div>

                    <div style={{ display: "flex", gap: "10px" }}>
                        <button
                            className="secondary-button"
                            onClick={() => navigate("/recommendations")}
                        >
                            ⭐ Discover People
                        </button>

                        <button
                            className="primary-button"
                            onClick={fetchConnections}
                        >
                            🔄 Refresh
                        </button>
                    </div>
                </header>

                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading your network...</p>
                    </div>
                ) : error ? (
                    <div className="error-card">
                        <p>{error}</p>

                        <button
                            className="primary-button"
                            onClick={fetchConnections}
                        >
                            Retry
                        </button>
                    </div>
                ) : connections.length === 0 ? (
                    <div
                        className="empty-state-card"
                        style={{
                            textAlign: "center",
                            padding: "3rem",
                            background: "white",
                            borderRadius: "16px",
                            maxWidth: "500px",
                            margin: "2rem auto"
                        }}
                    >
                        <div
                            style={{
                                fontSize: "3rem",
                                marginBottom: "1rem"
                            }}
                        >
                            🤝
                        </div>

                        <h2>No Connections Yet</h2>

                        <p
                            style={{
                                color: "#64748b",
                                marginBottom: "1.5rem"
                            }}
                        >
                            Explore recommendations and start matching with
                            potential partners to build your network.
                        </p>

                        <button
                            className="primary-button"
                            onClick={() => navigate("/recommendations")}
                        >
                            Explore Recommendations
                        </button>
                    </div>
                ) : (
                    <div
                        className="connections-grid"
                        style={{
                            display: "grid",
                            gridTemplateColumns:
                                "repeat(auto-fill, minmax(320px, 1fr))",
                            gap: "1.5rem"
                        }}
                    >
                        {connections.map((c) => (
                            <div
                                key={c.user_id}
                                className="card"
                                style={{
                                    background: "white",
                                    border:
                                        "1px solid var(--border-color, #e2e8f0)",
                                    borderRadius: "14px",
                                    padding: "1.5rem",
                                    boxShadow:
                                        "0 2px 4px rgba(0,0,0,0.03)"
                                }}
                            >
                                <div
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: "1rem",
                                        marginBottom: "1rem"
                                    }}
                                >
                                    <div
                                        style={{
                                            width: "50px",
                                            height: "50px",
                                            borderRadius: "50%",
                                            background:
                                                c.role === "PITCHER"
                                                    ? "#4338ca"
                                                    : "#065f46",
                                            color: "white",
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center",
                                            fontSize: "1.25rem",
                                            fontWeight: "bold"
                                        }}
                                    >
                                        {(c.name || c.email || "U")
                                            .charAt(0)
                                            .toUpperCase()}
                                    </div>

                                    <div>
                                        <h3
                                            style={{
                                                margin: "0 0 0.2rem",
                                                fontSize: "1.1rem"
                                            }}
                                        >
                                            {c.name ||
                                                c.email?.split("@")[0] ||
                                                "User"}
                                        </h3>

                                        <span
                                            style={{
                                                display: "inline-block",
                                                background:
                                                    c.role === "PITCHER"
                                                        ? "#e0e7ff"
                                                        : "#ecfdf5",
                                                color:
                                                    c.role === "PITCHER"
                                                        ? "#4338ca"
                                                        : "#065f46",
                                                padding: "2px 8px",
                                                borderRadius: "10px",
                                                fontSize: "0.75rem",
                                                fontWeight: "600"
                                            }}
                                        >
                                            {c.role === "PITCHER"
                                                ? "Founder"
                                                : "Investor"}
                                        </span>
                                    </div>
                                </div>

                                <div
                                    style={{
                                        fontSize: "0.85rem",
                                        color: "#64748b",
                                        marginBottom: "1.25rem"
                                    }}
                                >
                                    <div>📧 {c.email}</div>

                                    {c.connected_at && (
                                        <div style={{ marginTop: "4px" }}>
                                            🗓️ Connected{" "}
                                            {new Date(
                                                c.connected_at
                                            ).toLocaleDateString()}
                                        </div>
                                    )}
                                </div>

                                <div
                                    style={{
                                        display: "flex",
                                        gap: "0.5rem"
                                    }}
                                >
                                    <button
                                        className="secondary-button"
                                        style={{ flex: 1 }}
                                        onClick={() =>
                                            navigate(
                                                `/profile/${c.user_id}`
                                            )
                                        }
                                    >
                                        Profile
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default Connections;