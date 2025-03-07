import React, { useState, useRef, useEffect } from 'react';
import { Menu } from 'lucide-react';
import ReactMarkdown from "react-markdown";
import className = ReactMarkdown.propTypes.className;

interface ActionItem {
	name: string;
	icon: React.ComponentType<{ className?: string }>;
	onClick: () => void;
}

interface DropdownProps {
	title: string;
	actions: ActionItem[];
	className?: string;
}

export const ActionsDropdown: React.FC<DropdownProps> = ({ title="Actions", actions, className="" }) => {
	const [isOpen, setIsOpen] = useState(false);
	const dropdownRef = useRef<HTMLDivElement>(null);
	
	useEffect(() => {
		const handleClickOutside = (event: MouseEvent) => {
			if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
				setIsOpen(false);
			}
		};
		
		document.addEventListener('mousedown', handleClickOutside);
		return () => {
			document.removeEventListener('mousedown', handleClickOutside);
		};
	}, []);
	
	return (
		<div className="relative" ref={dropdownRef}>
			<button
				className={className || "btn btn-sm btn-secondary rounded-md"}
				onClick={() => setIsOpen(!isOpen)}
			>
				<Menu className="h-3.5 w-3.5 mr-2" />
				<span>{title}</span>
			</button>
			{isOpen && (
				<div className="absolute right-0 mt-2 w-36 bg-white rounded-md shadow-lg z-50 border border-gray-200">
					<div className="py-1">
						{actions.map((action) => (
							<button
								key={action.name}
								onClick={() => {
									action.onClick();
									setIsOpen(false);
								}}
								className="flex items-center w-full px-4 py-2 text-xs text-gray-700 hover:bg-gray-100"
							>
								<action.icon className="size-3.5 mr-2" />
								{action.name}
							</button>
						))}
					</div>
				</div>
			)}
		</div>
	);
};
