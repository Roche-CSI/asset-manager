import { lazy, LazyExoticComponent } from 'react';

/**
 * This file is used to register plugin components that can be dynamically loaded.
 * Each entry in the `pluginComponents` object should correspond to a component
 * exported from a plugin. The key is the category name used to reference the component,
 * and the value is a lazy-loaded component.
 * e.g. "my-plugin": lazy(() => import("path/to/my-plugin"))
 */
export const pluginComponents: Record<string, LazyExoticComponent<any>> = {

};

export default pluginComponents;