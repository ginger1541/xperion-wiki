import React from 'react';
import { cn } from '../../lib/utils';
import { FiArrowRight } from 'react-icons/fi';

export const Button = React.forwardRef(({
    className,
    variant = 'primary',
    size = 'md',
    children,
    ...props
}, ref) => {
    const variants = {
        primary: "bg-primary text-white hover:bg-primaryHover border-transparent shadow-sm",
        secondary: "bg-surfaceHover text-text-main hover:bg-black/5 border-transparent",
        outline: "bg-transparent border-border text-text-main hover:bg-surfaceHover border",
        ghost: "bg-transparent hover:bg-surfaceHover text-text-main",
    };

    const sizes = {
        sm: "px-3 py-1.5 text-xs",
        md: "px-4 py-2 text-sm",
        lg: "px-6 py-3 text-base",
    };

    return (
        <button
            ref={ref}
            className={cn(
                "inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20 disabled:opacity-50 disabled:pointer-events-none",
                variants[variant],
                sizes[size],
                className
            )}
            {...props}
        >
            {children}
        </button>
    );
});

Button.displayName = "Button";
