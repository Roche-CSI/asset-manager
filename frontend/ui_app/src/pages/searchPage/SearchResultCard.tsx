import React from 'react';
import {AssetEntry} from "pages/searchPage/AssetEntry";
import {Box, FileBox, UserCircle, AlertTriangle, SquareX} from "lucide-react";
import {Link} from "react-router-dom";
import {CLASS_ICONS} from "pages/classListPage/ClassIcons";
import {FormatHighlight, MetadataHighlight} from "pages/searchPage/MetadataHighlight";
import Status from "pages/searchPage/Status";

interface SearchResultCardProps {
	item: AssetEntry;
	highlightKeys?: string[];
	selectedTags?: string[];
}

interface HighlightedTextProps {
	item: AssetEntry;
	keyName: string;
	resultTitle?: string;
	highlightKeys: string[];
}

const HighlightedText: React.FC<HighlightedTextProps> = ({item, keyName, resultTitle, highlightKeys}) => {
	const value: string = resultTitle?? item[keyName] as string;
	
	if ((!highlightKeys || !item.es_highlight) || !highlightKeys.includes(keyName)) {
		return <span>{value}</span>;
	}
	
	const es_highlights: any = {};
	Object.keys(item.es_highlight).forEach(key => {
		if (key.endsWith('.ngram')) {
			es_highlights[key.slice(0, -6)] = item.es_highlight[key];
		} else if (key.endsWith('.text')) {
			es_highlights[key.slice(0, -5)] = item.es_highlight[key];
		} else {
			es_highlights[key] = item.es_highlight[key];
		}
	});
	
	if (!Object.keys(es_highlights).find(k => k === keyName)) {
		return <span>{value}</span>;
	}
	
	const highlights: string[] = es_highlights[keyName];
	const processedHighlights = highlights.map((highlight, index) => {
		return <FormatHighlight key={index} text={highlight}/>
	});
	
	return <span>{processedHighlights}</span>;
};

const Badge = ({label, children}: { label: string, children: any }) => (
	<span className="inline-flex items-center text-xs">
    <span className="text-gray-400 mr-1.5">{label}:</span>
    <span className="text-gray-600">{children}</span>
  </span>
);

const TagHighlight = ({item}) => {
	const highlightedTags = item.es_highlight && item.es_highlight["tags.ngram"];
	if (!highlightedTags) return null;
	
	const sanitized = highlightedTags.map((tag) => {
		return {
			[tag.replace(/<em>/g, "").replace(/<\/em>/g, "")]: tag
		}
	});
	const matchCount = sanitized.length;
	
	const remainingTags = item.tags.filter(tag => !sanitized.find(t => Object.keys(t)[0] === tag));
	remainingTags.forEach(tag => {
		sanitized.push({[tag]: tag});
	});
	
	return (
		<div className="mt-4 border-t border-base-200 py-4">
			<div className="flex flex-wrap gap-2 items-center mb-4">
				<span className="text-xs font-medium text-gray-500 mr-2">Tags:</span>
				<span className="px-2 py-0.5 text-xs rounded-full bg-blue-50 text-blue-600 font-medium">
				{matchCount} matches
				</span>
			</div>
			<div className="flex flex-wrap gap-4 items-center">
				{sanitized.map((tag, index) => {
						const tagName = Object.values(tag)[0];
						return (
							<span
								key={index}
								className="px-2 py-1 bg-blue-50 text-blue-600 rounded-full text-xs hover:bg-blue-100 transition-colors"
							>
							<FormatHighlight text={tagName as string}/>
						</span>
						)
					}
				)}
			</div>
		</div>
	)
}

const TagSelection = ({tags, selectedTags}) => {
	if (!tags || !selectedTags) return null;
	const filteredTags = tags.filter(tag => selectedTags.includes(tag));
	const matchCount = filteredTags.length;
	if (!matchCount) return null;
	
	return (
		<div className="border-t border-base-200 py-4">
			<div className="flex flex-wrap gap-2 items-center mb-4">
				<span className="text-xs font-medium text-gray-500 mr-2">Tags:</span>
				<span className="px-2 py-0.5 text-xs rounded-full bg-blue-50 text-blue-600 font-medium">
				{matchCount} {matchCount === 1 ? "match" : "matches"}
				</span>
			</div>
			<div className="flex flex-wrap gap-2 items-center">
				{tags.map((tag, index) => {
					const isSelected = filteredTags.includes(tag);
					return (
						<span
							key={index}
							className={`px-2 py-1 ${isSelected ? "bg-yellow-200" : "bg-base-200"} ${isSelected ? "text-gray-700 font-medium" : "text-gray-600"} rounded-full text-xs hover:bg-${isSelected ? "blue" : "gray"}-100 transition-colors`}
						>
							{tag}
					</span>
					)
				})}
			</div>
		</div>
	)
}

