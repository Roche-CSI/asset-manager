import React, { useState } from "react";
import { ChevronDown } from "lucide-react";

export const Dropdown = ({ children, onSelect, value }) => {
	const [isOpen, setIsOpen] = useState(false);
	
	const validChildren = React.Children.toArray(children).filter(child => React.isValidElement(child));
	
	if (validChildren.length === 0) {
		return null;  // Or return a placeholder component
	}
	
	return (
		<div className="relative inline-block text-left">
			<div>
				<button
					type="button"
					className="inline-flex justify-center w-full rounded-md border border-gray-300 px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
					onClick={() => setIsOpen(!isOpen)}
				>
					{value}
					<ChevronDown className="-mr-1 ml-2 h-5 w-5" aria-hidden="true" />
				</button>
			</div>
			
			{isOpen && (
				<div className="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5">
					<div className="py-1" role="menu" aria-orientation="vertical" aria-labelledby="options-menu">
						{validChildren.map((child, index) =>
							React.cloneElement(child, {
								key: index,
								onClick: () => {
									onSelect(child.props.eventKey);
									setIsOpen(false);
								}
							})
						)}
					</div>
				</div>
			)}
		</div>
	);
};

export const DropdownItem = ({ children, onClick }) => (
	<a
		href="#"
		className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
		role="menuitem"
		onClick={(e) => {
			e.preventDefault();
			onClick();
		}}
	>
		{children}
	</a>
);
