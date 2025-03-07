import React, { useEffect, useState } from 'react'
import { Asset, AssetClass } from "../../../servers/asset_server";
import { Link } from "react-router-dom";
import { convertToCurrentTimeZone, timeAgoString } from "../../../utils/dateUtils";
import "./reacttablefilter.css";
import { AssetClassIcon } from "../../assetClassBrowser";
import { ClassCategory } from "../../../pages/classListPage/ClassListPage";

import {
  Column,
  Table,
  useReactTable,
  ColumnFiltersState,
  getCoreRowModel,
  getFilteredRowModel,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFacetedMinMaxValues,
  getPaginationRowModel,
  sortingFns,
  getSortedRowModel,
  FilterFn,
  SortingFn,
  ColumnDef,
  flexRender,
  FilterFns,
} from '@tanstack/react-table'

import {
  RankingInfo,
  rankItem,
  compareItems,
} from '@tanstack/match-sorter-utils'

// import { makeData, Person } from './makeData'

declare module '@tanstack/table-core' {
  interface FilterFns {
    fuzzy: FilterFn<unknown>
  }
  interface FilterMeta {
    itemRank: RankingInfo
  }
}

const fuzzyFilter: FilterFn<any> = (row, columnId, value, addMeta) => {
  // Rank the item
  const itemRank = rankItem(row.getValue(columnId), value)

  // Store the itemRank info
  addMeta({
    itemRank,
  })

  // Return if the item should be filtered in/out
  return itemRank.passed
}

const fuzzySort: SortingFn<any> = (rowA, rowB, columnId) => {
  let dir = 0

  // Only sort by rank if the column has ranking information
  if (rowA.columnFiltersMeta[columnId]) {
    dir = compareItems(
      rowA.columnFiltersMeta[columnId]?.itemRank!,
      rowB.columnFiltersMeta[columnId]?.itemRank!
    )
  }

  // Provide an alphanumeric fallback for when the item ranks are equal
  return dir === 0 ? sortingFns.alphanumeric(rowA, rowB, columnId) : dir
}


interface TableProps {
  classList: AssetClass[],
  category: ClassCategory,
  projectId: string,
  onCreate?: Function,
  addToFavorite: Function,
  favoriteClasses?: any
}