export const SearchResultCard: React.FC<SearchResultCardProps> = ({
	                                                                  item,
	                                                                  highlightKeys,
	                                                                  selectedTags
                                                                  }) => {
	const formatDate = (timestamp: string | number) => {
		const date = typeof timestamp === 'number' ? new Date(timestamp * 1000) : new Date(timestamp);
		return date.toLocaleDateString();
	};
	
	const isDeprecatedOrObsolete = () => {
		const status = typeof item.status === 'number'
			? new Status(item.status).description().toLowerCase()
			: (item.status as string).toLowerCase();
		const classStatus = typeof item.class_status === 'number'
			? new Status(item.class_status).description().toLowerCase()
			: (item.class_status as string).toLowerCase();
		const projectStatus = typeof item.project_status === 'number'
			? new Status(item.project_status).description().toLowerCase()
			: (item.project_status as string).toLowerCase();
		const icons = [];
		
		if ([status, classStatus, projectStatus].includes("obsolete")) {
			icons.push(<SquareX key="obsolete" className="size-5 text-red-500"/>)
		}
		if ([status, classStatus, projectStatus].includes("deprecated")) {
			icons.push(<AlertTriangle key="deprecated" className="size-5 text-yellow-500"/>)
		}
		return icons;
	};
	
	const targetKeys = (highlightKeys || []).map(key => key.split('.')[0]);
	const Icons = isDeprecatedOrObsolete();
	const hasMetadata = item.metadata && targetKeys.includes("metadata");
	const hasTags = item.tags && targetKeys.includes("tags");
	
	const Icon = CLASS_ICONS[item.class_type] || CLASS_ICONS["default"];
	
	return (
		<div className="mb-8 p-4 border border-gray-200 rounded-md hover:shadow-md transition-shadow">
			<h2 className="text-xl mb-2 flex text-center justify-between">
				<Link
					className="text-[#0064FF] hover:underline cursor-pointer"
					to={`/asset/${item.project_id}/${item.class_name}/${item.seq_id}/files?version=${item?.leaf_version?.number || "0.0.0"}`}
				>
					<HighlightedText item={item} 
						resultTitle={item.title || item.alias || `${item.class_name}/${item.seq_id}`}
						keyName='title'
						highlightKeys={targetKeys}/>
				</Link>
				<div className="flex items-center ml-2">
					{Icons.map((Icon, index) => (
						<div key={index} className="flex items-center justify-center ml-1">
							{Icon}
						</div>
					))}
				</div>
			</h2>
			<p className="text-sm text-gray-600 pb-4 mb-4 border-b border-base-300">
				<HighlightedText item={item} keyName="description" highlightKeys={targetKeys}/>
			</p>
			<div className="text-xs text-gray-500 flex space-x-4 mb-4">
				<div className="flex items-center space-x-2">
					type: {item.class_type}
				</div>
				<div className="flex items-center space-x-2">
					<Box className="size-3 mr-1 text-gray-400"/>
					<p>Size: {(item.leaf_version.size / 1000000).toFixed(1)} MB</p>
				</div>
				<div className="flex items-center space-x-2">
					<FileBox className="size-3 mr-1 text-gray-400"/>
					<p>Files: {item.leaf_version.num_objects || 'N/A'}</p>
				</div>
				<div className="flex items-center space-x-2">
					<UserCircle className="size-3 mr-1 text-gray-400"/>
					<p>
						<span className="mr-2">Created by:</span>
						<HighlightedText item={item} keyName="created_by" highlightKeys={targetKeys}/>
						<span> on {formatDate(item.created_at)}</span>
					</p>
				</div>
				{item.modified_at && item.modified_at !== item.created_at && (
					<div className="flex items-center space-x-2">
						<UserCircle className="size-3 mr-1 text-gray-400"/>
						<p>
							<span className="mr-2">Last update:</span>
							<HighlightedText item={item} keyName="modified_by" highlightKeys={targetKeys}/>
							<span> on {formatDate(item.modified_at)}</span>
						</p>
					</div>
				)}
			</div>
			<div className="flex flex-wrap gap-2 pb-4">
				<Badge label="Project">
					<HighlightedText item={item} keyName="project_title" highlightKeys={targetKeys}/>
				</Badge>
				<Badge label="Collection">
					<HighlightedText item={item} keyName="class_title" highlightKeys={targetKeys}/>
				</Badge>
				<Badge label="Owner">
					<HighlightedText item={item} keyName="owner" highlightKeys={targetKeys}/>
				</Badge>
				<Badge label="Alias">
					<HighlightedText item={item} keyName="alias" highlightKeys={targetKeys}/>
				</Badge>
			</div>
			<TagSelection tags={item.tags} selectedTags={selectedTags}/>
			{hasTags && <TagHighlight item={item} />}
			{hasMetadata && <MetadataHighlight item={item} highlightKeys={highlightKeys}/>}
		</div>
	);
};
