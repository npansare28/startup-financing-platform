import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import Sidebar from "../components/Sidebar";

function Posts() {
    const navigate = useNavigate();
    const { user: currentUser } = useAuth();

    const [posts, setPosts] = useState([]);
    const [newPostContent, setNewPostContent] = useState("");
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState("");

    const [openComments, setOpenComments] = useState({});
    const [commentTexts, setCommentTexts] = useState({});

    const fetchPosts = async () => {
        try {
            setLoading(true);
            setError("");

            const response = await api.get("/posts");

            setPosts(response.data?.posts || []);
        } catch (err) {
            console.error("Posts fetch error:", err);

            setError(
                err.response?.data?.message ||
                "Failed to load feed"
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPosts();
    }, []);

    const handleCreatePost = async (e) => {
        e.preventDefault();

        if (!newPostContent.trim()) {
            return;
        }

        try {
            setSubmitting(true);

            await api.post("/posts", {
                content: newPostContent.trim()
            });

            setNewPostContent("");

            await fetchPosts();
        } catch (err) {
            console.error("Create post error:", err);

            alert(
                err.response?.data?.message ||
                "Failed to create post"
            );
        } finally {
            setSubmitting(false);
        }
    };

    const handleToggleLike = async (postId, currentlyLiked) => {
        try {
            if (currentlyLiked) {
                const res = await api.delete(
                    `/posts/${postId}/like`
                );

                setPosts((prev) =>
                    prev.map((p) =>
                        p.post_id === postId
                            ? {
                                  ...p,
                                  liked_by_me: 0,
                                  likes_count:
                                      res.data?.likes_count ??
                                      Math.max(
                                          0,
                                          (p.likes_count || 0) - 1
                                      )
                              }
                            : p
                    )
                );
            } else {
                const res = await api.post(
                    `/posts/${postId}/like`
                );

                setPosts((prev) =>
                    prev.map((p) =>
                        p.post_id === postId
                            ? {
                                  ...p,
                                  liked_by_me: 1,
                                  likes_count:
                                      res.data?.likes_count ??
                                      (p.likes_count || 0) + 1
                              }
                            : p
                    )
                );
            }
        } catch (err) {
            console.error("Toggle like error:", err);
        }
    };

    const handleDeletePost = async (postId) => {
        if (
            !window.confirm(
                "Are you sure you want to delete this post?"
            )
        ) {
            return;
        }

        try {
            await api.delete(`/posts/${postId}`);

            setPosts((prev) =>
                prev.filter((p) => p.post_id !== postId)
            );
        } catch (err) {
            console.error("Delete post error:", err);

            alert(
                err.response?.data?.message ||
                "Failed to delete post"
            );
        }
    };

    const toggleComments = async (postId) => {
        if (openComments[postId]) {
            setOpenComments((prev) => ({
                ...prev,
                [postId]: null
            }));

            return;
        }

        try {
            const res = await api.get(
                `/posts/${postId}/comments`
            );

            setOpenComments((prev) => ({
                ...prev,
                [postId]: res.data?.comments || []
            }));
        } catch (err) {
            console.error(
                "Fetch comments error:",
                err
            );
        }
    };

    const handleAddComment = async (e, postId) => {
        e.preventDefault();

        const text = commentTexts[postId]?.trim();

        if (!text) {
            return;
        }

        try {
            await api.post(
                `/posts/${postId}/comments`,
                {
                    content: text
                }
            );

            setCommentTexts((prev) => ({
                ...prev,
                [postId]: ""
            }));

            const res = await api.get(
                `/posts/${postId}/comments`
            );

            setOpenComments((prev) => ({
                ...prev,
                [postId]: res.data?.comments || []
            }));

            setPosts((prev) =>
                prev.map((p) =>
                    p.post_id === postId
                        ? {
                              ...p,
                              comments_count:
                                  (p.comments_count || 0) + 1
                          }
                        : p
                )
            );
        } catch (err) {
            console.error(
                "Add comment error:",
                err
            );

            alert("Failed to submit comment");
        }
    };

    return (
        <div className="dashboard-layout">
            <Sidebar />

            <div className="main-content">
                <header className="page-header">
                    <div>
                        <h1>Community Feed</h1>

                        <p>
                            Share startup milestones, ask questions,
                            or announce investment thesis updates.
                        </p>
                    </div>

                    <button
                        className="primary-button"
                        onClick={fetchPosts}
                    >
                        🔄 Refresh Feed
                    </button>
                </header>

                <div
                    className="card"
                    style={{
                        background: "white",
                        borderRadius: "14px",
                        padding: "1.5rem",
                        marginBottom: "2rem",
                        border:
                            "1px solid var(--border-color, #e2e8f0)",
                        boxShadow:
                            "0 2px 4px rgba(0,0,0,0.02)"
                    }}
                >
                    <form onSubmit={handleCreatePost}>
                        <textarea
                            placeholder="What are you building or investing in today? Share updates with the network..."
                            rows="3"
                            value={newPostContent}
                            onChange={(e) =>
                                setNewPostContent(
                                    e.target.value
                                )
                            }
                            style={{
                                width: "100%",
                                padding: "0.85rem",
                                borderRadius: "10px",
                                border:
                                    "1px solid #cbd5e1",
                                resize: "vertical",
                                fontSize: "0.95rem",
                                marginBottom: "1rem",
                                fontFamily: "inherit"
                            }}
                        />

                        <div
                            style={{
                                display: "flex",
                                justifyContent: "flex-end"
                            }}
                        >
                            <button
                                type="submit"
                                className="primary-button"
                                disabled={
                                    submitting ||
                                    !newPostContent.trim()
                                }
                            >
                                {submitting
                                    ? "Publishing..."
                                    : "🚀 Publish Post"}
                            </button>
                        </div>
                    </form>
                </div>

                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading community updates...</p>
                    </div>
                ) : error ? (
                    <div className="error-card">
                        <p>{error}</p>

                        <button
                            className="primary-button"
                            onClick={fetchPosts}
                        >
                            Try Again
                        </button>
                    </div>
                ) : posts.length === 0 ? (
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
                            📝
                        </div>

                        <h2>No Posts Yet</h2>

                        <p style={{ color: "#64748b" }}>
                            Be the first to share an update,
                            introduction, or opportunity with
                            the community!
                        </p>
                    </div>
                ) : (
                    <div
                        style={{
                            display: "flex",
                            flexDirection: "column",
                            gap: "1.5rem"
                        }}
                    >
                        {posts.map((post) => {
                            const isLiked =
                                Boolean(post.liked_by_me);

                            const isMine =
                                currentUser &&
                                String(
                                    currentUser.user_id
                                ) === String(post.user_id);

                            const comments =
                                openComments[post.post_id];

                            return (
                                <div
                                    key={post.post_id}
                                    className="card"
                                    style={{
                                        background: "white",
                                        borderRadius: "14px",
                                        padding: "1.75rem",
                                        border:
                                            "1px solid var(--border-color, #e2e8f0)",
                                        boxShadow:
                                            "0 2px 6px rgba(0,0,0,0.02)"
                                    }}
                                >
                                    <div
                                        style={{
                                            display: "flex",
                                            justifyContent:
                                                "space-between",
                                            alignItems:
                                                "flex-start",
                                            marginBottom: "1rem"
                                        }}
                                    >
                                        <div
                                            style={{
                                                display: "flex",
                                                alignItems:
                                                    "center",
                                                gap: "0.75rem"
                                            }}
                                        >
                                            <div
                                                style={{
                                                    width: "44px",
                                                    height: "44px",
                                                    borderRadius:
                                                        "50%",
                                                    background:
                                                        post.author_role ===
                                                        "PITCHER"
                                                            ? "#4338ca"
                                                            : "#065f46",
                                                    color: "white",
                                                    display: "flex",
                                                    alignItems:
                                                        "center",
                                                    justifyContent:
                                                        "center",
                                                    fontWeight:
                                                        "bold",
                                                    fontSize:
                                                        "1.1rem"
                                                }}
                                            >
                                                {(
                                                    post.author_name ||
                                                    "U"
                                                )
                                                    .charAt(0)
                                                    .toUpperCase()}
                                            </div>

                                            <div>
                                                <div
                                                    style={{
                                                        display:
                                                            "flex",
                                                        alignItems:
                                                            "center",
                                                        gap: "8px"
                                                    }}
                                                >
                                                    <strong
                                                        style={{
                                                            cursor:
                                                                "pointer",
                                                            color:
                                                                "#1e293b"
                                                        }}
                                                        onClick={() =>
                                                            navigate(
                                                                `/profile/${post.user_id}`
                                                            )
                                                        }
                                                    >
                                                        {
                                                            post.author_name
                                                        }
                                                    </strong>

                                                    <span
                                                        style={{
                                                            background:
                                                                post.author_role ===
                                                                "PITCHER"
                                                                    ? "#e0e7ff"
                                                                    : "#ecfdf5",
                                                            color:
                                                                post.author_role ===
                                                                "PITCHER"
                                                                    ? "#4338ca"
                                                                    : "#065f46",
                                                            padding:
                                                                "1px 7px",
                                                            borderRadius:
                                                                "8px",
                                                            fontSize:
                                                                "0.75rem",
                                                            fontWeight:
                                                                "600"
                                                        }}
                                                    >
                                                        {post.author_role ===
                                                        "PITCHER"
                                                            ? "Founder"
                                                            : "Investor"}
                                                    </span>
                                                </div>

                                                <span
                                                    style={{
                                                        fontSize:
                                                            "0.8rem",
                                                        color:
                                                            "#94a3b8"
                                                    }}
                                                >
                                                    {post.created_at
                                                        ? new Date(
                                                              post.created_at
                                                          ).toLocaleString()
                                                        : "Recently"}
                                                </span>
                                            </div>
                                        </div>

                                        {isMine && (
                                            <button
                                                style={{
                                                    background:
                                                        "transparent",
                                                    border: "none",
                                                    color:
                                                        "#ef4444",
                                                    cursor:
                                                        "pointer",
                                                    fontSize:
                                                        "0.85rem",
                                                    padding: "4px"
                                                }}
                                                onClick={() =>
                                                    handleDeletePost(
                                                        post.post_id
                                                    )
                                                }
                                                title="Delete post"
                                            >
                                                🗑️
                                            </button>
                                        )}
                                    </div>

                                    <p
                                        style={{
                                            color: "#334155",
                                            lineHeight: "1.6",
                                            fontSize: "1rem",
                                            margin:
                                                "0 0 1.25rem",
                                            whiteSpace:
                                                "pre-line"
                                        }}
                                    >
                                        {post.content}
                                    </p>

                                    <div
                                        style={{
                                            display: "flex",
                                            alignItems:
                                                "center",
                                            gap: "1.5rem",
                                            borderTop:
                                                "1px solid #f1f5f9",
                                            paddingTop: "0.75rem"
                                        }}
                                    >
                                        <button
                                            onClick={() =>
                                                handleToggleLike(
                                                    post.post_id,
                                                    isLiked
                                                )
                                            }
                                            style={{
                                                background:
                                                    "transparent",
                                                border: "none",
                                                color: isLiked
                                                    ? "#ef4444"
                                                    : "#64748b",
                                                cursor:
                                                    "pointer",
                                                display:
                                                    "flex",
                                                alignItems:
                                                    "center",
                                                gap: "6px",
                                                fontSize:
                                                    "0.9rem",
                                                fontWeight:
                                                    isLiked
                                                        ? "600"
                                                        : "normal"
                                            }}
                                        >
                                            {isLiked
                                                ? "❤️"
                                                : "🤍"}{" "}
                                            {post.likes_count ||
                                                0}{" "}
                                            Likes
                                        </button>

                                        <button
                                            onClick={() =>
                                                toggleComments(
                                                    post.post_id
                                                )
                                            }
                                            style={{
                                                background:
                                                    "transparent",
                                                border: "none",
                                                color:
                                                    "#64748b",
                                                cursor:
                                                    "pointer",
                                                display:
                                                    "flex",
                                                alignItems:
                                                    "center",
                                                gap: "6px",
                                                fontSize:
                                                    "0.9rem"
                                            }}
                                        >
                                            💬{" "}
                                            {post.comments_count ||
                                                0}{" "}
                                            Comments
                                        </button>
                                    </div>

                                    {comments && (
                                        <div
                                            style={{
                                                marginTop:
                                                    "1rem",
                                                paddingTop:
                                                    "1rem",
                                                borderTop:
                                                    "1px solid #f1f5f9"
                                            }}
                                        >
                                            <div
                                                style={{
                                                    display:
                                                        "flex",
                                                    flexDirection:
                                                        "column",
                                                    gap: "0.75rem",
                                                    marginBottom:
                                                        "1rem"
                                                }}
                                            >
                                                {comments.length ===
                                                0 ? (
                                                    <p
                                                        style={{
                                                            color:
                                                                "#94a3b8",
                                                            fontSize:
                                                                "0.85rem",
                                                            margin: 0
                                                        }}
                                                    >
                                                        No comments
                                                        yet. Be the
                                                        first!
                                                    </p>
                                                ) : (
                                                    comments.map(
                                                        (c) => (
                                                            <div
                                                                key={
                                                                    c.comment_id
                                                                }
                                                                style={{
                                                                    background:
                                                                        "#f8fafc",
                                                                    borderRadius:
                                                                        "8px",
                                                                    padding:
                                                                        "0.75rem 1rem",
                                                                    fontSize:
                                                                        "0.9rem"
                                                                }}
                                                            >
                                                                <div
                                                                    style={{
                                                                        display:
                                                                            "flex",
                                                                        justifyContent:
                                                                            "space-between",
                                                                        marginBottom:
                                                                            "4px"
                                                                    }}
                                                                >
                                                                    <strong
                                                                        style={{
                                                                            fontSize:
                                                                                "0.85rem",
                                                                            color:
                                                                                "#1e293b"
                                                                        }}
                                                                    >
                                                                        {
                                                                            c.author_name
                                                                        }
                                                                    </strong>

                                                                    <span
                                                                        style={{
                                                                            fontSize:
                                                                                "0.75rem",
                                                                            color:
                                                                                "#94a3b8"
                                                                        }}
                                                                    >
                                                                        {c.created_at
                                                                            ? new Date(
                                                                                  c.created_at
                                                                              ).toLocaleTimeString()
                                                                            : ""}
                                                                    </span>
                                                                </div>

                                                                <p
                                                                    style={{
                                                                        margin: 0,
                                                                        color:
                                                                            "#475569"
                                                                    }}
                                                                >
                                                                    {
                                                                        c.content
                                                                    }
                                                                </p>
                                                            </div>
                                                        )
                                                    )
                                                )}
                                            </div>

                                            <form
                                                onSubmit={(e) =>
                                                    handleAddComment(
                                                        e,
                                                        post.post_id
                                                    )
                                                }
                                                style={{
                                                    display:
                                                        "flex",
                                                    gap: "8px"
                                                }}
                                            >
                                                <input
                                                    type="text"
                                                    placeholder="Write a comment..."
                                                    value={
                                                        commentTexts[
                                                            post.post_id
                                                        ] || ""
                                                    }
                                                    onChange={(
                                                        e
                                                    ) =>
                                                        setCommentTexts(
                                                            (
                                                                prev
                                                            ) => ({
                                                                ...prev,
                                                                [post.post_id]:
                                                                    e
                                                                        .target
                                                                        .value
                                                            })
                                                        )
                                                    }
                                                    style={{
                                                        flex: 1,
                                                        padding:
                                                            "0.5rem 0.75rem",
                                                        borderRadius:
                                                            "8px",
                                                        border:
                                                            "1px solid #cbd5e1",
                                                        fontSize:
                                                            "0.9rem"
                                                    }}
                                                />

                                                <button
                                                    type="submit"
                                                    className="primary-button"
                                                    style={{
                                                        padding:
                                                            "0.5rem 1rem",
                                                        fontSize:
                                                            "0.85rem"
                                                    }}
                                                >
                                                    Post
                                                </button>
                                            </form>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}

export default Posts;