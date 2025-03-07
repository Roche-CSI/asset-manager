import React, {useEffect, useState} from 'react';
import { ButtonSpinner, FormStatusMessage, PostSaveOptions } from "./FormHelpers";
import {MarkdownEditor} from "components/markDownEditor";
import {isEmptyObject} from "utils";
import {AssetClass} from "servers/asset_server";
import {StoreNames, useStore} from "stores";

interface ReadMeFormProps {
	assetClass: AssetClass;
	initialContent?: string;
	onSave: (content: string) => void;
	onCancel: () => void;
}

export const ReadMeForm: React.FC<ReadMeFormProps> = ({ assetClass, initialContent = '', onSave, onCancel }) => {
	const [content, setContent] = useState(initialContent || '');
	const [error, setError] = useState('');
	const [isUpdating, setIsUpdating] = useState(false);
	const [statusMessage, setStatusMessage] = useState<{
		type: 'success' | 'error' | 'info';
		message: string;
	} | null>(null);
	const [showPostSaveOptions, setShowPostSaveOptions] = useState(false);
	
	const userStore = useStore(StoreNames.userStore);
	
	const handleContentChange = (value: string) => {
		setContent(value);
		if (error) {
			setError('');
		}
	};
	
	const handleSubmit = async (event: React.FormEvent) => {
		event.preventDefault();
		if (content.trim() === '') {
			setError('ReadMe content cannot be empty');
			setStatusMessage({ type: 'error', message: 'Please fix the errors in the form' });
			return;
		}
		
		const data = {readme: content};
		if (!isEmptyObject(data)) {
			data["user"] = userStore.get("user").username;
		}
		setIsUpdating(true);
		setTimeout(() => {
			AssetClass.update(assetClass!.id, data, false).then(res => {
				setIsUpdating(false);
				setStatusMessage({ type: 'success', message: 'Readme updated successfully', data: res });
				setShowPostSaveOptions(true);
			}).catch(error => {
				console.log("error:", error);
				setIsUpdating(false);
				setStatusMessage({
					type: 'error',
					message: 'Error updating asset class: ' + (error.status ? error.status + " " : "") + JSON.stringify(error.data || error)
				});
				setShowPostSaveOptions(false);
			})
		}, 1000);
	};
	
	const handleClose = () => {
		setShowPostSaveOptions(false);
		setStatusMessage(null);
		onSave(content);
	}
	
	return (
		<div className="p-6">
			{!showPostSaveOptions ? (
				<React.Fragment>
					<form onSubmit={handleSubmit} className="">
						<div className="mt-6 border border-base-300 rounded-md">
							<MarkdownEditor mode={"edit"}
							                showTabs={false}
							                onChange={handleContentChange}
							                readOnly={isUpdating}
							                mdContent={content}/>
							{error && <p className="text-red-500 text-xs mt-1">{error}</p>}
						</div>
						<div className="mt-12 flex justify-start space-x-4">
							<button
								type="button"
								onClick={onCancel}
								className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
								disabled={isUpdating}
							>
								Cancel
							</button>
							<button
								type="submit"
								className="px-4 py-2 text-sm font-medium text-white bg-secondary border border-transparent rounded-md shadow-sm hover:bg-primary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
								disabled={isUpdating}
							>
								{isUpdating ? <ButtonSpinner message="Updating..."/> : 'Save'}
							</button>
						</div>
					</form>
					{statusMessage && (
						<FormStatusMessage message={statusMessage.message} type={statusMessage.type}/>
					)}
				</React.Fragment>):
				(
					<PostSaveOptions message={statusMessage?.message as string} onClose={handleClose}/>
				)
			}
		</div>
	);
};
