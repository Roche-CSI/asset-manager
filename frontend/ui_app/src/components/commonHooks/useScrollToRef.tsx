import { useRef, useCallback } from 'react';

type ScrollToOptions = {
    behavior?: ScrollBehavior;
    block?: ScrollLogicalPosition;
};

const useScrollToRef = <T extends HTMLElement>() => {
    const ref = useRef<T | null>(null);

    const scrollToRef = useCallback((options: ScrollToOptions = { behavior: 'smooth', block: 'start' }) => {
        if (ref.current) {
            ref.current.scrollIntoView(options);
        }
    }, []);

    return [ref, scrollToRef] as const;
};

export default useScrollToRef;