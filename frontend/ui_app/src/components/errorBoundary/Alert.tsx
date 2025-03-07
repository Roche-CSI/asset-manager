import React from "react";
import { CheckCircle, XCircle, AlertCircle } from "lucide-react";

interface AlertProps {
	variant: 'success' | 'error' | 'warning';
	title: string;
	description?: string[];
	icon?: React.ReactNode;
}

export const Alert: React.FC<AlertProps> = ({ variant, title, description = [], icon }) => {
	
	const [show, setShow] = React.useState(true);
	
	const getAlertStyle = () => {
		switch (variant) {
			case 'success':
				return "bg-green-50 border-green-200 text-green-800";
			case 'error':
				return "bg-red-50 border-red-200 text-red-800";
			case 'warning':
				return "bg-yellow-50 border-yellow-200 text-yellow-800";
			default:
				return "";
		}
	};
	
	const Icon = icon || (
		variant === 'success' ? <CheckCircle className="size-5" /> :
			variant === 'error' ? <XCircle className="size-5" /> :
				<AlertCircle className="size-5" />
	);
	
	if (!show) {
		return null;
	}
	
	return (
		<div className={`flex items-start p-4 rounded-lg border-x-8 border ${getAlertStyle()}`} role="alert">
			<div className="flex-shrink-0 mr-3">
				<button onClick={() => setShow(false)}
				        aria-label="Close"
				        className={`btn btn-sm btn-ghost rounded-full`}>
					{Icon}
				</button>
			</div>
			<div>
				<h3 className="font-semibold text-lg">{title}</h3>
				<p className="text-sm flex space-x-4 mt-1">
					{
						description.map((desc, index) => (
						<span key={index}>{desc}</span>))
					}
				</p>
			</div>
		</div>
	);
};
