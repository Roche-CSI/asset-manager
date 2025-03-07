import React, { ReactNode } from 'react'
import DefaultHandle from './DefaultHandle';

interface Props {
    open?: boolean;
    value?: string;
    customTrigger?: any;
}

const Trigger = (props: Props) => {

    const defaultTrigger = ({value, open}) =>
        <button className='btn btn-sm border border-base-200 rounded-md'>
            {value ?? 'Select'}
            <DefaultHandle open={open} />
        </button>
    
    const Handle = props.customTrigger ? props.customTrigger : defaultTrigger;

    return (
        <div>
            <Handle value={props.value} open={props.open}/>
        </div>
    )
}

export default Trigger;
