import React from 'react';
import { ChonkyIconFA } from 'chonky-icon-fontawesome';
import { File, FileCode, FileJson, FileText } from "lucide-react";

const IconMap: { [iconName: string]: any } = {
	"file": File,
	"text": FileText,
	"database": FileJson,
	"config": FileCode
};

const iconStyle = "text-gray-500 h-4 w-4";

export const FileIcon = (props: any) => {
	const Icon = IconMap[props.icon];
	if (Icon) {
		return <div style={{color: "#b7b8ba"}}><Icon className={iconStyle}/></div>;
	} else {
		return <ChunkyFA icon={props.icon} />;
	}
};

const ChunkyFA = (props: any) => {
	return (
		<span className={iconStyle}>
            <ChonkyIconFA {...props} />
        </span>
	);
};
