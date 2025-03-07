import React, { ReactNode } from "react";


interface PopOverProps {
    popOver: ReactNode;
    trigger: ReactNode;
    placement: "top" | "right" | "bottom" | "left";
    className?: string;
}


const HoverPopOver = (props: PopOverProps) => {
    const positionClassName = (placement: string) => {
        switch (placement) {
            case "top":
                return `absolute bottom-full left-1/2 z-20 p-1 -translate-x-1/2 whitespace-nowrap rounded hidden group-hover:block ${props.className}`;
            case "right":
                return `absolute left-full top-1/2 z-20 p-1 -translate-y-1/2 whitespace-nowrap rounded hidden group-hover:block ${props.className}`;
            case "bottom":
                return `absolute top-full left-1/2 z-20 p-1 -translate-x-1/2 whitespace-nowrap rounded hidden group-hover:block ${props.className}`;
            case "left":
                return `absolute right-full top-1/2 z-20 p-1 -translate-y-1/2 whitespace-nowrap rounded hidden group-hover:block ${props.className}`;
        }
    }

    const markerClassName = (placement: string) => {
        switch (placement) {
            case "top":
                return `absolute bottom-[-1px] left-1/2 -z-10 
                w-0 h-0
                border-x-[3px] border-x-transparent
                border-t-[6px] border-t-black-500`;
            case "right":
                return `absolute left-[-1px] top-1/2 -z-10 
                w-0 h-0 
                border-y-[4px] border-y-transparent
                border-r-[8px] border-r-black-500`;
            case "bottom":
                return `absolute top-[-1px] left-1/2 -z-10 
                w-0 h-0 
                border-x-[3px] border-x-transparent
                border-b-[6px] border-b-black-500`;
            case "left":
                return `absolute right-[-1px] top-1/2 -z-10
                w-0 h-0 
                border-y-[3px] border-y-transparent
                border-l-[7px] border-l-black-500`;
        }
    }


    return (
        <div className='group relative inline-block'>
            {props.trigger}
            <div className={positionClassName(props.placement)}>
                <span className={markerClassName(props.placement)}></span>
                {props.popOver}
            </div>
        </div>
    )

}

export default HoverPopOver;