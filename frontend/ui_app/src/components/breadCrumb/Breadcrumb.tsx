import React, { FunctionComponent } from 'react';
import "./breadcrumb.css";
import { Link } from 'react-router-dom'

export interface BreadcrumbItem {
  index: number;
  name: string;
  url: string;
}

interface Props {
  items: Array<BreadcrumbItem>;
  title?: string;
  children?: any;
}

const Title: FunctionComponent<Props> = ({ title, items, children }) => (
  <div className="flex flex-row items-center gap-3">
    <h2 className='text-title-md2 font-semibold !text-black dark:text-white'>
      {title ?? items[items.length - 1].name}
    </h2>
    {children}
  </div>
)

const toDashCase = (str: string) => {
    return str
        // Replace spaces and underscores with dashes
        .replace(/[\s_]+/g, '-')
        // Remove any leading or trailing dashes
        .replace(/^-+|-+$/g, '')
        // Convert all characters to lowercase
        .toLowerCase();
}

const BreadcrumbItems: FunctionComponent<Props> = ({ items }) => (
  <nav>
    <ol className='flex items-center gap-2 px-4'>
      {items.map((item: BreadcrumbItem, index: number) => {
        if (index === items.length - 1) return (
          <li key={index} className='!text-primary font-medium max-w-xs overflow-hidden whitespace-nowrap text-ellipsis'>
            {toDashCase(item.name)}
          </li>
        )
        return (
          <li key={index}>
            <Link className='font-medium' to={item.url}>{toDashCase(item.name)} /</Link>
          </li>
        )
      }
      )}
    </ol>
  </nav>
)

const Breadcrumb: FunctionComponent<Props> = (props: Props) => {
  return (
    <div className='mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between'>
      {/*<Title title={props.title} items={props.items} children={props.children} />*/}
      <BreadcrumbItems items={props.items} />
    </div>
  )
}

export default Breadcrumb;
