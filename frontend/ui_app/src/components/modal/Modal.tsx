import React, { FunctionComponent } from 'react';
import "./breadcrumb.css";

interface Props {
  className?: string;
  children?: any;
}

const Modal: FunctionComponent<Props> = (props: Props) => {
  return (
    <div
      className={`
      fixed top-0 left-0 z-999999 flex h-full w-full items-center justify-center bg-black/70 px-4 py-5  
      overflow-auto` }>
      <div
        className={`w-3/4 h-full z-999999 overflow-auto rounded-lg bg-white p-4 text-center ${props.className}
        dark:bg-boxdark md:py-15 md:px-17.5`}
      >
        {props.children}
      </div>
    </div>

  )
}

export default Modal;