const ClassListReactTable = (props: TableProps) => {
  const [data, setData] = useState<AssetClass[]>(props.classList)

  useEffect(() => {
    setData(props.classList.filter((item: AssetClass) => props.category.filterFunction(item)))
  }, [props.classList, props.category])

  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>(
    []
  )
  const [globalFilter, setGlobalFilter] = useState('')

  const [columnVisibility, setColumnVisibility] = useState({
    title: false, // Set to false to hide the column initially
  });

  const classTitle = (row: any) => {
    // console.log(row)
    return (
      <div className="flex flex-row space-x-2">
        <div className='pt-1.5 text-lg'>
          <AssetClassIcon classType={row.class_type} />
        </div>
        <div className='flex flex-col space-y-1'>
          <div className="!text-slate-800 text-xl hover:!text-primary">
            <Link to={`/asset_class?project_id=${props.projectId}&name=${row.name}`}>
              {row.title}
            </Link>
          </div>
          <span className="text-slate-400 text-sm pr-1">
            {row.description}
          </span>
        </div>
      </div>
    )
  }

  const updatedDate = (row: any) => convertToCurrentTimeZone(row.modified_at || row.created_at, "date").toString()

  const updateDuration = (row: any) => timeAgoString(convertToCurrentTimeZone(row.modified_at || row.created_at, "date")).toString()


  const starIcon = (assetClass: any) =>
    <svg onClick={() => props.addToFavorite(assetClass)}
      className="star-icon"
      xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 576 512">
      <path className="icon-path"
        d="M316.9 18C311.6 7 300.4 0 288.1 0s-23.4 7-28.8 18L195 150.3 51.4 171.5c-12 1.8-22 10.2-25.7 21.7s-.7 24.2 7.9 32.7L137.8 329 113.2 474.7c-2 12 3 24.2 12.9 31.3s23 8 33.8 2.3l128.3-68.5 128.3 68.5c10.8 5.7 23.9 4.9 33.8-2.3s14.9-19.3 12.9-31.3L438.5 329 542.7 225.9c8.6-8.5 11.7-21.2 7.9-32.7s-13.7-19.9-25.7-21.7L381.2 150.3 316.9 18z" />
    </svg>


  const unstarIcon = (assetClass: any) =>
    <svg onClick={() => props.addToFavorite(assetClass)}
      className="unstar-icon"
      xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 576 512">
      <path className="icon-path"
        d="M287.9 0c9.2 0 17.6 5.2 21.6 13.5l68.6 141.3 153.2 22.6c9 1.3 16.5 7.6 19.3 16.3s.5 18.1-5.9 24.5L433.6 328.4l26.2 155.6c1.5 9-2.2 18.1-9.6 23.5s-17.3 6-25.3 1.7l-137-73.2L151 509.1c-8.1 4.3-17.9 3.7-25.3-1.7s-11.2-14.5-9.7-23.5l26.2-155.6L31.1 218.2c-6.5-6.4-8.7-15.9-5.9-24.5s10.3-14.9 19.3-16.3l153.2-22.6L266.3 13.5C270.4 5.2 278.7 0 287.9 0zm0 79L235.4 187.2c-3.5 7.1-10.2 12.1-18.1 13.3L99 217.9 184.9 303c5.5 5.5 8.1 13.3 6.8 21L171.4 443.7l105.2-56.2c7.1-3.8 15.6-3.8 22.6 0l105.2 56.2L384.2 324.1c-1.3-7.7 1.2-15.5 6.8-21l85.9-85.1L358.6 200.5c-7.8-1.2-14.6-6.1-18.1-13.3L287.9 79z" />
    </svg>

  const renderFavorite = (row: any) => {
    return row.favorite ? starIcon(row) : unstarIcon(row)
  }

  const columns = React.useMemo<ColumnDef<AssetClass, any>[]>(
    () => [
      {
        accessorFn: row => row,
        accessorKey: 'classTitle',
        header: "Class Title",
        cell: info => classTitle(info.getValue()),
        footer: props => props.column.id,
        size: 650,
      },
      {
        accessorFn: row => row.title,
        accessorKey: 'title',
        header: "Class Title",
        cell: info => info.getValue(),
        footer: props => props.column.id,
        filterFn: 'fuzzy', // Make the column searchable
        size: 0,
        enableHiding: true, // Enable hiding for this column
      },
      {
        accessorFn: row => row.name,
        // cell: info => <div className="w-70 break-words">{info.getValue()}</div>,
        cell: info => info.getValue(),
        header: "Name",
        footer: props => props.column.id,
        size: 150,
      },
      {
        accessorFn: row => row.owner,
        // id: 'fullName',
        header: 'Owner',
        cell: info => info.getValue(),
        footer: props => props.column.id,
        filterFn: 'fuzzy',
        sortingFn: fuzzySort,
        size: 100,
      },
      {
        accessorFn: row => row,
        cell: info => updatedDate(info.getValue()),
        header: "Updated",
        footer: props => props.column.id,
        size: 100,
      },
      {
        accessorFn: row => row,
        cell: info => updateDuration(info.getValue()),
        header: "Duration",
        footer: props => props.column.id,
        size: 100,
      },
      // {
      //   accessorFn: row => row.class_type,
      //   cell: info => info.getValue(),
      //   header: "Type",
      //   footer: props => props.column.id,
      //   size: 150,
      // },
      {
        accessorFn: row => row.counter,
        cell: info => info.getValue(),
        header: "Assets",
        footer: props => props.column.id,
        size: 100,
      },
      {
        accessorFn: row => row,
        cell: info => renderFavorite(info.getValue()),
        header: "Favorite",
        footer: props => props.column.id,
        size: 100,
      },
    ],
    []
  )

  // const data: AssetClass[] = props.classList

  const table = useReactTable({
    data,
    columns,
    filterFns: {
      fuzzy: fuzzyFilter,
    },
    state: {
      columnFilters,
      globalFilter,
      columnVisibility,
    },
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    globalFilterFn: fuzzyFilter,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    getFacetedMinMaxValues: getFacetedMinMaxValues(),
    debugTable: true,
    debugHeaders: true,
    debugColumns: false,
    enableColumnFilters: false
  })

  React.useEffect(() => {
    if (table.getState().columnFilters[0]?.id === 'fullName') {
      if (table.getState().sorting[0]?.id !== 'fullName') {
        table.setSorting([{ id: 'fullName', desc: false }])
      }
    }
  }, [table.getState().columnFilters[0]?.id])

  return (
    <div className=' dark:border-strokedark dark:bg-boxdark'>
      <div className='data-table-container data-table-common data-table-two max-w-full overflow-x-auto'>
        <div className='datatable-header'>
          <div className="datatable-search !w-[30rem]">
            <div className="relative">
              <DebouncedInput
                value={globalFilter ?? ''}
                onChange={value => setGlobalFilter(String(value))}
                placeholder="Filter by asset name..."
              />
              <div className="w-6 h-6 absolute left-0 top-3 ml-4 cursor-pointer">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
                  <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
                </svg>
              </div>
            </div>
            {/* <DebouncedInput
              value={globalFilter ?? ''}
              onChange={value => setGlobalFilter(String(value))}
              placeholder="Filter by asset name..."
            /> */}
          </div>
          <label>
            <select
              value={table.getState().pagination.pageSize}
              onChange={e => {
                table.setPageSize(Number(e.target.value))
              }}
            >
              {[10, 20, 30, 40, 50].map(pageSize => (
                <option key={pageSize} value={pageSize}>
                  {pageSize}
                </option>
              ))}
            </select>
            {" Entries Per Page "}
          </label>
        </div>
        <table className='table w-full table-auto datatable-table' id='reactTableFilter'>
          <thead>
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => {
                  return (
                    <th key={header.id} colSpan={header.colSpan}
                      style={{
                        width: header.getSize()
                        // header.getSize() !== 150 ? header.getSize() : undefined,
                      }}
                      className='!font-satoshi !text-base !font-normal !text-body'>
                      {header.isPlaceholder ? null : (
                        <>
                          <div
                            {...{
                              className: header.column.getCanSort()
                                ? 'cursor-pointer select-none'
                                : '',
                              onClick: header.column.getToggleSortingHandler(),
                            }}
                          >
                            {flexRender(
                              header.column.columnDef.header,
                              header.getContext()
                            )}
                            {{
                              asc: ' ▲',
                              desc: ' ▼',
                            }[header.column.getIsSorted() as string] ?? null}
                          </div>
                          {header.column.getCanFilter() ? (
                            <div>
                              <Filter column={header.column} table={table} />
                            </div>
                          ) : null}
                        </>
                      )}
                    </th>
                  )
                })}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map(row => {
              return (
                <tr key={row.id}>
                  {row.getVisibleCells().map(cell => {
                    return (
                      <td key={cell.id} className='!text-base !text-body'
                        style={{
                          // width: cell.column.columnDef.width
                        }}>
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </td>
                    )
                  })}
                </tr>
              )
            })}
          </tbody>
        </table>
        <div className="datatable-footer">
          <div className="datatable-info">
            {`Showing ${table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1} 
            to ${Math.min(table.getFilteredRowModel().rows.length, (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize)} 
            of ${table.getFilteredRowModel().rows.length} entries`}
          </div>
          <div className="datatable-pagination">
            {/* <button
              onClick={() => table.setPageIndex(0)}
              disabled={!table.getCanPreviousPage()}
            >
              {'<<'}
            </button> */}
            <button
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
            >
              {'<'}
            </button>
            {
              Array.from({ length: table.getPageCount() }, (v: number, k: number) => k).map((z: number) => {
                return (
                  <button
                    key={z}
                    className={z === table.getState().pagination.pageIndex ? "datatable-active" : ""}
                    onClick={() => table.setPageIndex(z)}
                  >
                    {z + 1}
                  </button>
                )
              })
            }
            <button
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
            >
              {'>'}
            </button>
            {/* <button
              onClick={() => table.setPageIndex(table.getPageCount() - 1)}
              disabled={!table.getCanNextPage()}
            >
              {'>>'}
            </button> */}
          </div>
          {/* <div>
            <span className="flex items-center gap-1">
              <div>Page</div>
              <span>
                {table.getState().pagination.pageIndex + 1} of{' '}
                {table.getPageCount()}
              </span>
            </span>
            <span className="flex items-center gap-1">
              | Go to page:
              <input
                type="number"
                defaultValue={table.getState().pagination.pageIndex + 1}
                onChange={e => {
                  const page = e.target.value ? Number(e.target.value) - 1 : 0
                  table.setPageIndex(page)
                }}
                className="border p-1 rounded w-16"
              />
            </span>
          </div> */}
        </div>
        {/* <div>{table.getPrePaginationRowModel().rows.length} Rows</div>
        <div>
          <button onClick={() => rerender()}>Force Rerender</button>
        </div> */}
        {/* <div>
        <button onClick={() => refreshData()}>Refresh Data</button>
      </div> */}
        {/* <pre>{JSON.stringify(table.getState(), null, 2)}</pre> */}
      </div>
    </div>
  )
}

