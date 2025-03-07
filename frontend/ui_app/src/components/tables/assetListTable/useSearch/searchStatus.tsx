import React from "react";
import { TokensField } from "../../../tokensField";
import { SearchObject } from "./searchForm";


interface Props {
    searchList: SearchObject[];
    setSearchList: Function;
    handleSearch: Function;
}


export default function SearchStatus(props: Props) {
    const { searchList, setSearchList, handleSearch } = props;

    // after each delete, refresh the search
    function handleDelete(idx: number) {
        let newSearchList: any[] = [...searchList]
        newSearchList.splice(idx, 1)
        setSearchList(newSearchList)
        handleSearch(newSearchList)
    }

    const renderToken = (token: any) => {
        return (<span className='flex flex-row'>
            {token.key !== "search_by" &&
                <span className='font-bold'>{token.key + ": "}</span>
            }
            <span className='mr-1'>{token.value}</span>
        </span>
        )
    }

    return (
        <div className="flex items-center h-9 px-1.5 mt-1.5 font-bold">
            <div className='flex flex-row items-center'>
                <span className='mr-1'>Showing result of</span>
                <div>
                    {searchList.length > 0 ?
                        <div>
                            <TokensField tokenList={searchList}
                                renderToken={renderToken}
                                onDelete={handleDelete}
                                inputField={() => <span></span>}
                                className="flex flex-row box-content" />
                        </div>
                        :
                        <span>all</span>
                    }
                </div>
            </div>
        </div>
    )
}