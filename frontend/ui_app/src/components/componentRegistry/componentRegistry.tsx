import React from "react";
import pluginConfig from './pluginConfig.json'


interface PluginMetadata {
    type: string;
    name: string;
    version: string;
    category: string;
}

export interface PluginComponent {
    metadata: PluginMetadata;
    component: React.ComponentType<any>;
}

/**
 * ComponentRegistry loads all the components from the plugins and provides a way to get the components by category.
 * pluginConfig is a list of plugins in the format of: 
 * e.g., {"name": "plugin-xyz", "modulePath": "src/plugin-xyz", "metadataPath": "src/plugin-xyz/medadata.json"}}
 * Each plugin has a modulePath and metadataPath.
 * modulePath is the path to the plugin module. In plugin's package.json, specify the entry point of the plugin, e.g. index.js.
 * metadataPath is the path to the metadata.json file of the plugin, it contains a PluginMetadata object.
 */

class ComponentRegistry {
    private components: Map<string, PluginComponent> = new Map();

    async discoverComponents() {
        for (const { modulePath, metadataPath } of pluginConfig) {
            // console.log('Attempting to load:', modulePath, metadataPath);
            try {
                const module = await import(modulePath);
                const metadata = await import(metadataPath);
                this.components.set(metadata.name, {
                    metadata,
                    component: module.default
                });
            } catch (error) {
                console.error(`Failed to load plugin: ${modulePath}`, error);
            }
        }
    }

    getComponentsByCategory(category: string): PluginComponent[] {
        return Array.from(this.components.values())
            .filter(plugin => plugin.metadata.category === category);
    }
}

export default ComponentRegistry;