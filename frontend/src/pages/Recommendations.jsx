import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import Sidebar from "../components/Sidebar";

function Recommendations() {
    const navigate = useNavigate();

    const [profiles, setProfiles] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [matchedUser, setMatchedUser] = useState(null);
    const [swiping, setSwiping] = useState(false);

    useEffect(() => {
        fetchRecommendations();
    }, []);

    const fetchRecommendations = async () => {
        try {
            setLoading(true);
            setError("");
            const response = await api.get("/matching");
            const list = response.data?.profiles || [];
            setProfiles(list);
            setCurrentIndex(0);
        } catch (err) {
            console.error("Recommendations fetch error:", err);
            setError(err.response?.data?.message || "Failed to load recommendations");
        } finally {
            setLoading(false);
        }
    };

    const handleSwipe = async (action) => {
        if (swiping || currentIndex >= profiles.length) return;
        const current = profiles[currentIndex];
        setSwiping(true);

        try {
            const response = await api.post("/matching/swipe", {
                target_user_id: current.user_id,
                action: action,
            });

            if (response.data?.matched) {
                setMatchedUser(current);
            }

            setCurrentIndex((prev) => prev + 1);
        } catch (err) {
            console.error("Swipe error:", err);
            // Move to next even if swipe failed or already swiped
            setCurrentIndex((prev) => prev + 1);
        } finally {
            setSwiping(false);
        }
    };

    const current = profiles[currentIndex];

    const getDisplayName = (p) => {
        if (!p) return "";
        return p.startup_name || p.investor_name || p.name || p.email.split("@")[0];
    };

    const getIndustry = (p) => {
        if (!p) return "Various";
        if (p.industry) return p.industry;
        if (p.industries && p.industries.length > 0) return p.industries.join(", ");
        return "General";
    };

    const getStage = (p) => {
        if (!p) return "All Stages";
        if (p.stage) return p.stage;
        if (p.preferred_stages && p.preferred_stages.length > 0) return p.preferred_stages.join(", ");
        return "Early Stage";
    };

    return (
        <div className="dashboard-layout">
            <Sidebar />

            <div className="main-content">
                <header className="page-header">
                    <div>
                        <h1>Recommendations & Matchmaking</h1>
                        <p>Discover founders and investors tailored for your goals.</p>
                    </div>
                    <button className="primary-button" onClick={fetchRecommendations}>
                        🔄 Refresh
                    </button>
                </header>

                {matchedUser && (
                    <div className="match-banner" style={{
                        background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                        color: "white",
                        padding: "1.2rem",
                        borderRadius: "12px",
                        marginBottom: "1.5rem",
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center"
                    }}>
                        <div>
                            <h3 style={{ margin: 0, fontSize: "1.2rem" }}>🎉 It's a Match!</h3>
                            <p style={{ margin: "4px 0 0" }}>
                                You and <strong>{getDisplayName(matchedUser)}</strong> liked each other. You can now connect and collaborate!
                            </p>
                        </div>
                        <div style={{ display: "flex", gap: "8px" }}>
                            <button
                                className="secondary-button"
                                style={{ background: "white", color: "#065f46" }}
                                onClick={() => navigate("/matches")}
                            >
                                View Matches
                            </button>
                            <button
                                className="secondary-button"
                                style={{ background: "rgba(255,255,255,0.2)", color: "white" }}
                                onClick={() => setMatchedUser(null)}
                            >
                                ✕
                            </button>
                        </div>
                    </div>
                )}

                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Finding the best matches for you...</p>
                    </div>
                ) : error ? (
                    <div className="error-card">
                        <p>{error}</p>
                        <button className="primary-button" onClick={fetchRecommendations}>
                            Try Again
                        </button>
                    </div>
                ) : current ? (
                    <div className="recommendations-container" style={{ maxWidth: "600px", margin: "0 auto" }}>
                        <div className="recommendation-card" style={{
                            background: "var(--card-bg, #ffffff)",
                            border: "1px solid var(--border-color, #e2e8f0)",
                            borderRadius: "16px",
                            padding: "2rem",
                            boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.05)"
                        }}>
                            <div className="recommendation-badge" style={{
                                display: "inline-block",
                                background: current.role === "PITCHER" ? "#e0e7ff" : "#ecfdf5",
                                color: current.role === "PITCHER" ? "#4338ca" : "#065f46",
                                padding: "4px 12px",
                                borderRadius: "20px",
                                fontSize: "0.85rem",
                                fontWeight: "600",
                                marginBottom: "1rem"
                            }}>
                                {current.role === "PITCHER" ? "🚀 Startup / Founder" : "💼 Investor"}
                            </div>

                            <h2 style={{ margin: "0 0 0.5rem", fontSize: "1.75rem" }}>
                                {getDisplayName(current)}
                            </h2>
                            <p style={{ color: "var(--text-muted, #64748b)", margin: "0 0 1.5rem" }}>
                                {current.email}
                            </p>

                            <div style={{
                                display: "grid",
                                gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
                                gap: "1rem",
                                padding: "1rem",
                                background: "var(--bg-subtle, #f8fafc)",
                                borderRadius: "10px",
                                marginBottom: "1.5rem"
                            }}>
                                <div>
                                    <div style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "uppercase" }}>Industry</div>
                                    <strong style={{ fontSize: "0.95rem" }}>{getIndustry(current)}</strong>
                                </div>
                                <div>
                                    <div style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "uppercase" }}>Location</div>
                                    <strong style={{ fontSize: "0.95rem" }}>📍 {current.location || "Not specified"}</strong>
                                </div>
                                <div>
                                    <div style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "uppercase" }}>Stage</div>
                                    <strong style={{ fontSize: "0.95rem" }}>{getStage(current)}</strong>
                                </div>
                                {current.funding_required && (
                                    <div>
                                        <div style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "uppercase" }}>Target Funding</div>
                                        <strong style={{ fontSize: "0.95rem", color: "#2563eb" }}>₹{Number(current.funding_required).toLocaleString()}</strong>
                                    </div>
                                )}
                                {(current.min_investment || current.max_investment) && (
                                    <div>
                                        <div style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "uppercase" }}>Check Size</div>
                                        <strong style={{ fontSize: "0.95rem", color: "#059669" }}>
                                            ₹{Number(current.min_investment || 0).toLocaleString()} - ₹{Number(current.max_investment || 0).toLocaleString()}
                                        </strong>
                                    </div>
                                )}
                            </div>

                            {typeof current.compatibility_score === "number" && (
                                <div style={{
                                    marginBottom: "1.5rem",
                                    padding: "1rem",
                                    background: "#f0fdf4",
                                    border: "1px solid #bbf7d0",
                                    borderRadius: "12px"
                                }}>
                                    <div style={{
                                        display: "flex",
                                        justifyContent: "space-between",
                                        alignItems: "center",
                                        marginBottom: "0.75rem"
                                    }}>
                                        <strong style={{ color: "#166534" }}>🤖 ML Compatibility</strong>
                                        <strong style={{ color: "#15803d", fontSize: "1.2rem" }}>
                                            {current.compatibility_score}%
                                        </strong>
                                    </div>

                                    {current.compatibility_features && (
                                        <div style={{ display: "grid", gap: "6px", fontSize: "0.85rem", color: "#475569" }}>
                                            <div style={{ display: "flex", justifyContent: "space-between" }}>
                                                <span>Industry match</span>
                                                <strong>{Math.round((current.compatibility_features.industry_match || 0) * 100)}%</strong>
                                            </div>
                                            <div style={{ display: "flex", justifyContent: "space-between" }}>
                                                <span>Stage match</span>
                                                <strong>{Math.round((current.compatibility_features.stage_match || 0) * 100)}%</strong>
                                            </div>
                                            <div style={{ display: "flex", justifyContent: "space-between" }}>
                                                <span>Investment fit</span>
                                                <strong>{Math.round((current.compatibility_features.investment_fit || 0) * 100)}%</strong>
                                            </div>
                                            <div style={{ display: "flex", justifyContent: "space-between" }}>
                                                <span>Location match</span>
                                                <strong>{Math.round((current.compatibility_features.location_match || 0) * 100)}%</strong>
                                            </div>
                                            <div style={{ display: "flex", justifyContent: "space-between" }}>
                                                <span>Profile similarity</span>
                                                <strong>{Math.round((current.compatibility_features.text_similarity || 0) * 100)}%</strong>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            <div style={{ marginBottom: "1.5rem" }}>
                                <h4 style={{ margin: "0 0 0.5rem", color: "var(--text-secondary, #334155)" }}>About</h4>
                                <p style={{ color: "var(--text-muted, #64748b)", lineHeight: "1.6", margin: 0 }}>
                                    {current.description || "No description provided yet."}
                                </p>
                            </div>

                            {current.website && (
                                <div style={{ marginBottom: "1.5rem" }}>
                                    <a
                                        href={current.website.startsWith("http") ? current.website : `https://${current.website}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        style={{ color: "#2563eb", textDecoration: "none", fontSize: "0.9rem" }}
                                    >
                                        🌐 {current.website}
                                    </a>
                                </div>
                            )}

                            <div style={{
                                display: "flex",
                                justifyContent: "center",
                                alignItems: "center",
                                gap: "1.5rem",
                                paddingTop: "1rem",
                                borderTop: "1px solid var(--border-color, #e2e8f0)"
                            }}>
                                <button
                                    disabled={swiping}
                                    onClick={() => handleSwipe("LEFT")}
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "center",
                                        width: "60px",
                                        height: "60px",
                                        borderRadius: "50%",
                                        border: "2px solid #ef4444",
                                        background: "white",
                                        color: "#ef4444",
                                        fontSize: "1.5rem",
                                        cursor: "pointer",
                                        transition: "all 0.2s ease"
                                    }}
                                    title="Pass"
                                >
                                    ✕
                                </button>

                                <button
                                    onClick={() => navigate(`/profile/${current.user_id}`)}
                                    className="secondary-button"
                                    style={{ padding: "0.6rem 1.2rem" }}
                                >
                                    View Full Profile
                                </button>

                                <button
                                    disabled={swiping}
                                    onClick={() => handleSwipe("RIGHT")}
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "center",
                                        width: "60px",
                                        height: "60px",
                                        borderRadius: "50%",
                                        border: "none",
                                        background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                                        color: "white",
                                        fontSize: "1.6rem",
                                        cursor: "pointer",
                                        boxShadow: "0 4px 12px rgba(16, 185, 129, 0.4)",
                                        transition: "all 0.2s ease"
                                    }}
                                    title="Interested"
                                >
                                    ♥
                                </button>
                            </div>
                            <div style={{ textAlign: "center", marginTop: "1rem", color: "#94a3b8", fontSize: "0.85rem" }}>
                                {currentIndex + 1} of {profiles.length} available
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="empty-state-card" style={{
                        textAlign: "center",
                        padding: "3rem",
                        background: "white",
                        borderRadius: "16px",
                        maxWidth: "500px",
                        margin: "2rem auto"
                    }}>
                        <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>✨</div>
                        <h2>You're All Caught Up!</h2>
                        <p style={{ color: "#64748b", marginBottom: "1.5rem" }}>
                            You've swiped through all available profiles. New candidates will appear as more founders and investors join.
                        </p>
                        <button className="primary-button" onClick={fetchRecommendations}>
                            Check for New Profiles
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Recommendations;