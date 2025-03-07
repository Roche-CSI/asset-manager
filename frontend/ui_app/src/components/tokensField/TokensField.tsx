import React, { FunctionComponent } from 'react';

interface Props {
    tokenList: any[]; // - List of tokens to be displayed
    renderToken?: Function // - Component to display each token
    onDelete?: Function; // - Function when a token is deleted
    inputField?: Function; // - Component to be used as the input field
    onChange?: Function; // - Function when the input field changes
    className?: string; // - component class name
}

/** Input Field with tag/token capabilities */
const TokensField: FunctionComponent<Props> = (props: Props) => {

    const DeleteMarker = () => {
        return (
            <span className='flex items-center cursor-pointer pl-1 hover:text-danger'>
                <svg
                    width='12'
                    height='12'
                    viewBox='0 0 12 12'
                    fill='none'
                    xmlns='http://www.w3.org/2000/svg'
                >
                    <path
                        fillRule='evenodd'
                        clipRule='evenodd'
                        d='M9.35355 3.35355C9.54882 3.15829 9.54882 2.84171 9.35355 2.64645C9.15829 2.45118 8.84171 2.45118 8.64645 2.64645L6 5.29289L3.35355 2.64645C3.15829 2.45118 2.84171 2.45118 2.64645 2.64645C2.45118 2.84171 2.45118 3.15829 2.64645 3.35355L5.29289 6L2.64645 8.64645C2.45118 8.84171 2.45118 9.15829 2.64645 9.35355C2.84171 9.54882 3.15829 9.54882 3.35355 9.35355L6 6.70711L8.64645 9.35355C8.84171 9.54882 9.15829 9.54882 9.35355 9.35355C9.54882 9.15829 9.54882 8.84171 9.35355 8.64645L6.70711 6L9.35355 3.35355Z'
                        fill='currentColor'
                    ></path>
                </svg>
            </span>
        )
    }

    const defaultInputField = () => {
        return (
            <input
                name=''
                id=''
                className='absolute left-0 top-0 z-20 h-full w-full bg-transparent opacity-0'
                placeholder='Type here to add a token'
                onChange={(e) => props.onChange && props.onChange(e.target.value)}
            />
        )
    }

    const defaultClassName: string = 'flex flex-row items-center relative z-20 w-full rounded border border-stroke p-1.5 font-medium outline-none transition focus:border-primary active:border-primary dark:border-form-strokedark dark:bg-form-input'

    return (
        <div className={props.className ?? defaultClassName}>
            {props.tokenList.map((token: any, index: number) => {
                return (
                    <div key={index} className='m-0.5 flex items-center justify-center rounded border-[.5px] border-stroke bg-gray px-2 py-1 text-sm font-medium dark:border-strokedark dark:bg-white/30'>
                        {
                            props.renderToken ?
                                props.renderToken(token) : <span>{token}</span>
                        }
                        <div onClick={() => props.onDelete && props.onDelete(index)}>
                            <DeleteMarker />
                        </div>
                    </div>
                )
            })
            }
            {props.inputField ? props.inputField() : defaultInputField()}
        </div>
    )
}

export default TokensField;