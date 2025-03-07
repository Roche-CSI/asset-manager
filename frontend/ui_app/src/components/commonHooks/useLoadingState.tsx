import React, { useState } from 'react';

import Spinner from "../spinner/Spinner";
import { Alert } from "../errorBoundary";

export enum DataState {
    not_started,
    fetching,
    completed,
    error
}

interface UseLoadingStateReturn {
    loadingState: {
        data_state: DataState;
        error: string | null;
    };
    startFetchingState: () => void;
    completeFetchingState: () => void;
    catchFetchingError: (error: any) => void;
    fetchingLoader: () => JSX.Element | null;
    fetchingError: () => JSX.Element | null;
}

/**
 * Custom hook to manage loading states and provide a loader component.
 *
 * @returns {UseLoadingStateReturn} An object containing:
 * - `loadingState`: The current state of the loading process.
 * - `startFetchingState`: Function to set the state to fetching.
 * - `completeFetchingState`: Function to set the state to completed.
 * - `catchFetchingError`: Function to set the state to error with an error message.
 * - `loader`: Function to render a spinner component if the state is fetching.
 */
const useLoadingState = (): UseLoadingStateReturn => {
    const [loadingState, setLoadingState] = useState<{ data_state: DataState, error: string | null }>({
        data_state: DataState.not_started,
        error: null
    });

    const startFetchingState = () => {
        setLoadingState({ data_state: DataState.fetching, error: null });
    };

    const completeFetchingState = () => {
        setLoadingState({ data_state: DataState.completed, error: null });
    };

    const catchFetchingError = (error: any) => {
        setLoadingState({ data_state: DataState.error, error: error.toString() });
    };

    const fetchingLoader = (): JSX.Element | null => {
        return loadingState.data_state === DataState.fetching ? <Spinner message={"loading"} /> : null;
    };

    const fetchingError = (): JSX.Element | null => {
        if (loadingState.data_state === DataState.error && loadingState.error) {
            return (
                <Alert variant="error"
                        title="Oh snap! You got an error!"
                        description={[loadingState.error.toString(), "Make sure you are connected to VPN"]}
                />
            );
        }
        return null;
    }

    return {
        loadingState,
        startFetchingState,
        completeFetchingState,
        catchFetchingError,
        fetchingLoader,
        fetchingError
    };
};

export default useLoadingState;