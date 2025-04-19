import React from 'react';
import { WifiOff } from 'lucide-react';

interface OfflineBannerProps {
    isOffline: boolean;
}

const OfflineBanner: React.FC<OfflineBannerProps> = ({ isOffline }) => {
    if (!isOffline) return null;

    return (
        <div className="fixed bottom-4 right-4 bg-amber-50 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300 p-4 rounded-lg shadow-lg flex items-center gap-3 max-w-md z-50">
            <div className="bg-amber-200 dark:bg-amber-800 p-2 rounded-full">
                <WifiOff className="h-5 w-5 text-amber-700 dark:text-amber-300" />
            </div>
            <div>
                <h3 className="font-medium mb-1">Offline Mode</h3>
                <p className="text-sm">
                    You're currently offline. You can view saved analyses, but cannot
                    make new requests.
                </p>
            </div>
        </div>
    );
};

export default OfflineBanner;