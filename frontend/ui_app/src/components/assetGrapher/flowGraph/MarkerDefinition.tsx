//ref: https://github.com/wbkd/react-flow/issues/915
import React, { ReactNode } from 'react'

interface MarkerProps {
    id: string
    className?: string
    children: ReactNode
}

const Marker = ({ id, className, children }: MarkerProps) => (
    <marker
        className={className || 'react-flow__arrowhead'}
        id={id}
        markerWidth="30"
        markerHeight="15"
        viewBox="-40 -10 40 20"
        orient="auto"
        markerUnits="userSpaceOnUse"
        refX="0"
        refY="0"
    >
        {children}
    </marker>
)

interface MarkerDefinitionsProps {
    id: string
    color: string
}

export default function MarkerDefinition({ color, id }: MarkerDefinitionsProps) {
    return (
        <svg>
            <defs>
                <Marker id={id}>
                    <polyline
                        stroke={color}
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="1"
                        fill={color}
                        points="-12,-6 0,0 -12,6 -12,-6"
                    />
                </Marker>
            </defs>
        </svg>
    )
}