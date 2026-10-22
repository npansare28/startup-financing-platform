import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = [
    { path: "/dashboard",       icon: "🏠", label: "Dashboard" },
    { path: "/profile",         icon: "👤", label: "Profile" },
    { path: "/search",          icon: "🔍", label: "Search" },
    { path: "/recommendations", icon: "⭐", label: "Recommendations" },
    { path: "/connections",     icon: "🤝", label: "Connections" },
    { path: "/matches",         icon: "💫", label: "Matches" },
    { path: "/posts",           icon: "📝", label: "Posts" },
    { path: "/notifications",   icon: "🔔", label: "Notifications" },
];

function Sidebar() {
    const navigate  = useNavigate();
    const location  = useLocation();
    const { user, logout } = useAuth();

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    return (
        <aside className="sidebar">

            <div className="logo">
                <h2>StartFund</h2>
                <span>Financing Platform</span>
            </div>

            <nav className="sidebar-nav">
                {NAV_ITEMS.map((item) => (
                    <button
                        key={item.path}
                        className={
                            location.pathname === item.path
                                ? "nav-item active"
                                : "nav-item"
                        }
                        onClick={() => navigate(item.path)}
                    >
                        {item.icon} {item.label}
                    </button>
                ))}
            </nav>

            <div className="sidebar-user">
                <span className="sidebar-email">
                    {user?.email || "User"}
                </span>
                <span className="sidebar-role-badge">
                    {user?.role === "PITCHER" ? "Founder" : "Investor"}
                </span>
            </div>

            <button
                className="logout-button"
                onClick={handleLogout}
            >
                Logout
            </button>

        </aside>
    );
}

export default Sidebar;
