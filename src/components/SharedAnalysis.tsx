'use client'

import React, { useState, useEffect } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import { Button } from './ui/button';
import { ArrowLeft, Brain, ExternalLink, Share2 } from 'lucide-react';

// Define the shared item interface
interface ShareItem {
    id: string;
    prompt: string;
    output: string;
    models: string[];
    ultraModel: string;
    timestamp: string;
    usingDocuments?: boolean;
    documents?: { id: string, name: string }[];
    shareId: string;
    shareUrl: string;
    createdAt: string;
}

export default function SharedAnalysis() {
    const { shareId } = useParams<{ shareId: string }>();
    const [sharedItem, setSharedItem] = useState<ShareItem | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Load the shared item from localStorage
    useEffect(() => {
        const loadSharedItem = () => {
            try {
                setLoading(true);
                setError(null);

                // Try to find the shared item in localStorage
                const savedSharedItems = localStorage.getItem('ultraAiSharedItems');
                if (savedSharedItems) {
                    const parsedItems: ShareItem[] = JSON.parse(savedSharedItems);
                    const item = parsedItems.find(item => item.shareId === shareId);

                    if (item) {
                        setSharedItem(item);
                    } else {
                        setError('Shared analysis not found. It may have been deleted or the link is invalid.');
                    }
                } else {
                    setError('No shared analyses found. The content may have been deleted.');
                }
            } catch (err) {
                console.error('Failed to load shared item:', err);
                setError('An error occurred while loading the shared analysis.');
            } finally {
                setLoading(false);
            }
        };

        if (shareId) {
            loadSharedItem();
        } else {
            setError('Invalid share link. Please check the URL and try again.');
            setLoading(false);
        }
    }, [shareId]);

    // Format date for display
    const formatDate = (dateString: string) => {
        try {
            return new Date(dateString).toLocaleString();
        } catch (e) {
            return 'Unknown date';
        }
    };

    // Get model display name
    const getModelDisplayName = (modelId: string) => {
        const modelNames: { [key: string]: string } = {
            'gpt4o': 'GPT-4o',
            'gpt4turbo': 'GPT-4 Turbo',
            'gpto3mini': 'GPT-3.5',
            'gpto1': 'GPT-o1',
            'claude37': 'Claude 3.5',
            'claude3opus': 'Claude 3 Opus',
            'gemini15': 'Gemini 1.5',
            'llama3': 'Llama 3'
        };

        return modelNames[modelId] || modelId;
    };

    // Render loading state
    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-4 md:p-6 flex items-center justify-center">
                <div className="max-w-4xl w-full mx-auto bg-black border-4 border-cyan-700 rounded-lg shadow-2xl shadow-cyan-500/20 p-8 text-center">
                    <div className="relative h-24 w-24 mx-auto mb-6">
                        <div className="absolute inset-0 opacity-30 rounded-full border-4 border-cyan-500"></div>
                        <div className="absolute inset-0 rounded-full border-t-4 border-cyan-300 animate-spin"></div>
                        <div className="absolute inset-2 rounded-full border-b-4 border-pink-500 animate-spin animate-delay-500"></div>
                        <div className="absolute inset-0 flex items-center justify-center">
                            <Brain className="h-12 w-12 text-cyan-400 opacity-80" />
                        </div>
                    </div>
                    <h2 className="text-xl font-semibold text-cyan-300 mb-2">Loading Shared Analysis</h2>
                    <p className="text-gray-400">Please wait while we retrieve the content...</p>
                </div>
            </div>
        );
    }

    // Render error state
    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-4 md:p-6">
                <div className="max-w-4xl mx-auto bg-black border-4 border-cyan-700 rounded-lg shadow-2xl shadow-cyan-500/20 p-8">
                    <div className="text-center mb-6">
                        <h1 className="text-3xl font-bold text-red-400 mb-4">Analysis Not Found</h1>
                        <p className="text-gray-300 mb-6">{error}</p>
                        <RouterLink to="/" className="inline-block">
                            <Button className="bg-cyan-700 hover:bg-cyan-600">
                                <ArrowLeft className="h-4 w-4 mr-2" />
                                Return to Ultra AI
                            </Button>
                        </RouterLink>
                    </div>
                </div>
            </div>
        );
    }

    // Render shared analysis
    return (
        <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white p-4 md:p-6">
            <div className="max-w-4xl mx-auto bg-black border-4 border-cyan-700 rounded-lg shadow-2xl shadow-cyan-500/20 p-6 md:p-8">
                {/* Header */}
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-500 via-cyan-500 to-green-500">
                            UltrAI
                        </h1>
                        <p className="text-gray-400 mt-1">Shared Analysis</p>
                    </div>
                    <RouterLink to="/" className="inline-block">
                        <Button variant="outline" className="border-cyan-700 text-cyan-400 hover:bg-cyan-950">
                            <ArrowLeft className="h-4 w-4 mr-2" />
                            Try UltrAI
                        </Button>
                    </RouterLink>
                </div>

                {/* Shared by banner */}
                <div className="mb-6 bg-purple-900/20 border border-purple-800 rounded-lg p-3 flex items-center">
                    <Share2 className="h-5 w-5 text-purple-400 mr-2" />
                    <span className="text-purple-300">
                        Shared on {formatDate(sharedItem?.createdAt || '')}
                    </span>
                </div>

                {/* Prompt */}
                <div className="mb-6">
                    <h2 className="text-xl font-bold text-cyan-400 mb-2">Prompt</h2>
                    <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                        <p className="text-gray-200 whitespace-pre-wrap">{sharedItem?.prompt}</p>
                    </div>
                </div>

                {/* Models used */}
                <div className="mb-6">
                    <h2 className="text-lg font-semibold text-cyan-400 mb-2">AI Models Used</h2>
                    <div className="flex flex-wrap gap-2">
                        {sharedItem?.models.map((model, index) => (
                            <div
                                key={index}
                                className="bg-gray-800 border border-gray-700 rounded-full px-3 py-1 text-sm"
                            >
                                {getModelDisplayName(model)}
                                {model === sharedItem.ultraModel && (
                                    <span className="ml-1 text-amber-400">(Synthesizer)</span>
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Output */}
                <div className="border-2 border-cyan-700 rounded-lg p-6 bg-black/50 relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-900/20 to-purple-900/20"></div>
                    <div className="relative z-10">
                        <h2 className="text-xl font-bold text-cyan-400 mb-4">Analysis Results</h2>
                        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
                            <div className="prose prose-invert max-w-none">
                                <div className="whitespace-pre-line text-lg leading-relaxed text-cyan-50">
                                    {sharedItem?.output}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="mt-8 text-center">
                    <p className="text-gray-500 text-sm">
                        This is a shared analysis from UltrAI - Multiple AI models working together to provide better results.
                    </p>
                    <RouterLink to="/" className="inline-block mt-2">
                        <Button variant="link" className="text-cyan-400 hover:text-cyan-300">
                            <ExternalLink className="h-4 w-4 mr-1" />
                            Create your own analysis with UltrAI
                        </Button>
                    </RouterLink>
                </div>
            </div>
        </div>
    );
}