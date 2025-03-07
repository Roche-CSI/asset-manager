import React, { useEffect } from 'react'
import { AssetClass } from "../../../servers/asset_server";
import { convertToCurrentTimeZone } from "../../../utils";
import { Link } from "react-router-dom";
import styles from "./class_table.module.scss";
import { DataTable } from "../dataTable"

const badge = (str: string) =>
  <button className='rounded-full bg-[#EFEFEF] p-1 text-xs font-normal text-[#212B36] ml-2'>
    {str}
  </button>


const headIcons = (header: string) => {
  switch (header) {
    case "Owner":
      return (
        <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 448 512">
          <path fill="#17a2b8" d="M304 128a80 80 0 1 0 -160 0 80 80 0 1 0 160 0zM96 128a128 128 0 1 1 256 0A128 128 0 1 1 96 128zM49.3 464H398.7c-8.9-63.3-63.3-112-129-112H178.3c-65.7 0-120.1 48.7-129 112zM0 482.3C0 383.8 79.8 304 178.3 304h91.4C368.2 304 448 383.8 448 482.3c0 16.4-13.3 29.7-29.7 29.7H29.7C13.3 512 0 498.7 0 482.3z" />
        </svg>
      )
    case "Created At":
      return (
        <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 448 512">
          <path d="M128 0c17.7 0 32 14.3 32 32V64H288V32c0-17.7 14.3-32 32-32s32 14.3 32 32V64h48c26.5 0 48 21.5 48 48v48H0V112C0 85.5 21.5 64 48 64H96V32c0-17.7 14.3-32 32-32zM0 192H448V464c0 26.5-21.5 48-48 48H48c-26.5 0-48-21.5-48-48V192zm64 80v32c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V272c0-8.8-7.2-16-16-16H80c-8.8 0-16 7.2-16 16zm128 0v32c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V272c0-8.8-7.2-16-16-16H208c-8.8 0-16 7.2-16 16zm144-16c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V272c0-8.8-7.2-16-16-16H336zM64 400v32c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V400c0-8.8-7.2-16-16-16H80c-8.8 0-16 7.2-16 16zm144-16c-8.8 0-16 7.2-16 16v32c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V400c0-8.8-7.2-16-16-16H208zm112 16v32c0 8.8 7.2 16 16 16h32c8.8 0 16-7.2 16-16V400c0-8.8-7.2-16-16-16H336c-8.8 0-16 7.2-16 16z"
            fill="#dc3545"
          />
        </svg>
      )
    case "Count":
      return (
        <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 512 512">
          <path fill='#6f42c1' d="M251.7 127.6l0 0c10.5 10.5 24.7 16.4 39.6 16.4H448c8.8 0 16 7.2 16 16v32H48V96c0-8.8 7.2-16 16-16H197.5c4.2 0 8.3 1.7 11.3 4.7l33.9-33.9L208.8 84.7l42.9 42.9zM48 240H464V416c0 8.8-7.2 16-16 16H64c-8.8 0-16-7.2-16-16V240zM285.7 93.7L242.7 50.7c-12-12-28.3-18.7-45.3-18.7H64C28.7 32 0 60.7 0 96V416c0 35.3 28.7 64 64 64H448c35.3 0 64-28.7 64-64V160c0-35.3-28.7-64-64-64H291.3c-2.1 0-4.2-.8-5.7-2.3z" />
        </svg>
      )
    default:
      return null
  }
}

const tableHeading = [
  'Asset Class',
  'Owner',
  'Created At',
  'Count',
]

const columns: any = [
  {
    select: 0,
    sortSequence: ['desc', 'asc'],
    headerClass: `${styles.bigHeader}`,
  },
  {
    select: 1,
    sortSequence: ['desc', 'asc'],
  },
  {
    select: 2,
    sortSequence: ['desc', 'asc'],
  },
  {
    select: 3,
    sortSequence: ['desc', 'asc'],
  },
]

const renderHead = (item: any, index: number, onCreate?: Function) => {
  return (
    <th key={index}>
      <div className='flex items-center gap-1.5'>
        {headIcons(item)}
        <div>{item}</div>
        <div className='inline-flex flex-col space-y-[2px]'>
          <span className='inline-block'>
            <svg
              className='fill-current'
              width='10'
              height='5'
              viewBox='0 0 10 5'
              fill='none'
              xmlns='http://www.w3.org/2000/svg'
            >
              <path d='M5 0L0 5H10L5 0Z' fill='' />
            </svg>
          </span>
          <span className='inline-block'>
            <svg
              className='fill-current'
              width='10'
              height='5'
              viewBox='0 0 10 5'
              fill='none'
              xmlns='http://www.w3.org/2000/svg'
            >
              <path
                d='M5 5L10 0L-4.37114e-07 8.74228e-07L5 5Z'
                fill=''
              />
            </svg>
          </span>
        </div>
      </div>
    </th>
  )
}

const renderBody = (item: any, index: number, projectId: string) => {
  return (
    <tr key={index}>
      <td>
        <Link to={`/asset_class?project_id=${projectId}&name=${item.name}`}>
          {item.title}
        </Link>
        {badge(item.name)}
      </td>
      <td>{item.owner}</td>
      <td>{convertToCurrentTimeZone(item.created_at, "date").toString()}</td>
      <td>{item.counter}</td>
    </tr>
  )
}

interface TableProps {
  classList: AssetClass[],
  projectId: string,
  onCreate?: Function
}

export default function ClassListDataTable(props: TableProps) {
  const onCreate = (event: any) => {
    console.log(event)
    props.onCreate && props.onCreate();
  }

  return (
    <>
      <DataTable
        paging={true}
        numsPerPage={20}
        perPageSelect={[10, 20, 30, ["All", -1]]}
        columns={columns}
        headData={tableHeading}
        renderHead={(item: any, index: number) => renderHead(item, index, onCreate)}
        bodyData={props.classList}
        renderBody={(item: any, index: number) => renderBody(item, index, props.projectId)}
        styles={styles}
      />
      {/* {message && <span style={{ padding: 50 }}>{message}</span>} */}
    </>
  )
}
