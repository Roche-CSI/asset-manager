import React from 'react';
import { Link } from 'react-router-dom';
import { Home, ChevronRight } from 'lucide-react';

const BreadcrumbItem = ({ children, url, isLast = false }) => {
	const commonClasses = "flex items-center text-sm font-medium transition-colors duration-200";
	const classes = isLast
		? `${commonClasses} text-primary`
		: `${commonClasses} text-gray-500 hover:text-blue-600`;
	
	return isLast ? (
		<span className={classes}>{children}</span>
	) : (
		<Link to={url} className={classes}>{children}</Link>
	);
};

export const BreadCrumbV2 = ({ items }) => {
	return (
		<nav aria-label="Breadcrumb" className="flex">
			<ol className="flex items-center space-x-1">
				<li>
					<BreadcrumbItem url="/">
						<Home className="w-4 h-4 mr-1" />
						<span className="sr-only">Home</span>
					</BreadcrumbItem>
				</li>
				{items.map((item, index) => (
					<li key={index} className="flex items-center">
						<ChevronRight className="size-3 text-base-400 mx-1" />
						<BreadcrumbItem url={item.url} isLast={index === items.length - 1}>
							{item.label}
						</BreadcrumbItem>
					</li>
				))}
			</ol>
		</nav>
	);
};
