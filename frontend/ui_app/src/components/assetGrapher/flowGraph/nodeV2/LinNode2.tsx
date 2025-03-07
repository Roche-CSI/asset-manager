import React, {useState} from 'react';
import { Handle, NodeProps } from 'reactflow';
import {ChevronDown, ChevronUp, Layers, Minus, Plus} from "lucide-react";
import {useParams} from "react-router-dom";


interface NodeProps {
	data: {
		label: string;
		children: any[];
		isStartNode: boolean;
	};
}

export const LinNode2: React.FC<NodeProps> = (node: NodeProps) => {
	const { project_id } = useParams();
	const [showChildren, setShowChildren] = useState(false);
	const children = node.data.children;
	let classLabel: string = node.data.label; //default for root node
	
	if (children.length > 0) { //for in/out node
		const className = children[0].data.label.split("/")[0];
		classLabel = children.length > 1 ? `${className}` : children[0].data.label.split("/").slice(0, 2).join("/");
	}
	
	const toggleChildren = () => {
		setShowChildren(!showChildren);
	};
	
	const NodeBox = ({node}) => {
		return (
			<div className="flex items-center h-full box-border bg bg-red-800">
				<span className="flex-1 p-2 ml-2 text-lg">{node.data.label}</span>
			</div>
		);
	}
	
	return (
		<div className="flex flex-col">
			<div
				className={`border w-64 border-gray-400 rounded-md shadow-sm h-full ${node.data.isStartNode ? "ml-2" : ""}`}>
				<Handle type="target" position="left" style={{borderRadius: 0}}/>
				<div className="flex items-center h-full w-full">
					<div className="bg-base-200 border-r boder-base-200 h-full flex items-center justify-center p-3 rounded-l-md">
						<Layers className="w-5 h-5 text-neutral-500"/>
					</div>
					<span className="flex-1 p-2 ml-2 text-lg w-full">{classLabel}</span>
					{children.length > 1 && (
						<button
							onClick={toggleChildren}
							className="p-2 hover:bg-gray-200 rounded-full"
						>
							{showChildren ? <Minus className="w-5 h-5"/> : <Plus className="w-5 h-5"/>}
						</button>
					)}
				</div>
				<Handle type="source" position="right" style={{borderRadius: 0}}/>
			</div>
			{showChildren && children.length > 0 && (
				<div className="ml-8 mt-2 bg-gray-200">
					{children.map((child, index) => (
						<NodeBox key={index} node={child} />
					))}
				</div>
			)}
		</div>
	);
}

