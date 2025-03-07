/* eslint-disable no-mixed-spaces-and-tabs */
import React from "react";
import {TagView, GroupLabel} from "./TagView";
import {TagGroup} from "./taggable";

interface GenericTagListProps {
	groups: GroupLabel[];
	activeGroupName: string;
	groupData: TagGroup;
	onSelectedTagsChange?: (group: TagGroup) => void;
	onSelectedGroupChange?: (name: string) => void;
}

export const GenericTagList: React.FC<GenericTagListProps> = ({
	                                                              groups,
	                                                              activeGroupName,
	                                                              groupData,
	                                                              onSelectedTagsChange,
	                                                              onSelectedGroupChange
                                                              }: GenericTagListProps) => {
	
	// const groupNames = groups.map(group => group.name);
	return (
		<React.Fragment>
			<TagView groups={groups}
			         activeGroupName={activeGroupName}
			         groupData={groupData}
			         onSelectedTagsChange={onSelectedTagsChange}
			         onSelectedGroupChange={onSelectedGroupChange}/>
		</React.Fragment>
	);
};
