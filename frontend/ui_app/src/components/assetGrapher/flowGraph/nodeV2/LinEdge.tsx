import React from 'react';
import { getSmoothStepPath } from 'reactflow';

interface LinEdgeProps {
	id: string;
	sourceX: number;
	sourceY: number;
	targetX: number;
	targetY: number;
	sourcePosition: any;
	targetPosition: any;
	style?: React.CSSProperties;
	arrowHeadType?: string;
	markerEndId: string;
}

export const LinEdge = ({
	                        id,
	                        sourceX,
	                        sourceY,
	                        targetX,
	                        targetY,
	                        sourcePosition,
	                        targetPosition,
	                        style = {},
	                        markerEndId,
                        }: LinEdgeProps) => {
	const [edgePath] = getSmoothStepPath({
		sourceX,
		sourceY,
		sourcePosition,
		targetX,
		targetY,
		targetPosition,
	});
	
	const defaultStyle = {
		strokeWidth: 1.5,
		stroke: '#94a3b8', // Tailwind's gray-400
		...style,
	};
	
	return (
		<>
			<path
				id={id}
				style={defaultStyle}
				className="react-flow__edge-path"
				d={edgePath}
				markerEnd={markerEndId ? `url(#${markerEndId})` : undefined}
			/>
			{markerEndId && (
				<marker
					id={markerEndId}
					markerWidth="12"
					markerHeight="12"
					refX="6"
					refY="6"
					orient="auto"
					markerUnits="userSpaceOnUse"
				>
					<path
						d="M0,1 L0,11 L10,6 z"
						fill="#94a3b8" // Matching the edge color
						transform="translate(1,0)"
					/>
				</marker>
			)}
		</>
	);
};
