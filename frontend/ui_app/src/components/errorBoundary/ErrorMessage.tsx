import {AlertCircle} from "lucide-react";
import React from "react";

export const ErrorMessage = ({ message }) => {
	if (!message) return null;
	
	return (
		<div className="bg-red-50 border-x-4 border-red-400 p-4 my-4 rounded-md shadow-sm">
			<div className="flex items-center">
				<AlertCircle className="h-5 w-5 text-red-400 mr-3" />
				<div>
					<p className="text-red-700 font-medium">Error</p>
					<p className="text-red-600 mt-1">{message}</p>
				</div>
			</div>
		</div>
	);
};
