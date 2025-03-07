import { AssetRef } from "../../servers/asset_server";
import NodeData from "./flowGraph/node/nodeData"
import EdgeData from "./flowGraph/edge/edgeData";
import { isEmptyObject } from "../../utils";
import styles from "./flowGraph/graph.module.scss";


export default class GraphGenerator {
	height: number = 500;
	inboundRef: AssetRef[] = []
	outboundRef: AssetRef[] = []
	hasInbound: boolean = false
	hasOutbound: boolean = false
	nodes: object[] = [];
	edges: object[] = []
	
	constructor(inboundRef: AssetRef[], outboundRef: AssetRef[], height?: number) {
		if (height) {
			this.height = height;
		}
		this.inboundRef = inboundRef;
		this.outboundRef = outboundRef;
		this.hasInbound = inboundRef.length > 0;
		this.hasOutbound = outboundRef.length > 0;
		console.log("inboundRef:", inboundRef, "outboundRef:", outboundRef);
	}
	
	createGraph() {
		let inboundTree;
		let outboundTree;
		let graphId;
		let inboundGraph;
		let outboundGraph;
		let bidirectionalNodes;
		// do one tree for the time being
		if (this.hasInbound) {
			inboundTree = this.constructInboundTree(this.inboundRef)
			console.log("inboundTree:", inboundTree);
			graphId = Object.keys(inboundTree)[0]
			inboundGraph = inboundTree[graphId]
		}
		if (this.hasOutbound) {
			outboundTree = this.constructOutboundTree(this.outboundRef)
			console.log("outboundTree:", outboundTree);
			graphId = Object.keys(outboundTree)[0]
			outboundGraph = outboundTree[graphId]
		}
		if (this.hasInbound && this.hasOutbound) {
			bidirectionalNodes = this.constructBidirectional(inboundGraph, outboundGraph)
		}
		let nodes: object[] = this.createNodes(inboundGraph, outboundGraph, bidirectionalNodes);
		let edges: object[] = this.createEdges(inboundGraph, outboundGraph, bidirectionalNodes);
		return [nodes, edges]
	}
	
	// TODO: Improve node position calculation
	private createNodes(inboundGraph: any, outboundGraph: any, bidirectionalNodes: any) {
		// todo: determine if we need to display multiple trees
		let minGapY = 120;
		let minGapX = 400;
		let positionX = 250;
		let positionY = minGapY;
		let nodes = []
		if (this.hasInbound) {
			let sources: NodeData[] = Object.values(inboundGraph["sources"]);
			sources.forEach((node: NodeData, index: number) => {
				node.position = {x: positionX, y: positionY};
				node.type = "special";
				positionX += 0; //todo: improve this - its hacky currently
				positionY += minGapY;
				nodes.push(node);
			})
			let target = inboundGraph["target"];
			positionX += minGapX; // extra distance for target node
			target.position = {x: positionX, y: positionY / 2 + 50}; // center of screen
			target.type = "special";
			nodes.push(target);
		}
		if (this.hasOutbound) {
			// positionY = minGapY + 200; // reset vertical axis for outbound node
			positionY = minGapY
			positionX = minGapX + 200
			if (!this.hasInbound) {
				let source = outboundGraph["source"];
				source.position = { x: positionX, y: positionY / 2 + 100}; // center of screen
				source.type = "special";
				nodes.push(source);
			}
			positionX += minGapX; // extra distance for outbound node
			positionY -= 300; // reset vertical axis for outbound node
			let targets: NodeData[] = Object.values(outboundGraph["targets"]);
			targets.forEach((node: NodeData, index: number) => {
				positionX += 0; //todo: improve this - its hacky currently
				positionY += minGapY + 100;
				node.position = { x: positionX, y: positionY };
				node.type = "special";
				nodes.push(node);
			})
		}
		if (!isEmptyObject(bidirectionalNodes)) {
			positionX = 2 * minGapX
			positionY = minGapY + 250
			let bidirectionalTargets: NodeData[] = Object.values(bidirectionalNodes)
			bidirectionalTargets.forEach((node: NodeData, index: number) => {
				node.position = {x: positionX, y: positionY};
				node.type = "special";
				positionX += minGapX /2 + 50;
				nodes.push(node)
			})
		}
		return nodes;
	}
	
