enum EdgePositions {
	LEFT = "left",
	RIGHT = "right",
	TOP = "top",
	BOTTOM = "bottom"
};

/**
 * ReactFlow NodeData
 */
interface NodeDataInterface {
	id: any;
	label: string;
    category?: string;
	className: string;
	ref?: any;
	type?: string;
	x?: number;
	y?: number;
	children?: any;
	isInbound?: boolean;
	isBidirectional?: boolean;
	extra?: any;
}

interface NodeValue {
	label?: string;
	category?: string;
	ref?: string;
	children?: Array<any>;
	isInbound?: boolean;
	isBidirectional?: boolean;
	extra?: any;
}

export default class NodeData {
	// data structure required by ReactFlow
	id: string;
	sourcePosition: string; // the edge to next node is connected here
	targetPosition: string; // edge from previous node is connected here
	data: NodeValue;
	position: object;
	className: string;
	type: string;
	isBidirectional?: boolean;
	
	constructor({
		            id,
		            label,
		            category = "",
		            className = "",
		            extra = {},
		            type = "default",
		            ref = null,
		            x = 0,
		            y = 0,
		            children = [],
		            isInbound,
		            isBidirectional
	            }: NodeDataInterface) {
		this.id = id.toString();
		this.targetPosition = isBidirectional ? EdgePositions.BOTTOM : EdgePositions.LEFT;
		this.sourcePosition = isBidirectional ? EdgePositions.TOP : EdgePositions.RIGHT; // left to right graph
		this.data = {
			label: label,
			ref: ref,
			children: children,
			category: category,
			extra: extra,
			isInbound: isInbound,
			isBidirectional: isBidirectional
		};
		this.position = {x: x || 0, y: y || 0};
		this.className = className;
		this.type = type;
	}
	
	getId() {
		return this.id
	}
	
	getLabel() {
		return this.data.label
	}
	
	getRef() {
		return this.data.ref
	}
	
	isInbound() {
		return this.data.isInbound
	}
	
	addChild(childNode: any) {
		this.data.children?.push(childNode)
	}
	
	getChildren() {
		return this.data.children
	}
	
	// constructor(id: any,
	//             label:string,
	//             className: string = "",
	//             type: string = "default",
	//             x?: number,
	//             y?: number,
	//             ) {
	//     this.id = id.toString();
	//     this.targetPosition = EdgePositions.LEFT;
	//     this.sourcePosition = EdgePositions.RIGHT; // left to right graph
	//     this.data = {label: label};
	//     this.position = {x: x || 0, y: y || 0};
	//     this.className = className;
	//     this.type = type;
	// }
}
