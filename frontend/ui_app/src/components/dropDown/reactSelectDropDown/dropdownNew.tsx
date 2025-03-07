import React, { useRef, ReactNode } from 'react'
import { useOutsideClick } from "../../commonHooks";
import useOpen from './useOpen';
import Trigger from './Trigger';
import Menu from './Menu';

interface DropDownProps {
    value?: string;
    items?: ReactNode[];
    customTrigger?: any;
    customMenu?: ReactNode;
    className?: string;
}

const DropDownNew = (props: DropDownProps) => {
    const { open, handleOpen, handleOutsideClick } = useOpen()
    const triggerRef = useRef<HTMLInputElement>(null)

    /** Handle outside click */
    useOutsideClick(triggerRef, handleOutsideClick)

    return (
        <div className='relative'>
            <div
                ref={triggerRef}
                onClick={handleOpen}
            >
                <Trigger open={open} value={props.value} customTrigger={props.customTrigger}/>
            </div>
            <div
                className={`absolute right-0 z-9999 space-y-1 border border-stroke bg-white p-1.5 shadow-default dark:border-strokedark dark:bg-boxdark ${
                    open === true ? 'block' : 'hidden'
                } ${props.className && props.className}`}
            >
                <Menu items={props.items} customMenu={props.customMenu}/>
            </div>
        </div>
        // <div className="overflow-hidden origin-top-right scale-0 transition-transform duration-300 ease-linear">
        //     <div className='relative inline-block'>
        //         <div
        //             ref={triggerRef}
        //             onClick={handleOpen}
        //         >
        //             <Trigger open={open} value={props.value} customTrigger={props.customTrigger}/>
        //         </div>
        //         <div
        //             className={`absolute right-0 z-9999 w-24 space-y-1 border border-stroke bg-white p-1.5 shadow-default dark:border-strokedark dark:bg-boxdark ${
        //                 open === true ? 'block' : 'hidden'
        //             } ${props.className && props.className}`}
        //         >
        //             <Menu items={props.items} customMenu={props.customMenu}/>
        //         </div>
        //     </div>
        // </div>
    )
}

export default DropDownNew;
