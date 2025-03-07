import React, { useEffect, useRef } from 'react';

/**
 * Custom hook to simulate componentDidUpdate(), which is invoked immediately after updating occurs. 
 * This method is not called for the initial render.
 * @param callback 
 * @param dependencies 
 */
const useDidMountEffect = (callback: Function, dependencies: any[]) => {
    const didMount = useRef(false);

    useEffect(() => {
        if (didMount.current) callback();
        else didMount.current = true;
    }, dependencies);
}

export default useDidMountEffect;