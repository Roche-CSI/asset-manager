import React from 'react';
import {
    BaseEdge,
    getBezierPath,
    EdgeLabelRenderer,
    Position,
    getMarkerEnd
} from 'reactflow';
import styles from "./custom_edge.module.scss";

/**
 * custom edge rendering
 * ref:
 * 1. https://reactflow.dev/docs/examples/edges/edge-with-button/
 * 2. https://reactflow.dev/docs/examples/edges/custom-edge/
 */

interface EdgeProps {
    id: string;
    sourceX: number;
    sourceY: number;
    targetX: number;
    targetY: number;
    sourcePosition: Position;
    targetPosition: Position;
    style: object;
    data: any;
    arrowHeadType?: any;
    label?: string;
    labelBgStyle?: any;
    sourceHandle?: string;
    targetHandle?: string;
}

export default function CustomEdge(props: any) {

    const [edgePath, labelX, labelY] = getBezierPath({
        sourceX: props.sourceX,
        sourceY: props.sourceY,
        sourcePosition: props.sourcePosition,
        targetX: props.targetX,
        targetY: props.targetY,
        targetPosition: props.targetPosition,
    });

    const markerEnd = getMarkerEnd(props.arrowHeadType, props.data.markerEndId);

    console.log("edge props:", props);

    const textSize: any = measureText(props.label as string, 14)

    let xPosition: any = props.data.isInbound ? props.sourceX + 5 : props.targetX - textSize.width - 12;
    let yPosition: any = props.data.isInbound ? props.sourceY - textSize.height / 2 : props.targetY - textSize.height / 2
    if (props.data.isBidirectional) {
        xPosition = props.targetX - textSize.width / 2
        yPosition = props.targetY - 40
    }

    let edgeStyle: any = {
        position: 'absolute',
        transform: `translate(${xPosition}px,${yPosition}px)`,
        width: textSize.width, height: textSize.height
    }

    return (
        <>
            <BaseEdge path={edgePath}
                markerEnd={markerEnd} style={props.style} />
            <EdgeLabelRenderer>
                <div className={`${styles.edgeLabel} ${props.data.isInbound ? '' : styles.outbound}`}
                    style={edgeStyle}
                >
                    {props.label}
                </div>
            </EdgeLabelRenderer>
        </>
    );

    /**
     * calculates the rendering size of text
     * @param pText
     * @param pFontSize
     * @param pStyle
     * ref: https://stackoverflow.com/questions/118241/calculate-text-width-with-javascript
     */
    function measureText(pText: string, pFontSize: number, pStyle?: string) {
        let lDiv: any = document.createElement('div');
        document.body.appendChild(lDiv);
        if (pStyle != null) {
            lDiv.style = pStyle;
        }
        lDiv.style.fontSize = "" + pFontSize + "px";
        lDiv.style.position = "absolute";
        lDiv.style.left = -1000;
        lDiv.style.top = -1000;

        lDiv.textContent = pText;

        let lResult = {
            width: lDiv.clientWidth,
            height: lDiv.clientHeight
        };

        document.body.removeChild(lDiv);
        lDiv = null;

        return lResult;
    }
}