import React from "react";
import { Handle, Position } from 'reactflow';
import { HoverPopOver } from "../../../popOvers";
import { useParams } from "react-router-dom";
import RefFields from "./RefFields";
import ChildrenFields from "./ChildrenFields";

const PLACEMENT: any = {
    INBOUND: 'left',
    OUTBOUND: 'right',
    ROOT: 'top'
}


const CustomNodeComponent = (node: any) => {
    console.log("node:", node);
    const { project_id } = useParams();
    // const [className, seq_id, version] = node.data.label.split("/");
    const children = node.data.children
    let classLabel: string = node.data.label; //default for root node
    if (children.length > 0) { //for in/out node
        const className = children[0].data.label.split("/")[0];
        classLabel = children.length > 1 ? `${className}/*` : children[0].data.label;
    }

    return (
        <div className="nowheel">
            {children.length === 0 ?
                <div>
                    {rootNode()}
                </div>
                :
                <div>
                    {groupNode()}
                </div>
            }
        </div>
    );

    function rootNode(){
        const trigger = () => (
            <div>
                <Handle type="target" id="inbound-left" position={Position.Left} />
                <div className='min-w-[150px] p-2.5 box-border'>
                    {classLabel}
                </div>
                <Handle
                    type="source"
                    position={Position.Right}
                    id="outbound-right"
                />
                <Handle type="source" id="source-bottom" position={Position.Bottom} />
                <Handle type="target" id="target-bottom" position={Position.Bottom} />
            </div>

        )

        const popOver = () => (
            <div className='border-2 border-zinc-200 rounded-md'>
                <div className='min-h-3 flex justify-center box-border py-2 px-3 bg-zinc-100
                                text-sm font-normal '>
                    {classLabel}
                </div>
                <div className='flex justify-center'>
                    <RefFields assetRef={node.data.ref}/>
                </div>
            </div>
        )

        return (
            <HoverPopOver placement={PLACEMENT.ROOT} trigger={trigger()} popOver={popOver()} />
        )
    }

    function groupNode(){
        const trigger = () => (
            <div>
                {node.data.isBidirectional &&
                    <Handle type="target" id="target-top" position={Position.Top} />}
                {node.data.isBidirectional &&
                    <Handle type="source" id="source-top" position={Position.Top} />}
                {!node.data.isInbound &&
                    <Handle type="target" id="outbound-left" position={Position.Left} />}
                <div className='min-w-[150px] p-2.5 box-border'>
                    {classLabel}
                </div>
                {node.data.isInbound && !node.data.isBidirectional &&
                    <Handle type="source" id="inbound-right" position={Position.Right} />}
            </div>
        )

        const popOver = () => (
            <div className='border-2 border-zinc-200 rounded-md'>
                <div className='min-h-3 flex justify-start border-b-2 border-zinc-200 box-border py-2 px-3 bg-zinc-100
                                text-sm font-normal'>
                    {classLabel}
                </div>
                <div className='flex justify-center py-2 px-3 box-border text-sm font-normal'>
                    <ChildrenFields children={children} project_id={project_id} />
                </div>
            </div>
        )

        return (
            <HoverPopOver
                placement={node.data.isInbound ? PLACEMENT.INBOUND : PLACEMENT.OUTBOUND}
                trigger={trigger()}
                popOver={popOver()} />
        )
    }


};

export default CustomNodeComponent;
