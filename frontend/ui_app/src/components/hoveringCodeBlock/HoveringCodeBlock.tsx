import React, {useEffect, useRef, useState} from 'react';
import {Code, X, CurlyBraces} from 'lucide-react';
import {CodeBlock, dracula} from "react-code-blocks";

const CodeBox = ({codeVersions}: {codeVersions: Record<string, string>}) => {
	const [currentLanguage, setCurrentLanguage] = useState(Object.keys(codeVersions)[0]);
	const [dimensions, setDimensions] = useState({height: '16rem', width: '100%'});
	const containerRef = useRef(null);
	const measureRef = useRef(null);
	
	useEffect(() => {
		const calculateMaxDimensions = () => {
			const lineHeightPx = 18; // Adjust based on your font size and line height
			let maxLines = 0;
			let longestLine = '';
			
			Object.values(codeVersions).forEach(code => {
				const lines = code.split('\n');
				maxLines = Math.max(maxLines, lines.length);
				const longest = lines.reduce((a, b) => a.length > b.length ? a : b, '');
				if (longest.length > longestLine.length) {
					longestLine = longest;
				}
			});
			
			const calculatedHeight = Math.min(
				maxLines * lineHeightPx,
				window.innerHeight - 200
			);
			
			if (measureRef.current) {
				measureRef.current.textContent = longestLine;
				const measuredWidth = measureRef.current.offsetWidth;
				const maxWidth = window.innerWidth - 80; // Account for right margin and some buffer
				const calculatedWidth = Math.min(measuredWidth + 32, maxWidth);
				
				setDimensions({
					height: `${calculatedHeight}px`,
					width: `${calculatedWidth}px`
				});
			}
		};
		
		calculateMaxDimensions();
		window.addEventListener('resize', calculateMaxDimensions);
		
		return () => window.removeEventListener('resize', calculateMaxDimensions);
	}, [codeVersions]);
	
	return (
		<div className="border rounded-md overflow-hidden bg-white shadow-lg"
		     ref={containerRef}
		     style={{width: dimensions.width}}>
			<div className="bg-gray-100 p-2 flex justify-between items-center">
				<div className="flex space-x-2">
					{Object.keys(codeVersions).map((lang) => (
						<button
							key={lang}
							onClick={() => setCurrentLanguage(lang)}
							className={`px-2 py-1 rounded text-xs ${
								currentLanguage === lang
									? 'bg-blue-500 text-white'
									: 'bg-gray-200 text-gray-700 hover:bg-gray-300'
							}`}
						>
							{lang}
						</button>
					))}
				</div>
			</div>
			<div className="overflow-auto"
			     style={
				     {
					     height: dimensions.height,
					     width: dimensions.width,
					     backgroundColor: 'rgb(40, 42, 54)' // Dracula theme background color
				     }
			     }>
				<CodeBlock
					text={codeVersions[currentLanguage]}
					language={currentLanguage.toLowerCase()}
					showLineNumbers={true}
					theme={dracula}
					customStyle={{
						fontSize: '1rem',
						padding: '0.5rem',
					}}
				/>
			</div>
			<div
				ref={measureRef}
				style={{
					position: 'absolute',
					visibility: 'hidden',
					whiteSpace: 'pre',
					fontSize: '0.75rem',
					fontFamily: 'monospace'
				}}
			/>
		</div>
	);
};

interface HoveringCodeBlockProps {
	codeVersions: Record<string, string>;
	positionClasses?: string;
}

export const HoveringCodeBlock = ({codeVersions, positionClasses}: HoveringCodeBlockProps) => {
	const [isCodeVisible, setIsCodeVisible] = useState(false);
	
	const toggleCodeVisibility = () => {
		setIsCodeVisible(!isCodeVisible);
	};
	
	return (
		<div
			className={`fixed bottom-4 right-4 flex flex-col items-end ${isCodeVisible ? 'pointer-events-auto' : 'pointer-events-none'}`}>
			<div
				className={`absolute bottom-full right-0 mb-2 transition-all duration-300 ease-in-out ${
					isCodeVisible
						? 'opacity-100 translate-y-0 scale-100 pointer-events-auto'
						: 'opacity-0 translate-y-4 scale-95 pointer-events-none'
				}`}
			>
				<CodeBox codeVersions={codeVersions}/>
			</div>
			<button
				onClick={toggleCodeVisibility}
				className="p-2 mr-12 bg-primary rounded-full shadow-lg hover:bg-blue-900 transition-all duration-200 pointer-events-auto"
			>
				{isCodeVisible ? (
					<X className="w-6 h-6 text-white"/>
				) : (
					<CurlyBraces className="w-6 h-6 text-white"/>
				)}
			</button>
		</div>
	);
};
