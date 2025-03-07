import React from 'react';

import { Asset } from "../../servers/asset_server";
// import your template views here


function parseURL(pathName: string) {
	const pathSegments = pathName.split('/').filter(segment => segment);
	return {
		project_id: pathSegments[1] || null,
		class_name: pathSegments[2] || null,
		seq_id: pathSegments[3] || null,
		view: pathSegments[4] || null,
	};
}

interface Props {
	templateName: string;
	asset: Asset;
	switchComponent: React.ReactNode;
}

const Templates: Record<string, any> = {
	// add your template views here
}

const TemplateAssetView: React.FC<Props> = ({ templateName, asset, switchComponent }) => {
	console.log("asset:", asset);
	
	const Template = Templates[templateName];
	if (Template) {
		return <Template asset={asset} switchComponent={switchComponent} />
	} else {
		return null;
	}
};

export default TemplateAssetView;
