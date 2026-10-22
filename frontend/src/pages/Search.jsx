import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import Sidebar from "../components/Sidebar";

function Search() {
    const navigate = useNavigate();

    const [query, setQuery] = useState("");
    const [industry, setIndustry] = useState("");
    const [location, setLocation] = useState("");
    const [stage, setStage] = useState("");

    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [, setSearched] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchMatches = async () => {
            try {
                // existing code
            } catch (error) {
                console.error(error);
            }
        };

        fetchMatches();
    }, []);

    const handleSearch = async (event) => {
        if (event) event.preventDefault();

        setLoading(true);
        setError("");
        setSearched(true);

        try {
            const params = {};
            if (query.trim()) params.query = query.trim();
            if (industry.trim()) params.industry = industry.trim();
            if (location.trim()) params.location = location.trim();
            if (stage.trim()) params.stage = stage.trim();

            const response = await api.get("/search", { params });
            const list = response.data?.results || response.data?.users || [];
            setResults(Array.isArray(list) ? list : []);
        } catch (err) {
            console.error("Search error:", err);
            setError(err.response?.data?.message || "Unable to complete search.");
            setResults([]);
        } finally {
            setLoading(false);
        }
    };

    const clearSearch = () => {
        setQuery("");
        setIndustry("");
        setLocation("");
        setStage("");
        setSearched(false);
        setError("");
    };

    return (
        <div className="dashboard-layout">
            <Sidebar />

            <div className="main-content">
                <header className="page-header">
                    <div>
                        <h1>Discover Opportunities</h1>
                        <p>Search and filter founders, startups, and investors across sectors and stages.</p>
                    </div>
                </header>

                {/* Filter / Search Form */}
                <div className="card" style={{
                    background: "white",
                    borderRadius: "14px",
                    padding: "1.5rem",
                    marginBottom: "2rem",
                    border: "1px solid var(--border-color, #e2e8f0)",
                    boxShadow: "0 2px 4px rgba(0,0,0,0.02)"
                }}>
                    <form onSubmit={handleSearch}>
                        <div style={{
                            display: "grid",
                            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                            gap: "1rem",
                            marginBottom: "1rem"
                        }}>
                            <div>
                                <label style={{ display: "block", marginBottom: "0.4rem", fontSize: "0.85rem", fontWeight: "600" }}>Keywords / Name</label>
                                <input
                                    type="text"
                                    placeholder="Search by keyword, name, bio..."
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    style={{ width: "100%", padding: "0.6rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                />
                            </div>

                            <div>
                                <label style={{ display: "block", marginBottom: "0.4rem", fontSize: "0.85rem", fontWeight: "600" }}>Industry</label>
                                <input
                                    type="text"
                                    placeholder="e.g. FinTech, AI, HealthTech"
                                    value={industry}
                                    onChange={(e) => setIndustry(e.target.value)}
                                    style={{ width: "100%", padding: "0.6rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                />
                            </div>

                            <div>
                                <label style={{ display: "block", marginBottom: "0.4rem", fontSize: "0.85rem", fontWeight: "600" }}>Location</label>
                                <input
                                    type="text"
                                    placeholder="e.g. Bangalore, Mumbai, Remote"
                                    value={location}
                                    onChange={(e) => setLocation(e.target.value)}
                                    style={{ width: "100%", padding: "0.6rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                />
                            </div>

                            <div>
                                <label style={{ display: "block", marginBottom: "0.4rem", fontSize: "0.85rem", fontWeight: "600" }}>Stage</label>
                                <select
                                    value={stage}
                                    onChange={(e) => setStage(e.target.value)}
                                    style={{ width: "100%", padding: "0.6rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                >
                                    <option value="">Any Stage</option>
                                    <option value="Idea">Idea</option>
                                    <option value="Pre-Seed">Pre-Seed</option>
                                    <option value="Seed">Seed</option>
                                    <option value="Series A">Series A</option>
                                    <option value="Series B+">Series B+</option>
                                </select>
                            </div>
                        </div>

                        <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
                            {(query || industry || location || stage) && (
                                <button type="button" className="secondary-button" onClick={clearSearch}>
                                    Clear Filters
                                </button>
                            )}
                            <button type="submit" className="primary-button" disabled={loading}>
                                {loading ? "Searching..." : "🔍 Search"}
                            </button>
                        </div>
                    </form>
                </div>

                {/* Results Section */}
                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Finding matching opportunities...</p>
                    </div>
                ) : error ? (
                    <div className="error-card">
                        <p>{error}</p>
                    </div>
                ) : results.length === 0 ? (
                    <div className="empty-state-card" style={{
                        textAlign: "center",
                        padding: "3rem",
                        background: "white",
                        borderRadius: "16px",
                        maxWidth: "500px",
                        margin: "2rem auto"
                    }}>
                        <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🔍</div>
                        <h2>No Results Found</h2>
                        <p style={{ color: "#64748b" }}>
                            Try adjusting your search criteria or clearing filters to see more members.
                        </p>
                    </div>
                ) : (
                    <div>
                        <div style={{ marginBottom: "1rem", color: "#64748b", fontSize: "0.9rem" }}>
                            Found <strong>{results.length}</strong> matching profiles
                        </div>
                        <div style={{
                            display: "grid",
                            gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
                            gap: "1.5rem"
                        }}>
                            {results.map((r) => {
                                const title = r.startup_name || r.investor_name || r.name || r.email.split("@")[0];
                                const isPitcher = r.role === "PITCHER";

                                return (
                                    <div
                                        key={r.user_id}
                                        className="card"
                                        style={{
                                            background: "white",
                                            border: "1px solid var(--border-color, #e2e8f0)",
                                            borderRadius: "14px",
                                            padding: "1.5rem",
                                            display: "flex",
                                            flexDirection: "column",
                                            justifyContent: "space-between",
                                            boxShadow: "0 2px 4px rgba(0,0,0,0.03)"
                                        }}
                                    >
                                        <div>
                                            <div style={{
                                                display: "flex",
                                                justifyContent: "space-between",
                                                alignItems: "flex-start",
                                                marginBottom: "0.75rem"
                                            }}>
                                                <span style={{
                                                    background: isPitcher ? "#e0e7ff" : "#ecfdf5",
                                                    color: isPitcher ? "#4338ca" : "#065f46",
                                                    padding: "3px 10px",
                                                    borderRadius: "12px",
                                                    fontSize: "0.8rem",
                                                    fontWeight: "600"
                                                }}>
                                                    {isPitcher ? "🚀 Startup" : "💼 Investor"}
                                                </span>
                                                {r.location && (
                                                    <span style={{ fontSize: "0.8rem", color: "#64748b" }}>
                                                        📍 {r.location}
                                                    </span>
                                                )}
                                            </div>

                                            <h3 style={{ margin: "0 0 0.4rem", fontSize: "1.2rem" }}>
                                                {title}
                                            </h3>

                                            <p style={{
                                                color: "#64748b",
                                                fontSize: "0.85rem",
                                                lineHeight: "1.5",
                                                marginBottom: "1rem",
                                                maxHeight: "60px",
                                                overflow: "hidden"
                                            }}>
                                                {r.description || (isPitcher ? `Startup in ${r.industry || 'Tech'}` : `Investor focusing on ${r.investor_type || 'early-stage'}`)}
                                            </p>

                                            <div style={{
                                                display: "flex",
                                                flexWrap: "wrap",
                                                gap: "6px",
                                                marginBottom: "1rem"
                                            }}>
                                                {r.industry && (
                                                    <span style={{ background: "#f1f5f9", padding: "2px 8px", borderRadius: "6px", fontSize: "0.75rem" }}>
                                                        🏷️ {r.industry}
                                                    </span>
                                                )}
                                                {r.stage && (
                                                    <span style={{ background: "#f1f5f9", padding: "2px 8px", borderRadius: "6px", fontSize: "0.75rem" }}>
                                                        📈 {r.stage}
                                                    </span>
                                                )}
                                                {r.funding_required && (
                                                    <span style={{ background: "#eff6ff", color: "#1d4ed8", padding: "2px 8px", borderRadius: "6px", fontSize: "0.75rem", fontWeight: "600" }}>
                                                        ₹{Number(r.funding_required).toLocaleString()}
                                                    </span>
                                                )}
                                                {r.min_investment && (
                                                    <span style={{ background: "#ecfdf5", color: "#065f46", padding: "2px 8px", borderRadius: "6px", fontSize: "0.75rem", fontWeight: "600" }}>
                                                        ₹{Number(r.min_investment).toLocaleString()} - ₹{Number(r.max_investment || 0).toLocaleString()}
                                                    </span>
                                                )}
                                            </div>
                                        </div>

                                        <button
                                            className="secondary-button"
                                            style={{ width: "100%", marginTop: "0.5rem" }}
                                            onClick={() => navigate(`/profile/${r.user_id}`)}
                                        >
                                            View Full Profile
                                        </button>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Search;