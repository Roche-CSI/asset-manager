import React, { ReactNode } from 'react'


interface MenuProps {
    items?: ReactNode[];
    customMenu?: ReactNode
}

const Menu = (props: MenuProps) => {

    const defaultMenu = (items: ReactNode[]) => (
        <ul className={'flex flex-col max-h-40'}>
            {items.map((item: ReactNode, index: number) => {
                return (
                    <li key={index}>
                        {item}
                    </li>
                )
            }
            )}
        </ul>
    )

    return (
        <div>
            {props.customMenu ? props.customMenu : defaultMenu(props.items ? props.items : [])}
        </div>
    )
}

export default Menu;
