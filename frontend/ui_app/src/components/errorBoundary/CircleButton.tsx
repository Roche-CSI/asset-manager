import React from 'react';
import {LucideIcon} from 'lucide-react';

interface CircularButtonProps {
	icon: LucideIcon;
	onClick: () => void;
	size?: 'sm' | 'md' | 'lg';
	color?: 'primary' | 'secondary' | 'success' | 'danger';
	disabled?: boolean;
}

const CircleButton: React.FC<CircularButtonProps> = ({
	                                                     icon: Icon,
	                                                     onClick,
	                                                     size = 'md',
	                                                     color = 'primary',
	                                                     disabled = false,
                                                     }) => {
	const sizeClasses = {
		sm: 'w-8 h-8',
		md: 'w-12 h-12',
		lg: 'w-16 h-16',
	};
	
	const colorClasses = {
		primary: 'bg-blue-500 hover:bg-blue-600 focus:ring-blue-300',
		secondary: 'bg-gray-500 hover:bg-gray-600 focus:ring-gray-300',
		success: 'bg-green-500 hover:bg-green-600 focus:ring-green-300',
		danger: 'bg-red-500 hover:bg-red-600 focus:ring-red-300',
	};
	
	const iconSizes = {
		sm: 16,
		md: 24,
		lg: 32,
	};
	
	return (
		<button
			onClick={onClick}
			disabled={disabled}
			className={`
        ${sizeClasses[size]}
        ${colorClasses[color]}
        rounded-full
        flex
        items-center
        justify-center
        text-white
        focus:outline-none
        focus:ring-2
        focus:ring-offset-2
        transition-colors
        duration-200
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}>
			<Icon size={iconSizes[size]}/>
		</button>
	);
};

export default CircleButton;
