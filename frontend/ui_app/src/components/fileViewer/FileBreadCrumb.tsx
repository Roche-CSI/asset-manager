import React from 'react';
import { ChevronRight, Folder, Home, File } from "lucide-react";

interface BreadcrumbProps {
	path: string;
	onClick: (path: string) => void;
	separator?: React.ReactNode;
	className?: string;
	showRoot?: boolean;
}

const FileBreadCrumb: React.FC<BreadcrumbProps> = ({
	                                                   showRoot = true,
	                                                   path,
	                                                   onClick,
	                                                   separator = <ChevronRight className="w-4 h-4 mx-2 text-gray-400 flex-shrink-0" />,
	                                                   className = ""
                                                   }) => {
	const parts = path ? path.split('/') : [];
	
	return (
		<nav className={`flex items-end text-sm font-medium ${className}`}>
			{showRoot && (
				<React.Fragment>
					<div
						className="flex text-xs items-center px-2 py-0.5 space-x-1 text-blue-600 bg-blue-100 rounded-md cursor-pointer hover:bg-blue-200 transition-colors duration-200"
						onClick={() => onClick('')}>
						<Home className="size-3" />
						<span>asset</span>
					</div>
					<span className="ml-1">
						{separator}
					</span>
				</React.Fragment>
			)}
			<div className="flex items-end overflow-hidden">
				{parts.map((part, index) => (
					<React.Fragment key={index}>
						{
							index > 0 &&
                            <span className="mr-1">{separator}</span>
						}
						{index === parts.length - 1 ? (
							<div className="flex text-xs items-center px-2 py-0.5 space-x-1">
								<File className="size-3"/>
								<span className="font-semibold text-neutral-600">{part}</span>
							</div>
						) : (
							<div
								className="flex items-end space-x-1 rounded-md cursor-pointer hover:bg-gray-100 transition-colors duration-200"
								onClick={() => onClick(parts.slice(0, index + 1).join('/'))}
							>
								<div className="flex text-xs items-center px-2 py-0.5 space-x-1 rounded-md">
									<Folder className="size-3 text-yellow-500"/>
									<span className="text-blue-600 hover:underline">{part}</span>
								</div>
							</div>
						)}
					</React.Fragment>
				))}
			</div>
		</nav>
	);
};

export default FileBreadCrumb;
