import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MarkdownViewer } from '../components/ui/MarkdownViewer';
import { MarkdownEditor } from '../components/ui/MarkdownEditor';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { FiEdit2, FiSave, FiCornerUpLeft, FiTrash2, FiAlertCircle, FiLoader } from 'react-icons/fi';
import { getPage, createPage, updatePage, deletePage } from '../services/api';

// Helper function to generate slug from title
const generateSlug = (title) => {
    return title
        .toLowerCase()
        .replace(/[^a-z0-9가-힣\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .trim();
};

export default function WikiDetail() {
    const { projectId, docSlug, category } = useParams();
    const navigate = useNavigate();

    const [isEditing, setIsEditing] = useState(false);
    const [content, setContent] = useState('');
    const [title, setTitle] = useState('');
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);
    const [pageData, setPageData] = useState(null);

    const isNewDocument = docSlug === 'new';

    // Fetch document on mount
    useEffect(() => {
        if (isNewDocument) {
            // New document mode
            setIsEditing(true);
            setContent("# 새로운 문서\n\n여기에 내용을 입력하세요.");
            setTitle("Untitled");
            setLoading(false);
        } else {
            fetchDocument();
        }
    }, [docSlug]);

    const fetchDocument = async () => {
        try {
            setLoading(true);
            setError(null);

            const data = await getPage(docSlug);
            setPageData(data);
            setTitle(data.title);
            setContent(data.content);
        } catch (err) {
            console.error('Failed to fetch document:', err);
            setError(err.response?.data?.detail?.message || err.message || 'Failed to load document');
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        if (!title.trim()) {
            alert('Please enter a title');
            return;
        }

        try {
            setSaving(true);
            setError(null);

            if (isNewDocument) {
                // Create new document
                const slug = `${category}/${generateSlug(title)}`;
                const newPage = await createPage({
                    slug,
                    title: title.trim(),
                    category: category || 'general',
                    content,
                    author: 'User', // TODO: Get from auth context
                    status: 'active',
                    summary: '',
                    tags: [],
                    project_id: projectId
                });

                setIsEditing(false);
                // Navigate to the newly created document
                navigate(`../${newPage.slug}`, { replace: true });
            } else {
                // Update existing document
                const updatedPage = await updatePage(docSlug, {
                    title: title.trim(),
                    content,
                    status: pageData.status,
                    summary: pageData.summary || '',
                    tags: pageData.tags || [],
                    project_id: projectId,
                    expected_sha: pageData.github_sha,
                    force: false
                });

                setPageData(updatedPage);
                setIsEditing(false);
            }
        } catch (err) {
            console.error('Failed to save document:', err);
            const errorMessage = err.response?.data?.detail?.message || err.message || 'Failed to save document';
            setError(errorMessage);
            alert(`Error: ${errorMessage}`);
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async () => {
        if (!confirm('Are you sure you want to delete this document? This will move it to archived folder.')) {
            return;
        }

        try {
            setSaving(true);
            await deletePage(docSlug, false); // Soft delete
            navigate(-1);
        } catch (err) {
            console.error('Failed to delete document:', err);
            alert(`Error: ${err.response?.data?.detail?.message || err.message || 'Failed to delete document'}`);
        } finally {
            setSaving(false);
        }
    };

    const handleCancel = () => {
        if (isNewDocument) {
            navigate(-1);
        } else {
            setTitle(pageData.title);
            setContent(pageData.content);
            setIsEditing(false);
        }
    };

    // Loading state
    if (loading) {
        return (
            <div className="max-w-5xl mx-auto h-[calc(100vh-8rem)] flex items-center justify-center">
                <Card className="p-8 text-center">
                    <FiLoader className="w-12 h-12 text-primary mx-auto mb-4 animate-spin" />
                    <p className="text-text-muted">Loading document...</p>
                </Card>
            </div>
        );
    }

    // Error state
    if (error && !isNewDocument) {
        return (
            <div className="max-w-5xl mx-auto h-[calc(100vh-8rem)] flex items-center justify-center">
                <Card className="p-8 text-center max-w-md">
                    <FiAlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold mb-2">Failed to load document</h3>
                    <p className="text-text-muted mb-4">{error}</p>
                    <div className="flex gap-2 justify-center">
                        <Button variant="ghost" onClick={() => navigate(-1)}>Go Back</Button>
                        <Button onClick={fetchDocument}>Retry</Button>
                    </div>
                </Card>
            </div>
        );
    }

    return (
        <div className="max-w-5xl mx-auto min-h-[calc(100vh-8rem)] flex flex-col">
            {/* Toolbar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4 lg:mb-6 pb-4 border-b border-border">
                <div className="flex items-center gap-2 sm:gap-4 min-w-0">
                    <Button variant="ghost" size="icon" onClick={() => navigate(-1)} className="shrink-0">
                        <FiCornerUpLeft className="w-5 h-5" />
                    </Button>
                    {isEditing ? (
                        <input
                            type="text"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            className="text-xl sm:text-2xl lg:text-3xl font-bold bg-transparent border-none outline-none placeholder:text-text-muted/50 min-w-0 flex-1"
                            placeholder="Document Title"
                            disabled={saving}
                        />
                    ) : (
                        <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold truncate">{title}</h1>
                    )}
                </div>

                <div className="flex gap-2 shrink-0">
                    {isEditing ? (
                        <>
                            <Button
                                variant="ghost"
                                onClick={handleCancel}
                                disabled={saving}
                            >
                                Cancel
                            </Button>
                            <Button
                                onClick={handleSave}
                                disabled={saving}
                            >
                                {saving ? (
                                    <>
                                        <FiLoader className="mr-2 animate-spin" /> Saving...
                                    </>
                                ) : (
                                    <>
                                        <FiSave className="sm:mr-2" />
                                        <span className="hidden sm:inline">Save Changes</span>
                                    </>
                                )}
                            </Button>
                        </>
                    ) : (
                        <>
                            <Button
                                variant="ghost"
                                className="text-red-500 hover:text-red-600 hover:bg-red-50"
                                onClick={handleDelete}
                                disabled={saving}
                            >
                                <FiTrash2 className="w-4 h-4" />
                            </Button>
                            <Button
                                variant="outline"
                                onClick={() => setIsEditing(true)}
                                disabled={saving}
                            >
                                <FiEdit2 className="sm:mr-2" />
                                <span className="hidden sm:inline">Edit</span>
                            </Button>
                        </>
                    )}
                </div>
            </div>

            {/* Content Area */}
            <div className="flex-1 min-h-0">
                {isEditing ? (
                    <MarkdownEditor
                        content={content}
                        onChange={setContent}
                        disabled={saving}
                    />
                ) : (
                    <div className="bg-white rounded-lg border border-border p-8 min-h-full shadow-sm overflow-y-auto">
                        <MarkdownViewer content={content} />
                    </div>
                )}
            </div>
        </div>
    );
}
