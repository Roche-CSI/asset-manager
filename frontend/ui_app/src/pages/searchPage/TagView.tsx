/* eslint-disable no-mixed-spaces-and-tabs */
import React, {useState} from "react";
import {TagCategory, TagGroup} from "./taggable";
import {TagGrid} from "./TagGrid";

export interface GroupLabel {
	name: string;
	label: string;
	icon?: string;
}

interface TagViewProps {
	groups: GroupLabel[];
	activeGroupName: string;
	groupData: TagGroup;
	onSelectedTagsChange?: (group: TagGroup) => void;
	onSelectedGroupChange?: (name: string) => void;
	tagGridReplacer?: () => React.FC; // custom component to replace the default taggrid
}

export const TagView = ({
	                        groups,
	                        activeGroupName,
	                        groupData,
	                        onSelectedTagsChange,
	                        onSelectedGroupChange,
                        }: TagViewProps) => {
	
	const [selectedGroup, setSelectedGroup] = useState<string>(activeGroupName);
	
	const handleTagSelection = (categories: TagCategory[]) => {
		if (activeGroupName !== selectedGroup) return;
		const parsed: TagGroup = {...groupData, "categories": categories};
		onSelectedTagsChange && onSelectedTagsChange(parsed);
	}
	
	const handleGroupSelection = (name: string) => {
		onSelectedGroupChange && onSelectedGroupChange(name);
		setSelectedGroup(name);
	}
	
	return (
		<div className="">
			<div className="">
				{
					groups.map((group, index) => {
						return <TagLabel key={index}
						                 name={group.name}
						                 icon={group.icon}
						                 label={group.label}
						                 selected={group.name === selectedGroup}
						                 onClick={handleGroupSelection}/>
					})
				}
			</div>
			{
				<TagGrid groupName={selectedGroup}
				         data={groupData ? groupData.categories : []}
				         onSelectedTagsChange={handleTagSelection}/>
			}
		</div>
	);
};

const base: string = "btn btn-xs mr-2 mb-2 rounded-md box-content border-solid border-1 border-base-300";
const className: string = `${base} hover:bg-neutral hover:text-base-100`;
const classNameSelected: string = `${base} bg-base-content text-base-100 hover:text-base-content`;


export const TagLabel = ({name, label, selected, onClick, icon}: {
	name: string,
	label: string,
	selected: boolean,
	icon?: React.ReactElement,
	onClick: (name: string) => void
}) => {
	
	const Icon = icon ? icon : null;
	// console.log("name", name, "label", label, "selected", selected, "onClick", onClick);
	return (
		<button
			className={selected ? classNameSelected : className}
			onClick={() => onClick(name)}>
			{
				Icon && <Icon className="size-3"/>
			}
			{label}
		</button>
	)
}