	private createEdges(inboundGraph: any, outboundGraph: any, bidirectionalNodes: any): EdgeData[] {
		let edges: EdgeData[] = [];
		if (this.hasInbound) {
			let targetId = inboundGraph.target.getId();
			let sources = inboundGraph.sources
			for (const groupId in sources) {
				edges.push(new EdgeData({
					src_node_id: sources[groupId].getId(),
					dst_node_id: targetId,
					isInbound: true,
					label: sources[groupId].getLabel(),
				}))
			}
		}
		if (this.hasOutbound) {
			let sourceId = outboundGraph.source.getId();
			let targets = outboundGraph.targets
			for (const groupId in targets) {
				edges.push(new EdgeData({
					src_node_id: sourceId,
					dst_node_id: targets[groupId].getId(),
					isInbound: false,
					label: targets[groupId].getLabel(),
				}))
			}
		}
		if (!isEmptyObject(bidirectionalNodes)) {
			let sourceId = outboundGraph.source.getId(); // use the same root id as outbound
			for (const groupId in bidirectionalNodes) {
				edges.push(new EdgeData({
					src_node_id: sourceId,
					dst_node_id: bidirectionalNodes[groupId].getId(),
					isInbound: false,
					isBidirectional: true,
					label: bidirectionalNodes[groupId].getLabel(),
					sourceHandle: "source-bottom",
					targetHandle: "target-top"
				}))
				edges.push(new EdgeData({
					src_node_id:  bidirectionalNodes[groupId].getId(),
					dst_node_id: sourceId,
					isInbound: false,
					isBidirectional: true,
					sourceHandle: "source-top",
					targetHandle: "target-bottom"
				}))
			}
		}
		return edges;
	}
	
	
	/**
	 * Create ref tree for a dst_version
	 * @returns tree: an Object contains target and sources info {id: {target, sources}, ...}
	 */
	private constructInboundTree(refs: AssetRef[]): any {
		console.log("inbound refs:", refs);
		let tree: any = {};
		refs.forEach((ref: AssetRef, index: number) => {
			if (!(ref.dst_version.id in tree)) {
				const comps = ref.dst_version.name.split("/");
				if (ref.dst_version.class_title) {
					comps[0] = ref.dst_version.class_title; // replace class_name with class_title
				}else {
					console.log("class_title not found for:", ref.dst_version);
				}
				console.log("comps:", comps);
				tree[ref.dst_version.id] = {
					"target": new NodeData({
						id: ref.dst_version.id,
						label: comps.join("/"),
						className: styles.rootNode,
						category: ref.dst_version.class_type,
						extra: ref.dst_version
					}),
					"sources": {}
				}
			}
			let sources = tree[ref.dst_version.id]["sources"];
			let classId = ref.src_version.asset_class;
			let groupId = `${classId}-${ref.label}`
			if (!(groupId in sources)) {
				const inboundClassId: string = `${groupId}:inbound`;
				sources[groupId] = new NodeData({
					id: inboundClassId,
					label: ref.label,
					category: ref.category,
					className: styles.srcNode,
					isInbound: true,
					children: [],
				});
			}
			
			const labelComps = ref.src_version.name.split("/");
			if (ref.src_version.class_title) {
				labelComps[0] = ref.src_version.class_title; // replace class_name with class_title
			}
			
			let childNode = new NodeData({
				id: ref.src_version.id,
				label: ref.src_version.name,
				className: styles.srcNode,
				category: ref.src_version.class_type,
				extra: ref.src_version,
				isInbound: true,
				ref: ref
			});
			sources[groupId].addChild(childNode)
			tree[ref.dst_version.id]["sources"] = sources;
		});
		return tree;
	}
	
