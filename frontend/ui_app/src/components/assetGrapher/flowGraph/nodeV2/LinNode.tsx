import React, {useState} from 'react';
import {Handle} from 'reactflow';
import {
	Database,
	Cpu,
	FlaskConical,
	Box,
	Cloud,
	Plus,
	Minus,
	Container,
	Settings
} from 'lucide-react';

interface NodeData {
	label: string;
	children: any[];
	isStartNode?: boolean;
	category: string;
	extra?: any;
	metadata?: {
		version?: string;
		status?: string;
		type?: string;
	};
}

interface NodeProps {
	data: NodeData;
}

interface NodeContentProps {
	icon: React.ReactNode;
	data: NodeData;
	children?: React.ReactNode;
	bgColor: string;
}

interface NodeWrapperProps {
	children: React.ReactNode;
	borderColor: string;
	isStartNode?: boolean;
}

const getNodeSingleChildData = (data: NodeData): NodeData | null => {
	if (!data.extra?.count || data.extra.count !== 1) return null;
	return data.children[0].data;
}

const getNodeSeqId = (data: NodeData | null) => {
	if (!data?.extra?.name) return null;
	const assetName: string = data.extra.name;
	return assetName.split("/")[1];
}

const NodeContent = ({ icon, data, children, bgColor }: NodeContentProps) => {
	if (!data) return null;
	
	const label = data.extra?.class_title || data.label;
	const category = data.extra?.class_type || data.category;
	const version = data.extra?.name ? data.extra.name.split("/")[2] : null;
	const seq_id = getNodeSeqId(data) ?? (data.extra?.count === 1? getNodeSeqId(getNodeSingleChildData(data)) : null);
	const count = data.extra?.count;
	
	return (
		<div className="flex items-stretch h-full rounded-lg min-h-12">
			<div className={`${bgColor} flex items-center justify-center py-2 px-4 rounded-l-lg`}>
				{icon}
			</div>
			<div className="flex-1 py-2 px-3">
				<div className="flex items-center gap-2">
					<span className="text-sm font-medium">{label}</span>
					{seq_id && (
						<span className="px-1.5 py-0.5 bg-gray-100 rounded text-xs text-gray-600">
							#{seq_id}
						</span>
					)}
				</div>
				<div className="flex space-x-4 items-center mt-0.5">
					{category && (
						<div className="text-xs text-gray-500">
							<span className="text-gray-400">Data Type:</span> {category}
						</div>
					)}
					{version && (
						<div className="text-xs text-gray-500">
							<span className="text-gray-400">v</span>{version}
						</div>
					)}
					{count && (
						<div className="text-xs text-gray-500">
							<span className="text-gray-400">refs:</span>{count}
						</div>
					)}
				</div>
			</div>
			{children}
		</div>
	);
};

const NodeWrapper = ({children, borderColor, isStartNode}: NodeWrapperProps) => (
	<div className={`border ${borderColor} rounded-full bg-white min-w-64 ${isStartNode ? "ml-2" : ""}`}>
		<Handle
			type="target"
			position="left"
			className="!border-gray-400"
		/>
		{children}
		<Handle
			type="source"
			position="right"
			className="!border-gray-400"
		/>
	</div>
);

const ModelNode = ({data, children}: { data: NodeData; children?: React.ReactNode }) => (
	<NodeWrapper borderColor="border-purple-200" isStartNode={data.isStartNode}>
		<NodeContent
			icon={<Cpu className="text-white bg-purple-500 rounded size-5"/>}
			data={data}
			children={children}
			bgColor="bg-purple-500"
		/>
	</NodeWrapper>
);

const DatasetNode = ({data, children}: { data: NodeData; children?: React.ReactNode }) => (
	<NodeWrapper borderColor="border-green-200" isStartNode={data.isStartNode}>
		<NodeContent
			icon={<Database className="text-white bg-green-500 size-5"/>}
			data={data}
			children={children}
			bgColor="bg-green-500"
		/>
	</NodeWrapper>
);

