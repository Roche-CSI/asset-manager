import React, { useState, useReducer } from "react";
import { Alert } from "../../components/errorBoundary";
import { StoreNames, useStore } from "../../stores";
import { ErrorBoundary } from "../../components/errorBoundary";
import { fetchPost } from "../../servers/base";
import AssetURLs from "../../servers/asset_server/assetURLs";
import IssueTrackerFormV2, { repos } from "./IssueTrackerFormV2";
import useLoadingState, { DataState } from "../../components/commonHooks/useLoadingState";

interface FormState {
    title?: string;
    description?: string;
}

interface IssueTrackerState {
    validated: boolean;
    formData: FormState;
    formErrors: FormState;
}

const initialState: IssueTrackerState = {
    validated: false,
    formData: {
        title: '',
        description: '',
    },
    formErrors: {},
};

type Action =
    | { type: 'SET_VALIDATED'; payload: boolean }
    | { type: 'SET_FORM_DATA'; payload: Partial<FormState> }
    | { type: 'SET_FORM_ERRORS'; payload: Partial<FormState> };

function reducer(state: IssueTrackerState, action: Action): IssueTrackerState {
    switch (action.type) {
        case 'SET_VALIDATED':
            return { ...state, validated: action.payload };
        case 'SET_FORM_DATA':
            return { ...state, formData: { ...state.formData, ...action.payload } };
        case 'SET_FORM_ERRORS':
            return { ...state, formErrors: { ...state.formErrors, ...action.payload } };
        default:
            return state;
    }
}

export default function IssueTracker() {
    const userStore = useStore(StoreNames.userStore);
    const [state, dispatch] = useReducer(reducer, initialState);
    const {
        loadingState,
        startFetchingState,
        completeFetchingState,
        catchFetchingError,
        fetchingLoader,
        fetchingError,
    } = useLoadingState();

    const handleValidation = (isValid: boolean) => {
        dispatch({ type: 'SET_VALIDATED', payload: isValid });
    };

    const handleFormDataChange = (newData: Partial<FormState>) => {
        dispatch({ type: 'SET_FORM_DATA', payload: newData });
    };

    const handleFormErrorsChange = (newErrors: Partial<FormState>) => {
        dispatch({ type: 'SET_FORM_ERRORS', payload: newErrors });
    };

    return (
        <div className=''>
            <div className="h-[156px] bg-base-200 p-6 px-16 text-lg text-neutral font-semibold 
               flex items-center">
                <div className="w-1/2 max-w-4xl m-auto">
                    Report an issue
                </div>
            </div>
            <div className='mt-6 w-1/2 m-auto max-w-4xl p-6'>
                <ErrorBoundary>
                    <IssueTrackerFormV2 onSubmit={handleSubmit}
                        onFieldChanged={onFormFieldChange}
                        title={state.formData.title!}
                        description={state.formData.description!}
                        errors={state.formErrors}
                        loadingState={loadingState}
                        validated={state.validated} />
                </ErrorBoundary>
                {fetchingError()}
                {loadingState.data_state === DataState.completed && userAlert()}
            </div>
        </div>
    );

    function userAlert() {
        return (
            <div>
                <Alert variant={"success"} title={"Success!"} description={["Your issue has been successfully created."]} />
            </div>
        )
    }

    function handleSubmit(event: any) {
        const form = event.currentTarget;
        event.preventDefault();
        event.stopPropagation();
        createIssue()
        handleValidation(true);
    }

    function createIssue() {
        const userName: string = userStore.get("user").username;
        let data = {
            title: state.formData.title,
            user: userName,
            description: `${state.formData.description} - Submitted By: ${userName}`
        };
        // console.log(data)
        startFetchingState();
        fetchPost(new AssetURLs().issues_route(), data).then((data: any) => {
            completeFetchingState();
            handleFormDataChange({ title: '', description: '' });
        }).catch((err) => {
            catchFetchingError(err);
            handleFormErrorsChange(err.message);
        }
        );
    }

    function onFormFieldChange(e: any, field: string) {
        let update: any = {};
        update[field] = e.target.value;
        // console.log("on changed called: ", e, "field:", field);
        handleFormDataChange(update);
    }

}
