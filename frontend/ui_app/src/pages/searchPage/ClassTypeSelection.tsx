import React from 'react';
import {ClassType} from './SearchPage'

interface ClassTypeSelectionProps {
	tabs: ClassType[];
	activeTabs: string[];
	setSelectedTabs: (tabs: string[]) => void;
}

const ClassTypeSelection: React.FC<ClassTypeSelectionProps> = ({ tabs, activeTabs, setSelectedTabs }) => {

	const handleMultipleTabs = (tabs: ClassType[]) => {
		// If no tabs are selected, default to 'all'
		if (tabs.length === 0) {
			return ['all'];
		}

		// If any other tabs are selected, remove 'all'
		if (tabs.length >= 1 && tabs.includes('all')) {
			return tabs.filter(tab => tab !== 'all');
		}

		// Return the filtered tabs
		return tabs;
	};

	const handleTabClick = (tabName: string) => {
		// if 'all' tab is selected, deselect all other tabs
		if (tabName === 'all') {
			setSelectedTabs([tabName]);
			return;
		}
		// toggle activeTabs
		const newTabs = activeTabs.includes(tabName) ? activeTabs.filter((tab) => tab !== tabName) : [...activeTabs, tabName];
		setSelectedTabs(handleMultipleTabs(newTabs));
	}

	return (
		<React.Fragment>
			{tabs.map((tab) => (
				<button
					key={tab.name}
					type="button"
					onClick={() => handleTabClick(tab.name)}
					className={`btn rounded-full btn-ghost border border-base-300 shadow-sm font-normal ${activeTabs.includes(tab.name) ? 'bg-base-200 border-secondary text-primary font-semibold' : ''
						}`}
				>
					{tab.icon}
					{tab.label}
				</button>
			))}
		</React.Fragment>
	)
}


export default ClassTypeSelection;
