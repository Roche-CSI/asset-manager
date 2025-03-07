import React, { useState } from "react"
import { PaginationState } from '@tanstack/react-table'

interface Props {
    pageSize?: number;
}

export default function usePagination(props: Props) {
    const [{ pageIndex, pageSize }, setPagination] =
        useState<PaginationState>({
            pageIndex: 0,
            pageSize: props.pageSize ?? 10,
        })

    const pagination: PaginationState = React.useMemo(
        () => ({
            pageIndex,
            pageSize,
        }),
        [pageIndex, pageSize]
    )

    return { pagination, setPagination}
}