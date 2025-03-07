import React, {useEffect, useRef, useState} from 'react';
import ReactFlow, {Node, Edge, ReactFlowProvider} from 'reactflow';
import styles from "./grapher.module.scss";
import {CustomNodeComponent, CustomEdge, MarkerDefinition} from "./flowGraph";
import {markerEndColorId, markerEndColor} from "./flowGraph/edge/edgeData"

// const onLoad = (reactFlowInstance: any) => reactFlowInstance.fitView();
const onNodeMouseMove = (event: any, node: any) => {};
const onNodeContextMenu = (event: any, node: any) => {
   event.preventDefault();
   // console.log('context menu:', node);
};

interface ReactFlowProps {
    edges: any[],
    nodes: any[],
    onClick?: Function
}

const nodeTypes = {
    special: CustomNodeComponent,
};
const edgeTypes = {
    special: CustomEdge,
}

const HorizontalFlow = (props: ReactFlowProps) => {
    const [nodes, setNodes] = useState<Node[] | undefined>()
    const [edges, setEdges] = useState<Edge[] | undefined>()
    // react flow caching bug
    // https://github.com/wbkd/react-flow/issues/693
    const instanceRef = useRef(null);
    const onLoad = (reactFlowInstance: any) => {
        console.log("onload called: ", reactFlowInstance);
        if (reactFlowInstance) {
            instanceRef.current = reactFlowInstance;
        }
        (instanceRef.current as any).fitView();
        // reactFlowInstance.fitView();
    }
    const onNodeMouseEnter = (event: any, node: any) => {
        console.log("mouse enter:", node)
    };

    const onNodeMouseLeave = (event: any, node: any) => {
        console.log("mouse leave:", node)
    };

    useEffect(() => {
        setNodes(props.nodes);
        setEdges(props.edges);
        if (instanceRef.current) {
            (instanceRef.current as any).fitView();
        }
    }, [props.edges, props.nodes]);

    const onElementClick = (event: any, node: any) => {
        console.log('clicked:', node);
        event.preventDefault();
        // props.onClick && props.onClick(node.data.label);
    }
    console.log("nodes:", nodes, "edges:", edges);

    const defaultViewport = { x: 0, y: 0, zoom: 0.8 };

    return (
        <div className={styles.graphContainer}>
            <ReactFlowProvider>
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onLoad={onLoad}
                    selectNodesOnDrag={false}
                    // onNodeMouseEnter={onNodeMouseEnter}
                    // onNodeMouseMove={onNodeMouseMove}
                    // onNodeMouseLeave={onNodeMouseLeave}
                    // onNodeContextMenu={onNodeContextMenu}
                    defaultViewport={defaultViewport}
                    onNodeClick={onElementClick}
                    onEdgeClick={onElementClick}
                    nodeTypes={nodeTypes}
                    edgeTypes={edgeTypes}
                >
                <MarkerDefinition id={markerEndColorId.INBOUND} color={markerEndColor.INBOUND} />
                <MarkerDefinition id={markerEndColorId.OUTBOUND} color={markerEndColor.OUTBOUND} />
                <MarkerDefinition id={markerEndColorId.BIDIRECTIONAL} color={markerEndColor.BIDIRECTIONAL} />
                </ReactFlow>
            </ReactFlowProvider>
        </div>
    );
};

export default HorizontalFlow;