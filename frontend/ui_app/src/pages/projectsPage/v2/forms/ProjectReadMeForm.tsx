import React, {useState} from 'react';
import {MarkdownEditor} from "components/markDownEditor";
import {ProjectData} from "../../../../servers/asset_server/project";
import {StoreNames, useStore} from "stores";
import {isEmptyObject} from "utils";
import {Project} from "servers/asset_server";

type StatusMessageType = 'success' | 'error' | 'info';

interface ReadMeFormProps {
	project: ProjectData;
	initialContent?: string;
	onSave: (content: string) => void;
	onCancel: () => void;
}

interface FormStatusMessageProps {
	message: string;
	type: StatusMessageType;
}

interface StatusMessage {
	type: StatusMessageType;
	message: string;
}

const FormStatusMessage: React.FC<FormStatusMessageProps> = ({message, type}) => {
	const backgroundColors = {
		error: 'bg-red-50 text-red-700',
		success: 'bg-green-50 text-green-700',
		info: 'bg-blue-50 text-blue-700'
	};
	
	return (
		<div className={`p-4 rounded-md ${backgroundColors[type]}`}>
			<p className="text-sm font-medium">{message}</p>
		</div>
	);
};

const ButtonSpinner: React.FC<{ message: string }> = ({message}) => (
	<span className="flex items-center">
        <svg
	        className="w-5 h-5 mr-2 animate-spin"
	        xmlns="http://www.w3.org/2000/svg"
	        fill="none"
	        viewBox="0 0 24 24"
        >
            <circle
	            className="opacity-25"
	            cx="12"
	            cy="12"
	            r="10"
	            stroke="currentColor"
	            strokeWidth="4"
            />
            <path
	            className="opacity-75"
	            fill="currentColor"
	            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
        </svg>
		{message}
    </span>
);

const PostSaveOptions: React.FC<{ message: string; onClose: () => void }> = ({
	                                                                             message,
	                                                                             onClose
                                                                             }) => (
	<div className="space-y-4">
		<div className="p-4 rounded-md bg-green-50 text-green-700">
			<p className="text-sm font-medium">{message}</p>
		</div>
		<button
			onClick={onClose}
			className="px-4 py-2 text-sm font-medium text-white bg-secondary border border-transparent rounded-md shadow-sm hover:bg-primary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
		>
			Close
		</button>
	</div>
);

export const ProjectReadMeForm: React.FC<ReadMeFormProps> = ({
	                                                             project,
	                                                             initialContent,
	                                                             onSave,
	                                                             onCancel
                                                             }) => {
	const [content, setContent] = useState(initialContent || '');
	const [error, setError] = useState('');
	const [isUpdating, setIsUpdating] = useState(false);
	const [statusMessage, setStatusMessage] = useState<StatusMessage | null>(null);
	const [showPostSaveOptions, setShowPostSaveOptions] = useState(false);
	
	const userStore = useStore(StoreNames.userStore);
	
	const handleContentChange = (value: string) => {
		setContent(value);
		if (error) {
			setError('');
		}
	};
	
	const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		
		if (content.trim() === '') {
			setError('ReadMe content cannot be empty');
			setStatusMessage({
				type: 'error',
				message: 'Please fix the errors in the form'
			});
			return;
		}
		
		if (content === initialContent) {
			setStatusMessage({
				type: 'info',
				message: 'No changes detected'
			});
			return;
		}
		
		const data: Record<string, string> = {readme: content};
		if (!isEmptyObject(data)) {
			data.modified_by = userStore.get("user").username;
		}
		updateProject(data);
	};
	
	const updateProject = (data: object) => {
		setIsUpdating(true);
		Project.update(project.id!, userStore.get("user").username, data, false).then((res: any) => {
		    setContent(res.readme);
		    setIsUpdating(false);
		    setStatusMessage({ type: 'success', message: 'Project readme updated successfully' });
		    setShowPostSaveOptions(true);
		}).catch((error: any) => {
		    console.error("Error updating project:", error);
		    setIsUpdating(false);
		    setStatusMessage({
		        type: 'error',
		        message: 'Error updating project: ' + (error.status ? error.status + " " : "") + JSON.stringify(error.data || error)
		    });
		});
	}
	
	const handleClose = () => {
		setShowPostSaveOptions(false);
		setStatusMessage(null);
		onSave(content);
	};
	
	return (
		<div className="p-6">
			{!showPostSaveOptions ? (
				<>
					<form onSubmit={handleSubmit} className="space-y-6">
						<div className="border border-base-300 rounded-md">
							<MarkdownEditor
								mode="edit"
								showTabs={false}
								onChange={handleContentChange}
								readOnly={isUpdating}
								mdContent={content}
							/>
							{error && (
								<p className="text-red-500 text-xs mt-1">{error}</p>
							)}
						</div>
						<div className="flex justify-start space-x-4">
							<button
								type="button"
								onClick={onCancel}
								disabled={isUpdating}
								className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
							>
								Cancel
							</button>
							<button
								type="submit"
								disabled={isUpdating}
								className="px-4 py-2 text-sm font-medium text-white bg-secondary border border-transparent rounded-md shadow-sm hover:bg-primary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
							>
								{isUpdating ? (
									<ButtonSpinner message="Updating..."/>
								) : (
									'Save'
								)}
							</button>
						</div>
					</form>
					{statusMessage && (
						<div className="mt-4">
							<FormStatusMessage
								message={statusMessage.message}
								type={statusMessage.type}
							/>
						</div>
					)}
				</>
			) : (
				<PostSaveOptions
					message={statusMessage?.message || ''}
					onClose={handleClose}
				/>
			)}
		</div>
	);
};
