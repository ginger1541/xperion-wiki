import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card'; // Assuming path relative to pages folder vs components folder context
import { FiFileText, FiPlus, FiSearch, FiAlertCircle } from 'react-icons/fi';
import { Button } from '../components/ui/Button';
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

export default function WikiList() {
    const { projectId, category } = useParams();
    const navigate = useNavigate();

    const [docs, setDocs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        fetchDocuments();
    }, [projectId, category]);

    const fetchDocuments = async () => {
        try {
            setLoading(true);
            setError(null);

            // Fetch pages with project and category filter
            const result = await getPages({
                project_id: projectId,
                category: category ? `${category}` : undefined,
                status: 'active',
                sort: 'updated_at',
                order: 'desc',
                limit: 100
            });

            setDocs(result.pages || []);
        } catch (err) {
            console.error('Failed to fetch documents:', err);
            setError(err.message || 'Failed to load documents');
        } finally {
            setLoading(false);
        }
    };

    // Filter documents based on search query
    const filteredDocs = searchQuery
        ? docs.filter(doc =>
            doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            doc.slug.toLowerCase().includes(searchQuery.toLowerCase())
        )
        : docs;

    const categoryTitle = category ? category.charAt(0).toUpperCase() + category.slice(1) : 'All Documents';

    // Loading state
    if (loading) {
        return (
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-bold tracking-tight">{categoryTitle}</h2>
                        <p className="text-text-muted text-sm mt-1">Loading...</p>
                    </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {[...Array(8)].map((_, i) => (
                        <Card key={i} className="p-4 animate-pulse">
                            <div className="w-10 h-10 rounded-lg bg-surfaceHover mb-3"></div>
                            <div className="h-6 bg-surfaceHover rounded mb-2"></div>
                            <div className="h-4 bg-surfaceHover rounded w-2/3"></div>
                        </Card>
                    ))}
                </div>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-bold tracking-tight">{categoryTitle}</h2>
                    </div>
                </div>
                <Card className="p-8 text-center">
                    <FiAlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold mb-2">Failed to load documents</h3>
                    <p className="text-text-muted mb-4">{error}</p>
                    <Button onClick={fetchDocuments}>Retry</Button>
                </Card>
            </div>
        );
    }

    return (
        <div className="space-y-4 lg:space-y-6">
            {/* Action Bar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h2 className="text-xl lg:text-2xl font-bold tracking-tight">{categoryTitle}</h2>
                    <p className="text-text-muted text-sm mt-1">{filteredDocs.length} Documents found</p>
                </div>
                <div className="flex gap-2 sm:gap-3">
                    <div className="relative flex-1 sm:flex-none">
                        <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                        <input
                            type="text"
                            placeholder="Filter..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full sm:w-40 lg:w-auto pl-9 pr-4 py-2 border border-border rounded-md text-sm focus:ring-2 focus:ring-primary/20 outline-none"
                        />
                    </div>
                    <Button onClick={() => navigate('new')} className="whitespace-nowrap">
                        <FiPlus className="sm:mr-2" />
                        <span className="hidden sm:inline">New Document</span>
                    </Button>
                </div>
            </div>

            {/* Empty state */}
            {filteredDocs.length === 0 && (
                <Card className="p-8 text-center">
                    <FiFileText className="w-12 h-12 text-text-muted mx-auto mb-4" />
                    <h3 className="text-lg font-semibold mb-2">No documents found</h3>
                    <p className="text-text-muted mb-4">
                        {searchQuery ? 'Try a different search term' : 'Create your first document to get started'}
                    </p>
                    {!searchQuery && (
                        <Button onClick={() => navigate('new')}>
                            <FiPlus className="mr-2" /> New Document
                        </Button>
                    )}
                </Card>
            )}

            {/* Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {filteredDocs.map((doc) => (
                    <Card
                        key={doc.slug}
                        className="group cursor-pointer hover:border-primary/50 transition-all p-4"
                        onClick={() => navigate(doc.slug)}
                    >
                        <div className="flex items-start justify-between mb-3">
                            <div className="w-10 h-10 rounded-lg bg-surfaceHover flex items-center justify-center text-text-muted group-hover:text-primary group-hover:bg-primary/5 transition-colors">
                                <FiFileText className="w-5 h-5" />
                            </div>
                            <span className="text-xs text-text-muted bg-surfaceHover px-2 py-1 rounded-full">{CategoryLabel(doc.category)}</span>
                        </div>

                        <h3 className="font-bold text-lg mb-1 group-hover:text-primary transition-colors">{doc.title}</h3>
                        <p className="text-xs text-text-muted">
                            Last edited {formatRelativeTime(doc.updated_at)} by {doc.author}
                        </p>
                    </Card>
                ))}
            </div>
        </div>
    );
}

function CategoryLabel(cat) {
    if (!cat) return "Doc";
    return cat.substring(0, 3).toUpperCase();
}
