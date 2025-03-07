
export default interface FieldProps {
	label: string;
	fieldName: string;
	value: string | number;
	placeholder?: string;
	onChange: (value: string | number) => void;
	readOnly?: boolean;
	error?: string | null;
}