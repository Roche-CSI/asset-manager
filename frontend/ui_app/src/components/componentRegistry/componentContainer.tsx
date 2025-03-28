import React, { Suspense, LazyExoticComponent } from 'react';
import { pluginComponents } from './pluginComponents';

interface ComponentContainerProps {
    category: string;
    componentProps?: Record<string, any>;
}

const ComponentContainer: React.FC<ComponentContainerProps> = ({
    category,
    componentProps = {}
}) => {
    const LazyPluginComponent: LazyExoticComponent<any> = pluginComponents[category]

    return (
        <Suspense fallback={<div>Loading...</div>}>
            <div className="component-container">
                <LazyPluginComponent {...componentProps} />
            </div>
        </Suspense>
    );
};

export default ComponentContainer;