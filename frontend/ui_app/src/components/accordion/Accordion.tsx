import React, { useState } from 'react'
import AccordionItem, { AccordionItemObject } from './AccordionItem'

interface Props {
  itemsList: AccordionItemObject[];
}

const Accordion = (props: Props) => {
  const { itemsList } = props
  const [active, setActive] = useState(null)

  const handleToggle = (index: any) => {
    if (active === index) {
      setActive(null)
    } else {
      setActive(index)
    }
  }
  return (
    <div className='h-auto flex flex-col gap-7.5'>
      {itemsList.map((item: AccordionItemObject, index: number) => {
        return (
          <AccordionItem
            key={index}
            active={active}
            handleToggle={handleToggle}
            item={item}
          />
        )
      })}
    </div>
  )
}

export default Accordion
