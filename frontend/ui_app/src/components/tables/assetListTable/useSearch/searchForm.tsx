import React, { useState } from "react";
import SearchIcon from '@mui/icons-material/Search';
import { TokensField } from "../../../tokensField";


interface TableProps {
    searchKey: string;
    setSearchKey: Function;
    onSubmit: Function;
}

export interface SearchObject {
    key: string;
    value: string;
}

export default function SearchForm(props: TableProps) {
    const { searchKey, setSearchKey } = props;
    const [searchList, setSearchList] = useState<any[]>([]);

    const onSearch = (input: string, callback?: Function) => {
        if (input) {
            input = !input.includes(":") ? `search_by: ${input}` : input
            const [newInput, _] = input.split(",")
            const pair: string[] = newInput.split(":")
            const newSearchObject: SearchObject = { key: pair[0].trim(), value: pair[1].trim() }
            const newsearchList: SearchObject[] = [...searchList, newSearchObject]
            setSearchList(newsearchList)
            setSearchKey('')
            if (callback) {
                setSearchList([])
                callback(newsearchList)
            }
        } else {
            if (callback) {
                setSearchList([])
                callback(searchList)
            }
        }
    }

    function handleDelete(idx: number) {
        setSearchList((oldsearchList: SearchObject[]) => {
            let newsearchList = [...oldsearchList]
            newsearchList.splice(idx, 1)
            return newsearchList
        })
    }

    const handleKeyDown = (event: any) => {
        if (event.key === 'Enter') {
            const searchInput: string = event.target.value
            onSearch(searchInput, props.onSubmit)
        }
    }

    function onChange(searchInput: string) {
        // setMessage("")
        // setError("")
        setSearchKey(searchInput)
        if (searchInput.includes(",")) { // detect comma
            onSearch(searchInput)
            return
        }
    }

    const inputField = () => {
        return (
            <div className="w-full flex flex-row items-center justify-around ml-1">
                <input type="text"
                    className='w-11/12 z-20 bg-transparent border-none focus:outline-none'
                    value={searchKey}
                    placeholder="Type a keyword... or type owner: abc, alias: xyz, seq_id: 00 to refine your search"
                    onChange={(e: any) => onChange(e.target.value)}
                    onKeyDown={(e: any) => handleKeyDown(e)} />
                <SearchIcon onClick={() => onSearch(searchKey, props.onSubmit)}
                    className='w-1/12 !text-3xl mx-1 p-1 cursor-pointer' />
            </div>
        )
    }

    const renderToken = (token: SearchObject) => {
        return (
            <span className='flex flex-row'>
                {token.key !== "search_by" &&
                    <span className='font-bold'>{token.key + ": "}</span>
                }
                <span className='ml-1'>{token.value}</span>
            </span>
        )
    }

    return (
        <div className="h-12 w-full flex flex-row items-center">
            <TokensField
                tokenList={searchList}
                renderToken={renderToken}
                onDelete={handleDelete}
                inputField={inputField} />
        </div>
    )
}