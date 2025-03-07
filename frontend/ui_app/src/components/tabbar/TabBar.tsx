import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Menu } from 'lucide-react';

interface TabItem {
	name: string;
	label: string;
	icon: React.ReactNode;
	link: string;
	floatRight?: boolean;
	disabled?: boolean;  // Add disabled option
	bubble?: {
		text: string;
		color: string;
	};
}

interface TabBarProps {
	tabs: TabItem[];
	activeTab: string;
	onClick?: (name: string) => void;
}

export const TabBar: React.FC<TabBarProps> = ({ tabs, activeTab, onClick }: TabBarProps) => {
	const [rightMenuOpen, setRightMenuOpen] = useState(false);
	const [leftMenuOpen, setLeftMenuOpen] = useState(false);
	
	const leftTabs = tabs.filter(tab => !tab.floatRight);
	const rightTabs = tabs.filter(tab => tab.floatRight);
	
	return (
		<div className="flex w-full items-center">
			{/* Left tabs for extra large screens */}
			<ul className="hidden xl:flex space-x-8">
				{leftTabs.map((tab: TabItem) => (
					<li key={tab.name}>
						<TabLabel tab={tab} active={activeTab === tab.name} onClick={onClick} />
					</li>
				))}
			</ul>
			
			{/* Left menu dropdown for large screens and below */}
			<div className="xl:hidden relative">
				<button onClick={() => setLeftMenuOpen(!leftMenuOpen)} className="p-2">
					<Menu size={24} />
				</button>
				{leftMenuOpen && (
					<div className="absolute left-0 top-full mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-10">
						<div className="py-1" role="menu" aria-orientation="vertical" aria-labelledby="options-menu">
							{leftTabs.map((tab) => (
								<TabLabel key={tab.name} tab={tab} active={activeTab === tab.name} onClick={(name) => { onClick && onClick(name); setLeftMenuOpen(false); }} />
							))}
						</div>
					</div>
				)}
			</div>
			
			{/* Right menu dropdown for extra large screens and below */}
			{
				rightTabs.length > 0 && (
					<div className="ml-auto relative">
						<button onClick={() => setRightMenuOpen(!rightMenuOpen)} className="2xl:hidden p-2">
							<Menu size={24}/>
						</button>
						{rightMenuOpen && (
							<div
								className="absolute right-0 top-full mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-1">
								<div className="py-1" role="menu" aria-orientation="vertical"
								     aria-labelledby="options-menu">
									{rightTabs.map((tab) => (
										<TabLabel key={tab.name} tab={tab} active={activeTab === tab.name}
										          onClick={(name) => {
											          onClick && onClick(name);
											          setRightMenuOpen(false);
										          }}/>
									))}
								</div>
							</div>
						)}
					</div>
				)
			}
			
			{/* Right tabs for 2xl screens */}
			{
				rightTabs.length > 0 && (
					<ul className="hidden 2xl:flex space-x-8 ml-auto">
						{rightTabs.map((tab: TabItem) => (
							<li key={tab.name}>
								<TabLabel tab={tab} active={activeTab === tab.name} onClick={onClick} floatRight={true}/>
							</li>
						))}
					</ul>
				)
			}
		</div>
	);
}

interface TabLabelProps {
	tab: TabItem;
	active: boolean;
	onClick?: (name: string) => void;
	floatRight?: boolean;
}

// Update the TabItem interface
interface TabItem {
	name: string;
	label: string;
	icon: string;
	link: string;
	floatRight?: boolean;
	disabled?: boolean;  // Add disabled option
	bubble?: {
		text: string;
		color: string;
	};
}

// Rest of the code remains the same until TabLabel component

const TabLabel: React.FC<TabLabelProps> = ({tab, active, onClick, floatRight=false}) => {
	if (tab.disabled) {
		return (
			<div
				className={`cursor-not-allowed opacity-50 py-2 ${floatRight ? "pl-4" : "pr-4"} flex`}
				title="This option is currently disabled"
			>
                <span className="relative flex items-center justify-center">
                    {tab.icon}
	                {tab.label && <span className="text-sm">{tab.label}</span>}
	                {tab.bubble && (
		                <span
			                className={`absolute -top-2 -right-4 flex items-center justify-center w-4 h-4 text-[10px] font-semibold rounded-full ${tab.bubble.color} shadow-sm`}
		                >
                            {tab.bubble.text}
                        </span>
	                )}
                </span>
			</div>
		);
	}
	
	return (
		<Link
			to={tab.link}
			className={`flex box-border hover:no-underline hover:text-blue-500 py-2 
				${floatRight ? "pl-4" : "pr-4"} 
				${active ? 'border-b-2 border-gray-600 font-bold' : 'border-b-2 border-transparent'}
				`}
			onClick={() => onClick && onClick(tab.name)}
		>
            <span className="flex items-center justify-center">
                {tab.icon}
	            <span className="text-sm">{tab.label}</span>
	            {tab.bubble && (
		            <span
			            className={`mb-2 ml-1 bottom-1 left-1 flex items-center justify-center w-4 h-4 text-[10px] font-semibold rounded-full ${tab.bubble.color} shadow-sm`}
		            >
                        {tab.bubble.text}
                    </span>
	            )}
            </span>
		</Link>
	);
}
