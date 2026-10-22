import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import Sidebar from "../components/Sidebar";

function Matches() {
    const navigate = useNavigate();

    const [matches, setMatches] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const fetchMatches = async () => {
        try {
            setLoading(true);
            setError("");

            const response = await api.get("/matches");

            setMatches(response.data?.matches || []);
        } catch (err) {
            console.error("Fetch matches error:", err);

            setError(
                err.response?.data?.message ||
                "Failed to load matches"
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchMatches();
    }, []);

    return (
        <div className="dashboard-layout">
            <Sidebar />

            <div className="main-content">
                <header className="page-header">
                    <div>
                        <h1>Mutual Matches</h1>

                        <p>
                            Users who mutually swiped right with you.
                            Reach out and start collaborating!
                        </p>
                    </div>

                    <button
                        className="primary-button"
                        onClick={fetchMatches}
                    >
                        🔄 Refresh
                    </button>
                </header>

                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading your matches...</p>
                    </div>
                ) : error ? (
                    <div className="error-card">
                        <p>{error}</p>

                        <button
                            className="primary-button"
                            onClick={fetchMatches}
                        >
                            Try Again
                        </button>
                    </div>
                ) : matches.length === 0 ? (
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
                            💫
                        </div>

                        <h2>No Matches Yet</h2>

                        <p
                            style={{
                                color: "#64748b",
                                marginBottom: "1.5rem"
                            }}
                        >
                            Head over to Recommendations and swipe right
                            on potential partners. When they swipe right
                            on you too, they'll appear here!
                        </p>

                        <button
                            className="primary-button"
                            onClick={() => navigate("/recommendations")}
                        >
                            Discover Recommendations
                        </button>
                    </div>
                ) : (
                    <div
                        className="matches-grid"
                        style={{
                            display: "grid",
                            gridTemplateColumns:
                                "repeat(auto-fill, minmax(320px, 1fr))",
                            gap: "1.5rem"
                        }}
                    >
                        {matches.map((match) => (
                            <div
                                key={match.user_id}
                                className="match-card"
                                style={{
                                    background: "white",
                                    border:
                                        "1px solid var(--border-color, #e2e8f0)",
                                    borderRadius: "14px",
                                    padding: "1.5rem",
                                    display: "flex",
                                    flexDirection: "column",
                                    justifyContent: "space-between",
                                    boxShadow:
                                        "0 4px 6px -1px rgba(0, 0, 0, 0.05)"
                                }}
                            >
                                <div>
                                    <div
                                        style={{
                                            display: "flex",
                                            justifyContent: "space-between",
                                            alignItems: "flex-start",
                                            marginBottom: "0.75rem"
                                        }}
                                    >
                                        <span
                                            style={{
                                                background:
                                                    match.role === "PITCHER"
                                                        ? "#e0e7ff"
                                                        : "#ecfdf5",
                                                color:
                                                    match.role === "PITCHER"
                                                        ? "#4338ca"
                                                        : "#065f46",
                                                padding: "3px 10px",
                                                borderRadius: "12px",
                                                fontSize: "0.8rem",
                                                fontWeight: "600"
                                            }}
                                        >
                                            {match.role === "PITCHER"
                                                ? "Founder"
                                                : "Investor"}
                                        </span>

                                        <span
                                            style={{
                                                fontSize: "0.8rem",
                                                color: "#94a3b8"
                                            }}
                                        >
                                            {match.matched_at
                                                ? new Date(
                                                      match.matched_at
                                                  ).toLocaleDateString()
                                                : "Recently"}
                                        </span>
                                    </div>

                                    <h3
                                        style={{
                                            margin: "0 0 0.25rem",
                                            fontSize: "1.25rem"
                                        }}
                                    >
                                        {match.name ||
                                            match.email?.split("@")[0] ||
                                            "User"}
                                    </h3>

                                    <p
                                        style={{
                                            color: "#64748b",
                                            fontSize: "0.9rem",
                                            margin: "0 0 1rem"
                                        }}
                                    >
                                        {match.email}
                                    </p>
                                </div>

                                <div
                                    style={{
                                        display: "flex",
                                        gap: "0.75rem",
                                        marginTop: "1rem"
                                    }}
                                >
                                    <button
                                        className="secondary-button"
                                        style={{ flex: 1 }}
                                        onClick={() =>
                                            navigate(
                                                `/profile/${match.user_id}`
                                            )
                                        }
                                    >
                                        View Profile
                                    </button>

                                    <button
                                        className="primary-button"
                                        style={{ flex: 1 }}
                                        onClick={() =>
                                            navigate("/connections")
                                        }
                                    >
                                        🤝 Connect
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

export default Matches;