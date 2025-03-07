import React from "react";

export const ButtonSpinner: React.FC<{ message: string }> = ({message = "Updating..."}) => {
	return (
		<span className="flex items-center">
                <svg className="w-5 h-5 mr-2 animate-spin"
                     xmlns="http://www.w3.org/2000/svg"
                     fill="none"
                     viewBox="0 0 24 24">
                    <circle className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4">
                    </circle>
                    <path className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                    </path>
                </svg>
			{message}
            </span>
	)
}

interface PostSaveOptionsProps {
	message: string,
	onClose: (data: any) => void,
	data?: any
}

export const PostSaveOptions: React.FC<PostSaveOptionsProps> = ({message, onClose, data = null}) => {
	return (
		<div className="space-y-4">
			<div className="p-4 rounded-md bg-green-50 text-green-700">
				<p className="text-sm font-medium">{message}</p>
			</div>
			<button
				onClick={() => onClose(data)}
				className="px-4 py-2 text-sm font-medium text-white bg-secondary border border-transparent rounded-md shadow-sm hover:bg-primary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
				Close
			</button>
		</div>
	)
}

interface FormStatusMessageProps {
	message: string,
	type: 'success' | 'error' | 'info'
}

export const FormStatusMessage: React.FC<FormStatusMessageProps> = ({message, type}) => {
	return (
		<div
			className={`p-4 rounded-md ${type === 'error' ? 'bg-red-50 text-red-700' :
				type === 'success' ? 'bg-green-50 text-green-700' : 'bg-blue-50 text-blue-700'}`}>
			<p className="text-sm font-medium">{message}</p>
		</div>
	)
}
