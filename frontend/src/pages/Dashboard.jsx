import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { FiUser, FiFileText, FiFolder, FiAlertCircle, FiLoader, FiClock } from 'react-icons/fi';
import { getPages } from '../services/api';

// Format relative time
const formatRelativeTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    return `${Math.floor(diffInSeconds / 604800)}w ago`;
};

// Category configurations
const CATEGORIES = [
    { key: 'characters', label: 'Characters', icon: FiUser },
    { key: 'locations', label: 'Locations', icon: FiFolder },
    { key: 'lore', label: 'Lore', icon: FiFileText },
];

export default function Dashboard() {
    const navigate = useNavigate();
    const { projectId } = useParams();
    const [categoryData, setCategoryData] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [recentDocs, setRecentDocs] = useState([]);

    useEffect(() => {
        fetchDashboardData();
    }, [projectId]);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            setError(null);

            // Fetch all active documents sorted by updated date
            const allDocs = await getPages({
                project_id: projectId,
                status: 'active',
                sort: 'updated_at',
                order: 'desc',
                limit: 100
            });

            // Group by category
            const grouped = {};
            allDocs.pages.forEach(doc => {
                const category = doc.category || 'uncategorized';
                if (!grouped[category]) {
                    grouped[category] = [];
                }
                grouped[category].push(doc);
            });

            setCategoryData(grouped);
            setRecentDocs(allDocs.pages.slice(0, 10)); // Top 10 recent
        } catch (err) {
            console.error('Failed to fetch dashboard data:', err);
            setError(err.message || 'Failed to load dashboard data');
        } finally {
            setLoading(false);
        }
    };

    const navigateToDoc = (category, slug) => {
        navigate(`/project/1/wiki/${category}/${slug}`);
    };

    // Loading state
    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Card className="p-8 text-center">
                    <FiLoader className="w-12 h-12 text-primary mx-auto mb-4 animate-spin" />
                    <p className="text-text-muted">Loading dashboard...</p>
                </Card>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <Card className="p-8 text-center">
                <FiAlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Failed to load dashboard</h3>
                <p className="text-text-muted mb-4">{error}</p>
                <button
                    onClick={fetchDashboardData}
                    className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primaryHover"
                >
                    Retry
                </button>
            </Card>
        );
    }

    return (
        <div className="space-y-4 lg:space-y-6">
            {/* Recent Documents Section */}
            {recentDocs.length > 0 && (
                <Card>
                    <div className="px-4 lg:px-6 py-3 lg:py-4 border-b border-border flex items-center justify-between bg-sidebar/50">
                        <div className="flex items-center gap-2">
                            <FiClock className="w-4 h-4 lg:w-5 lg:h-5 text-text-muted" />
                            <h2 className="text-base lg:text-lg font-bold text-text-main">Recently Updated</h2>
                        </div>
                        <span className="bg-white border border-border text-text-muted text-xs px-2 py-1 rounded-full font-medium">
                            {recentDocs.length}
                        </span>
                    </div>
                    <div className="p-3 lg:p-6 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-2 lg:gap-4">
                        {recentDocs.map((doc) => (
                            <div
                                key={doc.slug}
                                onClick={() => navigateToDoc(doc.category, doc.slug)}
                                className="group flex items-center gap-3 p-3 lg:p-4 rounded-lg border border-transparent hover:bg-surfaceHover hover:border-border transition-all cursor-pointer"
                            >
                                <div className="w-10 h-10 lg:w-12 lg:h-12 rounded-lg bg-surface border border-border flex items-center justify-center text-text-light group-hover:text-primary group-hover:border-primary/30 transition-colors flex-shrink-0">
                                    <FiFileText className="w-5 h-5 lg:w-6 lg:h-6" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <span className="text-sm lg:text-base font-medium text-text-main group-hover:text-primary transition-colors block truncate">
                                        {doc.title}
                                    </span>
                                    <span className="text-xs lg:text-sm text-text-muted">
                                        {formatRelativeTime(doc.updated_at)}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>
            )}

            {/* Category Sections */}
            {Object.keys(categoryData).length > 0 ? (
                Object.entries(categoryData).map(([category, docs]) => {
                    const categoryConfig = CATEGORIES.find(c => c.key === category);
                    const Icon = categoryConfig?.icon || FiFolder;
                    const label = categoryConfig?.label || category.charAt(0).toUpperCase() + category.slice(1);

                    return (
                        <Card key={category}>
                            <div className="px-4 lg:px-6 py-3 lg:py-4 border-b border-border flex items-center justify-between bg-sidebar/50">
                                <div className="flex items-center gap-2">
                                    <Icon className="w-4 h-4 lg:w-5 lg:h-5 text-text-muted" />
                                    <h2 className="text-base lg:text-lg font-bold text-text-main">{label}</h2>
                                </div>
                                <span className="bg-white border border-border text-text-muted text-xs px-2 py-1 rounded-full font-medium">
                                    {docs.length}
                                </span>
                            </div>
                            <div className="p-3 lg:p-6 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-2 lg:gap-4">
                                {docs.slice(0, 20).map((doc) => (
                                    <div
                                        key={doc.slug}
                                        onClick={() => navigateToDoc(category, doc.slug)}
                                        className="group flex items-center gap-3 p-3 lg:p-4 rounded-lg border border-transparent hover:bg-surfaceHover hover:border-border transition-all cursor-pointer"
                                    >
                                        <div className="w-10 h-10 lg:w-12 lg:h-12 rounded-lg bg-surface border border-border flex items-center justify-center text-text-light group-hover:text-primary group-hover:border-primary/30 transition-colors flex-shrink-0">
                                            <FiFileText className="w-5 h-5 lg:w-6 lg:h-6" />
                                        </div>
                                        <span className="text-sm lg:text-base font-medium text-text-main group-hover:text-primary transition-colors truncate flex-1 min-w-0">
                                            {doc.title}
                                        </span>
                                    </div>
                                ))}
                                {docs.length > 20 && (
                                    <div
                                        onClick={() => navigate(`/project/1/wiki/${category}`)}
                                        className="group flex items-center gap-3 p-3 rounded-lg border border-dashed border-border hover:bg-surfaceHover transition-all cursor-pointer"
                                    >
                                        <span className="text-sm font-medium text-text-muted group-hover:text-primary transition-colors">
                                            View all {docs.length} documents →
                                        </span>
                                    </div>
                                )}
                            </div>
                        </Card>
                    );
                })
            ) : (
                <Card className="p-8 lg:p-12 text-center">
                    <FiFileText className="w-16 h-16 text-text-muted mx-auto mb-4" />
                    <h3 className="text-xl font-semibold mb-2">No documents yet</h3>
                    <p className="text-text-muted mb-4">
                        Create your first document to get started
                    </p>
                </Card>
            )}
        </div>
    );
}
