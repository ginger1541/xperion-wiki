import React from 'react';
import { cn } from '../../lib/utils';

export const Card = ({ className, children, ...props }) => {
    return (
        <div
            className={cn(
                "bg-white border border-border rounded-lg shadow-sm overflow-hidden",
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
};
