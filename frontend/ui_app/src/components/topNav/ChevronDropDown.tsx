import React, { useEffect, useRef, useState } from 'react';
import { ChevronDown } from 'lucide-react';

interface ChevronDropdownProps {
	label?: string;
	children: React.ReactNode;
	trigger?: React.ReactElement;
	className?: string;
	buttonClassName?: string;
	dropdownClassName?: string;
}

export const ChevronDropdown: React.FC<ChevronDropdownProps> = ({
	label,
	children,
	trigger,
	className = '',
	buttonClassName = '',
	dropdownClassName = '',
}) => {
	const [isOpen, setIsOpen] = useState(false);
	const dropdownRef = useRef<HTMLDivElement>(null);

	const defaultButtonClass = "inline-flex justify-center w-full bg-transparent";
	const combinedButtonClass = `${defaultButtonClass} ${buttonClassName}`.trim();

	const defaultDropdownClass = "absolute mt-2 w-56 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-50 focus:outline-none transition-all duration-200 ease-in-out";
	const combinedDropdownClass = `${defaultDropdownClass} ${dropdownClassName}`.trim();

	const toggleOpen = () => setIsOpen(prevState => !prevState);

	const triggerElement = trigger ? React.cloneElement(trigger, {
		onClick: (e: React.MouseEvent) => {
			trigger.props.onClick && trigger.props.onClick(e);
			toggleOpen();
		},
	}) : null;

	useEffect(() => {
		const handleOutsideClick = (event: MouseEvent) => {
			if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
				setIsOpen(false);
			}
		};

		document.addEventListener('mousedown', handleOutsideClick);
		return () => {
			document.removeEventListener('mousedown', handleOutsideClick);
		};
	}, []);

	return (
		<div className={`inline-block text-left ${className}`.trim()} ref={dropdownRef}>
			<div>
				{trigger ? triggerElement :
					<button
						type="button"
						className={combinedButtonClass}
						onClick={toggleOpen}>
						{label}
						<ChevronDown
							className={`ml-2 -mr-1 h-5 w-5 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''
								}`}
							aria-hidden="true"
						/>
					</button>
				}
			</div>

			<div
				className={`
          ${combinedDropdownClass}
          ${isOpen
						? 'transform opacity-100 scale-100 duration-500 ease-in'
						: 'transform opacity-0 scale-95 pointer-events-none'}
        `}
			>
				<div className="py-1" role="menu" aria-orientation="vertical" aria-labelledby="options-menu" onClick={toggleOpen}>
					{children}
				</div>
			</div>
		</div>
	);
};