function Filter({
  column,
  table,
}: {
  column: Column<any, unknown>
  table: Table<any>
}) {
  const firstValue = table
    .getPreFilteredRowModel()
    .flatRows[0]?.getValue(column.id)

  const columnFilterValue = column.getFilterValue()

  const sortedUniqueValues = React.useMemo(
    () =>
      typeof firstValue === 'number'
        ? []
        : Array.from(column.getFacetedUniqueValues().keys()).sort(),
    [column.getFacetedUniqueValues()]
  )

  return typeof firstValue === 'number' ? (
    <div>
      <div className="flex space-x-2">
        <DebouncedInput
          type="number"
          min={Number(column.getFacetedMinMaxValues()?.[0] ?? '')}
          max={Number(column.getFacetedMinMaxValues()?.[1] ?? '')}
          value={(columnFilterValue as [number, number])?.[0] ?? ''}
          onChange={value =>
            column.setFilterValue((old: [number, number]) => [value, old?.[1]])
          }
          placeholder={`Min ${column.getFacetedMinMaxValues()?.[0]
            ? `(${column.getFacetedMinMaxValues()?.[0]})`
            : ''
            }`}
          className="w-24 border shadow rounded"
        />
        <DebouncedInput
          type="number"
          min={Number(column.getFacetedMinMaxValues()?.[0] ?? '')}
          max={Number(column.getFacetedMinMaxValues()?.[1] ?? '')}
          value={(columnFilterValue as [number, number])?.[1] ?? ''}
          onChange={value =>
            column.setFilterValue((old: [number, number]) => [old?.[0], value])
          }
          placeholder={`Max ${column.getFacetedMinMaxValues()?.[1]
            ? `(${column.getFacetedMinMaxValues()?.[1]})`
            : ''
            }`}
          className="w-24 border shadow rounded"
        />
      </div>
      <div className="h-1" />
    </div>
  ) : (
    <>
      <datalist id={column.id + 'list'}>
        {sortedUniqueValues.slice(0, 5000).map((value: any) => (
          <option value={value} key={value} />
        ))}
      </datalist>
      <DebouncedInput
        type="text"
        value={(columnFilterValue ?? '') as string}
        onChange={value => column.setFilterValue(value)}
        placeholder={`Search... (${column.getFacetedUniqueValues().size})`}
        className="w-36 border shadow rounded"
        list={column.id + 'list'}
      />
      <div className="h-1" />
    </>
  )
}

// A debounced input react component
function DebouncedInput({
  value: initialValue,
  onChange,
  debounce = 500,
  ...props
}: {
  value: string | number
  onChange: (value: string | number) => void
  debounce?: number
} & Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange'>) {
  const [value, setValue] = useState(initialValue)

  React.useEffect(() => {
    setValue(initialValue)
  }, [initialValue])

  React.useEffect(() => {
    const timeout = setTimeout(() => {
      onChange(value)
    }, debounce)

    return () => clearTimeout(timeout)
  }, [value])

  return (
    <input {...props} value={value} onChange={e => setValue(e.target.value)} />
  )
}


export default ClassListReactTable;