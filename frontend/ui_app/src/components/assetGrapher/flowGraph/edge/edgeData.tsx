/***
 * EdgeData class for ReactFlow
 */
export enum markerEndColorId {
    INBOUND = "edge-marker-green",
    OUTBOUND = "edge-marker-orange",
    BIDIRECTIONAL = "edge-marker-purple",
}

// corresponds to node colors in graph.module.scss
export enum markerEndColor {
    // INBOUND = "#7bdcb5",
    // OUTBOUND = "#fcb900",
    // BIDIRECTIONAL = "#d37fde",
    INBOUND = "#26282c",
    OUTBOUND = "#26282c",
    BIDIRECTIONAL = "#26282c",
}

/**
 * ReactFlow EdgeData
 */
 interface EdgeDataInterface {
    src_node_id: string;
    dst_node_id: string;
    isInbound: boolean;
    isBidirectional?: boolean;
    label?: string;
    sourceHandle?: string; // id for source handle in customNode
    targetHandle?: string;
}

export default class EdgeData {
    id: string;
    source: string; // source node id
    target: string; // target node id
    type: string = "smoothstep";
    animated: boolean = false; // set to true for animating edge
    label?: string;
    markerEndId?: string;
    arrowHeadType: string;
    labelBgStyle: object;
    className: string;
    labelBgPadding: number[];
    labelBgBorderRadius: number;
    data: Object;
    style: Object;
    sourceHandle?: string;
    targetHandle?: string;

    constructor({
            src_node_id,
            dst_node_id,
            isInbound,
            isBidirectional,
            label,
            sourceHandle,
            targetHandle
        }: EdgeDataInterface) {
        this.id = `${src_node_id}-${dst_node_id}`;
        this.source = src_node_id.toString();
        this.target = dst_node_id.toString();
        this.label = label;
        this.arrowHeadType = "arrowclosed"; //arrow
        this.labelBgStyle = { fill: '#FFCC00', color: '#fff', fillOpacity: 0.7 };
        this.className = 'normal-edge';
        this.labelBgPadding = [8, 4];
        this.labelBgBorderRadius = 4;
        this.type = "special";
        this.sourceHandle = sourceHandle;
        this.targetHandle = targetHandle;
        this.style = isInbound? { stroke: markerEndColor.INBOUND }
                        :
                        (isBidirectional?  { stroke: markerEndColor.BIDIRECTIONAL }
                        : { stroke: markerEndColor.OUTBOUND });
        this.data = {isInbound: isInbound,
                    isBidirectional: isBidirectional,
                    markerEndId: isInbound? markerEndColorId.INBOUND:
                    (isBidirectional? markerEndColorId.BIDIRECTIONAL: markerEndColorId.OUTBOUND)}
    }
}
