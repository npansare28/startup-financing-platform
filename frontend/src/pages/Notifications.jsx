import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import Sidebar from "../components/Sidebar";

function Notifications() {
    const navigate = useNavigate();

    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const fetchNotifications = async () => {
        try {
            setLoading(true);
            setError("");

            const response = await api.get("/notifications");

            setNotifications(response.data?.notifications || []);
            setUnreadCount(response.data?.unread_count || 0);
        } catch (err) {
            console.error("Notifications fetch error:", err);

            setError(
                err.response?.data?.message ||
                "Failed to load notifications"
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchNotifications();
    }, []);

    const markAsRead = async (id) => {
        try {
            await api.put(`/notifications/${id}/read`);

            setNotifications((prev) =>
                prev.map((n) =>
                    n.notification_id === id
                        ? { ...n, is_read: 1 }
                        : n
                )
            );

            setUnreadCount((prev) => Math.max(0, prev - 1));
        } catch (err) {
            console.error("Mark read error:", err);
        }
    };

    const markAllAsRead = async () => {
        try {
            await api.put("/notifications/read-all");

            setNotifications((prev) =>
                prev.map((n) => ({
                    ...n,
                    is_read: 1
                }))
            );

            setUnreadCount(0);
        } catch (err) {
            console.error("Mark all read error:", err);
        }
    };

    const getIcon = (type) => {
        switch (type?.toLowerCase()) {
            case "match":
                return "⭐";

            case "connection":
                return "🤝";

            case "like":
                return "♥";

            case "comment":
            case "post":
                return "📝";

            default:
                return "🔔";
        }
    };

    return (
        <div className="dashboard-layout">
            <Sidebar />

            <div className="main-content">
                <header className="page-header">
                    <div>
                        <h1>Notifications</h1>

                        <p>
                            Stay updated with matches, connection requests,
                            and platform activity.

                            {unreadCount > 0 && (
                                <span
                                    style={{
                                        marginLeft: "8px",
                                        background: "#ef4444",
                                        color: "white",
                                        padding: "2px 8px",
                                        borderRadius: "10px",
                                        fontSize: "0.8rem",
                                        fontWeight: "600"
                                    }}
                                >
                                    {unreadCount} unread
                                </span>
                            )}
                        </p>
                    </div>

                    <div
                        style={{
                            display: "flex",
                            gap: "10px"
                        }}
                    >
                        {unreadCount > 0 && (
                            <button
                                className="secondary-button"
                                onClick={markAllAsRead}
                            >
                                ✓ Mark All Read
                            </button>
                        )}

                        <button
                            className="primary-button"
                            onClick={fetchNotifications}
                        >
                            🔄 Refresh
                        </button>
                    </div>
                </header>

                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading notifications...</p>
                    </div>
                ) : error ? (
                    <div className="error-card">
                        <p>{error}</p>

                        <button
                            className="primary-button"
                            onClick={fetchNotifications}
                        >
                            Retry
                        </button>
                    </div>
                ) : notifications.length === 0 ? (
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
                            🔔
                        </div>

                        <h2>No Notifications Yet</h2>

                        <p style={{ color: "#64748b" }}>
                            You will receive notifications when people match
                            with you, interact with your posts, or connect.
                        </p>
                    </div>
                ) : (
                    <div
                        className="notifications-list"
                        style={{
                            display: "flex",
                            flexDirection: "column",
                            gap: "1rem"
                        }}
                    >
                        {notifications.map((n) => {
                            const isRead = Boolean(n.is_read);

                            return (
                                <div
                                    key={n.notification_id}
                                    style={{
                                        display: "flex",
                                        alignItems: "flex-start",
                                        justifyContent: "space-between",
                                        background: isRead
                                            ? "white"
                                            : "#f0fdf4",
                                        border: isRead
                                            ? "1px solid #e2e8f0"
                                            : "1px solid #86efac",
                                        borderRadius: "12px",
                                        padding: "1.25rem",
                                        boxShadow:
                                            "0 2px 4px rgba(0,0,0,0.02)",
                                        transition: "all 0.2s ease"
                                    }}
                                >
                                    <div
                                        style={{
                                            display: "flex",
                                            gap: "1rem",
                                            alignItems: "flex-start"
                                        }}
                                    >
                                        <div
                                            style={{
                                                fontSize: "1.5rem",
                                                width: "44px",
                                                height: "44px",
                                                borderRadius: "10px",
                                                background: isRead
                                                    ? "#f1f5f9"
                                                    : "#dcfce7",
                                                display: "flex",
                                                alignItems: "center",
                                                justifyContent: "center"
                                            }}
                                        >
                                            {getIcon(n.type)}
                                        </div>

                                        <div>
                                            <p
                                                style={{
                                                    margin:
                                                        "0 0 0.35rem",
                                                    fontSize: "0.95rem",
                                                    color: "#1e293b",
                                                    fontWeight: isRead
                                                        ? "normal"
                                                        : "600"
                                                }}
                                            >
                                                {n.message}
                                            </p>

                                            <span
                                                style={{
                                                    fontSize: "0.8rem",
                                                    color: "#94a3b8"
                                                }}
                                            >
                                                {n.created_at
                                                    ? new Date(
                                                          n.created_at
                                                      ).toLocaleString()
                                                    : "Just now"}
                                            </span>
                                        </div>
                                    </div>

                                    <div
                                        style={{
                                            display: "flex",
                                            alignItems: "center",
                                            gap: "10px"
                                        }}
                                    >
                                        {!isRead && (
                                            <button
                                                className="secondary-button"
                                                style={{
                                                    fontSize: "0.8rem",
                                                    padding: "4px 8px"
                                                }}
                                                onClick={() =>
                                                    markAsRead(
                                                        n.notification_id
                                                    )
                                                }
                                            >
                                                Mark read
                                            </button>
                                        )}

                                        {n.sender_id && (
                                            <button
                                                className="secondary-button"
                                                style={{
                                                    fontSize: "0.8rem",
                                                    padding: "4px 8px"
                                                }}
                                                onClick={() =>
                                                    navigate(
                                                        `/profile/${n.sender_id}`
                                                    )
                                                }
                                            >
                                                Profile
                                            </button>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}

export default Notifications;