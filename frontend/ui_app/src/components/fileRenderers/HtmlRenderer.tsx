import React, { useEffect, useRef } from "react";
import { Asset, AssetObject } from "../../servers/asset_server";
import { AssetVersion } from "../../servers/asset_server/assetVersion";

interface TableProps {
    content: any;
    asset?: Asset;
}

const NAMESPACE_CLASS = 'html-renderer-scope';

export default function HtmlRenderer(props: TableProps) {
    const { content, asset } = props;
    const containerRef = useRef<HTMLDivElement>(null);

    /** Add Add namespace to each CSS selector*/
    const scopeStyles = (cssText: string, scopeClass: string): string => {
        const scopedCSS = cssText.replace(/([^{}]*)(\{[^{}]*\})/g, function (match, selector, rules) {
            const scopedSelector = selector.split(',').map((s: any) => `.${scopeClass} ${s.trim()}`).join(', ');
            return `${scopedSelector} ${rules}`;
        });
        return scopedCSS;
    };

    const updateLinks = (fragment: DocumentFragment) => {
        const links = fragment.querySelectorAll('a');
        const currentUrl = new URL(window.location.href);

        links.forEach(link => {
            const href = link.getAttribute('href');
            if (href) {
                try {
                    new URL(href);
                } catch (_) {
                    // For relative path, update the `object` parameter by patching objectId to the href
                    const params = new URLSearchParams(currentUrl.search);
                    const currentParams: { [key: string]: string } = {};
                    params.forEach((value, key) => {
                        currentParams[key] = value;
                    });

                    let newObjectValue = href;
                    const currentAssetVersion = params.get('version');
                    if (asset?.versions) {
                        const version: AssetVersion | undefined = asset.versions.find((version: AssetVersion) => version.number === currentAssetVersion);
                        if (version && version.objects) {
                            const objects: AssetObject[] = version.objects;
                            const foundObject: AssetObject | undefined = objects.find((object: AssetObject) => object.path() === href);
                            if (foundObject) {
                                newObjectValue = foundObject.id;
                            }
                        }
                    }
                    currentParams['object'] = newObjectValue;

                    // Manually reconstruct the URL to avoid encoding issues
                    const newSearchParams = Object.entries(currentParams)
                        .map(([key, value]) => `${key}=${value}`)
                        .join('&');

                    const newUrl = `${currentUrl.origin}${currentUrl.pathname}?${newSearchParams}`;
                    link.setAttribute('href', newUrl);
                }
            }
        });
    };

    useEffect(() => {
        const fragment = document.createRange().createContextualFragment(content);

        const styleTags = fragment.querySelectorAll('style');
        const scripts = fragment.querySelectorAll('script');

        const scopedStyle = document.createElement('style');

        // Extract and transfer styles to the namespaced classNames
        styleTags.forEach(style => {
            const scopedCSS = scopeStyles(style.textContent || '', NAMESPACE_CLASS);
            scopedStyle.appendChild(document.createTextNode(scopedCSS));

            style.remove();
        });

        updateLinks(fragment);

        if (containerRef.current) {
            containerRef.current.innerHTML = '';
            containerRef.current.appendChild(fragment.cloneNode(true));
            containerRef.current.appendChild(scopedStyle);
        }

        scripts.forEach((script: any) => {
            const newScript: any = document.createElement('script');
            if (script.src) {
                newScript.src = script.src;
            } else {
                newScript.text = script.textContent || '';
            }
            document.body.appendChild(newScript);

            // Remove the script after execution to prevent duplication
            newScript.onload = () => newScript.remove();
        });
    }, [content]);

    return (
        <div
            ref={containerRef}
            className={NAMESPACE_CLASS}
        ></div>
    );
};