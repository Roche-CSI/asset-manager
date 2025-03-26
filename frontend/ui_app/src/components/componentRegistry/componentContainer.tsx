import React, { useEffect, useState } from 'react';
import ComponentRegistry, { PluginComponent } from './componentRegistry';
interface ComponentContainerProps {
    category: string;
    componentProps?: Record<string, any>;
}
const registry = new ComponentRegistry();
const ComponentContainer: React.FC<ComponentContainerProps> = ({
    category,
    componentProps = {}
}) => {
    const [components, setComponents] = useState<PluginComponent[]>([]);
    useEffect(() => {
        const loadComponents = async () => {
            await registry.discoverComponents();
            const discovered = registry.getComponentsByCategory(category);
            setComponents(discovered);
        };
        loadComponents();
    }, [category]);
    return (
        <div className="component-container">
            {components.map(({ component: Component, metadata }) => (
                <div key={metadata.name}>
                    <Component {...componentProps} />
                </div>
            ))}
        </div>
    );
};

export default ComponentContainer;