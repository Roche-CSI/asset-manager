import React from "react";
import {Project} from "../../../../servers/asset_server";

const MetricsListView: React.FC<{project: Project}> = ({project}) => {
	
	return (
		<div className="bg-base-100 w-full">
			<div className="text-lg text-neutral mb-6 font-semibold">Project Metrics</div>
			<div className="h-32 border border-base-300 rounded-md w-full">
				<div className="flex justify-center items-center h-full text-neutral-500">
					Metrics coming soon
				</div>
			</div>
		</div>
	);
}

export default MetricsListView;
