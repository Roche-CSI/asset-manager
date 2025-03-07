import React from "react";
import { Handle, Position } from 'reactflow';
import { HoverPopOver } from "../../popOvers";
import { Link, useParams } from "react-router-dom";
import { AssetRef } from "../../../servers/asset_server";
import { convertToCurrentTimeZone } from "../../../utils";
import NodeData from "./nodeData";

const optionsCursorTrueWithMargin = {
    followCursor: true,
    shiftX: 20,
    shiftY: 0
};

const PLACEMENT: any = {
    INBOUND: 'left-start',
    OUTBOUND: 'right-start',
    ROOT: 'top'
}

const refFields = (ref: AssetRef | null) => {
    if (!ref) return null;
    return (
        <table className='w-full text-xs'>
            <tbody>
                <tr>
                    <td>From:</td>
                    <td>{ref.src_version.name}</td>
                </tr>
                <tr>
                    <td>To:</td>
                    <td>{ref.dst_version.name}</td>
                </tr>
                <tr>
                    <td>Label</td>
                    <td>{ref.label}</td>
                </tr>
                <tr>
                    <td>Creator:</td>
                    <td>{ref.created_by}</td>
                </tr>
                <tr>
                    <td>Created:</td>
                    <td>{convertToCurrentTimeZone(ref.created_at, "date")}</td>
                </tr>
            </tbody>
        </table>
    )
}

const childrenFields = (children: NodeData[] | null, project_id: any) => {
    if (!children) return;
    // sort children
    children.sort((a: any, b: any) => a.id - b.id)
    return (
        <div className="max-h-48 overflow-y-auto">
            <table>
                <tbody>
                    {children.map((child: any, index: number) => {
                        const [className, seq_id, version] = child.data.label.split("/");
                        return (
                            <tr key={`${child.data.id}, ${index}`}>
                                <td>
                                    <Link to={`/asset/${project_id}/${className}/${seq_id}/files?version=${version}`}
                                        className='text-primary'>
                                        {child.data.label}
                                    </Link>
                                    {children.length === 1 &&
                                        refFields(child.data.ref)
                                    }
                                    {/* <HoverPopOver label={
                                    <Link to={`/asset/${className}/${seq_id}/files?version=${version}`}>
                                        {child.data.label}
                                    </Link>}>
                                    {refFields(child.data.ref)}
                                </HoverPopOver> */}
                                </td>
                            </tr>
                        )
                    }
                    )}
                </tbody>
            </table>
        </div>
    )
}

const CustomNodeComponent = (node: any) => {
    const { project_id } = useParams();
    const [className, seq_id, version] = node.data.label.split("/");
    const children = node.data.children
    let classLabel: string = node.data.label; //default for root node
    console.log("classLabel:", classLabel);
    if (children.length > 0) { //for in/out node
        const className = children[0].data.label.split("/")[0];
        classLabel = children.length > 1 ? `${className}/*` : children[0].data.label;
    }

    return (
        <div className="nowheel bg bg-red-800">
            {children.length === 0 ?
                <div>
                    <Handle type="target" id="inbound-left" position={Position.Left} />
                    <div>
                        <HoverPopOver label={
                            <div className='min-w-[150px] p-2.5 box-border'>
                                <Link to={`/asset/${project_id}/${className}/${seq_id}/files?version=${version}`}>
                                    {classLabel}
                                </Link>
                            </div>}
                            placement={PLACEMENT.ROOT}>
                            {refFields(node.data.ref)}
                        </HoverPopOver>
                    </div>
                    <Handle
                        type="source"
                        position={Position.Right}
                        id="outbound-right"
                    />
                    <Handle type="source" id="source-bottom" position={Position.Bottom} />
                    <Handle type="target" id="target-bottom" position={Position.Bottom} />
                </div>
                :
                <div>
                    {node.data.isBidirectional &&
                        <Handle type="target" id="target-top" position={Position.Top} />}
                    {node.data.isBidirectional &&
                        <Handle type="source" id="source-top" position={Position.Top} />}
                    {!node.data.isInbound &&
                        <Handle type="target" id="outbound-left" position={Position.Left} />}
                    <div>
                        <HoverPopOver label={
                            <div className='min-w-[150px] p-2.5 box-border'>{classLabel}</div>
                        }
                            placement={node.data.isInbound ? PLACEMENT.INBOUND : PLACEMENT.OUTBOUND}>
                            {childrenFields(children, project_id)}
                        </HoverPopOver>
                    </div>
                    {node.data.isInbound && !node.data.isBidirectional &&
                        <Handle type="source" id="inbound-right" position={Position.Right} />}
                </div>
            }
        </div>
    );
};

export default CustomNodeComponent;
