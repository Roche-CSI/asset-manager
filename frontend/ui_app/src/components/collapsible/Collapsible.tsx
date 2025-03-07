import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface CollapsibleProps {
	title: React.ReactNode;
	children: React.ReactNode;
	defaultOpen?: boolean;
	className?: string;
}


const Collapsible: React.FC<CollapsibleProps> = ({ title, children, defaultOpen, className="" }) => {
	const [isOpen, setIsOpen] = useState(defaultOpen ?? false);
	
	const toggleCollapsible = () => {
		setIsOpen(!isOpen);
	};
	const css = className || "mb-2"
	
	return (
		<div className={`${css} cursor-pointer`}>
			<div className={"flex w-full items-center justify-between pl-4 pr-2 pt-2"}
			     onClick={toggleCollapsible}>
				{title}
				<div
					className="ml-auto btn btn-ghost btn-sm"
					onClick={toggleCollapsible}>
					{isOpen ? (
						<ChevronUp className="h-5 w-5 text-gray-500"/>
					) : (
						<ChevronDown className="h-5 w-5 text-gray-500"/>
					)}
				</div>
			</div>
			{isOpen && (
				<div className="p-4 bg-white">
				{children}
				</div>
			)}
		</div>
	);
};

export default Collapsible;
