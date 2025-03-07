import React from "react";

interface Props {
  value: string | number
  onChange: (value: string | number) => void
  debounce?: number
}

// A debounced input react component
function DebouncedInput({
  value: initialValue,
  onChange,
  debounce = 500,
  ...props
}: Props & Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange'>) {
  const [value, setValue] = React.useState(initialValue)

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

export default DebouncedInput;