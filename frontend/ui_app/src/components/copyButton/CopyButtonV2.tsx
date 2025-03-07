import React, { useState } from "react";
import { Check, Copy } from 'lucide-react';


export default function CopyButtonV2({ textToCopy, iconClassName }: { textToCopy: string, iconClassName?: string }) {
    const [copied, setCopied] = useState(false);

    const copyToClipboard = async (text: string) => {
        try {
            await navigator.clipboard.writeText(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
    };

    const iconClass = iconClassName ? iconClassName : "size-5 text-neutral-400";

    return (
        <button
            onClick={() => copyToClipboard(textToCopy)}
            className={'rounded-full transition-all p-0.5'}
            title="Copy to clipboard"
        >
            {copied ? (
                <Check className={iconClass} />
            ) : (
                <Copy className={`${iconClass} hover:text-neutral`} />
            )}
        </button>

    )
}