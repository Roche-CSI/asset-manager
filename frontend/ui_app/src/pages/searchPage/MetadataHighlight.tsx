import React from 'react';
import {ChevronUp, ChevronDown} from 'lucide-react';

export const FormatHighlight = ({text}: { text: string }) => {
	if (!text) return null;
	const sections = text.split(/(<em>.*?<\/em>)/);
	return (
		<span className="inline">
            {sections.map((section, sectionIndex) => {
	            if (section.startsWith('<em>') && section.endsWith('</em>')) {
		            const innerText = section.replace(/<\/?em>/g, '');
		            return (
			            <span key={`${sectionIndex}`}
			                  className="bg-yellow-200 text-gray-900 px-1 py-0.5 rounded-sm font-medium">
                            {innerText}
                        </span>
		            );
	            }
	            return <React.Fragment key={`${sectionIndex}`}>{section}</React.Fragment>;
            })}
        </span>
	);
}

const RenderValue = ({value}) => {
	const RenderText = ({value}) => (
		<FormatHighlight text={value}/>
	);
	
	const RenderArray = ({value}) => (
		<div className="flex flex-wrap gap-2">
			{value.map((val, index) => (
				<span
					key={index}
					className="inline-flex items-center px-2 py-1 rounded-full bg-blue-50 text-blue-700 text-xs"
				>
                    {typeof val === 'object' ? (
	                    <div className="space-y-1">
		                    {Object.entries(val).map(([k, v]) => (
			                    <div key={k} className="flex items-center gap-1">
				                    <span className="text-blue-500 font-medium">{k}:</span>
				                    <RenderText value={v}/>
			                    </div>
		                    ))}
	                    </div>
                    ) : (
	                    <RenderText value={val}/>
                    )}
                </span>
			))}
		</div>
	);
	
	const RenderObject = ({value}) => (
		<div className="space-y-2">
			{Object.entries(value).map(([k, v]) => (
				<div key={k} className="flex items-start gap-2">
					<span className="text-gray-500 font-medium min-w-24">{k}:</span>
					<span className="flex-1">
                        <RenderValue value={v}/>
                    </span>
				</div>
			))}
		</div>
	);
	
	if (Array.isArray(value)) return <RenderArray value={value}/>;
	if (typeof value === "object" && value !== null) return <RenderObject value={value}/>;
	return <RenderText value={value}/>;
};

export const MetadataHighlight = ({item, highlightKeys}) => {
	const [showMetadata, setShowMetadata] = React.useState(true);
	const metadataKeys = highlightKeys.filter(key => key.startsWith("metadata"));
	
	if (metadataKeys.length === 0 || !item.metadata) return null;
	
	const displayData = {};
	metadataKeys.forEach(key => {
		if (item.es_highlight && item.es_highlight[key]) {
			const parts = key.split('.');
			const displayKey = parts.splice(1, parts.length - 2).join('.');
			displayData[displayKey] = item.es_highlight[key];
		}
	});
	
	if (Object.keys(displayData).length === 0) return null;
	
	return (
		<div className="mt-4 border-t border-base-200">
			<button
				onClick={() => setShowMetadata(!showMetadata)}
				className="w-full py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
			>
                <span className="text-xs font-medium text-gray-500 flex items-center gap-2">
                    <span>Metadata</span>
                    <span className="px-2 py-0.5 text-xs rounded-full bg-blue-50 text-blue-600">
                        {Object.keys(displayData).length} matches
                    </span>
                </span>
				{showMetadata ? (
					<ChevronUp className="size-4 text-gray-400"/>
				) : (
					<ChevronDown className="size-4 text-gray-400"/>
				)}
			</button>
			
			{showMetadata && (
				<div className="px-2 space-y-4">
					{Object.entries(displayData).map(([key, value]) => (
						<div key={key} className="flex gap-2 items-center">
                            <span className="text-xs font-medium text-gray-700">
                                 - {key}:
                            </span>
							<div className="text-xs text-gray-600">
								<RenderValue value={value}/>
							</div>
						</div>
					))}
				</div>
			)}
		</div>
	);
};