	/**
	 * Create ref tree for a src_version
	 * @returns tree: Object {id: {target, sources: {groupId, children:[NodeData, .....]} }, ...}
	 */
	private constructOutboundTree(refs: AssetRef[]): any {
		let tree: any = {};
		refs.forEach((ref: AssetRef, index: number) => {
			if (!(ref.src_version.id in tree)) {
				const comps = ref.src_version.name.split("/");
				if (ref.src_version.class_title) {
					comps[0] = ref.src_version.class_title; // replace class_name with class_title
				}else {
					console.log("class_title not found for:", ref.src_version);
				}
				console.log("comps:", comps);
				tree[ref.src_version.id] = {
					"source": new NodeData({
						id: ref.src_version.id,
						label: comps.join("/"),
						className: styles.rootNode,
						category: ref.src_version.class_type,
						extra: ref.src_version
					}),
					"targets": {}
				}
			}
			// debugger;
			let targets = tree[ref.src_version.id]["targets"];
			// console.log("targets:", targets);
			let classId = ref.dst_version.asset_class
			let groupId = `${classId}-${ref.label}`
			if (!(groupId in targets)) {
				const outboundClassId: string = `${groupId}:outbound`;
				targets[groupId] = new NodeData({
					id: outboundClassId,
					label: ref.label,
					className: styles.dstNode,
					isInbound: false,
					children: [],
				})
			}
			
			const labelComps = ref.dst_version.name.split("/");
			if (ref.dst_version.class_title) {
				labelComps[0] = ref.dst_version.class_title; // replace class_name with class_title
			}
			
			let childNode = new NodeData({
				id: ref.dst_version.id,
				label: labelComps.join("/"),
				className: styles.dstNode,
				isInbound: false,
				category: ref.dst_version.class_type,
				extra: ref.dst_version,
				ref: ref
			});
			targets[groupId].addChild(childNode)
			tree[ref.src_version.id]["targets"] = targets;
		});
		return tree;
	}
	
	private constructBidirectional(inboundGraph: any, outboundGraph: any) {
		let nodes: any = {};
		let inNodes: any = inboundGraph.sources;
		let outNodes: any = outboundGraph.targets;
		let commonIds = Object.keys(inNodes).filter((x: string) => Object.keys(outNodes).includes(x));
		for (let i = 0; i < commonIds.length; i++) {
			let groupId: string = commonIds[i]
			let sourceNode: any = inNodes[groupId]
			let targetNode: any = outNodes[groupId]
			if (!(groupId in nodes)) {
				const bidirectionalClassId: string = `${groupId}:bidirectional`;
				const newLabel: string = sourceNode.data.label !== targetNode.data.label?
					`${sourceNode.data.label} / ${targetNode.data.label}`:
					sourceNode.data.label;
				nodes[groupId] = new NodeData({
					id: bidirectionalClassId,
					label: newLabel,
					className: styles.biNode,
					isInbound: true,
					isBidirectional: true,
					children: [],
				})
			}
			let sourceChildren: any = sourceNode.data.children;
			let targetChildren: any = targetNode.data.children;
			const isSameChild = (a: any, b: any) => a.id === b.id;
			let biChildren: any = sourceChildren.filter(
				(x: any) => targetChildren.some((k: any) => isSameChild(x, k)))
			if (biChildren.length === 0) { // delete class if no common children found
				delete nodes[groupId]
			} else {
				// add common children to bidirectional graph and delete them from inbound and outbound
				nodes[groupId].data.children = biChildren
				sourceNode.data.children = sourceChildren.filter((x: any) => !biChildren.some((k: any) => isSameChild(x, k)))
				targetNode.data.children = targetChildren.filter((x: any) => !biChildren.some((k: any) => isSameChild(x, k)))
				if (sourceNode.data.children.length === 0) { // if inbound group has no assets left
					delete inNodes[groupId]
				}
				if (targetNode.data.children.length === 0) { // if outbound group has no assets left
					delete outNodes[groupId]
				}
			}
		}
		return nodes;
	}
}
