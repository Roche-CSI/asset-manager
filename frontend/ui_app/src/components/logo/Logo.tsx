import React from 'react';

interface LogoProps {
	width?: number;
	height?: number;
	className?: string;
}

export const Logo: React.FC<LogoProps> = ({ width = 72, height = 72, className = '' }) => {
	return (
		<svg
			width={width}
			height={height}
			viewBox="0 0 72 72"
			fill="none"
			xmlns="http://www.w3.org/2000/svg"
			className={className}
			aria-label="Brand Logo"
		>
			<path
				fillRule="evenodd"
				clipRule="evenodd"
				d="M56 61H49L30 25V12L30.233 12.4351L56 61Z"
				fill="#3294FF"
			/>
			<path
				fillRule="evenodd"
				clipRule="evenodd"
				d="M69 61H62L43 25V12L43.233 12.4351L69 61Z"
				fill="#007AFF"
			/>
			<path
				fillRule="evenodd"
				clipRule="evenodd"
				d="M4 61H11L30 25V17.578V12L4 61Z"
				fill="#AECBFA"
			/>
			<path
				fillRule="evenodd"
				clipRule="evenodd"
				d="M17 61H24L43 25V12L42.767 12.4427L17 61Z"
				fill="#007AFF"
			/>
			<path
				d="M37 50L31 61H43L37 50Z"
				fill="#007AFF"
			/>
		</svg>
	);
};

