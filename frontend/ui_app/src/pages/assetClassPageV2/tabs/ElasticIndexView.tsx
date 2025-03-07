import React, { useState } from 'react';
import { ChevronRight, ChevronDown, Database, Key, Calendar, Hash, Box, Tag, Settings } from 'lucide-react';

const getFieldIcon = (type) => {
	switch (type) {
		case 'keyword':
			return <Key className="size-4 text-gray-400" />;
		case 'date':
			return <Calendar className="w-4 h-4 text-gray-400" />;
		case 'integer':
		case 'long':
			return <Hash className="w-4 h-4 text-gray-400" />;
		case 'object':
			return <Box className="w-4 h-4 text-gray-400" />;
		case 'text':
			return <Tag className="w-4 h-4 text-gray-400" />;
		default:
			return <Settings className="w-4 h-4 text-gray-400" />;
	}
};

const Badge = ({ children }) => {
	return (
		<span className="btn btn-xs btn-ghost text-secondary border-secondary rounded-md">
			{children}
    </span>
	);
};

const Field = ({ name, field, depth = 0 }) => {
	const [isOpen, setIsOpen] = useState(depth < 2);
	const hasProperties = field.properties || (field.type === 'object' && field.dynamic === true);
	
	return (
		<div className="mt-2">
			<div className="flex flex-wrap items-center gap-2">
				<div
					className="flex items-center cursor-pointer hover:bg-base-200 rounded-lg transition-colors"
					onClick={() => setIsOpen(!isOpen)}
				>
					<div className="flex items-center min-w-[24px]">
						{hasProperties ? (
							<div className="w-6 h-6 flex items-center justify-center">
								{isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
							</div>
						) : (
							<div className="w-6 h-6 flex items-center justify-center">
								{getFieldIcon(field.type)}
							</div>
						)}
					</div>
					<span className="text-sm font-medium text-neutral ml-2">{name}</span>
				</div>
				
				{!hasProperties && (
					<div className="flex flex-wrap items-center gap-2">
						{field.type && (
							<Badge>{field.type}</Badge>
						)}
						{field.analyzer && (
							<Badge>analyzer: {field.analyzer}</Badge>
						)}
						{field.fields && Object.entries(field.fields).map(([subName, subField]) => (
							<div key={subName} className="flex items-center gap-2">
								<span className="text-sm text-neutral-500">{subName}:</span>
								<Badge>{subField.type}</Badge>
								{subField.analyzer && (
									<Badge>analyzer: {subField.analyzer}</Badge>
								)}
							</div>
						))}
					</div>
				)}
			</div>
			
			{isOpen && hasProperties && (
				<div className="ml-6 border-l-2 border-base-300 pl-4 mt-2 border">
					{Object.entries(field.properties || {}).map(([key, value]) => (
						<Field key={key} name={key} field={value} depth={depth + 1} />
					))}
				</div>
			)}
		</div>
	);
};

const ElasticIndexView = () => {
	const mapping = {
		dynamic: "strict",
		properties: {
			id: {type: "keyword"},
			title: {type: "text", analyzer: "standard", fields: {keyword: {type: "keyword"}}},
			description: {type: "text", analyzer: "standard"},
			tags: {type: "keyword"},
			metadata: {type: "object", dynamic: true},
			class_name: {type: "keyword", fields: {text: {type: "text", analyzer: "standard"}}},
			class_id: {type: "keyword"},
			project_name: {type: "keyword", fields: {text: {type: "text", analyzer: "standard"}}},
			project_id: {type: "keyword"},
			root_version: {
				type: "object",
				properties: {
					id: {type: "keyword"},
					created_at: {type: "date"},
					size: {type: "long"},
					num_objects: {type: "integer"}
				}
			},
			leaf_version: {
				type: "object",
				properties: {
					id: {type: "keyword"},
					created_at: {type: "date"},
					size: {type: "long"},
					num_objects: {type: "integer"}
				}
			},
			owner: {type: "keyword"},
			created_by: {type: "keyword"},
			created_at: {type: "date"},
			modified_by: {type: "keyword"},
			modified_at: {type: "date"},
			alias: {type: "keyword", fields: {text: {text: "text", analyzer: "standard"}}},
			seq_id: {type: "long"},
			name: {type: "keyword"},
			status: {type: "keyword"},
			class_status: {type: "keyword"},
			project_status: {type: "keyword"},
			num_versions: {type: "integer"}
		}
	};
	
	return (
		<div className="bg-base-100 w-full">
			<div className="mb-6 flex justify-between w-full">
        <span className="text-lg text-neutral font-semibold">
          Elastic Search Index Mapping
        </span>
			</div>
			
			<div className="border border-base-300 rounded-md mb-6">
				<div className="bg-base-100 p-4 rounded-md">
					<div className="flex items-center gap-2 mb-4">
						<Database className="w-4 h-4" />
						<span className="text-sm font-medium text-neutral">Dynamic Mode:</span>
						<Badge>{mapping.dynamic}</Badge>
					</div>
					
					{Object.entries(mapping.properties).map(([key, value]) => (
						<Field key={key} name={key} field={value} />
					))}
				</div>
			</div>
		</div>
	);
};

export default ElasticIndexView;
