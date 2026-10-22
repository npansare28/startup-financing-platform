import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";
import Sidebar from "../components/Sidebar";

function Profile() {
    const navigate = useNavigate();
    const { userId } = useParams();

    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({});
    const [saveLoading, setSaveLoading] = useState(false);
    const [saveSuccess, setSaveSuccess] = useState("");

    const isOwnProfile = !userId;

   useEffect(() => {
        const fetchProfile = async () => {
            try {
                setLoading(true);
                setError("");

                const url = userId
                    ? `/users/${userId}`
                    : "/profile";

                const response = await api.get(url);

                const data =
                    response.data?.profile ||
                    response.data?.user ||
                    response.data;

                setProfile(data);
                setFormData(data);

                // ---------------------------------------------
                // Record profile view
                // ---------------------------------------------
                // Only record when viewing another user's profile.
                // Do NOT record your own profile.
                // ---------------------------------------------

                if (userId) {
                    try {
                        await api.post(
                            `/profile-views/${userId}`
                        );
                    } catch (viewError) {
                        // Profile should still load even if
                        // recording the view fails.
                        console.error(
                            "Profile view error:",
                            viewError
                        );
                    }
                }

            } catch (err) {

                console.error(
                    "Profile error:",
                    err
                );

                setError(
                    err.response?.data?.message ||
                    err.message ||
                    "Unable to load profile"
                );

            } finally {

                setLoading(false);

            }
        };

        fetchProfile();

    }, [userId]);

    const fetchProfile = async () => {
        try {
            setLoading(true);
            setError("");

            const url = userId ? `/users/${userId}` : "/profile";
            const response = await api.get(url);
            const data = response.data?.profile || response.data?.user || response.data;
            setProfile(data);
            setFormData(data);
        } catch (err) {
            console.error("Profile error:", err);
            setError(err.response?.data?.message || err.message || "Unable to load profile");
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSave = async (e) => {
        e.preventDefault();
        try {
            setSaveLoading(true);
            setSaveSuccess("");
            setError("");

            // Parse numeric fields if needed
            const payload = { ...formData };
            if (payload.funding_required !== undefined && payload.funding_required !== "") {
                payload.funding_required = Number(String(payload.funding_required).replace(/[^0-9.]/g, "")) || null;
            }
            if (payload.revenue !== undefined && payload.revenue !== "") {
                payload.revenue = Number(String(payload.revenue).replace(/[^0-9.]/g, "")) || null;
            }
            if (payload.min_investment !== undefined && payload.min_investment !== "") {
                payload.min_investment = Number(String(payload.min_investment).replace(/[^0-9.]/g, "")) || null;
            }
            if (payload.max_investment !== undefined && payload.max_investment !== "") {
                payload.max_investment = Number(String(payload.max_investment).replace(/[^0-9.]/g, "")) || null;
            }
            if (payload.team_size !== undefined && payload.team_size !== "") {
                payload.team_size = parseInt(String(payload.team_size).replace(/[^0-9]/g, ""), 10) || null;
            }
            if (payload.founded_year !== undefined && payload.founded_year !== "") {
                payload.founded_year = parseInt(String(payload.founded_year).replace(/[^0-9]/g, ""), 10) || null;
            }

            await api.put("/profile", payload);
            setProfile(payload);
            setSaveSuccess("Profile updated successfully!");
            setIsEditing(false);
            setTimeout(() => setSaveSuccess(""), 4000);
        } catch (err) {
            console.error("Update profile error:", err);
            setError(err.response?.data?.message || "Failed to update profile");
        } finally {
            setSaveLoading(false);
        }
    };

    const role = profile?.role || "Member";
    const displayName =
        profile?.name ||
        profile?.startup_name ||
        profile?.investor_name ||
        profile?.email?.split("@")[0] ||
        "User";

    return (
        <div className="dashboard-layout">
            <Sidebar />

            <div className="main-content">
                <header className="page-header">
                    <div>
                        <h1>{isOwnProfile ? "My Profile" : `${displayName}'s Profile`}</h1>
                        <p>{isOwnProfile ? "Manage your profile details and preferences." : "Viewing user profile and venture information."}</p>
                    </div>

                    <div style={{ display: "flex", gap: "10px" }}>
                        {!isOwnProfile && (
                            <button className="secondary-button" onClick={() => navigate(-1)}>
                                ← Back
                            </button>
                        )}
                        {isOwnProfile && !isEditing && (
                            <button className="primary-button" onClick={() => setIsEditing(true)}>
                                ✏️ Edit Profile
                            </button>
                        )}
                    </div>
                </header>

                {saveSuccess && (
                    <div className="success-banner" style={{
                        background: "#ecfdf5",
                        color: "#065f46",
                        padding: "1rem",
                        borderRadius: "8px",
                        marginBottom: "1.5rem",
                        border: "1px solid #a7f3d0"
                    }}>
                        ✓ {saveSuccess}
                    </div>
                )}

                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading profile...</p>
                    </div>
                ) : error ? (
                    <div className="error-card">
                        <p>{error}</p>
                        <button className="primary-button" onClick={fetchProfile}>
                            Retry
                        </button>
                    </div>
                ) : !profile ? (
                    <div className="empty-state-card">
                        <p>Profile not found.</p>
                    </div>
                ) : isEditing ? (
                    /* Edit Form */
                    <div className="card" style={{
                        background: "white",
                        padding: "2rem",
                        borderRadius: "16px",
                        border: "1px solid var(--border-color, #e2e8f0)",
                        maxWidth: "800px"
                    }}>
                        <h2 style={{ marginTop: 0, marginBottom: "1.5rem" }}>Edit Profile</h2>
                        <form onSubmit={handleSave}>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
                                <div>
                                    <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Name</label>
                                    <input
                                        type="text"
                                        name="name"
                                        value={formData.name || ""}
                                        onChange={handleInputChange}
                                        style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                    />
                                </div>
                                <div>
                                    <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Location</label>
                                    <input
                                        type="text"
                                        name="location"
                                        value={formData.location || ""}
                                        onChange={handleInputChange}
                                        placeholder="City, Country"
                                        style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                    />
                                </div>
                            </div>

                            <div style={{ marginTop: "1.5rem" }}>
                                <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Website</label>
                                <input
                                    type="text"
                                    name="website"
                                    value={formData.website || ""}
                                    onChange={handleInputChange}
                                    placeholder="https://yourwebsite.com"
                                    style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                />
                            </div>

                            <div style={{ marginTop: "1.5rem" }}>
                                <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Description / Bio</label>
                                <textarea
                                    name="description"
                                    rows="4"
                                    value={formData.description || ""}
                                    onChange={handleInputChange}
                                    placeholder="Tell us about your venture or investment focus..."
                                    style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", border: "1px solid #cbd5e1", resize: "vertical" }}
                                />
                            </div>

                            {/* Pitcher specific fields */}
                            {role === "PITCHER" && (
                                <>
                                    <h3 style={{ marginTop: "2rem", marginBottom: "1rem" }}>Startup Details</h3>
                                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
                                        <div>
                                            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Startup Name</label>
                                            <input
                                                type="text"
                                                name="startup_name"
                                                value={formData.startup_name || ""}
                                                onChange={handleInputChange}
                                                style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                            />
                                        </div>
                                        <div>
                                            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Industry</label>
                                            <input
                                                type="text"
                                                name="industry"
                                                value={formData.industry || ""}
                                                onChange={handleInputChange}
                                                placeholder="e.g. FinTech, AI, HealthTech"
                                                style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                            />
                                        </div>
                                        <div>
                                            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Stage</label>
                                            <select
                                                name="stage"
                                                value={formData.stage || ""}
                                                onChange={handleInputChange}
                                                style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                            >
                                                <option value="">Select Stage</option>
                                                <option value="Idea">Idea</option>
                                                <option value="Pre-Seed">Pre-Seed</option>
                                                <option value="Seed">Seed</option>
                                                <option value="Series A">Series A</option>
                                                <option value="Series B+">Series B+</option>
                                            </select>
                                        </div>
                                        <div>
                                            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Funding Required (₹)</label>
                                            <input
                                                type="number"
                                                name="funding_required"
                                                value={formData.funding_required || ""}
                                                onChange={handleInputChange}
                                                placeholder="e.g. 5000000"
                                                style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                            />
                                        </div>
                                        <div>
                                            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Team Size</label>
                                            <input
                                                type="number"
                                                name="team_size"
                                                value={formData.team_size || ""}
                                                onChange={handleInputChange}
                                                style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                            />
                                        </div>
                                        <div>
                                            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Founded Year</label>
                                            <input
                                                type="number"
                                                name="founded_year"
                                                value={formData.founded_year || ""}
                                                onChange={handleInputChange}
                                                placeholder="e.g. 2024"
                                                style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                            />
                                        </div>
                                        <div>
                                            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Annual Revenue / ARR (₹)</label>
                                            <input
                                                type="number"
                                                name="revenue"
                                                value={formData.revenue || ""}
                                                onChange={handleInputChange}
                                                placeholder="e.g. 5000000"
                                                style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                            />
                                        </div>
                                        <div>
                                            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Traction</label>
                                            <input
                                                type="text"
                                                name="traction"
                                                value={formData.traction || ""}
                                                onChange={handleInputChange}
                                                placeholder="e.g. 10k Active Users"
                                                style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                            />
                                        </div>
                                    </div>
                                </>
                            )}

                            {/* Investor specific fields */}
                            {role === "INVESTOR" && (
                                <>
                                    <h3 style={{ marginTop: "2rem", marginBottom: "1rem" }}>Investor Details</h3>
                                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
                                        <div>
                                            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Firm / Investor Name</label>
                                            <input
                                                type="text"
                                                name="investor_name"
                                                value={formData.investor_name || ""}
                                                onChange={handleInputChange}
                                                style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                            />
                                        </div>
                                        <div>
                                            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Investor Type</label>
                                            <select
                                                name="investor_type"
                                                value={formData.investor_type || ""}
                                                onChange={handleInputChange}
                                                style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                            >
                                                <option value="">Select Type</option>
                                                <option value="Angel">Angel Investor</option>
                                                <option value="VC">Venture Capital</option>
                                                <option value="Family Office">Family Office</option>
                                                <option value="Syndicate">Syndicate</option>
                                                <option value="Corporate VC">Corporate VC</option>
                                            </select>
                                        </div>
                                        <div>
                                            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Min Check Size (₹)</label>
                                            <input
                                                type="number"
                                                name="min_investment"
                                                value={formData.min_investment || ""}
                                                onChange={handleInputChange}
                                                placeholder="e.g. 500000"
                                                style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                            />
                                        </div>
                                        <div>
                                            <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Max Check Size (₹)</label>
                                            <input
                                                type="number"
                                                name="max_investment"
                                                value={formData.max_investment || ""}
                                                onChange={handleInputChange}
                                                placeholder="e.g. 50000000"
                                                style={{ width: "100%", padding: "0.75rem", borderRadius: "8px", border: "1px solid #cbd5e1" }}
                                            />
                                        </div>
                                    </div>
                                </>
                            )}

                            <div style={{ display: "flex", gap: "1rem", marginTop: "2rem" }}>
                                <button
                                    type="submit"
                                    className="primary-button"
                                    disabled={saveLoading}
                                >
                                    {saveLoading ? "Saving..." : "Save Profile"}
                                </button>
                                <button
                                    type="button"
                                    className="secondary-button"
                                    onClick={() => {
                                        setFormData(profile);
                                        setIsEditing(false);
                                    }}
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                ) : (
                    /* View Profile Card */
                    <div className="profile-card" style={{
                        background: "white",
                        borderRadius: "16px",
                        border: "1px solid var(--border-color, #e2e8f0)",
                        padding: "2.5rem",
                        maxWidth: "800px"
                    }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "1.5rem", marginBottom: "2rem" }}>
                            <div className="profile-avatar" style={{
                                width: "72px",
                                height: "72px",
                                borderRadius: "50%",
                                background: role === "PITCHER" ? "#4338ca" : "#065f46",
                                color: "white",
                                fontSize: "2rem",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                fontWeight: "bold"
                            }}>
                                {displayName.charAt(0).toUpperCase()}
                            </div>
                            <div>
                                <h2 style={{ margin: "0 0 0.25rem", fontSize: "1.75rem" }}>{displayName}</h2>
                                <span style={{
                                    display: "inline-block",
                                    background: role === "PITCHER" ? "#e0e7ff" : "#ecfdf5",
                                    color: role === "PITCHER" ? "#4338ca" : "#065f46",
                                    padding: "3px 12px",
                                    borderRadius: "12px",
                                    fontSize: "0.85rem",
                                    fontWeight: "600"
                                }}>
                                    {role === "PITCHER" ? "🚀 Startup Founder" : "💼 Investor"}
                                </span>
                            </div>
                        </div>

                        <div className="profile-details-grid" style={{
                            display: "grid",
                            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                            gap: "1.5rem",
                            marginBottom: "2rem",
                            padding: "1.5rem",
                            background: "var(--bg-subtle, #f8fafc)",
                            borderRadius: "12px"
                        }}>
                            <div>
                                <span style={{ fontSize: "0.8rem", color: "#64748b", textTransform: "uppercase" }}>Email</span>
                                <strong style={{ display: "block", fontSize: "1rem" }}>{profile.email || "Not provided"}</strong>
                            </div>
                            <div>
                                <span style={{ fontSize: "0.8rem", color: "#64748b", textTransform: "uppercase" }}>Location</span>
                                <strong style={{ display: "block", fontSize: "1rem" }}>📍 {profile.location || "Not specified"}</strong>
                            </div>
                            <div>
                                <span style={{ fontSize: "0.8rem", color: "#64748b", textTransform: "uppercase" }}>Member Since</span>
                                <strong style={{ display: "block", fontSize: "1rem" }}>
                                    {profile.created_at ? new Date(profile.created_at).toLocaleDateString() : "Recently"}
                                </strong>
                            </div>
                            {profile.website && (
                                <div>
                                    <span style={{ fontSize: "0.8rem", color: "#64748b", textTransform: "uppercase" }}>Website</span>
                                    <strong style={{ display: "block", fontSize: "1rem" }}>
                                        <a href={profile.website.startsWith("http") ? profile.website : `https://${profile.website}`} target="_blank" rel="noreferrer" style={{ color: "#2563eb" }}>
                                            {profile.website}
                                        </a>
                                    </strong>
                                </div>
                            )}
                        </div>

                        {/* Role-Specific Sections */}
                        {role === "PITCHER" && (
                            <div style={{ marginBottom: "2rem" }}>
                                <h3 style={{ borderBottom: "1px solid #e2e8f0", paddingBottom: "0.5rem" }}>Startup Profile</h3>
                                <div style={{
                                    display: "grid",
                                    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                                    gap: "1rem",
                                    marginTop: "1rem"
                                }}>
                                    {profile.startup_name && (
                                        <div>
                                            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Startup Name</span>
                                            <p style={{ margin: "2px 0 0", fontWeight: "600" }}>{profile.startup_name}</p>
                                        </div>
                                    )}
                                    {profile.industry && (
                                        <div>
                                            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Industry</span>
                                            <p style={{ margin: "2px 0 0", fontWeight: "600" }}>{profile.industry}</p>
                                        </div>
                                    )}
                                    {profile.stage && (
                                        <div>
                                            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Stage</span>
                                            <p style={{ margin: "2px 0 0", fontWeight: "600" }}>{profile.stage}</p>
                                        </div>
                                    )}
                                    {profile.funding_required && (
                                        <div>
                                            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Target Funding</span>
                                            <p style={{ margin: "2px 0 0", fontWeight: "600", color: "#2563eb" }}>
                                                ₹{Number(profile.funding_required).toLocaleString()}
                                            </p>
                                        </div>
                                    )}
                                    {profile.team_size && (
                                        <div>
                                            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Team Size</span>
                                            <p style={{ margin: "2px 0 0", fontWeight: "600" }}>{profile.team_size} members</p>
                                        </div>
                                    )}
                                    {profile.founded_year && (
                                        <div>
                                            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Founded</span>
                                            <p style={{ margin: "2px 0 0", fontWeight: "600" }}>{profile.founded_year}</p>
                                        </div>
                                    )}
                                    {profile.revenue && (
                                        <div>
                                            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Revenue</span>
                                            <p style={{ margin: "2px 0 0", fontWeight: "600" }}>{profile.revenue}</p>
                                        </div>
                                    )}
                                    {profile.traction && (
                                        <div>
                                            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Traction</span>
                                            <p style={{ margin: "2px 0 0", fontWeight: "600" }}>{profile.traction}</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        {role === "INVESTOR" && (
                            <div style={{ marginBottom: "2rem" }}>
                                <h3 style={{ borderBottom: "1px solid #e2e8f0", paddingBottom: "0.5rem" }}>Investment Profile</h3>
                                <div style={{
                                    display: "grid",
                                    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                                    gap: "1rem",
                                    marginTop: "1rem"
                                }}>
                                    {profile.investor_name && (
                                        <div>
                                            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Firm Name</span>
                                            <p style={{ margin: "2px 0 0", fontWeight: "600" }}>{profile.investor_name}</p>
                                        </div>
                                    )}
                                    {profile.investor_type && (
                                        <div>
                                            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Investor Type</span>
                                            <p style={{ margin: "2px 0 0", fontWeight: "600" }}>{profile.investor_type}</p>
                                        </div>
                                    )}
                                    {(profile.min_investment || profile.max_investment) && (
                                        <div>
                                            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Check Size Range</span>
                                            <p style={{ margin: "2px 0 0", fontWeight: "600", color: "#059669" }}>
                                                ₹{Number(profile.min_investment || 0).toLocaleString()} - ₹{Number(profile.max_investment || 0).toLocaleString()}
                                            </p>
                                        </div>
                                    )}
                                    {profile.industries && profile.industries.length > 0 && (
                                        <div>
                                            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Focus Industries</span>
                                            <p style={{ margin: "2px 0 0", fontWeight: "600" }}>{profile.industries.join(", ")}</p>
                                        </div>
                                    )}
                                    {profile.preferred_stages && profile.preferred_stages.length > 0 && (
                                        <div>
                                            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Preferred Stages</span>
                                            <p style={{ margin: "2px 0 0", fontWeight: "600" }}>{profile.preferred_stages.join(", ")}</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        <div style={{ marginBottom: "2rem" }}>
                            <h3 style={{ borderBottom: "1px solid #e2e8f0", paddingBottom: "0.5rem" }}>About</h3>
                            <p style={{ color: "#475569", lineHeight: "1.6" }}>
                                {profile.description || "No description provided yet."}
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Profile;