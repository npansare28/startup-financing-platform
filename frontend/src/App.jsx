import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";

import Login         from "./pages/login";
import Signup        from "./pages/Signup";
import Dashboard     from "./pages/Dashboard";
import Search        from "./pages/Search";
import Recommendations from "./pages/Recommendations";
import Matches       from "./pages/Matches";
import Connections   from "./pages/Connections";
import Posts         from "./pages/Posts";
import Notifications from "./pages/Notifications";
import Profile       from "./pages/Profile";

function App() {
    return (
        <BrowserRouter>
            <Routes>

                {/* Public routes */}
                <Route path="/"       element={<Navigate to="/login" replace />} />
                <Route path="/login"  element={<Login />} />
                <Route path="/signup" element={<Signup />} />

                {/* Protected routes */}
                <Route path="/dashboard"     element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                <Route path="/search"        element={<ProtectedRoute><Search /></ProtectedRoute>} />
                <Route path="/recommendations" element={<ProtectedRoute><Recommendations /></ProtectedRoute>} />
                <Route path="/matches"       element={<ProtectedRoute><Matches /></ProtectedRoute>} />
                <Route path="/connections"   element={<ProtectedRoute><Connections /></ProtectedRoute>} />
                <Route path="/posts"         element={<ProtectedRoute><Posts /></ProtectedRoute>} />
                <Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
                <Route path="/profile"       element={<ProtectedRoute><Profile /></ProtectedRoute>} />
                <Route path="/profile/:userId" element={<ProtectedRoute><Profile /></ProtectedRoute>} />

            </Routes>
        </BrowserRouter>
    );
}

export default App;