const ContainerNode = ({data, children}: { data: NodeData; children?: React.ReactNode }) => {
	return (
		<NodeWrapper borderColor="border-orange-200" isStartNode={data.isStartNode}>
			<NodeContent
				icon={<Container className="text-white bg-orange-500 size-5"/>}
				data={data}
				children={children}
				bgColor="bg-orange-500"
			/>
		</NodeWrapper>
	);
}

const DeploymentNode = ({data, children}: { data: NodeData; children?: React.ReactNode }) => (
	<NodeWrapper borderColor="border-gray-200" isStartNode={data.isStartNode}>
		<NodeContent
			icon={<Cloud className="text-white bg-gray-500 size-5"/>}
			data={data}
			children={children}
			bgColor="bg-gray-500"
		/>
	</NodeWrapper>
);

const ExperimentNode = ({data, children}: { data: NodeData; children?: React.ReactNode }) => (
	<NodeWrapper borderColor="border-green-200" isStartNode={data.isStartNode}>
		<NodeContent
			icon={<FlaskConical className="text-white bg-green-500 size-5"/>}
			data={data}
			children={children}
			bgColor="bg-green-500"
		/>
	</NodeWrapper>
);

const ConfigurationNode = ({data, children}: { data: NodeData; children?: React.ReactNode }) => (
	<NodeWrapper borderColor="border-yellow-200" isStartNode={data.isStartNode}>
		<NodeContent
			icon={<Settings className="text-white bg-yellow-500 size-5"/>}
			data={data}
			children={children}
			bgColor="bg-yellow-500"
		/>
	</NodeWrapper>
);

const DefaultNode = ({data, children}: { data: NodeData; children?: React.ReactNode }) => (
	<NodeWrapper borderColor="border-blue-200" isStartNode={data.isStartNode}>
		<NodeContent
			icon={<Box className="text-white bg-blue-500 size-5"/>}
			data={data}
			children={children}
			bgColor="bg-blue-500"
		/>
	</NodeWrapper>
);

const ChildrenToggle = ({showChildren, onClick}: { showChildren: boolean; onClick: () => void }) => (
	<button
		onClick={onClick}
		className="btn btn-sm btn-ghost rounded-full hover:bg-gray-200 mt-2"
	>
		{showChildren ? <Minus className="w-4 h-4"/> : <Plus className="w-4 h-4"/>}
	</button>
);

export const LinNode: React.FC<NodeProps> = (props) => {
	const [showChildren, setShowChildren] = useState(false);
	const {data} = props;
	const children = data.children;
	
	const classTitle = children.length > 0 ? children[0].data.extra?.class_title  || children[0].data.extra?.name : data.label;
	let classLabel: string = classTitle.split("/")[0];
	const category = children.length > 0 ? children[0].data.extra?.class_type : null;
	const count = children.length > 0 ? children.length : null;
	
	const nodeData = {
		...data,
		label: classLabel,
		category: category,
		extra: {
			...data.extra,
			count: count
		}
	};
	
	const childToggle = children.length > 1 ? (
		<ChildrenToggle
			showChildren={showChildren}
			onClick={() => setShowChildren(!showChildren)}
		/>
	) : null;
	
	const renderNode = () => {
		const nodeProps = {data: nodeData, children: childToggle};
		let category = data.extra?.class_type || data.category;
		if (!category && children.length > 0) {
			category = children[0].data.extra?.class_type;
		}
		switch (category) {
			case 'models':
				return <ModelNode {...nodeProps} />;
			case 'datasets':
				return <DatasetNode {...nodeProps} />;
			case 'docker':
				return <ContainerNode {...nodeProps} />;
			case 'deployment':
				return <DeploymentNode {...nodeProps} />;
			case 'experiment':
				return <ExperimentNode {...nodeProps} />;
			case 'configuration':
				return <ConfigurationNode {...nodeProps} />;
			default:
				return <DefaultNode {...nodeProps} />;
		}
	};
	
	return (
		<div className="flex flex-col">
			{renderNode()}
			{showChildren && children.length > 0 && (
				<div className="ml-8 mt-2">
					{children.map((child, index) => (
						<div key={index} className="mb-2">
							<LinNode data={child.data}/>
						</div>
					))}
				</div>
			)}
		</div>
	);
};
