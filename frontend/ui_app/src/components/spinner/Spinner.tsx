import React from "react";

const Spinner: React.FC<{message: string}> = ({message="Loading..."}) => (
	<div className="flex items-center justify-center h-full w-full">
		<div className="flex flex-col items-center justify-center space-y-4">
			<div className="relative">
				<div className="w-12 h-12 rounded-full border-t-4 border-b-4 border-blue-500 animate-spin"></div>
				<div className="w-12 h-12 rounded-full border-r-4 border-l-4 border-blue-300 animate-spin absolute top-0 left-0"></div>
			</div>
			<div className="text-blue-500 text-lg font-semibold animate-pulse">
				{message}
			</div>
		</div>
	</div>
);

export default Spinner;
