import React from "react";
import {MarkdownEditor} from "../../../components/markDownEditor";
import {Asset} from "../../../servers/asset_server";


const AssetReadMeView: React.FC<{asset: Asset, readme?: string}> = ({asset, readme}) => {
	
	return (
		<div className="bg-base-100 w-full">
			<div className="my-6 flex justify-between w-full">
				<div className="text-lg text-neutral mb-6 font-semibold">Asset ReadMe</div>
			</div>
			{
				readme && (
					<div className="">
						<div className="border border-base-300 rounded-md">
							<MarkdownEditor mode={"preview"}
							                showTabs={false}
							                mdContent={readme || ""}/>
						</div>
					</div>
				)
			}
			{
				!readme && (
					<div className="h-32 border border-base-300 rounded-md w-full">
						<div className="flex justify-center items-center h-full text-neutral-500">
							No ReadMe content available
						</div>
					</div>
				)
			}
		</div>
	);
}

export default AssetReadMeView;
