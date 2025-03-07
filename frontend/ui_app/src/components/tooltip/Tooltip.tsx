import React, { useState, useMemo } from 'react';
import { CodeBlockIcon } from "../icons";

interface TooltipProps {
    tooltip: string;
    iconClassName?: string;
    tooltipClassName?: string;
    position?: 'top' | 'bottom' | 'left' | 'right';
    CustomIcon?: () => JSX.Element;
    CustomTooltip?: () => JSX.Element;
}

const DefaultIcon: React.FC<{ className?: string }> = ({ className = '' }) => (
    <CodeBlockIcon className={className} />
);

const DefaultTooltip: React.FC<{ tooltip: string, className?: string }> =
    ({ tooltip, className = '' }) => (
        <div className={className}>
            {tooltip}
        </div>
    );

const Tooltip: React.FC<TooltipProps> = ({
    tooltip,
    iconClassName = "",
    tooltipClassName = "",
    position = 'bottom',
    CustomIcon,
    CustomTooltip
}) => {
    const [isHovered, setIsHovered] = useState(false);

    const defaultIconClassName = "h-4 w-4 text-gray-600 hover:text-blue-500";

    const positionClassNames = {
        top: "top-0 left-1/2 transform -translate-x-1/2 -translate-y-full mb-2",
        bottom: "bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full mt-2",
        left: "left-0 top-1/2 transform -translate-x-full -translate-y-1/2 mr-2",
        right: "right-0 top-1/2 transform translate-x-full -translate-y-1/2 ml-2",
    };

    const defaultTooltipClassName = `absolute p-1 z-10 w-auto 
      transition-all duration-1000 ease-in-out 
      ${positionClassNames[position]}`;

    const Icon = useMemo(() => {
        return CustomIcon ? <CustomIcon /> : <DefaultIcon className={`${defaultIconClassName} ${iconClassName}`} />;
    }, [CustomIcon, iconClassName]);

    const TooltipContent = useMemo(() => {
        return CustomTooltip ? <CustomTooltip /> : <DefaultTooltip tooltip={tooltip} className={`${defaultTooltipClassName} ${tooltipClassName}`} />;
    }, [CustomTooltip, tooltip, tooltipClassName]);

    return (
        <div
            className="relative flex items-center"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            <span className="cursor-pointer">
                {Icon}
            </span>
            <div className={`${isHovered ? 'opacity-100' : 'opacity-0'}`}>
                {TooltipContent}
            </div>
        </div>
    );
};

export default Tooltip;